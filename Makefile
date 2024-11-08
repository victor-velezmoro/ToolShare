# Makefile

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

ps:
	docker-compose ps

rebuild:
	docker-compose up -d --build

stop:
	docker-compose stop
