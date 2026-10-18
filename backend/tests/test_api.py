import io
import zipfile
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_api_version_and_capabilities():
    res_ver = client.get("/api/version")
    assert res_ver.status_code == 200
    assert res_ver.json()["name"] == "RebuildOS"

    res_cap = client.get("/api/capabilities")
    assert res_cap.status_code == 200
    assert "supported_analyzers" in res_cap.json()


def test_api_scan_local(fixtures_dir):
    valid_path = str((fixtures_dir / "python_perfect").resolve())
    res = client.post("/api/scan/local", json={"directory_path": valid_path})
    assert res.status_code == 200
    data = res.json()
    assert data["readiness_score"] >= 80
    assert "Python" in data["detected_languages"]

    # Non-existent path
    res_404 = client.post("/api/scan/local", json={"directory_path": "C:\\nonexistent_dir_12345"})
    assert res_404.status_code == 404


def test_api_scan_zip(fixtures_dir):
    # Create in-memory zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("package.json", '{"name":"my-app","version":"1.0.0"}')
        zf.writestr("package-lock.json", '{}')
        zf.writestr("README.md", "# My App\nnpm install\n")
    zip_buffer.seek(0)

    res = client.post(
        "/api/scan",
        files={"file": ("my-app.zip", zip_buffer, "application/zip")},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["project_name"] == "my-app"
    assert "JavaScript" in data["detected_languages"]
