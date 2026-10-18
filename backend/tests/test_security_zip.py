import zipfile
import tempfile
from pathlib import Path
import pytest

from app.core.security import is_safe_zip_entry, safe_extract_zip, SecurityError


def test_is_safe_zip_entry():
    base_dir = Path("/tmp/rebuildos_test").resolve()

    assert is_safe_zip_entry(base_dir, "src/index.js")
    assert is_safe_zip_entry(base_dir, "requirements.txt")
    assert is_safe_zip_entry(base_dir, "app/models/schemas.py")

    # Path traversal attempts
    assert not is_safe_zip_entry(base_dir, "../secret.txt")
    assert not is_safe_zip_entry(base_dir, "foo/../../bar.txt")
    assert not is_safe_zip_entry(base_dir, "/etc/passwd")
    assert not is_safe_zip_entry(base_dir, "\\Windows\\System32")
    assert not is_safe_zip_entry(base_dir, "C:/Windows/System32")
    assert not is_safe_zip_entry(base_dir, "D:\\data")


def test_safe_extract_zip_path_traversal_rejection(tmp_path):
    malicious_zip = tmp_path / "malicious.zip"
    with zipfile.ZipFile(malicious_zip, "w") as zf:
        zf.writestr("../evil.txt", "malicious payload")

    with pytest.raises(SecurityError) as exc_info:
        with safe_extract_zip(malicious_zip):
            pass

    assert "Path traversal vulnerability" in str(exc_info.value) or "Zip Slip" in str(exc_info.value)


def test_safe_extract_empty_zip_rejection(tmp_path):
    empty_zip = tmp_path / "empty.zip"
    with zipfile.ZipFile(empty_zip, "w"):
        pass

    with pytest.raises(SecurityError) as exc_info:
        with safe_extract_zip(empty_zip):
            pass

    assert "empty" in str(exc_info.value).lower()


def test_safe_extract_valid_zip_and_cleanup(tmp_path):
    valid_zip = tmp_path / "valid.zip"
    with zipfile.ZipFile(valid_zip, "w") as zf:
        zf.writestr("README.md", "# Test Project")
        zf.writestr("src/main.py", "print('hello')")

    extracted_dir = None
    with safe_extract_zip(valid_zip) as scan_root:
        extracted_dir = scan_root
        assert (scan_root / "README.md").exists()
        assert (scan_root / "src" / "main.py").exists()

    # Verify temp dir was deleted after context exit
    assert not extracted_dir.exists()
