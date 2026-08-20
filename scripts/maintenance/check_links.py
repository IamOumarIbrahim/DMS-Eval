"""Check repository Markdown, HTML, and LaTeX references for broken targets."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {".md", ".tex", ".html", ".htm"}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
HTML_LINK = re.compile(r"(?:href|src)=[\"']([^\"']+)[\"']", re.IGNORECASE)
INCLUDE_GRAPHICS = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
GRAPHICS_PATH = re.compile(r"\\graphicspath\{((?:\{[^}]+\})+)\}")
LATEX_FILE = re.compile(r"\\(?:bibliography|bibliographystyle)\{([^}]+)\}")
IF_FILE_EXISTS = re.compile(r"\\IfFileExists\{([^}]+)\}")
EXTERNAL_SCHEMES = {"http", "https"}


def repository_files() -> list[Path]:
    command = ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"]
    result = subprocess.run(command, cwd=REPO_ROOT, check=True, capture_output=True)
    paths = result.stdout.decode("utf-8").split("\0")
    return sorted(
        path
        for raw in paths
        if raw and (path := REPO_ROOT / raw).is_file() and path.suffix.lower() in TEXT_SUFFIXES
    )


def clean_markdown_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    return target.split(maxsplit=1)[0] if target else ""


def local_candidates(source: Path, raw_target: str, kind: str, graphics_dirs: list[Path]) -> list[Path]:
    target = unquote(raw_target.split("#", 1)[0].split("?", 1)[0])
    if not target:
        return []
    base = source.parent / target
    if kind == "graphics":
        extensions = ("", ".png", ".jpg", ".jpeg", ".pdf")
        return [directory / f"{target}{extension}" for directory in graphics_dirs for extension in extensions]
    if kind == "latex":
        extensions = ("", ".bib", ".bst", ".cls")
        return [Path(f"{base}{extension}") for extension in extensions]
    return [base]


def references(source: Path) -> tuple[list[tuple[str, str, int]], list[Path], set[str]]:
    text = source.read_text(encoding="utf-8", errors="replace")
    found: list[tuple[str, str, int]] = []
    for pattern in (MARKDOWN_LINK, HTML_LINK):
        for match in pattern.finditer(text):
            found.append(("link", clean_markdown_target(match.group(1)), text.count("\n", 0, match.start()) + 1))
    graphics_dirs = [source.parent]
    for match in GRAPHICS_PATH.finditer(text):
        graphics_dirs.extend(source.parent / item for item in re.findall(r"\{([^}]+)\}", match.group(1)))
    for match in INCLUDE_GRAPHICS.finditer(text):
        found.append(("graphics", match.group(1), text.count("\n", 0, match.start()) + 1))
    for match in LATEX_FILE.finditer(text):
        for item in match.group(1).split(","):
            found.append(("latex", item.strip(), text.count("\n", 0, match.start()) + 1))
    guarded = {match.group(1) for match in IF_FILE_EXISTS.finditer(text)}
    return found, graphics_dirs, guarded


def check_external(url: str, timeout: float) -> str | None:
    encoded_url = quote(url, safe=":/?#[]@!$&'()*+,;=%")
    request = Request(encoded_url, headers={"User-Agent": "DMS-Eval-link-check/1.0"}, method="HEAD")
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status < 400:
                return None
    except HTTPError as exc:
        if exc.code in {401, 403, 405, 406, 429}:
            return None
        if exc.code not in {404, 410}:
            return f"HTTP {exc.code}"
        return f"HTTP {exc.code}"
    except (URLError, TimeoutError, OSError, UnicodeError) as exc:
        return str(exc)
    return "unreachable"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external", action="store_true", help="Also verify HTTP(S) targets")
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    broken: list[str] = []
    external_locations: dict[str, list[str]] = {}
    checked_local = 0
    for source in repository_files():
        found, graphics_dirs, guarded = references(source)
        for kind, target, line in found:
            if not target or target.startswith(("#", "mailto:", "data:", "javascript:")):
                continue
            parsed = urlparse(target)
            location = f"{source.relative_to(REPO_ROOT).as_posix()}:{line}"
            if parsed.scheme in EXTERNAL_SCHEMES:
                external_locations.setdefault(target, []).append(location)
                continue
            candidates = local_candidates(source, target, kind, graphics_dirs)
            checked_local += 1
            guarded_missing = kind == "graphics" and any(target == item or target in item for item in guarded)
            if candidates and not any(candidate.resolve().exists() for candidate in candidates) and not guarded_missing:
                broken.append(f"{location} -> {target}")

    checked_external = 0
    if args.external and external_locations:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(check_external, url, args.timeout): url for url in external_locations}
            for future in as_completed(futures):
                url = futures[future]
                checked_external += 1
                failure = future.result()
                if failure:
                    locations = ", ".join(external_locations[url])
                    broken.append(f"{locations} -> {url} ({failure})")

    print(
        f"Link audit: {checked_local} local targets, "
        f"{checked_external}/{len(external_locations)} external targets checked, {len(broken)} broken"
    )
    for failure in broken:
        print(f"BROKEN: {failure}", file=sys.stderr)
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
