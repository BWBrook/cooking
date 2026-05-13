#!/usr/bin/env python3
"""Build recipe/research EPUBs and optionally send them to Kindle."""

from __future__ import annotations

import argparse
import os
import re
import smtplib
import ssl
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr
from getpass import getpass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCAL_CONFIG = ROOT / ".cooking.local.yml"
EXAMPLE_CONFIG = ROOT / "config" / "kindle.example.yml"
CREATIVE_WRITER_CONFIG = Path(
    "/Users/bwbrook/games/creative-writer/.creative-writer.local.yml"
)
LOCAL_CONFIG_ENV = "COOKING_LOCAL_CONFIG"
DEFAULT_KEYCHAIN_SERVICE = "creative-writer/gmail-smtp"


class CookingKindleError(RuntimeError):
    """Expected command-line failure."""


@dataclass(frozen=True)
class BuiltEpub:
    source_files: list[Path]
    title: str
    slug: str
    epub_path: Path


def fail(message: str) -> None:
    raise CookingKindleError(message)


def parse_scalar(value: str) -> str | int:
    value = value.strip()
    if not value:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if value.isdigit():
        return int(value)
    return value


def load_simple_yaml(path: Path) -> dict[str, dict[str, str | int]]:
    """Load the tiny two-level config schema without a YAML dependency."""

    data: dict[str, dict[str, str | int]] = {}
    section: str | None = None
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not raw.startswith(" ") and line.endswith(":"):
            section = line[:-1].strip()
            data[section] = {}
            continue
        if section is None:
            fail(f"Invalid config at {path}:{line_no}: expected a section header.")
        if ":" not in line:
            fail(f"Invalid config at {path}:{line_no}: expected key/value.")
        key, value = line.split(":", 1)
        data[section][key.strip()] = parse_scalar(value)
    return data


def dump_simple_yaml(data: dict[str, dict[str, str | int]], path: Path) -> None:
    lines: list[str] = []
    for section in ("kindle", "smtp"):
        lines.append(f"{section}:")
        for key, value in data[section].items():
            if isinstance(value, int):
                lines.append(f"  {key}: {value}")
            else:
                escaped = str(value).replace('"', '\\"')
                lines.append(f'  {key}: "{escaped}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def local_config_path() -> Path:
    override = os.environ.get(LOCAL_CONFIG_ENV)
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            path = ROOT / path
        return path.resolve()
    return DEFAULT_LOCAL_CONFIG


def load_config() -> tuple[Path, dict[str, dict[str, str | int]]]:
    path = local_config_path()
    if not path.exists():
        fail(
            "Missing local Kindle delivery config.\n"
            f"Expected: {path}\n"
            f"Create it with: make kindle-init-config\n"
            f"Or copy/edit: {EXAMPLE_CONFIG}"
        )
    config = load_simple_yaml(path)
    for section in ("kindle", "smtp"):
        if section not in config:
            fail(f"Config {path} is missing required `{section}` section.")
    return path, config


def init_config() -> Path:
    target = local_config_path()
    if target.exists():
        print(f"Local config already exists: {target}")
        return target

    if CREATIVE_WRITER_CONFIG.exists():
        config = load_simple_yaml(CREATIVE_WRITER_CONFIG)
        config.setdefault("kindle", {})
        config.setdefault("smtp", {})
        config["kindle"]["sender_name"] = "Cooking Notebook"
        config["kindle"]["subject_prefix"] = "Cooking: "
        config["smtp"]["password_env"] = "COOKING_SMTP_PASSWORD"
        config["smtp"].setdefault("keychain_service", DEFAULT_KEYCHAIN_SERVICE)
        dump_simple_yaml(config, target)
        print(f"Created local config from creative-writer settings: {target}")
        print("No SMTP password was copied; the existing Keychain service can be reused.")
        return target

    config = load_simple_yaml(EXAMPLE_CONFIG)
    dump_simple_yaml(config, target)
    print(f"Created local config from example: {target}")
    print("Edit the Kindle address and sender details before sending.")
    return target


def keychain_account(smtp: dict[str, str | int]) -> str:
    account = str(smtp.get("keychain_account") or "").strip()
    return account or str(smtp.get("username") or "").strip()


def read_keychain_password(service: str, account: str) -> str | None:
    command = [
        "security",
        "find-generic-password",
        "-w",
        "-s",
        service,
        "-a",
        account,
    ]
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        fail("The macOS `security` tool is not available.")
        raise AssertionError from exc
    except subprocess.CalledProcessError:
        return None
    password = completed.stdout.strip()
    return password or None


def resolve_smtp_password(smtp: dict[str, str | int]) -> tuple[str, str]:
    env_name = str(smtp.get("password_env") or "COOKING_SMTP_PASSWORD").strip()
    if env_name:
        env_value = os.environ.get(env_name)
        if env_value:
            return env_value, f"env:{env_name}"

    service = str(smtp.get("keychain_service") or DEFAULT_KEYCHAIN_SERVICE).strip()
    account = keychain_account(smtp)
    if service and account:
        password = read_keychain_password(service, account)
        if password:
            return password, f"keychain:{service}:{account}"

    fail(
        "No SMTP password is configured for Kindle delivery.\n"
        f"Set {env_name} in the environment or run `make kindle-store-password`."
    )
    raise AssertionError("unreachable")


def store_smtp_password(password: str | None = None) -> str:
    _, config = load_config()
    smtp = config["smtp"]
    service = str(smtp.get("keychain_service") or DEFAULT_KEYCHAIN_SERVICE)
    account = keychain_account(smtp)
    if not account:
        fail("SMTP keychain account/username is not configured.")
    secret = password if password is not None else getpass(f"SMTP password for {account}: ")
    if not secret.strip():
        fail("No SMTP password was provided.")
    command = [
        "security",
        "add-generic-password",
        "-U",
        "-a",
        account,
        "-s",
        service,
        "-w",
        secret,
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)
    print(f"Stored password in Keychain service `{service}` for `{account}`.")
    return f"{service}:{account}"


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "cooking-note"


def strip_yaml_front_matter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            after = text.find("\n", end + 4)
            return text[after + 1 :] if after != -1 else ""
    return text


def extract_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    block = text[4:end]
    data: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = str(parse_scalar(value))
    return data


def title_for_file(path: Path, text: str) -> str:
    front = extract_front_matter(text)
    if front.get("title"):
        return front["title"]
    for line in strip_yaml_front_matter(text).splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()


def find_linked_research(text: str, source_path: Path) -> list[Path]:
    paths: list[Path] = []
    for match in re.finditer(r"research/[A-Za-z0-9_.\-/]+\.md", text):
        path = (ROOT / match.group(0)).resolve()
        if path.exists() and path != source_path.resolve() and path not in paths:
            paths.append(path)
    return paths


def prepare_markdown(source: Path, include_linked_research: bool) -> tuple[str, str, list[Path]]:
    source = source.resolve()
    if not source.exists():
        fail(f"Source markdown does not exist: {source}")
    if ROOT not in source.parents and source != ROOT:
        fail(f"Source must be inside this repo: {source}")

    text = source.read_text(encoding="utf-8")
    title = title_for_file(source, text)
    body_parts = [strip_yaml_front_matter(text).strip()]
    sources = [source]

    if include_linked_research:
        linked = find_linked_research(text, source)
        if linked:
            body_parts.append("# Supporting Research")
            for research_path in linked:
                research_text = strip_yaml_front_matter(
                    research_path.read_text(encoding="utf-8")
                ).strip()
                body_parts.append(research_text)
                sources.append(research_path)

    combined = "\n\n".join(part for part in body_parts if part) + "\n"
    return title, combined, sources


def build_epub(file_arg: str, include_linked_research: bool) -> BuiltEpub:
    if not file_arg.strip():
        fail("Pass FILE=path/to/recipe.md or --file path/to/recipe.md.")
    source = (ROOT / file_arg).resolve() if not Path(file_arg).is_absolute() else Path(file_arg).resolve()
    title, markdown, sources = prepare_markdown(source, include_linked_research)
    slug = slugify(title)
    output_dir = ROOT / "build" / "kindle" / slug
    output_dir.mkdir(parents=True, exist_ok=True)
    epub_path = output_dir / f"{slug}.epub"

    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as tmp:
        tmp.write(markdown)
        tmp_path = Path(tmp.name)

    try:
        command = [
            "pandoc",
            str(tmp_path),
            "--from",
            "markdown+yaml_metadata_block",
            "--to",
            "epub3",
            "--standalone",
            "--metadata",
            f"title={title}",
            "--metadata",
            "author=Barry W. Brook",
            "--output",
            str(epub_path),
        ]
        subprocess.run(command, check=True, cwd=ROOT)
    except FileNotFoundError as exc:
        fail("`pandoc` is required to build EPUB files and was not found on PATH.")
        raise AssertionError from exc
    finally:
        tmp_path.unlink(missing_ok=True)

    report_path = output_dir / "build-report.md"
    report_path.write_text(
        "\n".join(
            [
                f"# EPUB Build: {title}",
                "",
                f"- Built (UTC): `{datetime.now(timezone.utc).isoformat()}`",
                f"- EPUB: `{epub_path}`",
                "- Sources:",
                *[f"  - `{path.relative_to(ROOT)}`" for path in sources],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Built EPUB: {epub_path}")
    return BuiltEpub(sources, title, slug, epub_path)


def delivery_report_path(slug: str) -> Path:
    report_dir = ROOT / "build" / "kindle" / slug / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir / "kindle-delivery.md"


def write_delivery_report(
    built: BuiltEpub,
    config_path: Path,
    config: dict[str, dict[str, str | int]],
    password_source: str,
    status: str,
    note: str,
) -> Path:
    kindle = config["kindle"]
    smtp = config["smtp"]
    path = delivery_report_path(built.slug)
    path.write_text(
        "\n".join(
            [
                f"# Kindle Delivery: {built.title}",
                "",
                f"- Status: **{status}**",
                f"- Timestamp (UTC): `{datetime.now(timezone.utc).isoformat()}`",
                f"- Attachment: `{built.epub_path}`",
                f"- Local config: `{config_path}`",
                f"- Recipient: `{kindle.get('send_to')}`",
                f"- Sender: `{kindle.get('sender')}`",
                f"- SMTP: `{smtp.get('host')}:{smtp.get('port')}` (`{smtp.get('security')}`)",
                f"- Password source: `{password_source}`",
                f"- Note: {note}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def preflight(file_arg: str, include_linked_research: bool) -> None:
    built = build_epub(file_arg, include_linked_research)
    config_path, config = load_config()
    _, password_source = resolve_smtp_password(config["smtp"])
    report = write_delivery_report(
        built,
        config_path,
        config,
        password_source,
        "READY",
        "EPUB built successfully and SMTP credentials resolved. No email sent.",
    )
    print(f"Kindle preflight ready: {report}")


def send(file_arg: str, include_linked_research: bool) -> None:
    built = build_epub(file_arg, include_linked_research)
    config_path, config = load_config()
    password, password_source = resolve_smtp_password(config["smtp"])
    kindle = config["kindle"]
    smtp_config = config["smtp"]

    subject = f"{kindle.get('subject_prefix', '')}{built.title}"
    message = EmailMessage()
    message["From"] = formataddr(
        (str(kindle.get("sender_name") or "Cooking Notebook"), str(kindle["sender"]))
    )
    message["To"] = str(kindle["send_to"])
    message["Subject"] = subject
    message.set_content(
        f"Cooking Notebook is sending '{built.title}' as an EPUB attachment."
    )
    message.add_attachment(
        built.epub_path.read_bytes(),
        maintype="application",
        subtype="epub+zip",
        filename=built.epub_path.name,
    )

    host = str(smtp_config.get("host") or "smtp.gmail.com")
    port = int(smtp_config.get("port") or 465)
    security = str(smtp_config.get("security") or "ssl")
    username = str(smtp_config["username"])

    context = ssl.create_default_context()
    if security == "ssl":
        with smtplib.SMTP_SSL(host, port, context=context) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
    elif security == "starttls":
        with smtplib.SMTP(host, port) as smtp:
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(message)
    else:
        fail("SMTP security must be `ssl` or `starttls`.")

    report = write_delivery_report(
        built,
        config_path,
        config,
        password_source,
        "SENT",
        "EPUB emailed to the configured Send-to-Kindle address.",
    )
    print(f"Sent EPUB to Kindle: {report}")


def list_markdown() -> None:
    for folder in ("recipes", "research"):
        for path in sorted((ROOT / folder).rglob("*.md")):
            relative = path.relative_to(ROOT)
            if path.name == "README.md":
                continue
            if relative == Path("recipes/ingest.md"):
                continue
            if "templates" in relative.parts:
                continue
            print(relative)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_file_args(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--file", required=True, help="Recipe or research Markdown file.")
        subparser.add_argument(
            "--include-linked-research",
            action="store_true",
            help="Append linked research notes found in the source Markdown.",
        )

    add_file_args(subparsers.add_parser("epub"))
    add_file_args(subparsers.add_parser("kindle-preflight"))
    add_file_args(subparsers.add_parser("kindle"))
    subparsers.add_parser("kindle-store-password")
    subparsers.add_parser("init-config")
    subparsers.add_parser("list")

    args = parser.parse_args(argv)
    try:
        if args.command == "epub":
            build_epub(args.file, args.include_linked_research)
        elif args.command == "kindle-preflight":
            preflight(args.file, args.include_linked_research)
        elif args.command == "kindle":
            send(args.file, args.include_linked_research)
        elif args.command == "kindle-store-password":
            store_smtp_password()
        elif args.command == "init-config":
            init_config()
        elif args.command == "list":
            list_markdown()
        else:
            parser.error(f"Unknown command: {args.command}")
    except CookingKindleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        details = exc.stderr.decode() if isinstance(exc.stderr, bytes) else exc.stderr
        print(f"error: command failed: {exc.cmd}\n{details or ''}", file=sys.stderr)
        return exc.returncode or 1
    except smtplib.SMTPException as exc:
        print(f"error: SMTP rejected the Kindle delivery attempt: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
