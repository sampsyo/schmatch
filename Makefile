.PHONY: dev
dev:
	FLASK_APP=schmatch FLASK_ENV=development pipenv run flask run

.PHONY: setup
setup:
	pipenv run python -m schmatch.create_db
