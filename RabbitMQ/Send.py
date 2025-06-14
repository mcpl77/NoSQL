import pika

# Параметры подключения к RabbitMQ
credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)

# Список очередей и сообщений
queues = ['queue1', 'queue2', 'queue3']
messages = ['Hello, RabbitMQ!', 'I love music', 'Go for a walk']


# Функция для отправки сообщений
def send_messages():
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Создаем очереди, если они еще не существуют
    for queue in queues:
        channel.queue_declare(queue=queue, durable=True)

    # Отправляем сообщения в соответствующие очереди
    for queue, message in zip(queues, messages):
        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # Делаем сообщения устойчивыми
        )
        print(f" [x] Sent '{message}' to {queue}")

    connection.close()


if __name__ == "__main__":
    print("Sending messages...")
    send_messages()