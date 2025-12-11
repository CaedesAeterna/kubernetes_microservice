# Kafka Architecture & Cheatsheet

## Event Architecture
The project uses a **Fan-out** pattern for asynchronous communication.

### Topic: `user-registered`
*   **Producer:** `user-service` (Node.js)
    *   Trigger: When a new user successfully registers.
    *   Payload: JSON `{ username: "...", email: "..." }`
*   **Consumer 1:** `media-service` (Python)
    *   Group ID: `media-service-group`
    *   Action: Creates an empty "default" watchlist for the new user.
*   **Consumer 2:** `notification-service` (Python)
    *   Group ID: `notification-service-group`
    *   Action: Simulates sending a welcome email (logs to console).

## Useful Commands (Strimzi/Minikube)

### Consuming Messages (Debugging)
Spawns a temporary pod to listen to a topic.
```bash
kubectl -n kafka run kafka-consumer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.8.0 \
  --rm=true --restart=Never \
  -- bin/kafka-console-consumer.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --topic user-registered --from-beginning
```

### Producing Messages (Debugging)
Spawns a temporary pod to send messages to a topic.
```bash
kubectl -n kafka run kafka-producer -ti \
  --image=quay.io/strimzi/kafka:0.43.0-kafka-3.8.0 \
  --rm=true --restart=Never \
  -- bin/kafka-console-producer.sh \
  --bootstrap-server my-cluster-kafka-bootstrap:9092 \
  --topic user-registered
```

### Checking Kafka Status
```bash
watch -n 0.5 -d 'kubectl get pod -A | grep -E "NAMESPACE|default|kafka"'
```

