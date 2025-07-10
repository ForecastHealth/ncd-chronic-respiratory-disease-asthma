"""
Cleanup utilities for temporary files and directories.

This module handles the cleanup of temporary files created during validation.
"""

import shutil
from pathlib import Path


def cleanup_tmp_directory() -> None:
    """Clean up temporary files."""
    tmp_dir = Path("tmp")
    if tmp_dir.exists():
        print(f"\n🧹 Cleaning up temporary files...")
        try:
            # Remove all files in tmp directory but keep the directory
            for item in tmp_dir.iterdir():
                if item.is_file():
                    item.unlink()
                    print(f"   Removed: {item}")
                elif item.is_dir():
                    shutil.rmtree(item)
                    print(f"   Removed directory: {item}")
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"⚠️  Warning: Failed to clean up tmp directory: {e}")


def ensure_tmp_directory() -> Path:
    """Ensure tmp directory exists and return its path."""
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(exist_ok=True)
    return tmp_dir