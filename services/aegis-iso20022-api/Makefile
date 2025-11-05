.PHONY: api run tests

api:
	. .venv/bin/activate && uvicorn src.translator_api.routes:app --reload --port 8080

tests:
	. .venv/bin/activate && pytest -q