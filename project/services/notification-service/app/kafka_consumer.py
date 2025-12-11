import asyncio
import os
import json
import logging
from aiokafka import AIOKafkaConsumer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification-service")

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092")
TOPIC = "user-registered"

async def consume():
    logger.info(f"Starting Kafka Consumer on topic: {TOPIC}, Broker: {KAFKA_BROKER}")
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id="notification-service-group" # Distinct group ID for fan-out
    )
    try:
        await consumer.start()
        logger.info(f"Kafka Consumer started successfully.")
        try:
            async for msg in consumer:
                try:
                    data = json.loads(msg.value.decode('utf-8'))
                    username = data.get("username", "Unknown")
                    email = data.get("email", "unknown@example.com") # Assuming email might be in payload or we just simulate it
                    
                    # Simulate sending an email
                    logger.info("----------------------------------------------------------------")
                    logger.info(f"📨 NOTIFICATION SERVICE: Sending Welcome Email to {username} ({email})")
                    logger.info("   Subject: Welcome to Media Tracker!")
                    logger.info("   Body: Hi there! Thanks for joining. Start tracking your media now.")
                    logger.info("----------------------------------------------------------------")
                    
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode message: {msg.value}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        finally:
            await consumer.stop()
            logger.info("Kafka Consumer stopped.")
    except Exception as e:
        logger.error(f"Kafka connection failed: {e}")
        # Retry logic could go here, but for now we'll rely on k8s restarts or loop
