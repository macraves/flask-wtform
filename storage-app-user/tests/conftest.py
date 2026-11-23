"""Pytest setup for storage-app-user: make the app modules importable."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
