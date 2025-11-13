# MongoDB 8 Replica Set on Kubernetes

This deployment creates a 3-node MongoDB 8.0 replica set on Kubernetes with persistent storage.

## Prerequisites

- Kubernetes cluster with kubectl access
- Storage class that supports ReadWriteOnce volumes

## Deployment

1. Deploy the MongoDB replica set:
```bash
kubectl apply -f mongodb-replica-set.yaml
```

2. Wait for all pods to be ready:
```bash
kubectl get pods -l role=mongo -w
```

3. Initialize the replica set by connecting to the primary pod:
```bash
kubectl exec -it mongo-0 -- mongosh
```

4. In the MongoDB shell, initialize the replica set:
```javascript
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo-0.mongo:27017" },
    { _id: 1, host: "mongo-1.mongo:27017" },
    { _id: 2, host: "mongo-2.mongo:27017" }
  ]
})
```

5. Check replica set status:
```javascript
rs.status()
```

## Usage in Applications

### Connection String
```
mongodb://mongo-0.mongo,mongo-1.mongo,mongo-2.mongo/mydb?replicaSet=rs0
```

### Node.js Example
```javascript
const { MongoClient } = require('mongodb');
const uri = 'mongodb://mongo-0.mongo,mongo-1.mongo,mongo-2.mongo/mydb?replicaSet=rs0';
const client = new MongoClient(uri);
```

### Python Example
```python
from pymongo import MongoClient
client = MongoClient('mongodb://mongo-0.mongo,mongo-1.mongo,mongo-2.mongo/mydb?replicaSet=rs0')
```

## Cleanup

```bash
kubectl delete -f mongodb-replica-set.yaml
kubectl delete pvc -l role=mongo
```

## Features

- MongoDB 8.0 with replica set configuration
- Persistent storage (5Gi per instance)
- Headless service for stable network identities
- Resource limits and requests
- Journal enabled for data durability
- Proper log file configuration