const { Kafka } = require('kafkajs');
const pool = require('./config/db');
const producer = require('./config/kafka'); // Import existing producer

const kafka = new Kafka({
  clientId: 'user-service-consumer',
  brokers: [process.env.KAFKA_BROKER || 'my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092'],
});

const consumer = kafka.consumer({ groupId: 'user-service-group' });

const runConsumer = async () => {
  await consumer.connect();
  await consumer.subscribe({ topic: 'media-updates', fromBeginning: false });

  await consumer.run({
    eachMessage: async ({ topic, partition, message }) => {
      try {
        const value = message.value.toString();
        console.log(`[User Service] Received media-update: ${value}`);
        const event = JSON.parse(value);

        if (event.event_type === 'media_deleted') {
             const { media_id } = event;
             console.log(`[User Service] Processing deletion for media ID: ${media_id}`);
             
             // Cleanup user libraries
             const query = 'DELETE FROM user_library WHERE media_id = $1';
             await pool.query(query, [media_id]);
             console.log(`[User Service] Removed media ${media_id} from all user libraries.`);
        }
        else if (event.event_type === 'new_episode') {
          const { media_id, media_title, season, episode, episode_title } = event;

          // Find users watching this media
          // We check for 'Watching' status.
          const query = `
            SELECT user_id FROM user_library 
            WHERE media_id = $1 AND status = 'Watching'
          `;
          const res = await pool.query(query, [media_id]);
          const users = res.rows;

          console.log(`[User Service] Found ${users.length} users watching '${media_title}'`);

          for (const user of users) {
            const notification = {
              user_id: user.user_id,
              type: 'new_release',
              message: `New Episode Released: ${media_title} - S${season}E${episode} "${episode_title}"`
            };
            
            // Produce notification event
            // Note: We reuse the producer connected in config/kafka.js
            // Ensure producer is connected before sending (it should be)
            await producer.send({
              topic: 'notification-dispatch',
              messages: [
                { value: JSON.stringify(notification) },
              ],
            });
            console.log(`[User Service] Sent notification for user ${user.user_id}`);
          }
        }
      } catch (err) {
        console.error('[User Service] Error processing message:', err);
      }
    },
  });
};

module.exports = runConsumer;
