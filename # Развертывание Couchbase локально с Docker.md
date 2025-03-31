# Развертывание Couchbase локально с Docker

## 1. Установка Couchbase

### 1.1 Создаем Docker Network
```bash
docker network create couchbase-net
```
Эта сеть обеспечит связь между узлами Couchbase.

### 1.2 Запускаем контейнер Couchbase (первый узел)
```bash
docker run -d --name couchbase --network couchbase-net -p 8091-8096:8091-8096 -p 11210:11210 couchbase
```

---

## 2. Настройка кластера
1. Открываем [http://localhost:8091](http://localhost:8091).  
2. Нажимаем **"Setup New Cluster"**.  
3. Вводим имя кластера (`NoSQL_Cluster`) и логин/пароль.  
4. Завершаем настройку.  

---

## 3. Создание базы данных и тестовых данных

### 3.1 Создаем Bucket
1. В Couchbase Web UI переходим в **Buckets → Add Bucket**.  
2. Вводим имя `WorkBucket`, выделяем память (256MB), **Create**.  

### 3.2 Создаем Scope и Collection
```sql
CREATE SCOPE `WorkBucket`.workScope;  
CREATE COLLECTION `WorkBucket`.workScope.employees;
```

### 3.3 Добавляем 10 тестовых записей
```sql
INSERT INTO `WorkBucket`.workScope.employees (KEY, VALUE) VALUES 
("emp1", {"name": "Алексей Смирнов", "age": 32, "position": "Инженер", "city": "Москва"});
INSERT INTO `WorkBucket`.workScope.employees (KEY, VALUE) VALUES 
("emp2", {"name": "Ольга Иванова", "age": 28, "position": "Маркетолог", "city": "Санкт-Петербург"});
INSERT INTO `WorkBucket`.workScope.employees (KEY, VALUE) VALUES 
("emp3", {"name": "Дмитрий Козлов", "age": 40, "position": "Руководитель отдела", "city": "Екатеринбург"});
INSERT INTO `WorkBucket`.workScope.employees (KEY, VALUE) VALUES 
("emp4", {"name": "Марина Петрова", "age": 25, "position": "Дизайнер", "city": "Новосибирск"});
INSERT INTO `WorkBucket`.workScope.employees (KEY, VALUE) VALUES 
("emp5", {"name": "Игорь Сидоров", "age": 35, "position": "Разработчик", "city": "Казань"});
INSERT INTO `WorkBucket`.workScope.employees (KEY, VALUE) VALUES 
("emp6", {"name": "Татьяна Орлова", "age": 30, "position": "HR-менеджер", "city": "Ростов-на-Дону"});
INSERT INTO `WorkBucket`.workScope.employees (KEY, VALUE) VALUES 
("emp7", {"name": "Сергей Васильев", "age": 45, "position": "Финансовый аналитик", "city": "Челябинск"});
INSERT INTO `WorkBucket`.workScope.employees (KEY, VALUE) VALUES 
("emp8", {"name": "Екатерина Михайлова", "age": 27, "position": "Тестировщик", "city": "Омск"});
INSERT INTO `WorkBucket`.workScope.employees (KEY, VALUE) VALUES 
("emp9", {"name": "Андрей Павлов", "age": 29, "position": "Продуктовый менеджер", "city": "Уфа"});
INSERT INTO `WorkBucket`.workScope.employees (KEY, VALUE) VALUES 
("emp10", {"name": "Наталья Федорова", "age": 31, "position": "Бизнес-аналитик", "city": "Владивосток"});
```

### 3.4 Проверка данных
```sql
SELECT * FROM `WorkBucket`.workScope.employees;
```

---

## 4. Проверка отказоустойчивости

### 4.1 Добавляем второй узел в сеть
```bash
docker run -d --name couchbase2 --network couchbase-net couchbase
``` 

Затем в **Servers → Add Server**, добавляем `couchbase2`.  

### 4.2 Остановливаем первый узел и проверяем доступность
```bash
docker stop couchbase
```
Выполняем запрос:  
```sql
SELECT * FROM `WorkBucket`.workScope.employees;
```

### 4.3 Перезапускаем узел и проверяем синхронизацию
```bash
docker start couchbase
```