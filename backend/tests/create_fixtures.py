"""
Generates test fixtures for RebuildOS automated tests.
"""
from pathlib import Path

fixtures_root = Path(__file__).resolve().parent / "fixtures"

def create_fixtures():
    # 1. Python Perfect
    py_perf = fixtures_root / "python_perfect"
    py_perf.mkdir(parents=True, exist_ok=True)
    (py_perf / "requirements.txt").write_text("fastapi==0.115.0\nuvicorn==0.32.0\npydantic==2.9.2\n", encoding="utf-8")
    (py_perf / ".python-version").write_text("3.12.0\n", encoding="utf-8")
    (py_perf / ".env.example").write_text("PORT=8000\nENV=production\n", encoding="utf-8")
    (py_perf / ".gitignore").write_text("__pycache__/\n*.pyc\n.venv/\nvenv/\n.env\n", encoding="utf-8")
    (py_perf / "README.md").write_text("# Python Service\n## Setup\n```bash\npython -m venv .venv\npip install -r requirements.txt\n```\n", encoding="utf-8")
    (py_perf / "main.py").write_text("import os\nfrom fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")
    (py_perf / "tests").mkdir(exist_ok=True)
    (py_perf / "tests" / "test_main.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    # 2. Python Broken
    py_broken = fixtures_root / "python_broken"
    py_broken.mkdir(parents=True, exist_ok=True)
    (py_broken / "requirements.txt").write_text("fastapi\nuvicorn\npydantic\n", encoding="utf-8")
    (py_broken / "main.py").write_text("import os\nfrom fastapi import FastAPI\nkey = os.environ['SECRET_KEY']\napp = FastAPI()\n", encoding="utf-8")

    # 3. Node Perfect
    node_perf = fixtures_root / "node_perfect"
    node_perf.mkdir(parents=True, exist_ok=True)
    (node_perf / "package.json").write_text("""{
  "name": "node-app",
  "version": "1.0.0",
  "engines": { "node": ">=20.0.0" },
  "scripts": {
    "build": "vite build",
    "test": "vitest run"
  },
  "dependencies": {
    "react": "^18.3.0"
  }
}""", encoding="utf-8")
    (node_perf / "package-lock.json").write_text('{"name": "node-app", "lockfileVersion": 3}', encoding="utf-8")
    (node_perf / ".env.example").write_text("VITE_API_URL=http://localhost:8000\n", encoding="utf-8")
    (node_perf / ".gitignore").write_text("node_modules/\n.env\ndist/\n", encoding="utf-8")
    (node_perf / "README.md").write_text("# Node App\n## Setup\n```bash\nnpm install\nnpm run build\n```\n", encoding="utf-8")
    (node_perf / "src").mkdir(exist_ok=True)
    (node_perf / "src" / "index.js").write_text("console.log('hello');\n", encoding="utf-8")

    # 4. Node Conflicting Locks
    node_conflict = fixtures_root / "node_conflicting"
    node_conflict.mkdir(parents=True, exist_ok=True)
    (node_conflict / "package.json").write_text('{"name": "conflict", "dependencies": {"express": "4.19.0"}}', encoding="utf-8")
    (node_conflict / "package-lock.json").write_text('{}', encoding="utf-8")
    (node_conflict / "yarn.lock").write_text('# yarn lockfile v1\n', encoding="utf-8")

    # 5. Java Maven Perfect
    mvn_perf = fixtures_root / "java_maven_perfect"
    mvn_perf.mkdir(parents=True, exist_ok=True)
    (mvn_perf / "pom.xml").write_text("""<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>demo</artifactId>
  <version>1.0.0</version>
  <properties>
    <java.version>17</java.version>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter</artifactId>
    </dependency>
  </dependencies>
</project>""", encoding="utf-8")
    (mvn_perf / "mvnw").write_text("#!/bin/sh\n", encoding="utf-8")
    (mvn_perf / "mvnw.cmd").write_text("@REM Maven wrapper\n", encoding="utf-8")
    (mvn_perf / ".mvn" / "wrapper").mkdir(parents=True, exist_ok=True)
    (mvn_perf / ".mvn" / "wrapper" / "maven-wrapper.properties").write_text("distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.6-bin.zip\n", encoding="utf-8")
    (mvn_perf / "src" / "test" / "java").mkdir(parents=True, exist_ok=True)
    (mvn_perf / "src" / "test" / "java" / "AppTest.java").write_text("public class AppTest {}\n", encoding="utf-8")
    (mvn_perf / "README.md").write_text("# Java Service\n./mvnw clean test\n", encoding="utf-8")

    # 6. Docker Perfect
    docker_perf = fixtures_root / "docker_perfect"
    docker_perf.mkdir(parents=True, exist_ok=True)
    (docker_perf / "Dockerfile").write_text("""FROM python:3.12-slim-bookworm
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
USER appuser
CMD ["python", "main.py"]
""", encoding="utf-8")
    (docker_perf / ".dockerignore").write_text(".git\n__pycache__\n.venv\n", encoding="utf-8")
    (docker_perf / "docker-compose.yml").write_text("""services:
  db:
    image: postgres:16-alpine
""", encoding="utf-8")

    # 7. Docker Floating
    docker_float = fixtures_root / "docker_floating"
    docker_float.mkdir(parents=True, exist_ok=True)
    (docker_float / "Dockerfile").write_text("""FROM node:latest
COPY . .
RUN npm install
CMD ["node", "index.js"]
""", encoding="utf-8")
    (docker_float / "compose.yaml").write_text("""services:
  cache:
    image: redis:latest
""", encoding="utf-8")

    print("Test fixtures generated at:", fixtures_root)

if __name__ == "__main__":
    create_fixtures()
