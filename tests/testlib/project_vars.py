""" This module contains project variables used for testing
"""
import os

file_dir = os.path.dirname(__file__)

ASSETS_DIR = os.path.normpath(os.path.join(
                 file_dir, '..', 'assets'))
SRC_DIR = os.path.normpath(os.path.join(
                 file_dir, '..', '..', 'pronunciation_master'))
