#!/bin/bash

echo "Starting MongoDB cluster setup..."

# Задержка для того, чтобы все контейнеры поднялись
sleep 30

# Настройка серверов конфигурации
echo "Initializing config servers..."
mongosh --host mongocfg1 --eval 'rs.initiate({
  _id: "mongors1conf",
  configsvr: true,
  members: [
    { _id: 0, host: "mongocfg1:27017" },
    { _id: 1, host: "mongocfg2:27017" },
    { _id: 2, host: "mongocfg3:27017" }
  ]
})'

echo "Checking config server status..."
mongosh --host mongocfg1 --eval 'rs.status()'

# Настройка набора реплик первого шарда
echo "Initializing shard 1 replica set..."
mongosh --host mongors1n1 --eval 'rs.initiate({
  _id: "mongors1",
  members: [
    { _id: 0, host: "mongors1n1:27017" },
    { _id: 1, host: "mongors1n2:27017" },
    { _id: 2, host: "mongors1n3:27017" }
  ]
})'

echo "Checking shard 1 replica set status..."
mongosh --host mongors1n1 --eval 'rs.status()'

# Добавление первого шарда в маршрутизаторы
echo "Adding shard 1 to mongos..."
mongosh --host mongos1 --eval 'sh.addShard("mongors1/mongors1n1:27017")'

# Настройка набора реплик второго шарда
echo "Initializing shard 2 replica set..."
mongosh --host mongors2n1 --eval 'rs.initiate({
  _id: "mongors2",
  members: [
    { _id: 0, host: "mongors2n1:27017" },
    { _id: 1, host: "mongors2n2:27017" },
    { _id: 2, host: "mongors2n3:27017" }
  ]
})'

echo "Checking shard 2 replica set status..."
mongosh --host mongors2n1 --eval 'rs.status()'

# Добавление второго шарда в маршрутизаторы
echo "Adding shard 2 to mongos..."
mongosh --host mongos1 --eval 'sh.addShard("mongors2/mongors2n1:27017")'

# Проверка статуса шардирования
echo "Checking sharding status..."
mongosh --host mongos1 --eval 'sh.status()'

echo "MongoDB cluster setup completed successfully!"
