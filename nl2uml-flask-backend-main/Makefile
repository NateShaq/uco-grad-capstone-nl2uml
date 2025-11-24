
.PHONY: build run save

build:
	docker build -t nl2uml:local .

run:
	docker run --rm -p 8080:8080 -v $$PWD/data:/var/lib/nl2uml nl2uml:local

save:
	docker save nl2uml:local > nl2uml-local.tar



up:
\tdocker compose up --build --profile ollama

recreate:
\tdocker compose down
\tdocker compose up --force-recreate --profile ollama

clean:
\tdocker compose down --volumes --remove-orphans || true
\tdocker image prune -f || true
\tdocker rmi nl2uml:local || true
\tdocker compose build --no-cache
\tdocker compose up --profile ollama


curl http://localhost:8080/healthz
docker compose ps
docker compose logs -f


docker compose down
docker compose up --force-recreate --profile ollama