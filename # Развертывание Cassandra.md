# Развертывание Cassandra

## 1. Создание рабочей директории

```bash
mkdir C:\Cass
cd C:\Cass
```

## 2. Docker-compose файл
Создание файла docker-compose.yml со следующим содержимым:

```yaml
version: '3.8'

volumes:
  cass1_data:
  cass2_data:
  cass3_data:

services:
  cass1:
    image: cassandra:4.0.9
    container_name: cass1
    hostname: cass1
    mem_limit: 3g
    healthcheck:
      test: ["CMD-SHELL", "[ $$(nodetool statusgossip) = running ] || exit 1"]
      interval: 15s
      timeout: 30s
      retries: 30
      start_period: 120s
    environment:
      - HEAP_NEWSIZE=512M
      - MAX_HEAP_SIZE=2G
      - CASSANDRA_SEEDS=cass1,cass2
      - CASSANDRA_CLUSTER_NAME=RussianCluster
      - CASSANDRA_DC=datacenter1
      - CASSANDRA_RACK=rack1
      - CASSANDRA_ENDPOINT_SNITCH=GossipingPropertyFileSnitch
    volumes:
      - cass1_data:/var/lib/cassandra
    ports:
      - "9042:9042"
      - "7000:7000"

  cass2:
    image: cassandra:4.0.9
    container_name: cass2
    hostname: cass2
    mem_limit: 3g
    depends_on:
      cass1:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "[ $$(nodetool statusgossip) = running ] || exit 1"]
      interval: 15s
      timeout: 30s
      retries: 30
    environment:
      - HEAP_NEWSIZE=512M
      - MAX_HEAP_SIZE=2G
      - CASSANDRA_SEEDS=cass1,cass2
    volumes:
      - cass2_data:/var/lib/cassandra
    ports:
      - "9043:9042"

  cass3:
    image: cassandra:4.0.9
    container_name: cass3
    hostname: cass3
    mem_limit: 3g
    depends_on:
      cass2:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "[ $$(nodetool statusgossip) = running ] || exit 1"]
      interval: 15s
      timeout: 30s
      retries: 30
    environment:
      - HEAP_NEWSIZE=512M
      - MAX_HEAP_SIZE=2G
      - CASSANDRA_SEEDS=cass1,cass2
    volumes:
      - cass3_data:/var/lib/cassandra
    ports:
      - "9044:9042"
```

### 2.1. Запуск кластера
```bash
docker-compose up -d
```

## 3. Создание структуры данных

### 3.1 Подключение к Cassandra:
```bash
docker exec -it cass1 cqlsh
```

Выполнение следующих команд:

-- 1. Ключевое пространство для российских данных
```sql
CREATE KEYSPACE ru_data WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 2
};
```

```sql
USE ru_data;
```

-- 2. Таблица российских городов
```sql
CREATE TABLE russian_cities (
  region text,
  city text,
  population int,
  foundation_year int,
  area_km2 float,
  is_administrative_center boolean,
  PRIMARY KEY ((region), city)
) WITH CLUSTERING ORDER BY (city ASC);
```

-- 3. Таблица российских компаний
```sql
CREATE TABLE russian_companies (
  industry text,
  company_name text,
  revenue_mln_rub decimal,
  employees int,
  founded_year int,
  headquarters text,
  PRIMARY KEY ((industry), revenue_mln_rub, company_name)
) WITH CLUSTERING ORDER BY (revenue_mln_rub DESC, company_name ASC);
```

-- 4. Таблица российской одежды
```sql
CREATE TABLE russian_clothing (
  clothing_type text,
  brand text,
  price_rub decimal,
  size text,
  in_stock boolean,
  made_in text,
  PRIMARY KEY ((clothing_type), brand, price_rub)
) WITH CLUSTERING ORDER BY (brand ASC, price_rub DESC);
```

-- 5. Заполнение данными российских городов
```sql
INSERT INTO russian_cities (region, city, population, foundation_year, area_km2, is_administrative_center)
VALUES ('Московская область', 'Москва', 12655050, 1147, 2561.5, true);

INSERT INTO russian_cities (region, city, population, foundation_year, area_km2, is_administrative_center)
VALUES ('Ленинградская область', 'Санкт-Петербург', 5384342, 1703, 1439, true);

INSERT INTO russian_cities (region, city, population, foundation_year, area_km2, is_administrative_center)
VALUES ('Свердловская область', 'Екатеринбург', 1493749, 1723, 495, true);

INSERT INTO russian_cities (region, city, population, foundation_year, area_km2, is_administrative_center)
VALUES ('Новосибирская область', 'Новосибирск', 1625631, 1893, 505.6, true);

INSERT INTO russian_cities (region, city, population, foundation_year, area_km2, is_administrative_center)
VALUES ('Краснодарский край', 'Краснодар', 948827, 1793, 339.3, true);
```

-- 6. Заполнение данными российских компаний
```sql
INSERT INTO russian_companies (industry, company_name, revenue_mln_rub, employees, founded_year, headquarters)
VALUES ('Нефтегазовая', 'Газпром', 10079000, 466000, 1989, 'Москва');

INSERT INTO russian_companies (industry, company_name, revenue_mln_rub, employees, founded_year, headquarters)
VALUES ('IT', 'Яндекс', 336000, 18600, 1997, 'Москва');

INSERT INTO russian_companies (industry, company_name, revenue_mln_rub, employees, founded_year, headquarters)
VALUES ('Розничная торговля', 'Магнит', 2000000, 316000, 1994, 'Краснодар');

INSERT INTO russian_companies (industry, company_name, revenue_mln_rub, employees, founded_year, headquarters)
VALUES ('Металлургия', 'Норникель', 1500000, 73000, 1935, 'Москва');

INSERT INTO russian_companies (industry, company_name, revenue_mln_rub, employees, founded_year, headquarters)
VALUES ('IT', 'VK', 125000, 12500, 1998, 'Санкт-Петербург');
```

-- 7. Заполнение данными российской одежды
```sql
INSERT INTO russian_clothing (clothing_type, brand, price_rub, size, in_stock, made_in)
VALUES ('Пальто', 'ZARINA', 7999.99, 'M', true, 'Москва');

INSERT INTO russian_clothing (clothing_type, brand, price_rub, size, in_stock, made_in)
VALUES ('Джинсы', 'Gloria Jeans', 3499.50, 'L', true, 'Новосибирск');

INSERT INTO russian_clothing (clothing_type, brand, price_rub, size, in_stock, made_in)
VALUES ('Платье', 'Love Republic', 5999.00, 'S', false, 'Санкт-Петербург');

INSERT INTO russian_clothing (clothing_type, brand, price_rub, size, in_stock, made_in)
VALUES ('Куртка', 'Baon', 8999.99, 'XL', true, 'Екатеринбург');

INSERT INTO russian_clothing (clothing_type, brand, price_rub, size, in_stock, made_in)
VALUES ('Футболка', 'Sela', 1499.00, 'M', true, 'Краснодар');
```

## 4. Запросы

-- 1. Города с населением более 1 миллиона
```sql
SELECT * FROM russian_cities WHERE population > 1000000 ALLOW FILTERING;
```
Ответ:
```bash

 region                | city            | area_km2  | foundation_year | is_administrative_center | population
-----------------------+-----------------+-----------+-----------------+--------------------------+------------
  Свердловская область |    Екатеринбург |       495 |            1723 |                     True |    1493749
    Московская область |          Москва |    2561.5 |            1147 |                     True |   12655050
 Ленинградская область | Санкт-Петербург |      1439 |            1703 |                     True |    5384342
 Новосибирская область |     Новосибирск | 505.60001 |            1893 |                     True |    1625631

(4 rows)
```

-- 2. Компании IT-индустрии с сортировкой по доходу
```sql
SELECT * FROM russian_companies WHERE industry = 'IT';
```
Ответ:
```bash

 industry | revenue_mln_rub | company_name | employees | founded_year | headquarters
----------+-----------------+--------------+-----------+--------------+-----------------
       IT |          336000 |       Яндекс |     18600 |         1997 |          Москва
       IT |          125000 |           VK |     12500 |         1998 | Санкт-Петербург

(2 rows)
```
-- 3. Одежда бренда ZARINA
```sql
SELECT * FROM russian_clothing WHERE brand = 'ZARINA' ALLOW FILTERING;
```
Ответ:
```bash

 clothing_type | brand  | price_rub | in_stock | made_in | size
---------------+--------+-----------+----------+---------+------
        Пальто | ZARINA |   7999.99 |     True |  Москва |    M

(1 rows)
```
-- 4. Создание индекса для поиска по наличию товара
```sql
CREATE INDEX ON russian_clothing (in_stock);
```

-- 5. Поиск одежды в наличии
```sql
SELECT * FROM russian_clothing WHERE in_stock = true;
```
Ответ:
```bash

 clothing_type | brand        | price_rub | in_stock | made_in      | size
---------------+--------------+-----------+----------+--------------+------
      Футболка |         Sela |   1499.00 |     True |    Краснодар |    M
        Джинсы | Gloria Jeans |   3499.50 |     True |  Новосибирск |    L
        Куртка |         Baon |   8999.99 |     True | Екатеринбург |   XL
        Пальто |       ZARINA |   7999.99 |     True |       Москва |    M

(4 rows)
```