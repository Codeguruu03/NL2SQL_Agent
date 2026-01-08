# tests/conftest.py
"""
Pytest configuration file.
Sets up the Python path for test imports.
"""
import sys
import os

# Add project root and src to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))
