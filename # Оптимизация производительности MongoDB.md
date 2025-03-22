# Шаг 1: Создание директории для хранения данных каждого инстанса MongoDB

```sh
mkdir C:\Mongo\config
mkdir C:\Mongo\shard1
mkdir C:\Mongo\shard2
mkdir C:\Mongo\shard3
```

# Шаг 2: Создание `docker-compose.yml` для шардированного кластера

```yaml
version: '3.8'
services:
  # Шард 1 (3 инстанса)
  shard1-1:
    image: mongo:6.0
    container_name: shard1-1
    ports:
      - "27022:27017"
    volumes:
      - ./shard1:/data/db
    command: mongod --shardsvr --replSet shard1 --bind_ip_all --dbpath /data/db --port 27017

  shard1-2:
    image: mongo:6.0
    container_name: shard1-2
    ports:
      - "27023:27017"
    volumes:
      - ./shard1:/data/db
    command: mongod --shardsvr --replSet shard1 --bind_ip_all --dbpath /data/db --port 27017

  shard1-3:
    image: mongo:6.0
    container_name: shard1-3
    ports:
      - "27024:27017"
    volumes:
      - ./shard1:/data/db
    command: mongod --shardsvr --replSet shard1 --bind_ip_all --dbpath /data/db --port 27017

  # Шард 2 (3 инстанса)
  shard2-1:
    image: mongo:6.0
    container_name: shard2-1
    ports:
      - "27025:27017"
    volumes:
      - ./shard2:/data/db
    command: mongod --shardsvr --replSet shard2 --bind_ip_all --dbpath /data/db --port 27017

  shard2-2:
    image: mongo:6.0
    container_name: shard2-2
    ports:
      - "27026:27017"
    volumes:
      - ./shard2:/data/db
    command: mongod --shardsvr --replSet shard2 --bind_ip_all --dbpath /data/db --port 27017

  shard2-3:
    image: mongo:6.0
    container_name: shard2-3
    ports:
      - "27027:27017"
    volumes:
      - ./shard2:/data/db
    command: mongod --shardsvr --replSet shard2 --bind_ip_all --dbpath /data/db --port 27017

  # Шард 3 (3 инстанса)
  shard3-1:
    image: mongo:6.0
    container_name: shard3-1
    ports:
      - "27028:27017"
    volumes:
      - ./shard3:/data/db
    command: mongod --shardsvr --replSet shard3 --bind_ip_all --dbpath /data/db --port 27017

  shard3-2:
    image: mongo:6.0
    container_name: shard3-2
    ports:
      - "27029:27017"
    volumes:
      - ./shard3:/data/db
    command: mongod --shardsvr --replSet shard3 --bind_ip_all --dbpath /data/db --port 27017

  shard3-3:
    image: mongo:6.0
    container_name: shard3-3
    ports:
      - "27030:27017"
    volumes:
      - ./shard3:/data/db
    command: mongod --shardsvr --replSet shard3 --bind_ip_all --dbpath /data/db --port 27017

  # Маршрутизатор (mongos)
  router:
    image: mongo:6.0
    container_name: router
    ports:
      - "27018:27018"
    depends_on:
      - shard1-1
      - shard1-2
      - shard1-3
      - shard2-1
      - shard2-2
      - shard2-3
      - shard3-1
      - shard3-2
      - shard3-3
    command: mongos --configdb config/config1:27019,config2:27019,config3:27019 --bind_ip_all --port 27018
```

# Шаг 3: Запуск кластера

```sh
docker-compose up -d
docker ps
```

# Шаг 4: Инициализация реплик

## Конфигурационные серверы
```sh
docker exec -it config1 mongosh --port 27019
```
```js
rs.initiate({
  _id: "config",
  members: [
    { _id: 0, host: "config1:27019" },
    { _id: 1, host: "config2:27019" },
    { _id: 2, host: "config3:27019" }
  ]
});
```

## Инициализация шарда 1
```sh
docker exec -it shard1-1 mongosh --port 27017
```
```js
rs.initiate({
  _id: "shard1",
  members: [
    { _id: 0, host: "shard1-1:27017" },
    { _id: 1, host: "shard1-2:27017" },
    { _id: 2, host: "shard1-3:27017" }
  ]
});
```

# Шаг 5: Добавление шардов

```sh
docker exec -it router mongosh --port 27018
```
```js
sh.addShard("shard1/shard1-1:27017,shard1-2:27017,shard1-3:27017")
sh.addShard("shard2/shard2-1:27017,shard2-2:27017,shard2-3:27017")
sh.addShard("shard3/shard3-1:27017,shard3-2:27017,shard3-3:27017")
```

# Шаг 6: Настройка балансировки

```js
sh.enableSharding("sample_mflix")
sh.shardCollection("sample_mflix.movies", { "_id": 1 })
```

# Шаг 7: Тестирование отказоустойчивости

Останавливаем один из инстансов шарда:

```sh
docker stop shard1-1
docker exec -it router mongosh --port 27018
```
```js
sh.status()
```
Результат:

```yaml
PS C:\Mongo> docker exec -it router mongosh --port 27018
Current Mongosh Log ID: 67def1a5623e3704ce6b140a
Connecting to:          mongodb://127.0.0.1:27018/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.4.2
Using MongoDB:          6.0.21
Using Mongosh:          2.4.2

For mongosh info see: https://www.mongodb.com/docs/mongodb-shell/

------
   The server generated these startup warnings when booting
   2025-03-22T17:14:40.869+00:00: Access control is not enabled for the database. Read and write access to data and configuration is unrestricted
------

[direct: mongos] test> sh.status()
shardingVersion
{ _id: 1, clusterId: ObjectId('67dee537702360d8771b34f9') }
---
shards
[
  {
    _id: 'shard1',
    host: 'shard1/shard1-1:27017,shard1-2:27017,shard1-3:27017',
    state: 1,
    topologyTime: Timestamp({ t: 1742661175, i: 1 })
  },
  {
    _id: 'shard2',
    host: 'shard2/shard2-1:27017,shard2-2:27017,shard2-3:27017',
    state: 1,
    topologyTime: Timestamp({ t: 1742661180, i: 2 })
  },
  {
    _id: 'shard3',
    host: 'shard3/shard3-1:27017,shard3-2:27017,shard3-3:27017',
    state: 1,
    topologyTime: Timestamp({ t: 1742661214, i: 5 })
  }
]
---
active mongoses
[ { '6.0.21': 1 } ]
---
autosplit
{ 'Currently enabled': 'yes' }
---
balancer
{
  'Currently enabled': 'yes',
  'Currently running': 'no',
  'Failed balancer rounds in last 5 attempts': 0,
  'Migration Results for the last 24 hours': 'No recent migrations'
}
---
shardedDataDistribution
[
  {
    ns: 'sample_mflix.movies',
    shards: [
      {
        shardName: 'shard1',
        numOrphanedDocs: 0,
        numOwnedDocuments: 0,
        ownedSizeBytes: null,
        orphanedSizeBytes: null
      }
    ]
  },
  {
    ns: 'config.system.sessions',
    shards: [
      {
        shardName: 'shard1',
        numOrphanedDocs: 0,
        numOwnedDocuments: 0,
        ownedSizeBytes: null,
        orphanedSizeBytes: null
      }
    ]
  }
]
---
databases
[
  {
    database: { _id: 'config', primary: 'config', partitioned: true },
    collections: {
      'config.system.sessions': {
        shardKey: { _id: 1 },
        unique: false,
        balancing: true,
        chunkMetadata: [ { shard: 'shard1', nChunks: 1024 } ],
        chunks: [
          { min: { _id: MinKey() }, max: { _id: { id: UUID('00400000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 1 }) },
          { min: { _id: { id: UUID('00400000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('00800000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 2 }) },
          { min: { _id: { id: UUID('00800000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('00c00000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 3 }) },
          { min: { _id: { id: UUID('00c00000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('01000000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 4 }) },
          { min: { _id: { id: UUID('01000000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('01400000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 5 }) },
          { min: { _id: { id: UUID('01400000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('01800000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 6 }) },
          { min: { _id: { id: UUID('01800000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('01c00000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 7 }) },
          { min: { _id: { id: UUID('01c00000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('02000000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 8 }) },
          { min: { _id: { id: UUID('02000000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('02400000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 9 }) },
          { min: { _id: { id: UUID('02400000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('02800000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 10 }) },
          { min: { _id: { id: UUID('02800000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('02c00000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 11 }) },
          { min: { _id: { id: UUID('02c00000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('03000000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 12 }) },
          { min: { _id: { id: UUID('03000000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('03400000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 13 }) },
          { min: { _id: { id: UUID('03400000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('03800000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 14 }) },
          { min: { _id: { id: UUID('03800000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('03c00000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 15 }) },
          { min: { _id: { id: UUID('03c00000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('04000000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 16 }) },
          { min: { _id: { id: UUID('04000000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('04400000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 17 }) },
          { min: { _id: { id: UUID('04400000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('04800000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 18 }) },
          { min: { _id: { id: UUID('04800000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('04c00000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 19 }) },
          { min: { _id: { id: UUID('04c00000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('05000000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 20 }) },
          'too many chunks to print, use verbose if you want to force print'
        ],
        tags: []
      }
    }
  },
  {
    database: {
      _id: 'sample_mflix',
      primary: 'shard1',
      partitioned: false,
      version: {
        uuid: UUID('082ce770-3cbe-42ae-881a-dd927bdc8c5e'),
        timestamp: Timestamp({ t: 1742661238, i: 1 }),
        lastMod: 1
      }
    },
    collections: {
      'sample_mflix.movies': {
        shardKey: { _id: 1 },
        unique: false,
        balancing: true,
        chunkMetadata: [ { shard: 'shard1', nChunks: 1 } ],
        chunks: [
          { min: { _id: MinKey() }, max: { _id: MaxKey() }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 0 }) }
        ],
        tags: []
      }
    }
  }
]
````
Один из инстансов шарда стал недоступен, но данные остаются доступными благодаря репликации.

Восстанавливаем инстанс:
```sh
docker start shard1-1
```
Проверяем состояние снова:
```js
sh.status()
```
Инстанс восстановлен и снова стал частью реплики.
Результат:
```yaml
[direct: mongos] test> sh.status()
shardingVersion
{ _id: 1, clusterId: ObjectId('67dee537702360d8771b34f9') }
---
shards
[
  {
    _id: 'shard1',
    host: 'shard1/shard1-1:27017,shard1-2:27017,shard1-3:27017',
    state: 1,
    topologyTime: Timestamp({ t: 1742661175, i: 1 })
  },
  {
    _id: 'shard2',
    host: 'shard2/shard2-1:27017,shard2-2:27017,shard2-3:27017',
    state: 1,
    topologyTime: Timestamp({ t: 1742661180, i: 2 })
  },
  {
    _id: 'shard3',
    host: 'shard3/shard3-1:27017,shard3-2:27017,shard3-3:27017',
    state: 1,
    topologyTime: Timestamp({ t: 1742661214, i: 5 })
  }
]
---
active mongoses
[ { '6.0.21': 1 } ]
---
autosplit
{ 'Currently enabled': 'yes' }
---
balancer
{
  'Currently enabled': 'yes',
  'Failed balancer rounds in last 5 attempts': 0,
  'Currently running': 'no',
  'Migration Results for the last 24 hours': 'No recent migrations'
}
---
shardedDataDistribution
[
  {
    ns: 'sample_mflix.movies',
    shards: [
      {
        shardName: 'shard1',
        numOrphanedDocs: 0,
        numOwnedDocuments: 0,
        ownedSizeBytes: null,
        orphanedSizeBytes: null
      }
    ]
  },
  {
    ns: 'config.system.sessions',
    shards: [
      {
        shardName: 'shard1',
        numOrphanedDocs: 0,
        numOwnedDocuments: 0,
        ownedSizeBytes: null,
        orphanedSizeBytes: null
      }
    ]
  }
]
---
databases
[
  {
    database: { _id: 'config', primary: 'config', partitioned: true },
    collections: {
      'config.system.sessions': {
        shardKey: { _id: 1 },
        unique: false,
        balancing: true,
        chunkMetadata: [ { shard: 'shard1', nChunks: 1024 } ],
        chunks: [
          { min: { _id: MinKey() }, max: { _id: { id: UUID('00400000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 1 }) },
          { min: { _id: { id: UUID('00400000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('00800000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 2 }) },
          { min: { _id: { id: UUID('00800000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('00c00000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 3 }) },
          { min: { _id: { id: UUID('00c00000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('01000000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 4 }) },
          { min: { _id: { id: UUID('01000000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('01400000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 5 }) },
          { min: { _id: { id: UUID('01400000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('01800000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 6 }) },
          { min: { _id: { id: UUID('01800000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('01c00000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 7 }) },
          { min: { _id: { id: UUID('01c00000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('02000000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 8 }) },
          { min: { _id: { id: UUID('02000000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('02400000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 9 }) },
          { min: { _id: { id: UUID('02400000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('02800000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 10 }) },
          { min: { _id: { id: UUID('02800000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('02c00000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 11 }) },
          { min: { _id: { id: UUID('02c00000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('03000000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 12 }) },
          { min: { _id: { id: UUID('03000000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('03400000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 13 }) },
          { min: { _id: { id: UUID('03400000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('03800000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 14 }) },
          { min: { _id: { id: UUID('03800000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('03c00000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 15 }) },
          { min: { _id: { id: UUID('03c00000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('04000000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 16 }) },
          { min: { _id: { id: UUID('04000000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('04400000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 17 }) },
          { min: { _id: { id: UUID('04400000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('04800000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 18 }) },
          { min: { _id: { id: UUID('04800000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('04c00000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 19 }) },
          { min: { _id: { id: UUID('04c00000-0000-0000-0000-000000000000') } }, max: { _id: { id: UUID('05000000-0000-0000-0000-000000000000') } }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 20 }) },
          'too many chunks to print, use verbose if you want to force print'
        ],
        tags: []
      }
    }
  },
  {
    database: {
      _id: 'sample_mflix',
      primary: 'shard1',
      partitioned: false,
      version: {
        uuid: UUID('082ce770-3cbe-42ae-881a-dd927bdc8c5e'),
        timestamp: Timestamp({ t: 1742661238, i: 1 }),
        lastMod: 1
      }
    },
    collections: {
      'sample_mflix.movies': {
        shardKey: { _id: 1 },
        unique: false,
        balancing: true,
        chunkMetadata: [ { shard: 'shard1', nChunks: 1 } ],
        chunks: [
          { min: { _id: MinKey() }, max: { _id: MaxKey() }, 'on shard': 'shard1', 'last modified': Timestamp({ t: 1, i: 0 }) }
        ],
        tags: []
      }
    }
  }
]
```
# Шаг 8: Настройка аутентификации и многоролевого доступа

Создаем пользователя администратора:
```sh
docker exec -it router mongosh --port 27018
```
```js
use admin
db.createUser({
  user: "admin",
  pwd: "password",
  roles: [ { role: "root", db: "admin" } ]
})
```

Создаем пользователя для базы данных sample_mflix:
```js
use sample_mflix
db.createUser({
  user: "readWriteUser",
  pwd: "password",
  roles: [ { role: "readWrite", db: "sample_mflix" } ]
})
```

Создаем пользователя с правами только на чтение:
```js
db.createUser({
  user: "readOnlyUser",
  pwd: "password",
  roles: [ { role: "read", db: "sample_mflix" } ]
})
```

Создаем пользователя с ограниченными правами (только для одной коллекции):
```js
db.createUser({
  user: "limitedUser",
  pwd: "password",
  roles: [
    { role: "readWrite", db: "sample_mflix", collection: "movies" }
  ]
})
```

# Шаг 9: Проверка списка пользователей
Подключаемся к MongoDB как администратор:
mongosh "mongodb://admin:password@localhost:27018/?authSource=admin"
Проверка списка пользователей в базе данных sample_mflix:

use sample_mflix
db.getUsers()

Результат:
```yaml
[direct: mongos] test> use sample_mflix
switched to db sample_mflix
[direct: mongos] sample_mflix> db.getUsers()
{
  users: [
    {
      _id: 'sample_mflix.limitedUser',
      userId: UUID('867ae6ea-8ffa-4fdb-9cac-65eb47e22df5'),
      user: 'limitedUser',
      db: 'sample_mflix',
      roles: [ { role: 'readWrite', db: 'sample_mflix' } ],
      mechanisms: [ 'SCRAM-SHA-1', 'SCRAM-SHA-256' ]
    },
    {
      _id: 'sample_mflix.readOnlyUser',
      userId: UUID('542a3c46-2f32-4f04-81f5-e1d616868d86'),
      user: 'readOnlyUser',
      db: 'sample_mflix',
      roles: [ { role: 'read', db: 'sample_mflix' } ],
      mechanisms: [ 'SCRAM-SHA-1', 'SCRAM-SHA-256' ]
    },
    {
      _id: 'sample_mflix.readWriteUser',
      userId: UUID('84bd75d6-7786-44fe-840e-807b96a79646'),
      user: 'readWriteUser',
      db: 'sample_mflix',
      roles: [ { role: 'readWrite', db: 'sample_mflix' } ],
      mechanisms: [ 'SCRAM-SHA-1', 'SCRAM-SHA-256' ]
    }
  ],
  ok: 1,
  '$clusterTime': {
    clusterTime: Timestamp({ t: 1742667694, i: 1 }),
    signature: {
      hash: Binary.createFromBase64('AAAAAAAAAAAAAAAAAAAAAAAAAAA=', 0),
      keyId: Long('0')
    }
  },
  operationTime: Timestamp({ t: 1742667694, i: 1 })
}
````
# Проблемы при выполнении задания:
- Возникала нехватка памяти из-за докера, в связи с чем периодически отпадала связь c базой данных и не было возможности проводит манипуляции по части шардов и пользователей.
