"""
LAR-OS Multi-Node Cloud Shell Cluster Bridge
Direct SSH Bridge to Google Cloud Shell Distributed Worker Nodes
"""
import subprocess
import sys
from pathlib import Path

SSH_KEY = Path.home() / ".ssh" / "google_compute_engine"

# Active Node Registry
NODES = {
    "thuaquan228": {
        "user": "thuaquan228",
        "port": 56602,
        "host": "127.0.0.1",
        "hostname": "cs-314392929482-default",
        "ram": "16 GB"
    },
    "giabaohuynh0512": {
        "user": "giabaohuynh0512",
        "port": 59956,
        "host": "127.0.0.1",
        "hostname": "cs-111277341354-default",
        "ram": "8 GB"
    }
}

def run_remote_command(cmd: str, node_name="thuaquan228"):
    """Execute a bash command on a specific remote Cloud Shell node."""
    if node_name not in NODES:
        raise ValueError(f"Unknown node: {node_name}. Available: {list(NODES.keys())}")
    node = NODES[node_name]
    ssh_args = [
        "ssh",
        "-i", str(SSH_KEY),
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "LogLevel=ERROR",
        "-p", str(node["port"]),
        f"{node['user']}@{node['host']}",
        cmd
    ]
    res = subprocess.run(ssh_args, capture_output=True, text=True, encoding="utf-8")
    return res.returncode, res.stdout, res.stderr

def run_remote_python(code: str, node_name="thuaquan228"):
    """Pipe Python code directly into Python3 on a specific remote Cloud Shell node."""
    if node_name not in NODES:
        raise ValueError(f"Unknown node: {node_name}. Available: {list(NODES.keys())}")
    node = NODES[node_name]
    ssh_args = [
        "ssh",
        "-i", str(SSH_KEY),
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "LogLevel=ERROR",
        "-p", str(node["port"]),
        f"{node['user']}@{node['host']}",
        "python3"
    ]
    res = subprocess.run(ssh_args, input=code, capture_output=True, text=True, encoding="utf-8")
    return res.returncode, res.stdout, res.stderr

if __name__ == "__main__":
    print("=== LAR-OS DISTRIBUTED CLUSTER AUDIT ===")
    for name, info in NODES.items():
        print(f"\n[+] Testing Node: {name} ({info['hostname']} - {info['ram']})...")
        code, out, err = run_remote_command("hostname; whoami; uptime -p", node_name=name)
        if code == 0:
            print(f"    [ONLINE] Output:\n    " + out.replace("\n", "\n    ").strip())
        else:
            print(f"    [OFFLINE/ERROR]: {err.strip()}")

