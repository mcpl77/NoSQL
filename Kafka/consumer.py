from confluent_kafka import Consumer, KafkaError

def read_messages():
    conf = {
        'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
        'group.id': 'python-consumer-group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe(['test-topic'])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print('Reached end of partition')
                else:
                    print(f'Error: {msg.error()}')
            else:
                print(f'Received message: {msg.value().decode("utf-8")} [Partition {msg.partition()}]')
    except KeyboardInterrupt:
        consumer.close()

if __name__ == '__main__':
    read_messages()