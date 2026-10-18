.PHONY: install test test-backend test-cli build-frontend dev-backend dev-frontend run-docker

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.lock
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

test: test-backend

test-backend:
	cd backend && python -m pytest

test-cli:
	cd backend && python -m rebuildos.cli scan ./tests/fixtures/python_perfect

build-frontend:
	cd frontend && npm run build

dev-backend:
	cd backend && python -m uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

run-docker:
	docker compose up --build
