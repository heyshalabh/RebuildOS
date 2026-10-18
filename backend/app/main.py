"""
FastAPI Backend Application for RebuildOS.
Provides endpoints for repository scanning, local directory analysis, and report generation.
"""
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, List

from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from app.core.config import APP_NAME, APP_TAGLINE, SCANNER_VERSION, CATEGORY_CONFIG
from app.core.security import SecurityError
from app.models.schemas import (
    HealthResponse,
    ScanResult,
    LocalScanRequest,
    ReportExportRequest,
)
from app.services.scanner import scan_project_directory, scan_zip_archive
from app.services.report_service import generate_json_report, generate_markdown_report


app = FastAPI(
    title=f"{APP_NAME} API",
    description=f"{APP_TAGLINE} — Local-first repository reproducibility and rebuild readiness diagnostic engine.",
    version=SCANNER_VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Enable CORS for local development and web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def get_health() -> HealthResponse:
    """Returns system health and version."""
    return HealthResponse(
        status="ok",
        version=SCANNER_VERSION,
        service=APP_NAME,
    )


@app.get("/api/version", tags=["System"])
def get_version() -> Dict[str, Any]:
    """Returns detailed scanner version and capabilities."""
    return {
        "name": APP_NAME,
        "tagline": APP_TAGLINE,
        "version": SCANNER_VERSION,
        "mode": "local-deterministic",
        "requires_cloud_api": False,
        "requires_database": False,
    }


@app.get("/api/capabilities", tags=["System"])
def get_capabilities() -> Dict[str, Any]:
    """Returns supported analyzers, rule categories, and configuration limits."""
    return {
        "supported_analyzers": [
            {
                "name": "Python",
                "manifests": ["requirements.txt", "pyproject.toml", "Pipfile", "setup.py"],
                "lockfiles": ["poetry.lock", "uv.lock", "Pipfile.lock", "requirements.lock"],
                "package_managers": ["pip", "poetry", "uv", "pipenv"],
            },
            {
                "name": "Node.js",
                "manifests": ["package.json"],
                "lockfiles": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock"],
                "package_managers": ["npm", "yarn", "pnpm", "bun"],
            },
            {
                "name": "Java",
                "manifests": ["pom.xml", "build.gradle", "build.gradle.kts"],
                "wrappers": ["mvnw", "gradlew"],
                "package_managers": ["maven", "gradle"],
            },
            {
                "name": "Docker",
                "manifests": ["Dockerfile", "Dockerfile.*", "docker-compose.yml", "compose.yaml"],
                "checks": ["base_image_pinning", "dockerignore", "layer_caching_order", "non_root_user"],
            },
        ],
        "categories": CATEGORY_CONFIG,
    }


@app.post("/api/scan", response_model=ScanResult, tags=["Scanning"])
async def scan_uploaded_zip(file: UploadFile = File(...)) -> ScanResult:
    """
    Uploads and scans a project ZIP archive.
    Enforces path traversal defenses, zip-bomb protections, and isolated temporary extraction.
    """
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only valid .zip archives are supported.",
        )

    # Save to a temporary file for safe scanning
    temp_zip = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            temp_zip = Path(tmp.name)
            shutil.copyfileobj(file.file, tmp)

        # Execute safe scan
        project_name = Path(file.filename).stem
        result = scan_zip_archive(temp_zip, project_name=project_name)
        return result

    except SecurityError as sec_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security constraint violated: {str(sec_err)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )
    finally:
        if temp_zip and temp_zip.exists():
            try:
                temp_zip.unlink(missing_ok=True)
            except Exception:
                pass


@app.post("/api/scan/local", response_model=ScanResult, tags=["Scanning"])
def scan_local_directory(req: LocalScanRequest) -> ScanResult:
    """
    Analyzes a local directory on the machine.
    Used by developer workflows and local integrations.
    Validates directory existence and defensive path constraints.
    """
    target_path = Path(req.directory_path).resolve()

    if not target_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target directory does not exist: {req.directory_path}",
        )

    if not target_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Specified path is a file, not a directory: {req.directory_path}",
        )

    # Defensive boundary check: Disallow scanning root of drive (e.g. C:\ or /)
    if len(target_path.parts) <= 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Scanning root drives directly is prohibited for safety.",
        )

    try:
        result = scan_project_directory(target_path, project_name=target_path.name)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Local directory scan failed: {str(e)}",
        )


@app.post("/api/report", tags=["Reporting"])
def export_report(req: ReportExportRequest):
    """
    Generates a downloadable audit report in Markdown or JSON format.
    """
    if req.format == "json":
        json_content = generate_json_report(req.scan_result)
        return JSONResponse(
            content=json_content,
            headers={
                "Content-Disposition": f'attachment; filename="rebuildos_report_{req.scan_result.project_name.lower().replace(" ", "_")}.json"'
            },
        )
    else:
        md_content = generate_markdown_report(req.scan_result)
        return PlainTextResponse(
            content=md_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f'attachment; filename="rebuildos_report_{req.scan_result.project_name.lower().replace(" ", "_")}.md"'
            },
        )
