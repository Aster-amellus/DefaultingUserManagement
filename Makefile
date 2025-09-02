PY=python3
UV=uv

.PHONY: venv install dev run test fmt seed-demo clean deep-clean docker-clean docker-up docker-up-prod docker-down docker-build-prod package-release

venv:
	$(UV) venv .venv
	. .venv/bin/activate && $(UV) pip install -r requirements.txt

install:
	$(UV) pip install -r requirements.txt

dev:
	. .venv/bin/activate && uvicorn app.main:app --reload

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

test:
	. .venv/bin/activate && pytest -q

# Seed demo data (idempotent)
seed-demo:
	$(UV) run python scripts/seed_demo_data.py

# Remove common temporary files and caches
clean:
	rm -rf \
		**/__pycache__ \
		.pytest_cache \
		.mypy_cache \
		.ruff_cache \
		coverage coverage.xml .coverage .coverage.* htmlcov \
		dist frontend/dist \
		report_backend.xml \
		dev.db test.db \
		uploads/*

# Deep clean including envs and node modules (use with care)
deep-clean: clean
	rm -rf .venv frontend/node_modules

# Remove docker containers and volumes (DB data will be removed)
docker-clean:
	docker compose down -v

# Docker helpers
docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-build-prod:
	docker compose -f docker-compose.prod.yml build

docker-up-prod:
	docker compose -f docker-compose.prod.yml up -d --build

# Package release artifacts (frontend dist + docs)
package-release:
	cd frontend && npm ci && npm run build
	bash scripts/package_release.sh
