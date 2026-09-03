"""
LAR-OS Safe NotebookLM CLI Wrapper (Just-In-Time Auto-Authentication)
Ensures credentials are valid before executing any nlm command.
No background heartbeats needed.
"""
import subprocess
import sys
from pathlib import Path

NLM_PATH = Path(r"C:\Users\nswcl\.local\bin\nlm.exe")

def ensure_authenticated():
    """Checks if nlm credentials are valid; if not, automatically re-authenticates."""
    check_res = subprocess.run(
        [str(NLM_PATH), "login", "--check"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    if check_res.returncode == 0:
        return True

    print("[*] NotebookLM credentials expired. Auto re-authenticating...", file=sys.stderr)
    login_res = subprocess.run(
        [str(NLM_PATH), "login"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    if login_res.returncode == 0:
        print("[✓] Re-authenticated successfully via saved profile.", file=sys.stderr)
        return True
    else:
        print("[!] Auto re-auth failed:", login_res.stderr, file=sys.stderr)
        return False

def run_nlm(args):
    """Run an nlm command with automatic JIT authentication."""
    if not ensure_authenticated():
        sys.exit(1)

    cmd = [str(NLM_PATH)] + args
    res = subprocess.run(cmd)
    sys.exit(res.returncode)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nlm_safe.py <nlm-subcommand> [args...]")
        sys.exit(1)
    run_nlm(sys.argv[1:])
