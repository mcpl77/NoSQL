from confluent_kafka import Producer
import time

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [Partition {msg.partition()}]')

def send_messages():
    conf = {
        'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
        'client.id': 'python-producer'
    }
    producer = Producer(conf)

    topic = 'test-topic'
    messages = ['Hello from Python!', 'Message 2 from Python', 'Message 3 from Python']

    for message in messages:
        producer.produce(topic, value=message.encode('utf-8'), callback=delivery_report)
        producer.poll(0)
        time.sleep(1)  # Задержка для наглядности

    producer.flush()

if __name__ == '__main__':
    send_messages()