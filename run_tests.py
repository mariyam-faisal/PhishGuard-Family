"""
run_tests.py - owned by Person 1 (AI & prompt lead).

Runs every message in tests/test_messages.json through check_message()
and reports how many verdicts match.

Run:  python3 run_tests.py
Saves a copy of the results to tests/results.md for the README.
"""

import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
TESTS_FILE = HERE / "tests" / "test_messages.json"
RESULTS_FILE = HERE / "tests" / "results.md"

try:
    from checker import check_message, is_model_ready, warm_up, MODEL
except ImportError:
    print("checker.py isn't ready yet (it's Person 2's file).")
    print("Run 'git pull' to get it, then try again.")
    sys.exit(1)

URL_RE = re.compile(r"(https?://|www\.|\b[\w-]+\.(com|ca|net|org|info|xyz|io|co)\b|bit\.ly|tinyurl)", re.I)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE_RE = re.compile(r"\d[\d\-\s().]{6,}\d")


def leaks(warning):
    """Return what's wrong with a family_warning, or '' if it's clean."""
    if not warning:
        return ""
    problems = []
    if URL_RE.search(warning):
        problems.append("link")
    if EMAIL_RE.search(warning):
        problems.append("email")
    if PHONE_RE.search(warning):
        problems.append("phone")
    return ", ".join(problems)


def preview(text, n=45):
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1] + "…"


def main():
    cases = json.loads(TESTS_FILE.read_text(encoding="utf-8"))
    rows = []
    correct = 0
    scams_marked_safe = 0
    warning_leaks = 0

    if is_model_ready():
        print(f"Model {MODEL} is ready. Loading it into memory…")
        warm_up()
    else:
        print(f"⚠ Model {MODEL} isn't ready (is Ollama running? did 'ollama pull {MODEL}' finish?).")
        print("  Results below are RULE CHECKS ONLY. Safe messages will show as ERROR.\n")
    print(f"Running {len(cases)} test messages…\n")
    print(f"{'#':>2}  {'message preview':<46} {'lang':<9} {'expected':<11} {'got':<11} ok  warning")
    print("-" * 100)

    for i, case in enumerate(cases, start=1):
        start = time.time()
        result = check_message(case["text"], case["language"])
        seconds = time.time() - start

        if not result.get("ok", False):
            got = "ERROR"
            note = str(result.get("error", "unknown error"))
        else:
            got = result.get("verdict", "?")
            note = ""

        is_correct = got == case["expected"]
        correct += is_correct
        if case["expected"] == "Scam" and got == "Safe":
            scams_marked_safe += 1

        leak = leaks(result.get("family_warning", "")) if got != "ERROR" else ""
        if leak:
            warning_leaks += 1
        mark = "✓" if is_correct else "✗"
        warn_mark = f"✗ ({leak})" if leak else "✓"

        rows.append({
            "n": i,
            "preview": preview(case["text"]),
            "language": case["language"],
            "expected": case["expected"],
            "got": got,
            "mark": mark,
            "warning": warn_mark,
            "seconds": seconds,
            "note": note,
        })
        print(f"{i:>2}  {preview(case['text']):<46} {case['language']:<9} {case['expected']:<11} "
              f"{got:<11} {mark}   {warn_mark}   ({seconds:.1f}s)")
        if note:
            print(f"     error: {note}")

    accuracy = 100 * correct / len(cases)
    print("-" * 100)
    print(f"Accuracy: {correct}/{len(cases)} = {accuracy:.0f}%")
    print(f"Scams wrongly marked Safe: {scams_marked_safe}")
    print(f"Family warnings with a link/phone/email: {warning_leaks}")

    lines = [
        "# Test results",
        "",
        f"Model: Gemma 3 4B (local, via Ollama) · {len(cases)} test messages",
        "",
        f"**Accuracy: {correct}/{len(cases)} ({accuracy:.0f}%)** · "
        f"Scams marked Safe: {scams_marked_safe} · Family warnings leaking details: {warning_leaks}",
        "",
        "| # | Message | Language | Expected | Got | ✓/✗ | Family warning clean |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        msg = r["preview"].replace("|", "/")
        lines.append(f"| {r['n']} | {msg} | {r['language']} | {r['expected']} | {r['got']} | {r['mark']} | {r['warning']} |")
    RESULTS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSaved to {RESULTS_FILE.relative_to(HERE)}")


if __name__ == "__main__":
    main()
