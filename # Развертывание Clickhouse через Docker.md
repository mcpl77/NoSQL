# Развертывание ClickHouse
# 1. Развертывание ClickHouse в Docker
Запускаем ClickHouse в Docker:
```bash
docker run -d --name clickhouse-server -p 8123:8123 -p 9000:9000 -p 9009:9009 clickhouse/clickhouse-server
```
Проверка работы сервера:

```bash
docker exec -it clickhouse-server clickhouse-client
```

# 2. Импорт тестовой базы данных
Берем пример с данными о COVID-19:

```sql
CREATE DATABASE covid;
```
```sql
CREATE TABLE covid.daily_reports
(
    date Date,
    country String,
    province Nullable(String),
    confirmed UInt32,
    deaths UInt32,
    recovered UInt32
)
ENGINE = MergeTree()
ORDER BY (date, country);
```
-- Импорт данных
```sql
INSERT INTO covid.daily_reports VALUES
('2020-01-22', 'China', 'Hubei', 444, 17, 28),
('2020-01-23', 'China', 'Hubei', 444, 17, 28);
```

# 3. Тестирование скорости запросов
Выполняем несколько запросов:

## 3.1. Агрегирующий запрос
```sql
SELECT country, sum(confirmed) as total_confirmed 
FROM covid.daily_reports 
GROUP BY country 
ORDER BY total_confirmed DESC 
LIMIT 10;
```
## 3.2. Фильтрация по дате
```sql
SELECT date, sum(confirmed) as daily_confirmed
FROM covid.daily_reports
WHERE date BETWEEN '2020-01-01' AND '2020-03-01'
GROUP BY date
ORDER BY date;
```
# 4. Развертывание дополнительного тестового набора данных
Используем пример набора данных "UK Property Price Paid":

```sql
CREATE DATABASE uk_price_paid;
```
```sql
CREATE TABLE uk_price_paid.price_paid
(
    price UInt32,
    date Date,
    postcode1 LowCardinality(String),
    postcode2 LowCardinality(String),
    type Enum8('terraced' = 1, 'semi-detached' = 2, 'detached' = 3, 'flat' = 4, 'other' = 0),
    is_new UInt8,
    duration Enum8('freehold' = 1, 'leasehold' = 2, 'unknown' = 0),
    addr1 String,
    addr2 String,
    street LowCardinality(String),
    locality LowCardinality(String),
    town LowCardinality(String),
    district LowCardinality(String),
    county LowCardinality(String)
)
ENGINE = MergeTree
ORDER BY (postcode1, postcode2, addr1, addr2);
```
## 4.1. Загрузка данных
```sql
INSERT INTO uk_price_paid.price_paid
WITH
   splitByChar(' ', postcode) AS p
SELECT
    toUInt32(price_string) AS price,
    parseDateTimeBestEffortUS(time) AS date,
    p[1] AS postcode1,
    p[2] AS postcode2,
    transform(a, ['T', 'S', 'D', 'F', 'O'], ['terraced', 'semi-detached', 'detached', 'flat', 'other']) AS type,
    b = 'Y' AS is_new,
    transform(c, ['F', 'L', 'U'], ['freehold', 'leasehold', 'unknown']) AS duration,
    addr1,
    addr2,
    street,
    locality,
    town,
    district,
    county
FROM url(
    'http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv',
    'CSV',
    'uuid_string String,
    price_string String,
    time String,
    postcode String,
    a String,
    b String,
    c String,
    addr1 String,
    addr2 String,
    street String,
    locality String,
    town String,
    district String,
    county String,
    d String,
    e String'
)
SETTINGS max_http_get_redirects=10;
```

# 5. Тестирование скорости запросов на большом наборе данных

# 5.1. Средняя цена по годам
```sql
SELECT toYear(date) AS year, avg(price) AS avg_price
FROM uk_price_paid.price_paid
GROUP BY year
ORDER BY year;
```
Ответ:
Query id: ca4190ad-8441-43e6-8bce-0571511413fa

    ┌─year─┬──────────avg_price─┐
 1. │ 1995 │  67945.58412124863 │
 2. │ 1996 │  71519.86992415696 │
 3. │ 1997 │  78549.12299702695 │
 4. │ 1998 │  85447.26773253019 │
 5. │ 1999 │  96048.86315664383 │
 6. │ 2000 │ 107499.54147169006 │
 7. │ 2001 │ 118899.05025540263 │
 8. │ 2002 │ 137966.13349805077 │
 9. │ 2003 │  155905.4649989923 │
10. │ 2004 │  178907.4335630165 │
11. │ 2005 │ 189374.28565237502 │
12. │ 2006 │ 203544.98771591412 │
13. │ 2007 │ 219383.86830336793 │
14. │ 2008 │ 217140.74846109207 │
15. │ 2009 │  213413.2164136976 │
16. │ 2010 │ 236120.99021085928 │
17. │ 2011 │ 232813.09782321012 │
18. │ 2012 │  238401.7240080249 │
19. │ 2013 │ 256956.07881424163 │
20. │ 2014 │   280043.708202197 │
21. │ 2015 │ 297410.82016611344 │
22. │ 2016 │ 313682.46472144837 │
23. │ 2017 │   346955.081686374 │
24. │ 2018 │  351551.0360761172 │
25. │ 2019 │  355076.7617037351 │
26. │ 2020 │ 377777.77140715485 │
27. │ 2021 │  388990.8321255083 │
28. │ 2022 │   413481.607778139 │
29. │ 2023 │  402008.1290670158 │
30. │ 2024 │ 376468.17710806086 │
31. │ 2025 │  365872.1968669457 │
    └──────┴────────────────────┘

31 rows in set. Elapsed: 0.171 sec. Processed 30.03 million rows, 180.20 MB (175.14 million rows/s., 1.05 GB/s.)
Peak memory usage: 522.47 KiB.

# 5.2. Количество сделок по типам недвижимости
```sql
SELECT type, count() AS count
FROM uk_price_paid.price_paid
GROUP BY type
ORDER BY count DESC;
```
Ответ:
Query id: 1b4a8138-d7ec-4988-8161-141369759fc8

   ┌─type──────────┬───count─┐
1. │ terraced      │ 8937381 │
2. │ semi-detached │ 8197883 │
3. │ detached      │ 6924267 │
4. │ flat          │ 5415002 │
5. │ other         │  558666 │
   └───────────────┴─────────┘

5 rows in set. Elapsed: 0.060 sec. Processed 30.03 million rows, 30.03 MB (503.23 million rows/s., 503.23 MB/s.)
Peak memory usage: 40.17 KiB.

# 5.3. Топ-10 самых дорогих улиц
```sql
SELECT street, town, max(price) AS max_price
FROM uk_price_paid.price_paid
GROUP BY street, town
ORDER BY max_price DESC
LIMIT 10;
```
Ответ:
Query id: d9385376-f2ca-4732-8ab6-b3930a689939

    ┌─street────────────────────────────┬─town────────────────┬─max_price─┐
 1. │ VICTORIA ROAD                     │ ASHFORD             │ 900000000 │
 2. │ BAKER STREET                      │ LONDON              │ 594300000 │
 3. │ STANHOPE ROW                      │ LONDON              │ 569200000 │
 4. │ FORTESS ROAD                      │ LONDON              │ 542540820 │
 5. │ NINE ELMS LANE                    │ LONDON              │ 523000000 │
 6. │ NEWMARKET LANE                    │ LEEDS               │ 494400000 │
 7. │ COOPER STREET                     │ WOLVERHAMPTON       │ 480000000 │
 8. │ SUTHERLAND AVENUE                 │ WOLVERHAMPTON       │ 480000000 │
 9. │ SUMNER STREET                     │ LONDON              │ 448500000 │
10. │ HAWICK CRESCENT INDUSTRIAL ESTATE │ NEWCASTLE UPON TYNE │ 448300979 │
    └───────────────────────────────────┴─────────────────────┴───────────┘

10 rows in set. Elapsed: 0.950 sec. Processed 30.03 million rows, 243.96 MB (31.61 million rows/s., 256.80 MB/s.)
Peak memory usage: 140.11 MiB.