up:
	docker-compose up --build

testup:
	docker-compose -f test.docker-compose.yml up --build
test:
	docker exec -it web_drive-web-1 pytest -s
bash:
	docker exec -it web_drive-web-1 /bin/bash
down:
	docker-compose down --rmi all
