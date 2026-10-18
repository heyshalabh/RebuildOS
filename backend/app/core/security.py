"""
Security and safe archive handling utilities for RebuildOS.
Protects against Zip Slip (path traversal), Zip Bombs, Symlink attacks, and resource exhaustion.
"""
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Generator
from contextlib import contextmanager

from app.core.config import (
    MAX_ZIP_SIZE_BYTES,
    MAX_EXTRACTED_FILES,
    MAX_UNCOMPRESSED_SIZE_BYTES,
    MAX_SINGLE_FILE_SIZE_BYTES,
)


class SecurityError(Exception):
    """Raised when an uploaded file violates security constraints."""
    pass


def validate_zip_header(file_path: Path) -> None:
    """Verifies that the file starts with a valid zip header."""
    if not file_path.exists():
        raise SecurityError("Archive file does not exist.")
    
    file_size = file_path.stat().st_size
    if file_size > MAX_ZIP_SIZE_BYTES:
        raise SecurityError(
            f"Archive size ({file_size / (1024 * 1024):.1f} MB) exceeds maximum allowed limit of {MAX_ZIP_SIZE_BYTES // (1024 * 1024)} MB."
        )
    if file_size < 4:
        raise SecurityError("Archive file is empty or corrupted.")

    if not zipfile.is_zipfile(file_path):
        raise SecurityError("Uploaded file is not a valid ZIP archive.")


def is_safe_zip_entry(target_dir: Path, entry_name: str) -> bool:
    """
    Checks if an entry path is safe to extract into target_dir.
    Guards against Zip Slip (path traversal), absolute paths, and drive letters.
    """
    # Normalize entry path
    entry_path = entry_name.replace("\\", "/")
    
    # Check for empty path
    if not entry_path.strip():
        return False

    # Guard against Windows drive specifiers (e.g. C: or C:/)
    if len(entry_path) > 1 and entry_path[1] == ":":
        return False

    # Guard against root slashes
    if entry_path.startswith("/") or entry_path.startswith("\\"):
        return False

    # Check for relative traversal segments
    parts = Path(entry_path).parts
    if ".." in parts:
        return False

    # Resolve destination path and verify it stays strictly inside target_dir
    dest_path = (target_dir / entry_path).resolve()
    target_resolved = target_dir.resolve()

    try:
        dest_path.relative_to(target_resolved)
    except ValueError:
        return False

    return True


@contextmanager
def safe_extract_zip(zip_file_path: Path) -> Generator[Path, None, None]:
    """
    Extracts a zip file safely into a temporary isolated directory.
    Validates limits on uncompressed size, total file count, and individual file sizes.
    Rejects symlinks and path traversals.
    Cleans up the temporary directory reliably when done.
    """
    validate_zip_header(zip_file_path)
    temp_dir = Path(tempfile.mkdtemp(prefix="rebuildos_scan_"))

    try:
        with zipfile.ZipFile(zip_file_path, "r") as zf:
            infolist = zf.infolist()

            if len(infolist) == 0:
                raise SecurityError("Uploaded ZIP archive is empty.")

            if len(infolist) > MAX_EXTRACTED_FILES:
                raise SecurityError(
                    f"Archive contains {len(infolist)} files, exceeding limit of {MAX_EXTRACTED_FILES}."
                )

            total_uncompressed_bytes = 0

            for info in infolist:
                # Check for symlink (Unix attribute 0o120000 in upper 16 bits of external_attr)
                if (info.external_attr >> 16) & 0o120000 == 0o120000:
                    raise SecurityError(
                        f"Archive contains prohibited symbolic link entry: {info.filename}"
                    )

                if info.file_size > MAX_SINGLE_FILE_SIZE_BYTES:
                    raise SecurityError(
                        f"Archive contains entry '{info.filename}' exceeding single file limit of {MAX_SINGLE_FILE_SIZE_BYTES // (1024 * 1024)} MB."
                    )

                total_uncompressed_bytes += info.file_size
                if total_uncompressed_bytes > MAX_UNCOMPRESSED_SIZE_BYTES:
                    raise SecurityError(
                        f"Extracted archive size exceeds maximum limit of {MAX_UNCOMPRESSED_SIZE_BYTES // (1024 * 1024)} MB."
                    )

                if not is_safe_zip_entry(temp_dir, info.filename):
                    raise SecurityError(
                        f"Zip Slip / Path traversal vulnerability detected in entry: {info.filename}"
                    )

                # Extract safely entry by entry
                zf.extract(info, path=temp_dir)

        # Detect if the zip had a single top-level root folder (very common in GitHub zip downloads)
        extracted_items = [p for p in temp_dir.iterdir() if not p.name.startswith(".")]
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            scan_root = extracted_items[0]
        else:
            scan_root = temp_dir

        yield scan_root

    finally:
        # Guarantee cleanup of all extracted contents
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
