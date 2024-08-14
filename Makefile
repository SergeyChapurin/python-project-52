install:
	poetry install

migrate:
	poetry run python manage.py migrate

setup:
	cp -n .env.example .env || true
	make install
	make migrate

dev:
	poetry run python manage.py runserver

#PORT ?= 8000
#start:
#	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) task_manager.wsgi:application

start:
	poetry run gunicorn task_manager.wsgi --log-file -

check:
	poetry check

lint:
	poetry run flake8 task_manager

test:
	poetry run python manage.py test

test-coverage:
	poetry run coverage run manage.py test task_manager
	poetry run coverage html
	poetry run coverage report