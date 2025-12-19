const { Kafka } = require('kafkajs');
const pool = require('./config/db');
const producer = require('./config/kafka'); // Import existing producer

const kafka = new Kafka({
  clientId: 'user-service-consumer',
  brokers: [process.env.KAFKA_BROKER || 'my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092'],
});

const consumer = kafka.consumer({ groupId: 'user-service-group' });

const runConsumer = async () => {
  let connected = false;
  while (!connected) {
    try {
      await consumer.connect();
      await consumer.subscribe({ topic: 'media-updates', fromBeginning: false });
      connected = true;
      console.log('[User Service] Kafka Consumer connected');
    } catch (err) {
      console.error('[User Service] Failed to connect to Kafka. Retrying in 5s...', err.message);
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }

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
        else if (event.event_type === 'new_release' || event.event_type === 'new_episode') {
          // Handle both for backward compatibility or the new generic type
          const { media_id, media_title, media_type, release_title, season, episode, volume, chapter } = event;
          const epTitle = release_title || event.episode_title || "New Content";

          // Construct Message based on type
          let msgDetails = "";
          if (season && episode) {
            msgDetails = `S${season}E${episode}`;
          } else if (volume && chapter) {
            msgDetails = `Vol ${volume} Ch ${chapter}`;
          } else if (chapter) {
             msgDetails = `Ch ${chapter}`;
          }
          
          const fullMessage = `New Release: ${media_title} ${msgDetails ? '- ' + msgDetails : ''} "${epTitle}"`;

          // Find users watching/reading this media
          const query = `
            SELECT user_id FROM user_library 
            WHERE media_id = $1 AND status IN ('Watching', 'Reading')
          `;
          const res = await pool.query(query, [media_id]);
          const users = res.rows;

          console.log(`[User Service] Found ${users.length} users tracking '${media_title}'`);

          for (const user of users) {
            const notification = {
              user_id: user.user_id,
              type: 'new_release',
              message: fullMessage
            };
            
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
