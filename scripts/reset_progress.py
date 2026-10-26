"""Reset the learning record back to day 1.

Run:
    .venv\\Scripts\\python.exe scripts\\reset_progress.py --dry-run
    .venv\\Scripts\\python.exe scripts\\reset_progress.py --yes
    .venv\\Scripts\\python.exe scripts\\reset_progress.py --yes --all

Every file it replaces is first copied to ``<name>.<timestamp>.bak`` beside the
original, so a wrong reset is one copy away from being undone. The script obeys
``LAKSH_DATA_DIR`` / ``DEVI_DATA_DIR``, so it also works against a mounted
volume; it prints the data directory before touching anything.

What counts as progress: XP, exams, quizzes, debriefs, labs, drills, mastered
gates, watched videos, desk rounds, the streak and, with ``--all``, the profile.
"""
import argparse
import copy
import json
import os
import shutil
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.focus import DEFAULT_STATE, FOCUS_FILE  # noqa: E402
from lib.paths import DATA_DIR  # noqa: E402
from lib.storage import DEFAULT_PROFILE, DEFAULT_PROGRESS, PROFILE_FILE, PROGRESS_FILE  # noqa: E402


def _load(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _backup(path, stamp):
    if not os.path.exists(path):
        return None
    target = f"{path}.{stamp}.bak"
    shutil.copy2(path, target)
    return target


def _write(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _summary(progress):
    if not progress:
        return "no record"
    exams = progress.get("exam_scores", {})
    return (
        f"xp {progress.get('xp', 0)} | exams {len(exams)}"
        f" | quizzes {len(progress.get('quiz_scores', {}))}"
        f" | labs {len(progress.get('lab_runs', []))}"
        f" | start {progress.get('started_at') or '-'}"
    )


def main():
    parser = argparse.ArgumentParser(description="Reset the Laksh learning record to day 1.")
    parser.add_argument("-y", "--yes", action="store_true", help="skip the confirmation prompt")
    parser.add_argument("--all", action="store_true", help="also reset the profile (name, goal, target date)")
    parser.add_argument("--dry-run", action="store_true", help="show what would change, write nothing")
    args = parser.parse_args()

    targets = [(PROGRESS_FILE, copy.deepcopy(DEFAULT_PROGRESS), "progress"),
               (FOCUS_FILE, copy.deepcopy(DEFAULT_STATE), "focus")]
    if args.all:
        targets.append((PROFILE_FILE, copy.deepcopy(DEFAULT_PROFILE), "profile"))

    print(f"data dir: {DATA_DIR}")
    print(f"before:   {_summary(_load(PROGRESS_FILE))}")

    if args.dry_run:
        print("dry run: would reset " + ", ".join(label for _, _, label in targets))
        return 0

    if not args.yes:
        prompt = f"Reset {', '.join(label for _, _, label in targets)} in the directory above? [y/N] "
        try:
            answer = input(prompt) if sys.stdin.isatty() else ""
        except (EOFError, KeyboardInterrupt):
            answer = ""
        if answer.strip().lower() not in ("y", "yes"):
            print("aborted: nothing was changed (pass --yes to skip this prompt)")
            return 1

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for path, default, label in targets:
        backup = _backup(path, stamp)
        _write(path, default)
        print(f"{label:<8} reset" + (f" (backup: {os.path.basename(backup)})" if backup else " (no prior file)"))

    print(f"after:    {_summary(_load(PROGRESS_FILE))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
