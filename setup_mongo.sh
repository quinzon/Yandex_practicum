#!/bin/bash

echo "Starting MongoDB cluster setup..."

# Настройка серверов конфигурации
echo "Initializing config servers..."
docker exec -it mongocfg1 bash -c 'echo "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"mongocfg1\"}, {_id: 1, host: \"mongocfg2\"}, {_id: 2, host: \"mongocfg3\"}]})" | mongosh'

echo "Checking config server status..."
docker exec -it mongocfg1 bash -c 'echo "rs.status()" | mongosh'

# Настройка набора реплик первого шарда
echo "Initializing shard 1 replica set..."
docker exec -it mongors1n1 bash -c 'echo "rs.initiate({_id: \"mongors1\", members: [{_id: 0, host: \"mongors1n1\"}, {_id: 1, host: \"mongors1n2\"}, {_id: 2, host: \"mongors1n3\"}]})" | mongosh'

echo "Checking shard 1 replica set status..."
docker exec -it mongors1n1 bash -c 'echo "rs.status()" | mongosh'

# Добавление первого шарда в маршрутизаторы
echo "Adding shard 1 to mongos..."
docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors1/mongors1n1\")" | mongosh'

# Настройка набора реплик второго шарда
echo "Initializing shard 2 replica set..."
docker exec -it mongors2n1 bash -c 'echo "rs.initiate({_id: \"mongors2\", members: [{_id: 0, host: \"mongors2n1\"}, {_id: 1, host: \"mongors2n2\"}, {_id: 2, host: \"mongors2n3\"}]})" | mongosh'

echo "Checking shard 2 replica set status..."
docker exec -it mongors2n1 bash -c 'echo "rs.status()" | mongosh'

# Добавление второго шарда в маршрутизаторы
echo "Adding shard 2 to mongos..."
docker exec -it mongos1 bash -c 'echo "sh.addShard(\"mongors2/mongors2n1\")" | mongosh'

# Проверка статуса шардирования
echo "Checking sharding status..."
docker exec -it mongos1 bash -c 'echo "sh.status()" | mongosh'

echo "MongoDB cluster setup completed successfully!"
