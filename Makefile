up-ugc:
	docker-compose up --build -d mongors1n1 mongors1n2 mongors1n3 \
	mongors2n1 mongors2n2 mongors2n3 \
	mongocfg1 mongocfg2 mongocfg3 \
	mongos1 mongos2 mongo_init redis postgres nginx auth_service ugc_service

up-mongo:
	docker-compose up -d mongors1n1 mongors1n2 mongors1n3 \
	mongors2n1 mongors2n2 mongors2n3 \
	mongocfg1 mongocfg2 mongocfg3 \
	mongos1 mongos2 mongo_init

up-all:
	docker-compose up -d

clean-ugc:
	docker-compose down -v mongors1n1 mongors1n2 mongors1n3 \
	mongors2n1 mongors2n2 mongors2n3 \
	mongocfg1 mongocfg2 mongocfg3 \
	mongos1 mongos2 mongo_init redis postgres nginx auth_service ugc_service

clean-mongo:
	docker-compose down -v mongors1n1 mongors1n2 mongors1n3 \
	mongors2n1 mongors2n2 mongors2n3 \
	mongocfg1 mongocfg2 mongocfg3 \
	mongos1 mongos2 mongo_init
