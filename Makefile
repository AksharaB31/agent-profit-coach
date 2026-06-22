install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

test:
	pytest

train:
	python train_ml_models.py

lint:
	flake8 app

format:
	black app