import asyncio
import os
import json
from aiokafka import AIOKafkaConsumer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092")
TOPIC = "user-registered"

async def consume():
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id="media-service-group"
    )
    try:
        await consumer.start()
        print(f"Kafka Consumer started on topic {TOPIC}")
        try:
            async for msg in consumer:
                print(f"Consumed: {msg.topic} {msg.partition} {msg.offset} key={msg.key} value={msg.value}")
                # Logic to handle user registration (e.g. create default watchlist)
                data = json.loads(msg.value.decode('utf-8'))
                print(f"Processing new user: {data}")
        finally:
            await consumer.stop()
    except Exception as e:
        print(f"Kafka connection failed: {e}")
