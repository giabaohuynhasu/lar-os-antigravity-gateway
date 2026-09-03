import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from google_drive_connector import GoogleDriveConnector

class TestGoogleDriveConnector(unittest.TestCase):
    
    @patch("google_drive_connector.Path.exists")
    @patch("google_drive_connector.Path.mkdir")
    def test_discovery_mount_point_exists(self, mock_mkdir, mock_exists):
        expected_root = GoogleDriveConnector.POSSIBLE_ROOTS[0]
        
        # We need it to return True multiple times. It gets called once in __init__ and once in is_connected()
        mock_exists.return_value = True
        
        connector = GoogleDriveConnector()
        
        self.assertEqual(connector.drive_root, expected_root)
        self.assertEqual(connector.workspace_dir, expected_root / "LAR_OS_Gateway_v3")
        
        # Verify mkdir was called correctly
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        
        self.assertTrue(connector.is_connected())

    @patch("google_drive_connector.Path.exists")
    def test_graceful_fallback_absent_mount_point(self, mock_exists):
        # Setup mock to always return False for exists
        mock_exists.return_value = False
        
        connector = GoogleDriveConnector()
        
        self.assertIsNone(connector.drive_root)
        self.assertIsNone(connector.workspace_dir)
        self.assertFalse(connector.is_connected())
        
        status = connector.get_status()
        self.assertEqual(status["status"], "DISCONNECTED")
        self.assertEqual(status["message"], "Google Drive for PC not mounted on G:")

    @patch('sys.stdout', new_callable=MagicMock)
    @patch("google_drive_connector.Path.exists")
    @patch("google_drive_connector.Path.mkdir")
    @patch("google_drive_connector.shutil.copy2")
    def test_sync_dossier_path_handling(self, mock_copy2, mock_mkdir, mock_exists, mock_stdout):
        expected_root = GoogleDriveConnector.POSSIBLE_ROOTS[0]
        mock_exists.return_value = True
        
        connector = GoogleDriveConnector()
        
        local_path = Path("/some/local/path/dossier.txt")
        target_subfolder = "test_folder"
        
        result_path = connector.sync_file_to_drive(local_path, target_subfolder)
        
        expected_dest_dir = expected_root / "LAR_OS_Gateway_v3" / target_subfolder
        expected_dest_path = expected_dest_dir / "dossier.txt"
        
        # Verify result path
        self.assertEqual(result_path, expected_dest_path)
        
        # Verify copy2 was called correctly
        mock_copy2.assert_called_once_with(local_path, expected_dest_path)
        
        # Verify mkdir was called for the subfolder
        # Note: mkdir is called in __init__ for workspace_dir and in sync_file_to_drive for dest_dir
        self.assertEqual(mock_mkdir.call_count, 2)
        mock_mkdir.assert_called_with(parents=True, exist_ok=True)

if __name__ == '__main__':
    unittest.main()
