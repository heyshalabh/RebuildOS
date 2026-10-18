# RebuildOS Security Policy & Threat Model

RebuildOS handles arbitrary project repositories, archives, and configuration files. Security is baked directly into the design.

## Threat Mitigations

### 1. Zip Slip & Path Traversal
- **Risk**: Malicious zip files containing entries like `../../etc/passwd` or `..\..\Windows\System32\cmd.exe` attempting to overwrite host files.
- **Mitigation**: `safe_extract_zip()` validates every entry path. Normalizes slashes, checks for `..` segments, blocks root prefixes (`/` or `\`), blocks drive specifiers (`C:`), and asserts that destination paths resolve strictly within the isolated temporary folder.

### 2. Decompression Bombs (Zip Bombs)
- **Risk**: Highly compressed archives expanding into gigabytes of data to exhaust memory and disk space.
- **Mitigation**: Enforces strict upload limits:
  - Max archive file size: **50 MB**
  - Max total file count: **10,000 files**
  - Max uncompressed size: **200 MB**
  - Max single file size: **25 MB**

### 3. Symbolic Link Attacks
- **Risk**: Archives containing symlinks targeting sensitive host files (`/etc/shadow`, `.ssh/id_rsa`).
- **Mitigation**: Symbolic link zip entries (Unix attribute `0o120000`) are explicitly detected and aborted before extraction.

### 4. Zero Automatic Script Execution
- **Risk**: Remote code execution via `setup.py`, `postinstall`, or Docker builds.
- **Mitigation**: RebuildOS performs **pure static text and AST analysis**. It never runs `pip install`, `npm install`, shell scripts, or container builds during scans.

### 5. Local Filesystem Safety
- **Risk**: Remote clients requesting the server read arbitrary system directories.
- **Mitigation**: The `POST /api/scan/local` endpoint rejects system root drive paths (`/`, `C:\`), ensures paths exist, and is intended strictly for local development environments.

## Reporting Security Issues
If you discover a security vulnerability, please submit an issue or email security@rebuildos.local with reproduction steps.
