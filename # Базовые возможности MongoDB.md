# Описание развертывания MongoDB через Docker

## Шаг 1: Создание директории для хранения данных MongoDB
Чтобы данные MongoDB сохранялись на локальном диске даже после остановки контейнера, создаем папку для монтирования:

```sh
mkdir C:\Mongo\data
```

## Шаг 2: Запуск MongoDB в Docker-контейнере
Запускаем MongoDB в Docker-контейнере:

```sh
docker run -d --name mongodb-container -p 27017:27017 -v C:\Mongo\data:/data/db mongo
```

Проверяем статус контейнера:

```sh
docker ps
```

Должен отобразиться `mongodb-container`.

## Шаг 3: Установка и настройка mongoimport и mongosh
Для импорта данных и выполнения запросов потребуются утилиты `mongoimport` и `mongosh`.

Проверяем их установку:

```sh
mongoimport --version
mongosh --version
```

Если отобразились версии, продолжаем настройку.

## Шаг 4: Подключение к MongoDB

Подключаемся через MongoDB Shell (`mongosh`):

```sh
mongosh "mongodb://localhost:27017"
```

Проверяем список баз данных:

```sh
show dbs
```

## Шаг 5: Загрузка тестовых данных

Клонируем тестовый набор данных:

```sh
git clone https://github.com/neelabalan/mongodb-sample-dataset.git
```

Переходим в папку с репозиторием:

```sh
cd mongodb-sample-dataset
```

Импортируем данные для коллекции `movies`:

```sh
mongoimport --uri="mongodb://localhost:27017/sample_mflix" --collection=movies --file=./sample_mflix/movies.json
```

## Шаг 6: Выполнение запросов

### Выборка данных

Выборка фильмов с рейтингом IMDb выше 8.5:

```sh
use sample_mflix

db.movies.find({ "imdb.rating": { $gt: 8.5 } }, { title: 1, imdb: 1 }).pretty()
```

Выборка фильмов определённого года:

```sh
db.movies.find({ year: 1994 }, { title: 1, year: 1 }).pretty()
```

### Обновление данных

Обновление рейтинга фильма:

```sh
db.movies.updateOne(
  { title: "The Shawshank Redemption" },
  { $set: { "imdb.rating": 9.4 } }
)
```

Добавление нового поля:

```sh
db.movies.updateOne(
  { title: "The Godfather" },
  { $set: { tags: ["classic", "crime", "drama"] } }
)
