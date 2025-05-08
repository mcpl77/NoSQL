Развёртывание Redis в Docker и тестирование производительности с большими JSON-данными

# 1. Развёртывание Redis в Docker через PyCharm
## 1.1. Настройка docker-compose.yml
Создаем файл docker-compose.yml:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7.2-alpine
    container_name: redis_container
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --requirepass qwerty --save 60 1
    restart: unless-stopped

volumes:
  redis_data:
```

## 1.2. Запуск Redis
```bash
docker-compose up -d
```
Проверка:
```bash
docker ps
```
Должен отобразиться контейнер redis_container.

# 2. Подключение к Redis
## 2.1. Через redis-cli
```bash
docker exec -it redis_container redis-cli -a qwerty
```
Проверка подключения:
```bash
PING  # Должен вернуть "PONG"
```
## 2.2. Через Python (используем PyCharm)
Установливаем библиотеку:
```bash
pip install redis
```
Подключение (redis_test.py):
```python
import redis

r = redis.Redis(
    host='localhost',
    port=6379,
    password='your_strong_password',
    decode_responses=True
)

print("Подключение успешно:", r.ping())
```
# 3. Работа с JSON-файлом
## 3.1. Генерация тестового JSON
Создаем файл generate_json.py:
```python
import json
import random

data = {
    f"user_{i}": {
        "id": i,
        "name": f"User_{i}",
        "age": random.randint(18, 60),
        "email": f"user_{i}@example.com"
    }
    for i in range(1, 100000)  # ~20 МБ
}

with open("large_data.json", "w") as f:
    json.dump(data, f)

print("Файл large_data.json создан.")
```
Запуск:
```bash
python generate_json.py
```
## 3.2. Загрузка JSON в Redis
Используем оптимизированный код с Pipeline и Batch-обработкой (redis_test.py):
```python
import json
import time

def test_write_optimized(data, batch_size=1000):
    start = time.time()
    
    # 1. Запись как строки (если JSON < 500 КБ)
    if len(json.dumps(data)) < 500_000:
        r.set("big_json_str", json.dumps(data))
    
    # 2. Запись в Hash (пачками по batch_size)
    pipe = r.pipeline()
    for i, (key, value) in enumerate(data.items()):
        pipe.hset("optimized_hset", key, str(value))
        if (i + 1) % batch_size == 0:
            pipe.execute()
            pipe = r.pipeline()
    pipe.execute()
    
    # 3. Запись в ZSet
    pipe = r.pipeline()
    for idx, (key, value) in enumerate(data.items()):
        pipe.zadd("optimized_zset", {str(value): idx})
        if (idx + 1) % batch_size == 0:
            pipe.execute()
            pipe = r.pipeline()
    pipe.execute()
    
    # 4. Запись в List
    r.lpush("optimized_list", *[str(item) for item in list(data.items())[:10000]])
    
    return time.time() - start

if __name__ == "__main__":
    with open("large_data.json", "r") as f:
        big_json = json.load(f)
    
    write_time = test_write_optimized(big_json, batch_size=5000)
    print(f"Запись заняла: {write_time:.2f} сек")
```
Результат:

Запись заняла: 4.25 сек

# 4. Тестирование скорости чтения
Добавляем в redis_test.py:
```python
def test_read():
    start = time.time()
    
    r.get("big_json_str")
    r.hgetall("optimized_hset")
    r.zrange("optimized_zset", 0, -1)
    r.lrange("optimized_list", 0, -1)
    
    return time.time() - start

read_time = test_read()
print(f"Чтение заняло: {read_time:.2f} сек")
```
Вывод:

Чтение заняло: 0.87 сек

# 5. Проверка данных в Redis CLI
```bash
docker exec -it redis_container redis-cli -a your_strong_password
```
```bash
KEYS *
HGET optimized_hset user_1
ZRANGE optimized_zset 0 -1
LLEN optimized_list
```
# 6. Выводы
Метрика	| Результат
---------------------
Запись  |~4.25 сек
Чтение	|~0.87 сек

Оптимизации:

Использование Pipeline ускорило запись в 10-100 раз.

Batch-обработка предотвратила перегрузку Redis.
