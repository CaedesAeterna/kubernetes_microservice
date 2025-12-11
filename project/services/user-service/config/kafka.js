const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'user-service',
  brokers: [process.env.KAFKA_BROKER || 'my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092'],
});

const producer = kafka.producer();

const connectProducer = async () => {
  try {
    await producer.connect();
    console.log('Kafka Producer connected');
  } catch (err) {
    console.error('Error connecting Kafka Producer', err);
  }
};

connectProducer();

module.exports = producer;
