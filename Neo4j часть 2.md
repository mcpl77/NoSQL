# Neo4j часть 2

## Шаг 1: Создание нод для туроператоров
Создадим ноды для туроператоров:
```cypher
CREATE (:TourOperator {name: "TUI"});
CREATE (:TourOperator {name: "Coral Travel"});
CREATE (:TourOperator {name: "Pegas Touristik"});
CREATE (:TourOperator {name: "Anex Tour"});
```

## Шаг 2: Создание нод для направлений (страна - конкретное место)
Создадим направления, представляющие связь между страной и конкретным местом:
```cypher
CREATE (:Country {name: "Italy"})-[:HAS_PLACE]->(:Place {name: "Rome"});
CREATE (:Country {name: "Italy"})-[:HAS_PLACE]->(:Place {name: "Venice"});
CREATE (:Country {name: "Italy"})-[:HAS_PLACE]->(:Place {name: "Florence"});
CREATE (:Country {name: "Spain"})-[:HAS_PLACE]->(:Place {name: "Barcelona"});
CREATE (:Country {name: "Spain"})-[:HAS_PLACE]->(:Place {name: "Madrid"});
CREATE (:Country {name: "Spain"})-[:HAS_PLACE]->(:Place {name: "Valencia"});
CREATE (:Country {name: "France"})-[:HAS_PLACE]->(:Place {name: "Paris"});
CREATE (:Country {name: "France"})-[:HAS_PLACE]->(:Place {name: "Nice"});
CREATE (:Country {name: "Greece"})-[:HAS_PLACE]->(:Place {name: "Athens"});
CREATE (:Country {name: "Greece"})-[:HAS_PLACE]->(:Place {name: "Santorini"});
CREATE (:Country {name: "Turkey"})-[:HAS_PLACE]->(:Place {name: "Antalya"});
CREATE (:Country {name: "Turkey"})-[:HAS_PLACE]->(:Place {name: "Istanbul"});
CREATE (:Country {name: "Maldives"})-[:HAS_PLACE]->(:Place {name: "Male"});
CREATE (:Country {name: "Egypt"})-[:HAS_PLACE]->(:Place {name: "Cairo"});
CREATE (:Country {name: "Egypt"})-[:HAS_PLACE]->(:Place {name: "Hurghada"});
```

## Шаг 3: Связывание туроператоров с направлениями
Свяжем туроператоров с направлениями:
```cypher
MATCH (to:TourOperator {name: "TUI"}), (p:Place {name: "Rome"})
CREATE (to)-[:OFFERS]->(p);

MATCH (to:TourOperator {name: "TUI"}), (p:Place {name: "Barcelona"})
CREATE (to)-[:OFFERS]->(p);

MATCH (to:TourOperator {name: "Coral Travel"}), (p:Place {name: "Paris"})
CREATE (to)-[:OFFERS]->(p);

MATCH (to:TourOperator {name: "Coral Travel"}), (p:Place {name: "Santorini"})
CREATE (to)-[:OFFERS]->(p);

MATCH (to:TourOperator {name: "Pegas Touristik"}), (p:Place {name: "Antalya"})
CREATE (to)-[:OFFERS]->(p);

MATCH (to:TourOperator {name: "Pegas Touristik"}), (p:Place {name: "Hurghada"})
CREATE (to)-[:OFFERS]->(p);

MATCH (to:TourOperator {name: "Anex Tour"}), (p:Place {name: "Male"})
CREATE (to)-[:OFFERS]->(p);

MATCH (to:TourOperator {name: "Anex Tour"}), (p:Place {name: "Istanbul"})
CREATE (to)-[:OFFERS]->(p);
```

## Шаг 4: Создание нод для городов с аэропортами/вокзалами
Добавим города, ближайшие к туристическим локациям, с аэропортами или вокзалами:
```cypher
CREATE (:City {name: "Rome", hasAirport: true, hasTrainStation: true});
CREATE (:City {name: "Venice", hasAirport: true, hasTrainStation: true});
CREATE (:City {name: "Florence", hasAirport: false, hasTrainStation: true});
CREATE (:City {name: "Barcelona", hasAirport: true, hasTrainStation: true});
CREATE (:City {name: "Madrid", hasAirport: true, hasTrainStation: true});
CREATE (:City {name: "Valencia", hasAirport: true, hasTrainStation: true});
CREATE (:City {name: "Paris", hasAirport: true, hasTrainStation: true});
CREATE (:City {name: "Nice", hasAirport: true, hasTrainStation: false});
CREATE (:City {name: "Athens", hasAirport: true, hasTrainStation: false});
CREATE (:City {name: "Santorini", hasAirport: true, hasTrainStation: false});
CREATE (:City {name: "Antalya", hasAirport: true, hasTrainStation: false});
CREATE (:City {name: "Istanbul", hasAirport: true, hasTrainStation: true});
CREATE (:City {name: "Male", hasAirport: true, hasTrainStation: false});
CREATE (:City {name: "Cairo", hasAirport: true, hasTrainStation: true});
CREATE (:City {name: "Hurghada", hasAirport: true, hasTrainStation: false});
```

## Шаг 5: Создание маршрутов между городами
Добавим маршруты между городами, охарактеризованные видом транспорта:
```cypher
MATCH (c1:City {name: "Rome"}), (c2:City {name: "Venice"})
CREATE (c1)-[:ROUTE {transport: "train"}]->(c2);

MATCH (c1:City {name: "Barcelona"}), (c2:City {name: "Madrid"})
CREATE (c1)-[:ROUTE {transport: "train"}]->(c2);

MATCH (c1:City {name: "Paris"}), (c2:City {name: "Barcelona"})
CREATE (c1)-[:ROUTE {transport: "train"}]->(c2);

MATCH (c1:City {name: "Athens"}), (c2:City {name: "Rome"})
CREATE (c1)-[:ROUTE {transport: "plane"}]->(c2);

MATCH (c1:City {name: "Antalya"}), (c2:City {name: "Athens"})
CREATE (c1)-[:ROUTE {transport: "plane"}]->(c2);

MATCH (c1:City {name: "Male"}), (c2:City {name: "Cairo"})
CREATE (c1)-[:ROUTE {transport: "plane"}]->(c2);

MATCH (c1:City {name: "Hurghada"}), (c2:City {name: "Cairo"})
CREATE (c1)-[:ROUTE {transport: "bus"}]->(c2);
```

## Шаг 6: Запрос на поиск направления только наземным транспортом
Запрос, который выводит направление, которое можно осуществить только наземным транспортом:
```cypher
MATCH path = (start:City)-[r:ROUTE*]->(end:City)
WHERE ALL(rel IN r WHERE rel.transport = "train" OR rel.transport = "bus")
RETURN path;
```

## Шаг 7: Анализ плана запроса
```cypher
EXPLAIN MATCH path = (start:City)-[r:ROUTE*]->(end:City)
WHERE ALL(rel IN r WHERE rel.transport = "train" OR rel.transport = "bus")
RETURN path;
```

## Шаг 8: Добавление индексов
Добавим индексы для оптимизации запроса:
```cypher
CREATE INDEX FOR (c:City) ON (c.name);
CREATE INDEX FOR ()-[r:ROUTE]-() ON (r.transport);
```

## Шаг 9: Повторный анализ плана запроса
После добавления индексов проверим план запроса:
```cypher
EXPLAIN MATCH path = (start:City)-[r:ROUTE*]->(end:City)
WHERE ALL(rel IN r WHERE rel.transport = "train" OR rel.transport = "bus")
RETURN path;
```

## Запрос для получения всех данных на графе
```cypher
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m;
```

# Итог
- Создана графовая модель данных для туроператоров, направлений, городов и маршрутов.
- Сделаны запросы для анализа данных, включая поиск направлений только наземным транспортом.
- Проанализирован план запроса и проведена оптимизизация его с помощью индексов.