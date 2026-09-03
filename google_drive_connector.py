"""
LAR-OS Google Drive for PC Connector & Auto-Sync Bridge
Bridges local research assets, LAR-OS Gateway, and NotebookLM with Google Drive (G:)

Author: Gia Bao Huynh (Jun) · Antigravity Research OS
"""

import os
import sys
import shutil
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

class GoogleDriveConnector:
    """Universal connector for Google Drive for PC on Windows."""
    
    POSSIBLE_ROOTS = [
        Path(r"G:\Drive của tôi"),
        Path(r"G:\My Drive"),
        Path(r"G:"),
    ]

    def __init__(self):
        self.drive_root = self._detect_drive_root()
        self.workspace_dir = None
        if self.drive_root:
            self.workspace_dir = self.drive_root / "LAR_OS_Gateway_v3"
            self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def _detect_drive_root(self) -> Optional[Path]:
        for root in self.POSSIBLE_ROOTS:
            if root.exists():
                return root
        return None

    def is_connected(self) -> bool:
        return self.drive_root is not None and self.drive_root.exists()

    def get_status(self) -> Dict[str, Any]:
        if not self.is_connected():
            return {
                "status": "DISCONNECTED",
                "message": "Google Drive for PC not mounted on G:"
            }
        
        try:
            total, used, free = shutil.disk_usage(str(self.drive_root))
            files = list(self.workspace_dir.glob("*")) if self.workspace_dir else []
            return {
                "status": "CONNECTED",
                "mount_point": str(self.drive_root),
                "workspace": str(self.workspace_dir),
                "free_gb": round(free / (1024**3), 2),
                "total_gb": round(total / (1024**3), 2),
                "synced_files_count": len(files),
                "synced_files": [f.name for f in files]
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }

    def sync_file_to_drive(self, local_path: Path, target_subfolder: str = "") -> Optional[Path]:
        """Copies a local file to Google Drive workspace for cloud sync."""
        if not self.is_connected():
            print(f"[!] Cannot sync {local_path.name}: Google Drive not connected.")
            return None
        
        dest_dir = self.workspace_dir / target_subfolder if target_subfolder else self.workspace_dir
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / local_path.name
        shutil.copy2(local_path, dest_path)
        print(f"[✓] Synced '{local_path.name}' -> Google Drive ({dest_path})")
        return dest_path

    def list_drive_research_files(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Lists recent research documents in Google Drive."""
        if not self.is_connected():
            return []
        
        results = []
        try:
            for p in self.drive_root.glob("*"):
                if p.is_file():
                    stat = p.stat()
                    results.append({
                        "name": p.name,
                        "size_bytes": stat.st_size,
                        "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime)),
                        "path": str(p)
                    })
                if len(results) >= limit:
                    break
        except Exception as e:
            print(f"Error scanning Drive root: {e}")
        return results

# Singleton instance
drive_connector = GoogleDriveConnector()

if __name__ == "__main__":
    print("================================================================================")
    print("⚡ LAR-OS GOOGLE DRIVE FOR PC CONNECTOR AUDIT")
    print("================================================================================")
    status = drive_connector.get_status()
    for k, v in status.items():
        print(f"  • {k}: {v}")
    print("================================================================================")
