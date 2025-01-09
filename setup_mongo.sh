#!/bin/bash

# Функция ожидания, пока mongod/mongos не будет отвечать.
# Аргумент: имя хоста (например, mongocfg1), к которому будем пытаться подключиться.
function wait_for_mongo() {
  local host="$1"
  local max_attempts=20
  local attempt=1

  echo "Waiting for $host to be ready..."

  while (( attempt <= max_attempts ))
  do
    mongosh --quiet --host "$host" --eval 'db.adminCommand({ ping: 1 })' >/dev/null 2>&1 && {
      echo "Host $host is ready!"
      return 0
    }

    echo "Host $host is not up yet... retry #$attempt"
    sleep 5
    ((attempt++))
  done

  echo "ERROR: Host $host did not become ready after $max_attempts attempts."
  exit 1
}

echo "Starting MongoDB cluster setup..."

# Ожидаем конфигурационные серверы (mongocfg1, mongocfg2, mongocfg3)

wait_for_mongo "mongocfg1"
wait_for_mongo "mongocfg2"
wait_for_mongo "mongocfg3"
wait_for_mongo "mongos1"

sleep 2

#Инициализация конфигурационных серверов
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

wait_for_mongo "mongors1n1"
wait_for_mongo "mongors1n2"
wait_for_mongo "mongors1n3"

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
wait_for_mongo "mongos1"

echo "Adding shard 1 to mongos..."
mongosh --host mongos1 --eval 'sh.addShard("mongors1/mongors1n1:27017")'

# Настройка набора реплик второго шарда
echo "Initializing shard 2 replica set..."

# Убедимся, что ноды шарда 2 доступны
wait_for_mongo "mongors2n1"
wait_for_mongo "mongors2n2"
wait_for_mongo "mongors2n3"

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
wait_for_mongo "mongos1"

echo "Adding shard 2 to mongos..."
mongosh --host mongos1 --eval 'sh.addShard("mongors2/mongors2n1:27017")'

# Проверка статуса шардирования
echo "Checking sharding status..."
mongosh --host mongos1 --eval 'sh.status()'

echo "MongoDB cluster setup completed successfully!"
