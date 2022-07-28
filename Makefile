run: stop
	docker-compose up -d
stop:
	docker-compose down
build:
	docker-compose build


# DEV
dev-run: dev-stop
	docker-compose -f ./docker-compose.dev.yml up -d
dev-run-celery:
	docker-compose -f ./docker-compose.dev.yml up -d celery
dev-stop:
	docker-compose -f ./docker-compose.dev.yml down
dev-build: dev-stop
	docker-compose -f ./docker-compose.dev.yml build
