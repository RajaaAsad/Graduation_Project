"""Check public candidates, the Git index, and reachable history without leaking values."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRET_PATTERNS = (
    re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"AKIA[A-Z0-9]{16}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(
        rb"(?i)(?:api[_-]?key|token|password|secret)\s*[:=]\s*['\"][A-Za-z0-9_+/=-]{24,}['\"]"
    ),
)
PRIVATE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".safetensors",
    ".bin",
    ".pt",
    ".pth",
    ".csv",
    ".xlsx",
    ".docx",
    ".pdf",
}
PRIVATE_PARTS = {
    ".vercel",
    ".aws",
    ".codex",
    ".agents",
    "__pycache__",
    "output",
    ".venv",
    "venv",
    ".ruff_cache",
    ".pytest_cache",
    "build",
    "dist",
}
SKIP_PARTS = PRIVATE_PARTS | {".git"}


def inspect_content(name: str, content: bytes) -> list[str]:
    """Return only issue types and filenames; never print matching content."""
    issues = []
    path = Path(name)
    if (
        path.name.startswith(".env") and path.name != ".env.example"
    ) or path.name == "secrets.toml":
        issues.append(f"Private configuration: {name}")
    if (
        path.suffix in PRIVATE_SUFFIXES
        or PRIVATE_PARTS.intersection(path.parts)
        or any(part.endswith(".egg-info") for part in path.parts)
    ):
        issues.append(f"Private or generated artifact: {name}")
    if len(content) > 10_000_000:
        issues.append(f"Oversized public file: {name}")
    if any(pattern.search(content) for pattern in SECRET_PATTERNS):
        issues.append(f"Possible credential (value redacted): {name}")
    return issues


def check_release(root: Path, *, history: bool = True, all_files: bool = False) -> list[str]:
    """Scan public files plus tracked files even when .gitignore excludes them."""
    git = ["git", "-c", "safe.directory=" + root.as_posix(), "-C", str(root)]
    issues = []
    repository = (root / ".git").exists()
    if repository:

        def run(*args: str) -> bytes:
            result = subprocess.run(git + list(args), check=True, capture_output=True)
            return result.stdout

        tracked = run("ls-files", "-z").decode().split("\0")
        candidates = (
            run("ls-files", "--cached", "--others", "--exclude-standard", "-z").decode().split("\0")
        )
        for name in filter(None, set(tracked)):
            issues.extend(
                "INDEX: " + issue for issue in inspect_content(name, run("show", ":" + name))
            )
        if history:
            # Scan every unique historical blob. Deleted files can still leak credentials.
            revisions = run("rev-list", "--all").decode().splitlines()
            seen = set()
            for revision in revisions:
                for entry in run("ls-tree", "-rz", revision).split(b"\0"):
                    if not entry:
                        continue
                    metadata, name_bytes = entry.split(b"\t", 1)
                    _, kind, object_id = metadata.split()
                    if kind != b"blob" or object_id in seen:
                        continue
                    seen.add(object_id)
                    content = run("cat-file", "blob", object_id.decode())
                    name = name_bytes.decode(errors="replace")
                    issues.extend("HISTORY: " + issue for issue in inspect_content(name, content))
    else:
        candidates = [
            str(p.relative_to(root))
            for p in root.rglob("*")
            if p.is_file()
            and not SKIP_PARTS.intersection(p.relative_to(root).parts)
            and not any(part.endswith(".egg-info") for part in p.relative_to(root).parts)
        ]
    if all_files:
        # Manual uploads can include ignored files, so inspect those as well.
        candidates = [
            str(path.relative_to(root))
            for path in root.rglob("*")
            if path.is_file() and ".git" not in path.relative_to(root).parts
        ]
    for name in filter(None, set(candidates)):
        path = root / name
        # Untracked local secrets are intentionally excluded; tracked secrets are scanned above.
        if (
            not all_files
            and not repository
            and (path.name == ".env" or path.name == "secrets.toml")
        ):
            continue
        if path.is_file():
            issues.extend(inspect_content(name, path.read_bytes()))
    return sorted(set(issues))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--all-files", action="store_true", help="Also check ignored files before a manual upload."
    )
    args = parser.parse_args()
    try:
        issues = check_release(args.root.resolve(), all_files=args.all_files)
    except (OSError, subprocess.CalledProcessError):
        print("Release check failed to read files or Git metadata; publication is blocked.")
        return 1
    if issues:
        print("Release check failed:")
        for issue in issues:
            print("- " + issue)
        return 1
    print(
        "Release check passed. No detected credentials or private artifacts in public candidates."
    )
    print("Pattern checks cannot prove the absence of all secrets; review the staged diff as well.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
