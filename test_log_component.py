import unittest
import os
import time
from unittest.mock import patch
from LogComponent import ILog, AsyncLogWriter


class TestLogComponent(unittest.TestCase):
    def setUp(self):
        # Ensure that no log files are present before tests run
        self._cleanup_log_files()
        # Create a new ILog instance for each test
        self.log = ILog()

    def tearDown(self):
        # Stop the logging thread after each test
        self.log.stop(wait=True)
        # Clean up any log files created during the tests
        self._cleanup_log_files()

    def _cleanup_log_files(self):
        for f in os.listdir('./logs'):
            if f.endswith('.log'):
                file_path = os.path.join('./logs', f)
                try:
                    os.remove(file_path)
                except PermissionError as e:
                    print(f"Error deleting file {file_path}: {e}. Retrying...")
                    time.sleep(1)  # Wait a bit for the file to be released
                    try:
                        os.remove(file_path)
                    except PermissionError as e:
                        print(f"Could not delete file {file_path} after retry: {e}")

    def _get_log_files(self):
        return [f for f in os.listdir('./logs') if f.endswith('.log')]

    @patch.object(AsyncLogWriter, 'write')
    def test_ilog_write(self, mock_write):
        # Test that calling ILog.write results in AsyncLogWriter.write being called
        self.log.write("Test log entry")
        self.log.stop(wait=True)
        mock_write.assert_called_once_with("Test log entry")

    def test_midnight_file_creation(self):
        # Test that a new file is created if midnight is crossed
        with patch.object(AsyncLogWriter, '_should_rollover', return_value=True):
            for i in range(5):
                time.sleep(1)
                self.log.write(f"Test log entry {i}")

            files_after = self._get_log_files()
            self.assertTrue(len(files_after) > 1)  # new files should be created

    def test_stop_behavior(self):
        # Test the stop behavior of the ILog
        # Write some log entries
        for i in range(5):
            self.log.write(f"Test log entry {i}")

        # Test stopping without waiting
        self.log.stop(wait=False)
        self.assertTrue(self.log.writer.queue.empty())

        # Restarting log component for the next test
        self.log = ILog()

        # Write some log entries
        for i in range(5):
            self.log.write(f"Test log entry {i}")

        # Test stopping with waiting
        self.log.stop(wait=True)
        self.assertTrue(self.log.writer.queue.empty())
        # Ensure that the file has the log entries written to it
        files = self._get_log_files()
        self.assertTrue(len(files) > 0)
        with open("logs/" + files[0], 'r') as f:
            content = f.read()
            self.assertIn('Test log entry 0', content)
            self.assertIn('Test log entry 4', content)


if __name__ == '__main__':
    unittest.main()