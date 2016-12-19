# testlib.testcase.py
import os
import unittest

import project_vars


class BaseTestCase(unittest.TestCase):
    """
    All test cases should inherit from this class as any common
    functionality that is added here will then be available to all
    subclasses. This facilitates the ability to update in one spot
    and allow all tests to get the update for easy maintenance.
    """
    def asset_filename(self, path):
        """
        Given a path relative to the assets directory, returns the absolute
        path to the filename

        Returns:
            str: absolute path to the asset file given

        Example:
        >>> asset_filename('path/to/file.txt')
        '$PROJECT/path/to/file
        """
        return os.path.normpath(os.path.join(project_vars.ASSETS_DIR, path))

    def asset_contents(self, path):
        """
        Returns:
            str: contents of the asset file given the path to the asset file
            relative to the asset dir.
        """
        filename = self.asset_filename(path)
        with open(filename, 'rb') as f:
            return f.read()
