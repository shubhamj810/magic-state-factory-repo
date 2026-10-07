"""Turn a "Submit a factory" issue into a folder under community_contributions/submissions/.

Run by .github/workflows/submission.yml.  It reads the issue from the event
payload (GITHUB_EVENT_PATH), never from the command line, and writes

    community_contributions/submissions/YYYY-MM-DD_<login>_issue-<N>/
        description.txt      every field of the form, as the contributor typed it
        attachments/         files dragged into the form, downloaded as they are

The issue text is untrusted: it is only ever written to files.  Attachments are
fetched only from GitHub's own attachment host, at most MAX_FILES of at most
MAX_BYTES each, under sanitised names.  Nothing submitted is executed.

The folder's path is written to GITHUB_OUTPUT as ``folder``.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBMISSIONS = ROOT / "community_contributions" / "submissions"
ATTACHMENT = re.compile(r"https://github\.com/user-attachments/(?:files|assets)/[A-Za-z0-9._/%-]+")
MAX_FILES = 20
MAX_BYTES = 25 * 1024 * 1024
TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif", "image/svg+xml": ".svg",
         "application/pdf": ".pdf", "text/plain": ".txt", "text/csv": ".csv",
         "application/json": ".json", "application/zip": ".zip"}


def safe(name: str, fallback: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")[:100]
    return name or fallback


def sections(body: str) -> list[tuple[str, str]]:
    """An issue form's body is '### Label' headings, each followed by its answer."""
    out = []
    for block in re.split(r"^### ", body or "", flags=re.M)[1:]:
        label, _, value = block.partition("\n")
        value = value.strip()
        out.append((label.strip(), "" if value == "_No response_" else value))
    return out


def download(url: str, folder: Path, index: int) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "msfc-submission"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read(MAX_BYTES + 1)
        kind = (response.headers.get("Content-Type") or "").split(";")[0].strip()
    if len(data) > MAX_BYTES:
        raise ValueError("larger than 25 MB")
    last = url.rstrip("/").rsplit("/", 1)[-1]
    name = safe(urllib.request.unquote(last), f"attachment-{index}")
    if "." not in name:
        name += TYPES.get(kind, "")
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / name
    while target.exists():
        target = folder / f"{index}-{name}"
        index += 1
    target.write_bytes(data)
    return target.name


def main() -> int:
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    issue = event["issue"]
    number, login = int(issue["number"]), safe(issue["user"]["login"], "anonymous")
    date = issue["created_at"][:10]
    folder = SUBMISSIONS / f"{date}_{login}_issue-{number}"
    folder.mkdir(parents=True, exist_ok=True)

    body = issue.get("body") or ""
    fields = sections(body) or [("Submission", body.strip())]
    lines = [f"Submitted through issue #{number} by @{issue['user']['login']} on {date}.",
             issue["html_url"], ""]
    for label, value in fields:
        lines += [label, "-" * len(label), value or "(left blank)", ""]

    saved, failed = [], []
    for i, url in enumerate(dict.fromkeys(ATTACHMENT.findall(body))):
        if i >= MAX_FILES:
            failed.append(f"{url}: more than {MAX_FILES} files, not downloaded")
            continue
        try:
            saved.append(download(url, folder / "attachments", i + 1))
        except Exception as error:     # keep going: the text is what matters most
            failed.append(f"{url}: {error}")
    if saved:
        lines += ["Attachments", "-----------"] + [f"attachments/{name}" for name in saved] + [""]
    if failed:
        lines += ["Not downloaded", "--------------"] + failed + [""]
    (folder / "description.txt").write_text("\n".join(lines), encoding="utf-8")

    relative = folder.relative_to(ROOT).as_posix()
    print(f"wrote {relative}: description.txt and {len(saved)} attachment(s)"
          + (f", {len(failed)} not downloaded" if failed else ""))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
            out.write(f"folder={relative}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
