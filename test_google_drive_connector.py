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

    @patch("google_drive_connector.Path.exists")
    @patch("google_drive_connector.Path.mkdir")
    @patch("google_drive_connector.Path.glob")
    def test_list_drive_research_files_connected(self, mock_glob, mock_mkdir, mock_exists):
        mock_exists.return_value = True

        connector = GoogleDriveConnector()

        # Mocking the glob method on Path
        mock_file1 = MagicMock()
        mock_file1.is_file.return_value = True
        mock_file1.name = "test_file_1.pdf"
        mock_file1.__str__.return_value = str(connector.drive_root / "test_file_1.pdf")
        mock_stat1 = MagicMock()
        mock_stat1.st_size = 1024
        mock_stat1.st_mtime = 1672531200 # 2023-01-01 00:00:00
        mock_file1.stat.return_value = mock_stat1

        mock_file2 = MagicMock()
        mock_file2.is_file.return_value = True
        mock_file2.name = "test_file_2.docx"
        mock_file2.__str__.return_value = str(connector.drive_root / "test_file_2.docx")
        mock_stat2 = MagicMock()
        mock_stat2.st_size = 2048
        mock_stat2.st_mtime = 1672617600
        mock_file2.stat.return_value = mock_stat2

        mock_dir = MagicMock()
        mock_dir.is_file.return_value = False

        mock_glob.return_value = [mock_file1, mock_dir, mock_file2]

        results = connector.list_drive_research_files(limit=10)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["name"], "test_file_1.pdf")
        self.assertEqual(results[0]["size_bytes"], 1024)
        self.assertEqual(results[0]["path"], str(connector.drive_root / "test_file_1.pdf"))
        self.assertEqual(results[1]["name"], "test_file_2.docx")
        self.assertEqual(results[1]["size_bytes"], 2048)
        self.assertEqual(results[1]["path"], str(connector.drive_root / "test_file_2.docx"))

        # Test limit
        mock_glob.return_value = [mock_file1, mock_dir, mock_file2]
        results_limited = connector.list_drive_research_files(limit=1)
        self.assertEqual(len(results_limited), 1)
        self.assertEqual(results_limited[0]["name"], "test_file_1.pdf")

    @patch("google_drive_connector.Path.exists")
    def test_list_drive_research_files_disconnected(self, mock_exists):
        mock_exists.return_value = False

        connector = GoogleDriveConnector()

        results = connector.list_drive_research_files()

        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
