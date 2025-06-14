import pika

# Параметры подключения к RabbitMQ
credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)

# Список очередей
queues = ['queue1', 'queue2', 'queue3']


# Функция для чтения сообщений
def read_messages():
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Читаем сообщения из каждой очереди
    for queue in queues:
        channel.queue_declare(queue=queue, durable=True)
        method_frame, header_frame, body = channel.basic_get(queue=queue, auto_ack=False)
        if method_frame:
            print(f" [x] Received '{body.decode()}' from {queue}")
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)  # Подтверждаем обработку
        else:
            print(f" [ ] No message in {queue}")

    connection.close()


if __name__ == "__main__":
    print("Reading messages...")
    read_messages()