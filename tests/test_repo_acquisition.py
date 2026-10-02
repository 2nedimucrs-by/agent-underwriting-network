import unittest

from aun.repo_acquisition import DEFAULT_MANIFEST_PATHS, MAX_FILE_BYTES, MAX_FILES


class RepoAcquisitionTests(unittest.TestCase):
    def test_acquisition_is_bounded(self):
        self.assertLessEqual(len(DEFAULT_MANIFEST_PATHS), MAX_FILES)
        self.assertLessEqual(MAX_FILE_BYTES, 256_000)

    def test_manifest_paths_are_known_files(self):
        self.assertIn("pyproject.toml", DEFAULT_MANIFEST_PATHS)
        self.assertIn("package.json", DEFAULT_MANIFEST_PATHS)


if __name__ == "__main__":
    unittest.main()
