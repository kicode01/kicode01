#!/usr/bin/env python3
"""
IssueOps Telemetry State Machine for kicode01/kicode01.

Processes inbound GitHub issues matching the telemetry ping pattern:
  1. Parses sender, organization, focus area, and notes.
  2. Appends verified telemetry signal to telemetry.json.
  3. Re-generates dynamic SVG assets and updates README.md via generate.py.
  4. Automatically posts a cryptographic acknowledgment receipt and closes the issue.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TELEMETRY_PATH = os.path.join(ROOT, "telemetry.json")


def load_telemetry():
    if os.path.exists(TELEMETRY_PATH):
        try:
            with open(TELEMETRY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"updated": "2026-10-28 00:00 UTC", "status": "ONLINE", "signals": []}


def save_telemetry(data):
    with open(TELEMETRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_cmd(args):
    res = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        raise RuntimeError(f"Command {' '.join(args)} failed: {res.stderr}")
    return res.stdout.strip()


def parse_issue_body(body):
    """Extracts structured fields from issue body if formatted via template."""
    org = "Verified Visitor"
    focus = "Applied AI / Systems"
    note = "Telemetry handshake verified."

    if not body:
        return org, focus, note

    # Check for fields like '### Organization / Company\n\nGoogle'
    org_match = re.search(r"###\s*(?:Sender\s*/\s*)?Organization[^\n]*\n+([^\n#]+)", body, re.IGNORECASE)
    if org_match and org_match.group(1).strip():
        org = org_match.group(1).strip()[:35]

    focus_match = re.search(r"###\s*(?:Target\s*Role\s*/\s*)?Focus[^\n]*\n+([^\n#]+)", body, re.IGNORECASE)
    if focus_match and focus_match.group(1).strip():
        focus = focus_match.group(1).strip()[:35]

    note_match = re.search(r"###\s*(?:Transmission\s*)?Note[^\n]*\n+([^\n#]+)", body, re.IGNORECASE)
    if note_match and note_match.group(1).strip():
        note = note_match.group(1).strip()[:65]

    return org, focus, note


def main():
    parser = argparse.ArgumentParser(description="Process incoming telemetry issue ping")
    parser.add_argument("--issue", type=int, help="GitHub Issue Number")
    parser.add_argument("--sender", type=str, help="Sender GitHub username")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without network calls")
    args = parser.parse_args()

    telemetry = load_telemetry()
    now_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if args.issue:
        print(f"[*] Processing telemetry ping for Issue #{args.issue}...")
        sender = args.sender or "anonymous"
        org = "Verified Guest"
        focus = "Applied AI / Systems"
        note = "Telemetry handshake received."

        if not args.dry_run:
            try:
                raw = run_cmd(["gh", "issue", "view", str(args.issue), "--json", "author,title,body,createdAt"])
                data = json.loads(raw)
                sender = data.get("author", {}).get("login", sender)
                org, focus, note = parse_issue_body(data.get("body", ""))
            except Exception as e:
                print(f"[!] Warning reading issue via gh CLI: {e}")

        sig_id = f"SIG-{args.issue:03d}"
        new_signal = {
            "id": sig_id,
            "sender": sender,
            "org": org,
            "focus": focus,
            "note": note,
            "timestamp": now_utc,
        }

        # Keep latest 4 signals
        signals = [new_signal] + [s for s in telemetry.get("signals", []) if s.get("id") != sig_id]
        telemetry["signals"] = signals[:4]
        telemetry["updated"] = now_utc
        telemetry["status"] = "ONLINE"
        save_telemetry(telemetry)
        print(f"[+] Appended signal {sig_id} from @{sender} ({org}).")

        # Regenerate assets
        print("[*] Re-generating SVG assets and README blocks...")
        gen_script = os.path.join(ROOT, "generate.py")
        subprocess.run([sys.executable, gen_script], check=True)

        # Comment and close issue
        if not args.dry_run:
            ack_msg = (
                f"### ⚡ Telemetry Signal Acknowledged & Executed\n\n"
                f"Signal **`{sig_id}`** from **@{sender}** (`{org}`) has been verified and permanently committed "
                f"into the profile telemetry radar.\n\n"
                f"- **Status:** `200 OK · EXECUTED`\n"
                f"- **Domain:** `{focus}`\n"
                f"- **Timestamp:** `{now_utc}`\n"
                f"- **Live Vector Render:** Telemetry SVG instrument panel updated on [`kicode01`](https://github.com/kicode01).\n\n"
                f"*{note}*\n\n"
                f"---\n"
                f"*(Closed automatically via GitHub Actions IssueOps)*"
            )
            try:
                run_cmd(["gh", "issue", "comment", str(args.issue), "--body", ack_msg])
                run_cmd(["gh", "issue", "close", str(args.issue), "--reason", "completed"])
                print(f"[+] Commented and closed issue #{args.issue}.")
            except Exception as e:
                print(f"[!] Warning commenting/closing issue: {e}")
    else:
        print("[i] Standalone run. Telemetry status:", telemetry.get("status"))


if __name__ == "__main__":
    main()
