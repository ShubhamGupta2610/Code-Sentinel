DOCKER_COMPOSE = docker compose -f docker/docker-compose.yml

run:
	$(DOCKER_COMPOSE) up -d

stop:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f api worker

test:
	pytest tests/ -v --tb=short

eval:
	python scripts/run_evaluation.py

migrate:
	alembic upgrade head

shell:
	$(DOCKER_COMPOSE) exec api bash

flower:
	start http://localhost:5555

clean:
	$(DOCKER_COMPOSE) down -v
