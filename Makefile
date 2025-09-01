PY=python3
UV=uv

.PHONY: venv install dev run test fmt

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
