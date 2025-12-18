from aiokafka import AIOKafkaProducer
import json
import os
import asyncio

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092")

producer = None

async def get_producer():
    global producer
    if producer is None:
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await producer.start()
    return producer

async def close_producer():
    global producer
    if producer:
        await producer.stop()
        producer = None
