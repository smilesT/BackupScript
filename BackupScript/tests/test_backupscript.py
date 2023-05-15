# Tests
# Usage: poetry run python tests/test_backupscript.py


import unittest
import os
import tempfile
import shutil
import hashlib
from backupscript.BackupManager import BackupManager
from datetime import timedelta


def hash_file(filepath):
    # Utility function to calculate SHA256 hash of a file
    hasher = hashlib.sha256()
    with open(filepath, "rb") as file:
        buf = file.read()
        hasher.update(buf)
    return hasher.hexdigest()


class TestBackupManager(unittest.TestCase):
    def setUp(self):
        self.src_dir = tempfile.mkdtemp()
        self.dst_dir = tempfile.mkdtemp()
        self.interval = timedelta(days=7)

        self.src_file_path = os.path.join(self.src_dir, "testfile.txt")
        with open(self.src_file_path, "w") as f:
            f.write("This is a test file")

        self.bm = BackupManager({self.src_dir: self.dst_dir}, self.interval)

    def tearDown(self):
        shutil.rmtree(self.src_dir)
        shutil.rmtree(self.dst_dir)

    # def test_version():
    #     assert __version__ == "1.0.0"

    def test_full_backup(self):
        self.bm.fullBackup()

        expected_dst_file_path = os.path.join(self.dst_dir, "testfile.txt")
        self.assertTrue(os.path.isfile(expected_dst_file_path))

        # Check that source and destination file hashes match
        self.assertEqual(
            hash_file(self.src_file_path), hash_file(expected_dst_file_path)
        )

    def test_true(self):
        self.assertEqual(True, True)

    def test_incremental_backup(self):
        self.bm.incrementalBackup()

        expected_dst_file_path = os.path.join(self.dst_dir, "testfile.txt")
        self.assertTrue(os.path.isfile(expected_dst_file_path))

        # Check that source and destination file hashes match
        self.assertEqual(
            hash_file(self.src_file_path), hash_file(expected_dst_file_path)
        )

        # Modify source file
        with open(self.src_file_path, "w") as f:
            f.write("This is a modified test file")

        self.bm.incrementalBackup()

        # Check that source and destination file hashes match after modification
        self.assertEqual(
            hash_file(self.src_file_path), hash_file(expected_dst_file_path)
        )

    def test_file_permissions(self):
        os.chmod(self.src_file_path, 0o755)
        self.bm.fullBackup()

        expected_dst_file_path = os.path.join(self.dst_dir, "testfile.txt")
        src_file_stat = os.stat(self.src_file_path)
        dst_file_stat = os.stat(expected_dst_file_path)

        # Check that source and destination file permissions match
        self.assertEqual(src_file_stat.st_mode, dst_file_stat.st_mode)


if __name__ == "__main__":
    unittest.main()
