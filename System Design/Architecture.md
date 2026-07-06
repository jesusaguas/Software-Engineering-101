# Architecture for System Design Interviews

Architecting is the skill of turning requirements, scale, constraints, and trade-offs into a coherent system.

The other guides in this folder cover the deep fundamentals:
- `APIs.md`: API styles, auth, rate limiting, caching, retries, API gateways, service mesh.
- `Databases.md`: data modeling, database types, ACID, CAP, indexing, replication, sharding, CDC/outbox.
- `Networking.md`: protocols, DNS, load balancing, CDN, resilience, observability basics.

This guide focuses on how to put those pieces together into a complete Senior-level System Design interview answer.

---

## 1. What Good Architecture Means

A good architecture is not the biggest possible diagram. It is the simplest design that satisfies the requirements while leaving credible paths for scale, reliability, security, and future change.

In an interview, strong architecture shows that you can:
- Clarify ambiguous requirements quickly.
- Pick a reasonable baseline design.
- Identify bottlenecks before they become outages.
- Choose consistency, availability, latency, and cost trade-offs intentionally.
- Explain how data moves through the system.
- Explain what happens when dependencies fail.
- Evolve the design from simple to distributed without overengineering.

---

## 2. The System Design Interview Flow

Use this flow for most questions:

1. **Clarify requirements**
   - Functional: What should users be able to do?
   - Non-functional: Scale, latency, availability, consistency, privacy, durability.

2. **Define scope**
   - Explicitly say what is in scope and out of scope.
   - Avoid designing every feature of a real company product.

3. **Estimate scale**
   - Users, requests per second, reads vs writes, storage growth, bandwidth.
   - Rough numbers are enough; they guide architecture choices.

4. **Define core APIs**
   - Enough to expose the main user flows.
   - Keep protocol details short; APIs are covered in `APIs.md`.

5. **Model the data**
   - Main entities and relationships.
   - Source of truth vs derived data.
   - Data access patterns.

6. **Draw the high-level architecture**
   - Client -> edge/gateway -> services -> storage.
   - Add async processing, caches, search, object storage, analytics only when needed.

7. **Deep dive on bottlenecks**
   - Usually scale, consistency, hot keys, fan-out, real-time delivery, large files, ranking, or recovery.

8. **Discuss failure handling**
   - Timeouts, retries, idempotency, backpressure, fallback, disaster recovery.

9. **Close with trade-offs**
   - What is simple now?
   - What will break first?
   - How would you evolve it?

---

## 3. Baseline Architecture for Most Systems

Most system design questions start with a version of this:

```text
Clients
  |
DNS
  |
CDN / WAF
  |
API Gateway / Load Balancer
  |
Stateless Application Services
  |
Primary Data Store
```

Then you add pieces based on requirements:

```text
                        +------------------+
                        | Observability    |
                        | logs/metrics     |
                        | traces/alerts    |
                        +------------------+

Clients -> DNS -> CDN/WAF -> API Gateway/LB -> Services -> Database
                         |        |            |     |
                         |        |            |     +-> Cache
                         |        |            |     +-> Search Index
                         |        |            |     +-> Object Storage
                         |        |            |
                         |        |            +-> Queue/Stream -> Workers
                         |        |
                         |        +-> Auth, Rate Limits, Routing
                         |
                         +-> Static assets, DDoS protection
```

### Baseline Components

| Component | Purpose | Add When |
|---|---|---|
| DNS | Route users to the service entry point | Almost always |
| CDN | Cache static/public content close to users | Static assets, media, public read-heavy content |
| WAF | Block common attacks and abusive traffic | Public internet-facing systems |
| API Gateway | Auth, routing, rate limiting, SSL termination, request shaping | Multiple APIs/services or centralized edge policy |
| Load Balancer | Spread traffic across healthy instances | Multiple app instances |
| Stateless Services | Business logic, API handlers | Almost always |
| Primary DB | Source of truth | Almost always |
| Cache | Reduce latency/load for hot reads | Read-heavy, repeated queries, expensive computations |
| Queue | Async background work | Slow tasks, retries, decoupling |
| Stream | Ordered event log and event-driven consumers | Event replay, many consumers, high-volume event pipelines |
| Object Storage | Large files/blobs | Images, videos, exports, backups |
| Search Index | Full-text search and ranking | Search UX, autocomplete, filtering at scale |
| Workers | Background processing | Email, thumbnails, ML jobs, aggregation, webhooks |
| Scheduler/Cron | Time-based jobs | Periodic cleanup, reports, retries, reconciliation |
| Observability | Understand production behavior | Always |

### The Interview Shortcut

Start simple:

```text
Client -> API Gateway -> App Service -> DB
```

Then evolve:

```text
Need lower read latency? Add cache/CDN/read replicas.
Need slow work? Add queue + workers.
Need event history/replay? Add Kafka-style stream.
Need large files? Add object storage + metadata DB.
Need search? Add search index fed by CDC/events.
Need global availability? Add multi-AZ or multi-region strategy.
```

---

## 4. Requirements That Drive Architecture

Architecture is downstream of requirements. Before choosing components, identify which forces matter.

### Functional Requirements

Examples:
- Users can create posts.
- Users can search products.
- Users can upload videos.
- Drivers can send location updates.
- Merchants can receive payment notifications.

Convert each main requirement into:
- API or event.
- Data model.
- Read path.
- Write path.
- Failure behavior.

### Non-Functional Requirements

| Requirement | Architecture Impact |
|---|---|
| Low latency | Cache, CDN, regional placement, async work, efficient data access |
| High throughput | Horizontal scaling, partitioning, batching, queues/streams |
| Strong consistency (CAP) | Single source of truth, transactions, leader writes, careful caching |
| High availability (CAP) | Replication, multi-AZ, failover, graceful degradation |
| Durability | WAL-backed DB, replication, backups, object storage |
| Real-time updates | WebSocket/SSE, pub-sub, presence service |
| Large files | Object storage, multipart upload, CDN, background processing |
| Search | Search index, CDC/event indexing pipeline |
| Analytics | Event collection, stream/batch processing, warehouse |
| Security/privacy | Auth, authorization, encryption, audit logs, data retention |
| Cost sensitivity | Simpler managed services, caching discipline, storage lifecycle |

### Latency Targets

Use rough targets:
- User-facing API: usually under 100-300 ms p95 for common operations.
- Search: often under 200-500 ms p95.
- Real-time messaging: usually under 100-500 ms end-to-end.
- Background jobs: seconds to minutes may be acceptable.
- Analytics: minutes to hours may be acceptable.

Do not optimize every path equally. Identify the critical path.

---

## 5. Capacity Estimation

You do not need perfect math. You need enough math to justify design choices.

### Useful Inputs

| Metric | Why It Matters | Default Assumptions |
|---|---|---|
| DAU (daily active users) | User scale | 10M-100M DAU |
| Peak QPS | Service and load balancer sizing | 10K QPS x2(peak traffic) |
| Read/write ratio | Cache, replica, sharding strategy | 10:1 |
| Object size | Storage and bandwidth | 100B - 1KB -> 1 daily row 10M users = 1-10GB |
| Retention period | Total storage and lifecycle policy | 30 days |
| Fan-out factor | Queue, notification, feed, and stream pressure | 10 recipients per event |
| Hot key distribution | Cache and shard pressure |
| Availability target | Multi-AZ/multi-region complexity |

### Quick Math Patterns

```text
Average QPS = requests per day / 86,400
Peak QPS = average QPS * peak multiplier
Daily storage = writes per day * average record size
Total storage = daily storage * retention days * replication factor
Bandwidth = QPS * average response size
Fan-out writes = events per second * recipients per event
```

### Example

```text
10M DAU
Each user reads feed 20 times/day
Each feed request returns 100 KB

Daily feed reads = 200M
Average QPS = 200M / 86,400 = ~2.3K QPS
Peak QPS = 2.3K * 5 = ~11.5K QPS
Peak bandwidth = 11.5K * 100 KB = ~1.15 GB/s
```

That suggests:
- CDN/cache if content can be cached.
- Read replicas or denormalized feed store.
- Pagination.
- Possibly precomputed feeds for expensive ranking.

---

## 6. Architecture Styles

### Monolith

A single deployable application containing most business logic.

Best for:
- Early-stage products.
- Small teams.
- Strong consistency and simple transactions.
- Fast iteration.

Trade-offs:
- Easier to build and debug.
- Can become hard to deploy or scale by domain.
- Requires discipline around module boundaries.

### Modular Monolith

A monolith with explicit internal modules and ownership boundaries.

Best for:
- Most interview baselines when microservices are not clearly required.
- Systems that need clean domain separation without distributed complexity.

Examples:
```text
User module
Order module
Payment module
Inventory module
Notification module
```

Senior move:
- Start with a modular monolith unless scale or team structure justifies microservices.
- Explain that modules can later split into services along stable boundaries.

### Microservices

Multiple independently deployed services, each owning a bounded domain and often its own data.

Best for:
- Large organizations with independent teams.
- Domains with different scaling profiles.
- Isolation of critical capabilities.
- Independent deployments.

Trade-offs:
- Network calls replace local calls.
- Distributed transactions become hard.
- Testing, observability, and deployments become more complex.
- Requires strong API contracts and backward compatibility.

### Serverless

Functions and managed services handle execution and scaling.

Best for:
- Event-driven workloads.
- Infrequent jobs.
- Spiky traffic.
- Small teams wanting less infrastructure management.

Trade-offs:
- Cold starts.
- Vendor lock-in.
- Harder local testing and tracing.
- Execution time limits.

### Choosing the Style

| Situation | Good Default |
|---|---|
| Unknown scale, simple domain | Modular monolith |
| Massive read traffic | Stateless services + cache/CDN/read replicas |
| Independent domains and teams | Microservices |
| Event-triggered background work | Serverless or workers |
| Complex long-running workflows | Workflow engine |
| Strict financial consistency | Fewer services, transactional DB, ledger model |

---

## 7. Service Boundaries

Service boundaries should follow business capabilities, not technical layers.

Good boundaries:
- User Service
- Catalog Service
- Order Service
- Payment Service
- Inventory Service
- Notification Service

Weak boundaries:
- Controller Service
- Validation Service
- Database Service
- Utility Service

### Boundary Rules

- A service should own its data model.
- Other services should access that data through APIs or events, not direct DB joins.
- Split services when they have different scale, ownership, reliability, security, or release needs.
- Avoid splitting early if every user request would require many synchronous service calls.

### Bounded Contexts

A bounded context defines where a model has a specific meaning.

Example:
- In Catalog, `Product` means title, description, images, category.
- In Inventory, `Product` means SKU, stock count, warehouse location.
- In Pricing, `Product` means list price, discounts, tax rules.

Keeping contexts separate avoids one giant shared model that becomes impossible to change.

---

## 8. Request Path Architecture

For user-facing requests, design the critical path carefully.

```text
Client
  -> DNS
  -> CDN/WAF
  -> API Gateway
  -> Load Balancer
  -> Stateless Service
  -> Cache / DB / Other Service
  -> Response
```

### API Gateway Responsibilities

Do not overexplain this in the interview if already covered elsewhere, but know the architectural role:
- SSL/TLS termination.
- Request routing.
- Authentication enforcement.
- Rate limiting.
- Request size limits.
- API versioning support.
- Centralized logging.
- Sometimes response transformation.

### Stateless Services

Prefer stateless app servers:
- Easy horizontal scaling.
- Easy rolling deploys.
- Easy replacement after failure.
- No sticky sessions required for most APIs.

Store state in:
- Database for durable business data.
- Cache/session store for short-lived state.
- Object storage for large files.
- Queue/stream for async work.

### Backend for Frontend (BFF)

A BFF is an API layer tailored to a specific client type.

Use when:
- Web, iOS, Android, or partner clients need different response shapes.
- You want to reduce chatty client calls.
- You need client-specific aggregation.

Avoid when:
- It duplicates all business logic.
- The core API is already simple and client needs are similar.

---

## 9. Synchronous vs Asynchronous Communication

### Synchronous Calls

Use synchronous calls when the caller needs an immediate answer.

Examples:
- Login.
- Get product details.
- Check current account balance.
- Submit order and return order ID.

Trade-offs:
- Simple mental model.
- Immediate errors.
- Caller is coupled to downstream latency and availability.

### Asynchronous Messages

Use async communication when work can happen later or when you need to decouple producers from consumers.

Examples:
- Send email.
- Generate thumbnail.
- Recalculate ranking.
- Process payment webhook.
- Update search index.
- Fan out notification.

Trade-offs:
- Better resilience and throughput.
- Natural retries.
- More operational complexity.
- Eventual consistency.

### Rule of Thumb

```text
Need immediate answer? Synchronous API.
Need durable background work? Queue.
Need many consumers or replayable event history? Stream.
Need scheduled/time-based execution? Cron or scheduler.
Need long-running multi-step workflow? Workflow engine.
```

---

## 10. Queues, Streams, and Pub/Sub

The API guide mentions message queues as an API style. In architecture, focus on which async primitive fits the use case.

### Message Queues

A queue distributes tasks among workers. Usually each message is processed by one consumer.

Best for:
- Background jobs.
- Email sending.
- Image processing.
- Retrying unreliable external calls.
- Smoothing traffic spikes.

Key concepts:
- Visibility timeout or message lease.
- Retry count.
- Dead-letter queue.
- Idempotent workers.
- Backpressure.

```text
API Service -> Queue -> Worker Pool -> DB/Object Storage/External API
```

#### SQS
"Dumb broker, smart consumer" model. 
- The consumer has to actively pull messages from the queue and delete them when processed. AWS manages scaling and durability.
- At least once delivery; consumers must handle duplicates.
- Does not have built-in routing or filtering; if you want to fan out to multiple consumers, you need to create multiple queues or use SNS for pub/sub.

#### RabbitMQ
"Smart broker, dumb consumer" model.
- Delivers messages to consumers automatically.
- At most once by default (message is deleted as soon as it is consumed). Can be at least once if configured.
- The broker handles routing, filtering, and delivery to multiple consumers. Consumers can subscribe to queues or topics.

### Event Streaming

A stream is an ordered append-only log. Consumers track their own offsets and can replay events.

Best for:
- Event-driven architecture.
- Analytics pipelines.
- CDC events.
- Multiple independent consumers.
- Rebuilding derived views.

Examples:
- Kafka.
- Pulsar.
- Kinesis.

```text
Order Service -> order-events topic
                 |-> Notification Consumer
                 |-> Analytics Consumer
                 |-> Search Index Consumer
                 |-> Fraud Detection Consumer
```

#### Kafka
Apache Kafka is an open-source distributed event streaming platform that can be used either as a message queue or as a stream processing system.

A Kafka cluster is made up of multiple **brokers**. These are just individual servers (they can be physical or virtual). Each broker is responsible for storing data and serving clients. The more brokers you have, the more data you can store and the more clients you can serve.

Each broker has a number of **partitions**. Each partition is an ordered, immutable sequence of messages that is continually appended to -- think of like a log file. Partitions are the way Kafka scales as they allow for messages to be consumed in parallel.

A **topic** is just a logical grouping of partitions. Topics are the way you publish and subscribe to data in Kafka. When you publish a message, you publish it to a topic, and when you consume a message, you consume it from a topic. Topics are always multi-producer; that is, a topic can have zero, one, or many producers that write data to it.

![](../images/System%20Design/Architecture/Kafka.jpg)


### Pub/Sub

Pub/sub broadcasts messages to subscribers.
Architectural pattern where a publisher sends messages to a central Topic, and any subscribers interested in that topic receive those messages.

Best for:
- Real-time notifications.
- Cache invalidation.
- Internal event propagation.

Trade-off:
- Often less durable/replayable than a stream, depending on technology.

#### SNS
Amazon Simple Notification Service (SNS) is a fully managed pub/sub messaging service that makes it easy to setup, operate, and scale message-based applications.
SNS fans out messages to a large number of subscriber endpoints for parallel processing, including Amazon SQS queues, AWS Lambda functions, mobile push notifications, and HTTP/S webhooks.

### Queue vs Stream

| Need | Choose |
|---|---|
| One worker should process each task | Queue |
| Many consumers need the same event | Stream or pub/sub |
| Replay old events | Stream |
| Preserve order per key | Stream partitioned by key |
| Smooth traffic spike | Queue |
| Build audit/event history | Stream |

---

## 11. Kafka in Architecture

Kafka is a durable distributed event log.

A Kafka cluster is made up of multiple **brokers**. These are just individual servers (they can be physical or virtual). Each broker is responsible for storing data and serving clients. The more brokers you have, the more data you can store and the more clients you can serve.

Each broker has a number of **partitions**. Each partition is an ordered, immutable sequence of messages that is continually appended to -- think of like a log file. Partitions are the way Kafka scales as they allow for messages to be consumed in parallel.

A **topic** is just a logical grouping of partitions. Topics are the way you publish and subscribe to data in Kafka. When you publish a message, you publish it to a topic, and when you consume a message, you consume it from a topic. Topics are always multi-producer; that is, a topic can have zero, one, or many producers that write data to it.

![](../images/System%20Design/Architecture/Kafka.jpg)

Use Kafka when:
- Event volume is high.
- Multiple consumers need the same events.
- Consumers need replay.
- Ordering matters within a key, such as `order_id` or `user_id`.
- You want to build derived systems like search, recommendations, analytics, or materialized views.

Avoid Kafka when:
- You only need simple background jobs and a managed queue would be enough.
- You need request/response semantics.

### Kafka Mental Model

```text
Topic: order-events
Partitions: P0, P1, P2
Key: order_id

Producer writes event with key order_123
Kafka hashes key -> partition
Consumers in a group split partitions
Each consumer tracks offset
```

### Design Considerations

- **Partition key**: Determines ordering and load distribution.
- **Consumer group**: Allows horizontal scaling of consumers.
- **Retention**: How long events are available for replay.
- **Consumer lag**: Difference between latest event and processed event.
- **Schema evolution**: Use compatible event schemas.
- **Idempotency**: Consumers must handle duplicate delivery.

### Common Kafka Uses

| Use Case | Pattern |
|---|---|
| Search indexing | DB -> outbox/CDC -> Kafka -> indexer |
| Analytics | Services -> event topic -> stream processor -> warehouse |
| Notifications | Domain event -> notification consumer -> push/email/SMS |
| Fraud/risk | Payment event -> risk engine consumer |
| Audit log | Append immutable business events |

---

## 12. Background Workers

Workers execute work outside the user request path.

Use workers for:
- Sending email/SMS/push.
- Generating reports.
- Image/video processing.
- Calling slow third-party APIs.
- Retrying failed operations.
- Data cleanup.
- Reindexing search.

### Worker Design

```text
Job Producer -> Queue -> Worker Pool -> Result Store
                             |
                             +-> DLQ on repeated failure
```

Important properties:
- **Idempotent**: Processing the same job twice should be safe.
- **Observable**: Track job age, failure rate, queue depth, retries.
- **Bounded**: Limit concurrency to protect downstream systems.
- **Retryable**: Use backoff and dead-letter queues.
- **Recoverable**: A worker crash should not lose the job.

### Job Status Model

For long-running tasks, expose status:

```text
POST /exports -> returns job_id
GET /exports/{job_id} -> PENDING | RUNNING | COMPLETE | FAILED
```

Store job state in a DB table:
- `job_id`
- `type`
- `status`
- `attempt_count`
- `created_at`
- `started_at`
- `finished_at`
- `result_location`
- `error`

---

## 13. Cron Jobs and Schedulers

Cron jobs run work at specific times.

Use cron/schedulers for:
- Cleanup old sessions.
- Send daily digest emails.
- Reconcile payments.
- Refresh materialized views.
- Expire unpaid orders.
- Generate reports.
- Rotate keys or certificates.
- Archive old data.

### Cron Architecture

```text
Scheduler -> Job Queue -> Worker Pool -> DB/External Systems
```

Prefer having the scheduler enqueue jobs instead of doing heavy work itself.

### Avoid Duplicate Cron Execution

In distributed systems, multiple scheduler instances may run the same job.

Common approaches:
- Single scheduler instance with failover (leader election).
- Distributed lock with TTL.
- DB lease row.
- Idempotent job logic.
- Unique constraint for scheduled job keys.

Example:

```text
job_key = "daily-digest:2026-06-27"
Insert job_key with UNIQUE constraint.
Only one scheduler succeeds.
```

### Cron vs Workflow Engine

| Need | Choose |
|---|---|
| Simple periodic task | Cron/scheduler |
| Retry a single background task | Queue + worker |
| Multi-step process over minutes/days | Workflow engine |
| Human approval / timers / compensation | Workflow engine |

---

## 14. Workflow Engines

A workflow engine coordinates long-running multi-step processes.

Examples:
- Temporal.
- Cadence.
- AWS Step Functions.

Use when:
- A process has many steps.
- Steps need retries and timeouts.
- State must survive worker crashes.
- You need compensation logic.
- The workflow may run for minutes, hours, or days.
- Great for distributed transactions (saga pattern).

Example order workflow:

```text
Create Order
  -> Reserve Inventory
  -> Authorize Payment
  -> Create Shipment
  -> Send Confirmation

If payment fails:
  -> Release Inventory
  -> Mark Order Failed
```

Without a workflow engine, this logic often becomes scattered across services, queues, cron jobs, and manual recovery scripts.

---

## 15. Object Storage and Large Files

Do not store large files directly in the relational database.

Use object storage for:
- Images.
- Videos.
- Documents.
- Backups.
- Exports.
- ML datasets.

Examples:
- S3.
- Google Cloud Storage.
- Azure Blob Storage.

### Object Storage Architecture

```text
Client -> API Service -> Metadata DB
   |          |
   |          +-> Create pre-signed upload URL
   |
   +-> Upload directly to Object Storage
                    |
                    +-> Event -> Queue -> Worker
                                      |
                                      +-> validate/scan/thumbnail/transcode
                                      +-> update metadata DB
                                      +-> publish ready event
```

### Pre-Signed Upload Flow

1. Client requests upload.
2. API authenticates user and creates metadata row with status `PENDING`.
3. API returns pre-signed URL.
4. Client uploads directly to object storage.
5. Object storage emits event or client confirms upload.
6. Worker validates file, scans it, extracts metadata, creates thumbnails/transcodes.
7. Metadata row becomes `READY`.
8. CDN serves the final asset.

Why this is better:
- App servers do not proxy huge files.
- Uploads can scale independently.
- Object storage handles durability.
- CDN can cache downloads.

### Multipart Upload

Use multipart upload for large files.

```text
Client splits file into parts.
Client uploads parts in parallel.
Object storage assembles final object.
Failed parts can be retried independently.
```

Important concerns:
- Track upload session ID.
- Validate file size and content type.
- Abort incomplete uploads after timeout.
- Use checksums per part or whole object.
- Limit max file size.
- Store metadata separately from binary content.

### Blob Metadata

Store metadata in a database:
- `object_id`
- `owner_id`
- `bucket`
- `object_key`
- `status`
- `content_type`
- `size_bytes`
- `checksum`
- `created_at`
- `processed_at`

The object store holds bytes. The DB holds business meaning.

---

## 16. Data Architecture

Most systems have more than one data representation.

```text
Source of Truth DB
  -> Cache
  -> Search Index
  -> Analytics Warehouse
  -> Materialized Views
  -> Object Storage
```

### Source of Truth

The source of truth is where correctness lives.

Examples:
- Orders live in relational DB.
- Messages may live in a message store.
- Product images live in object storage, with metadata in DB.
- Events may live in Kafka plus warehouse, but current business state still often lives in an OLTP DB.

### Derived Data

Derived data is optimized for reads or analysis.

Examples:
- Redis cache.
- Elasticsearch index.
- Feed table.
- Recommendation table.
- Data warehouse.
- Aggregated counters.

Derived data can be rebuilt from source data or events. That is why source-of-truth modeling matters.

### Data Movement

Use reliable data movement:

```text
Application Transaction
  -> write business row
  -> write outbox event
CDC reads outbox
  -> publishes event
Consumers
  -> update cache/search/warehouse/other services
```

The database guide covers CDC/outbox in more depth. Architecturally, use it whenever a DB write must reliably trigger downstream work.

---

## 17. Caching in the Architecture

Caching is not one thing. Place the cache where it removes the most pain.

| Layer | Good For |
|---|---|
| Browser cache | Static assets, repeated client reads |
| CDN | Public static/media content, geographically distributed reads |
| API Gateway cache | Simple public/semi-public API responses |
| Application cache | Expensive computations, local hot data |
| Distributed cache | Shared hot data, sessions, rate limit counters |
| Database cache/read replica | Reducing primary DB read load |

### Cache Decision Questions

- Is the data safe to serve stale?
- What is the TTL?
- How is it invalidated?
- What happens on cache miss?
- Can one hot key overload the cache?
- Can cache failure bring down the system?

### Common Senior Answer

For read-heavy systems:

```text
Client -> CDN -> API Gateway -> Service -> Redis -> DB Read Replica -> Primary DB
```

But mention consistency:
- Cache may be stale.
- Read replicas may lag.
- For read-after-write, read from primary or update/invalidate cache after write.

---

## 18. Read and Write Paths

Great architecture answers separate read paths and write paths.

### Write Path

Example: create post.

```text
Client -> API Gateway -> Post Service
  -> validate/auth
  -> write post to primary DB
  -> write outbox event
  -> return success

CDC/Worker
  -> publish strem or PostCreated event
  -> Lambda/Worker reads event / stream, gets list of followers and push in NotificationSQS
  -> update feed/search/notification systems
```

Write path priorities:
- Correctness.
- Idempotency.
- Durability.
- Consistency boundaries.
- Avoiding slow downstream dependencies in the request path.

### Read Path

Example: read feed.

```text
Client -> API Gateway -> Feed Service
  -> check cache
  -> read precomputed feed / read model
  -> hydrate items
  -> return paginated response
```

Read path priorities:
- Latency.
- Pagination.
- Cacheability.
- Avoiding fan-out at read time if expensive.
- Serving degraded response if some enrichment fails.

### CQRS

Command Query Responsibility Segregation separates writes from reads.

Use when:
- Write model and read model have very different shapes.
- Reads need denormalized views.
- You can tolerate eventual consistency.

Example:
- Write model: normalized order tables.
- Read model: `user_order_history` table optimized for UI queries.

---

## 19. Consistency Strategy

Architecture needs a clear consistency story.

### Strong Consistency

Use when incorrect data is unacceptable:
- Payments.
- Inventory reservation.
- Account balances.
- Permissions.
- Unique usernames.

Typical choices:
- Single primary database for writes.
- Transactions.
- Unique constraints.
- Read from primary when freshness matters.
- Avoid async confirmation for critical state.

### Eventual Consistency

Use when temporary staleness is acceptable:
- Feed updates.
- Search indexing.
- Analytics.
- Recommendation updates.
- View counters.
- Notifications.

Typical choices:
- Events.
- Queues/streams.
- Derived read models.
- Reconciliation jobs.
- Idempotent consumers.

### Read-Your-Writes

Users often expect to see their own write immediately.

Strategies:
- Read from primary for a short window after write.
- Write through/update cache after write.
- Return newly created object directly.
- Use session token with last write timestamp and route reads accordingly.
- Optimistic UI with background reconciliation.

### Exactly-Once Reality

In distributed systems, assume at-least-once delivery unless a specific platform proves otherwise.

Design for:
- Idempotency keys.
- Deduplication tables.
- Unique constraints.
- Event IDs.
- Safe retries.

---

## 20. Idempotency and Deduplication

Idempotency is one of the most important architecture concepts for reliable systems.

### Where Idempotency Matters

- Payment creation.
- Order submission.
- Webhook processing.
- Queue consumers.
- File processing.
- Notification sending.
- Retried API calls.

### Idempotency Key Pattern

```text
Client sends:
Idempotency-Key: uuid

Server:
1. Check if key exists.
2. If exists, return stored result.
3. If not, process request.
4. Store key + result.
```

### Consumer Deduplication

For event consumers:

```text
processed_events(event_id PRIMARY KEY, processed_at)
```

Before processing:
- Insert `event_id`.
- If insert fails, skip as duplicate.
- Process event.

For high volume, deduplication can use TTL storage if duplicate windows are bounded.

---

## 21. Scaling the Architecture

Scale the bottleneck, not the diagram.

### Scaling Compute

Use stateless services:
- Add instances.
- Put behind load balancer.
- Autoscale by CPU, memory, QPS, queue depth, or latency.

### Scaling Reads

Options:
- CDN.
- Cache.
- Read replicas.
- Denormalized read models.
- Search indexes.
- Pagination.
- Precomputation.

### Scaling Writes

Options:
- Batch writes.
- Partition/shard by key.
- Async ingestion.
- Queue buffering.
- Reduce indexes.
- Separate hot/cold data.
- Use write-optimized stores.

### Scaling Storage

Options:
- Partition by tenant/user/time.
- Archive old data.
- Move blobs to object storage.
- Compress.
- Retention policies.
- Separate OLTP from analytics.

### Common Bottlenecks

| Symptom | Likely Bottleneck | Fix |
|---|---|---|
| High DB CPU | Expensive queries | Index, cache, query rewrite, read model |
| High DB connections | Too many app instances | Connection pooling |
| High p99 latency | Downstream dependency | Timeouts, circuit breaker, cache, async |
| Queue depth growing | Worker capacity | Scale workers, reduce per-job cost |
| Hot shard | Bad partition key | Repartition, isolate hot key, add cache |
| Cache overloaded | Hot keys | Local cache, replication, request coalescing |
| Search stale | Indexer lag | Scale consumers, monitor lag, backfill |

---

## 22. Hot Keys and Hot Partitions

A hot key receives disproportionate traffic.

Examples:
- Celebrity profile.
- Viral post.
- Popular product.
- Global counter.
- Current time partition.

### Mitigation Strategies

- Cache hot objects.
- Replicate hot objects across cache nodes.
- Use request coalescing.
- Split global counters into sharded counters.
- Add random suffix buckets for writes.
- Isolate celebrity/high-traffic tenants.
- Avoid purely time-based partition keys for high-write systems.

### Sharded Counter Example

```text
post_like_count:{post_id}:{bucket_id}

Increment random bucket 0..N
Read by summing buckets
Periodically compact to materialized total
```

Trade-off:
- Higher write scalability.
- Slightly more expensive reads or eventual total accuracy.

---

## 23. Multi-Tenancy

Multi-tenancy means one system serves many customers/organizations.

### Models

| Model | Pros | Cons |
|---|---|---|
| Shared DB, shared tables | Simple, cheap | Isolation risk, noisy neighbors |
| Shared DB, separate schemas | Better logical isolation | More migrations/operations |
| Separate DB per tenant | Strong isolation | Higher cost and operational complexity |
| Separate infrastructure per tenant | Best isolation/compliance | Most expensive |

### Design Concerns

- Tenant ID in every row.
- Authorization must enforce tenant boundaries.
- Per-tenant rate limits and quotas.
- Noisy neighbor protection.
- Tenant-aware backups and deletion.
- Data residency requirements.
- Migration strategy for large tenants.

Senior point:
- Start shared for small tenants.
- Move large or regulated tenants to isolated storage using a directory/tenant routing layer.

---

## 24. Real-Time Architecture

Real-time requirements change the architecture because clients need updates without repeatedly polling.

### Options

| Pattern | Best For |
|---|---|
| Polling | Simple status checks, low frequency |
| Long polling | Simple near-real-time updates |
| SSE | Server-to-client updates |
| WebSocket | Bidirectional real-time messaging |
| WebRTC | Peer-to-peer audio/video/data |

The API guide covers protocol details. Architecturally, focus on state, fan-out, and connection management.

### WebSocket Architecture

```text
Client -> NLB -> WebSocket Servers <- Fanout / Delivery Worker <- Kafka <- Notification Service
                        |                            |
                          Connection Registry (Redis) 
```
1. Client connects to a WebSocket server through the NLB.
2. WebSocket server stores connection ownership in Redis / DynamoDB (fast).
3. Notification Service writes events to Kafka.
4. Fanout / Delivery Worker consumes Kafka events.
5. Worker checks Redis to find which WebSocket server owns the user's connection.
6. Worker publishes/routes the message to that WebSocket server.
7. WebSocket server sends the message over the local socket.

Example connection registry (multiple connections because the same user may be connected from phone, laptop...):
```text
user:123 -> [
  { connection_id: c1, server_id: ws-7 },
  { connection_id: c2, server_id: ws-3 }
]
```

Important concerns:
- WebSocket connection state lives in memory on each WebSocket server.
- Store connection mapping externally: user_id -> connection_id/server_id.
- Use TTLs and heartbeats so stale Redis mappings expire if a server dies.
- Use pub/sub, gRPC, or an internal queue to route messages to the server holding the connection.
- Use Kafka as the durable event backbone.
- Commit Kafka offsets only after successful handoff to the delivery layer.
- Use message_id for idempotency because delivery is usually at-least-once.
- Persist important notifications for offline users or failed delivery.
- Backpressure slow clients; drop low-priority events if needed.
- Key Kafka messages by user_id if per-user ordering matters.

### Presence (Online/Offline)

Presence is usually eventually consistent.

```text
Client heartbeat -> Presence Service -> Redis TTL key
```

```
presence:user:123:conn:c1 -> "ws-7"   - TTL 30s
presence:user:123:conn:c2 -> "ws-3"   - TTL 30s
```

If heartbeat stops, key expires and user becomes offline.


## 26. Search Architecture

Use a search system when database queries are not enough for full-text search, ranking, tokenization, fuzzy matching, or complex filtering.

```text
Primary DB -> CDC/Outbox -> Indexer Lambda -> Search Index
Client -> Search API -> Search Index -> Results
```

The search index is not the source of truth. 
It is a denormalized, eventually consistent projection of primary data optimized for retrieval and ranking.

Search documents are often denormalized. Instead of joining multiple tables at query time, the indexer builds a document that already contains the fields needed for searching, filtering, ranking, and display.


A strong design clearly separates:

- Primary DB: correctness, transactions, ownership
- Search Index: fast retrieval, ranking, filtering, faceting
- Indexer: transforms source-of-truth data into searchable documents
- Search API: query construction, authorization, ranking, and result shaping


### Reindexing
You reindex when the existing index is no longer good enough or compatible with what you need.
For example, when the index schema or the ranking model changes.

Plan for reindexing:

```text
Create new index version
Backfill from source of truth
Dual-write or catch up from events
Switch alias to new index
Delete old index later
```

---

## 27. Analytics Architecture

Analytics workloads should usually not run on the primary application database.

```text
Services -> Event Collector -> Stream/Queue -> Processing -> Warehouse
                                             -> Real-time Dashboard
```

### Batch vs Streaming

| Pattern | Best For |
|---|---|
| Batch | Reports, daily metrics, large historical jobs |
| Streaming | Real-time dashboards, fraud detection, monitoring |
| Lambda-style hybrid | Historical correctness plus real-time approximation |

### Event Collection

Events should include:
- Event name.
- Event ID.
- User ID or anonymous ID.
- Tenant ID.
- Timestamp.
- Source service.
- Schema version.
- Properties.

Be careful with PII. Analytics events often spread widely.

---

## 28. File/Media Processing Architecture

Common for image, video, document, and audio systems.

```text
Client -> Pre-signed Upload -> Object Storage
                              |
                              +-> Object Event -> Queue
                                                 -> Processor Workers
                                                      |-> virus scan
                                                      |-> metadata extraction
                                                      |-> thumbnail/transcode into multiple resolutions
                                                      |-> moderation
                                                      |-> update DB
                                                      |-> publish ready event
```

1. Client asks API for upload permission.
2. API creates a media record in DB with status = "pending_upload".
3. API returns a pre-signed upload URL.
4. Client uploads directly to object storage.
5. Object storage emits an event when the upload completes.
6. Processor workers consume the event and start processing.

Example DB record:
```
{ 
  "media_id": "m123", 
  "user_id": "u456", 
  "original_object_key": "uploads/u456/m123/original.mp4", 
  "status": "pending_upload | processing | ready | failed", 
  "created_at": "2026-07-05T10:00:00Z" 
}
```

The processing pipeline is asynchronous, retryable, and idempotent.

### Video Specifics

For video streaming:
- Store original file (original.mp4).
- Transcode into multiple resolutions/bitrates (1080p, 720p).
- Package into HLS/DASH segments ((720p/segment_001.ts, 720p/segment_002.ts..) )
- Store segments in object storage.
- Serve segments through CDN.

**Adaptive bitrate streaming**: The client player chooses the appropriate bitrate based on network conditions.

### Design Concerns

- Large uploads can fail midway -> use multipart upload.
- Processing can take minutes -> use async workers and status tracking.
- Users need progress/status -> use DB status field and events.
- Processing can fail -> use retries, dead-letter queue, and make workers idempotent.
- Some files are invalid or malicious -> validate and scan.
- CDN serves stale content after replacement -> Implement invalidation logic or versioned object keys.
- Storage lifecycle policy controls cost -> implement retention and archival.


---

## 29. Payment and Order Architecture

Payments require strong correctness, careful idempotency, auditable state transitions, and reconciliation with the external payment provider.
It's essetially a state machine with external events.

```text
Client -> Order Service -> DB transaction creates PENDING order
                         -> Payment Service creates payment attempt
                         -> Payment Provider

Payment Provider Webhook -> Webhook Handler
                 -> verify signature
                 -> dedupe event
                 -> update payment/order state
                 -> publish PaymentSucceeded/Failed
```

1. Client submits checkout request with an idempotency key (POST /checkout).
````
POST /checkout
Idempotency-Key: 7f3c1a7e-9c6a-4c89-b6c4-2c58f3d8a111
````
2. Order Service checks the idempotency key in a separate idempotency table.
   - If this key was already processed, return the previous result.
   - Otherwise, continue.
3. Order Service creates a PENDING order, saves the idempotency key, and calls Payment Service.
4. Payment Service stores the payment attempt and calls the payment provider (Stripe) with new idempotency key.
5. Payment Provider returns a provider payment reference and a client-facing payment instruction.
6. Payment Service stores the payment reference and returns the payment instruction to the Order Service.
7. Order Service returns the payment instruction to the client.
8. Client completes payment using the provider instruction.
9. Payment Provider sends webhook to a Payment's Service API endpoint with the payment result (success/failure) and payment reference.
10. Payment Service publishes PaymentSucceeded/Failed events. 
11. Order Service consume the events and update the order state based on the payment result, publishes OrderPaid event.
12. Fulfillment Service consumes OrderPaid and starts fulfillment.
13. Client can poll the Order Service for order status or receive WebSocket/SSE notifications.

### Design Concerns

- Never trust only the client redirect/callback.
- Webhook handlers must be idempotent.
- Store payment attempts separately from orders.
- Use a ledger for money movement (payment provider takes X$, merchant receives Y$, tax authority receives Z$).
- Avoid distributed transactions with external payment providers.
- Webhook is missed -> reconciliation jobs (find pending payments and query provider).


## 30. Feed Architecture

Feeds are common in social networks, content platforms, marketplaces, and notification-style products. They force a core trade-off between doing work at write time and doing work at read time.

### Fan-Out on Read

```text
Read request -> fetch followed users -> fetch recent posts -> rank -> return
```

Best for:
- Users follow few accounts.
- Write volume is high.
- Freshness matters.

Trade-offs:
- Reads can be expensive.
- Hard for users following many accounts.

### Fan-Out on Write

```text
PostCreated -> fan out post_id into followers' feed inboxes (precomputed feed table)
Read request -> read precomputed feed table
```

Best for:
- Fast reads.
- Moderate fan-out.
- Feed is read frequently.

Trade-offs:
- Writes can explode for celebrities (millions of followers).
- Eventual consistency.
- Requires background workers.

### Hybrid

Common production approach:
- Fan out normal users (less than 10000 followers) on write.
- For celebrities, fan out on read, merging their posts with the precomputed feed of the user.


![](../images/System%20Design/Architecture/Feed.jpg)

---

## 31. Location and Matching Architecture

Use for ride-sharing, delivery, nearby search, and maps-like systems.

Location systems have two very different data types:

- **Location data**: high-volume, frequently updated, approximate, eventually consistent

- **Trip / order / assignment state**: lower-volume, business-critical, requires stronger consistency

```text
Driver App -> Location Ingestion Service -> Location Store (Redis/PostGIS)
                                         -> Stream location (Kafka/Kinesis) for analytics/ETA

Rider Request -> Matching Service -> nearby drivers -> offer/accept flow
```

1. Rider requests a ride (with pickup and destination location). 
2. Ride Service creates a ride request with status = SEARCHING and returns to the client the ride request ID.
3. RideRequested event is published and the Matching Service consumes it to start matching.
4. Matching Service filters eligible drivers (available, within service area...), ranks them (distance, rating..). 
5. Matching Service sends match offers to one or more drivers (push/websockets), stores offers with a TTL and delayed job. 
6. Driver accepts or rejects 
    - Accept: Matching Service atomically assigns the first valid accepting driver, emit TripAssigned event.
    - TTL expires with no accepted: A delayed job/timer restarts matching.
7. Trip Service updates trip state to ASSIGNED, and the driver/rider is notified.


### Design Concerns

- High write rate from location updates -> use in-memory geospatial store.
- TTL old locations.
- Low-latency nearby queries -> Geospatial indexing (geohashing or R-trees), with Redis or PostGIS.
- Matching must handle race conditions and avoid sending multiple requests to the same driver. -> Use distributed locks or atomic operations.
- Payments and trip state need stronger consistency than location updates.

### Common Pattern

- Store current location in Redis/geospatial store with TTL.
- Store trip state in relational DB.
- Publish location events to stream for analytics/ETA.
- Use WebSocket/SSE (browser) or APN/FCM (mobile) for live updates.

![](../images/System%20Design/Architecture/Uber.jpg)

1) How do we handle frequent driver location updates and efficient proximity searches on location data?
  - **Real-Time In-Memory Geospatial Indexing**: Use an in-memory data store like Redis with geospatial indexing capabilities to store driver locations. Each driver’s location is updated frequently (e.g., every few seconds) and stored with a TTL to ensure stale data is automatically removed. This allows for efficient proximity searches using geospatial queries.
2) How can we manage system overload from frequent driver location updates while ensuring location accuracy?
  -  **Adaptive Location Update Frequency**: dynamically adjust the frequency of location updates based on contextual factors such as driver activity (speed, direction) and location. For example, if a driver is stationary or moving slowly, reduce the frequency of updates.
3) How do we prevent multiple ride requests from being sent to the same driver simultaneously?
  - **Distributed Lock with TTL**: Implement a distributed locking mechanism (e.g., using Redis) to ensure that once a driver is matched with a rider, they are temporarily locked for a short duration (e.g., 30 seconds) to prevent multiple ride requests from being sent to the same driver simultaneously. The lock can have a TTL to automatically release if the driver does not respond in time.
4) How can we ensure no ride requests are dropped during peak demand periods?
  - **Queueing and Backpressure/Dynamic Scaling**: Use a message queue (e.g., Kafka or RabbitMQ) to buffer incoming ride requests during peak demand periods. Implement backpressure mechanisms to slow down the rate of incoming requests if the system is overwhelmed, ensuring that no ride requests are dropped and that they are processed in a controlled manner.
5) What happens if a driver fails to respond in a timely manner?
  - **Timeouts and Fallbacks**: Implement timeouts for driver responses. If a driver does not respond within a specified time frame (e.g., 30 seconds), the system can automatically release the lock and attempt to match the rider with another available driver. Additionally, maintain a list of backup drivers to quickly reassign the ride request if the initial driver fails to respond.
6) How can you further scale the system to reduce latency and improve throughput?
  - **Geo-Sharding and Read Replicas**: Partition the location data based on geographic regions (geo-sharding) to distribute the load across multiple servers. This allows for localized queries and reduces latency. Additionally, use read replicas for the location store to handle high read traffic efficiently, ensuring that proximity searches can be performed quickly without overloading the primary data store.

---

## 32. Rate Limiting and Abuse Architecture

Rate limiting is covered in the API guide. Architecturally, place controls at multiple layers.

```text
Edge/WAF -> API Gateway -> Service-level limiter -> Downstream quota limiter
```

### Dimensions

- IP address.
- User ID.
- Tenant ID.
- API key.
- Endpoint.
- Device ID.
- Payment method.

### Abuse Controls

- WAF rules.
- CAPTCHA for suspicious flows.
- Bot detection.
- Signup throttles.
- Password attempt limits.
- Per-tenant quotas.
- Anomaly detection.

Senior point:
- Rate limits protect user experience and downstream dependencies, not only security.

---

## 33. Security Architecture

Security should appear throughout the design, not as a final sentence.

### Layers

| Layer | Controls |
|---|---|
| Edge | TLS, WAF, DDoS protection, rate limits |
| API | Auth, authorization, input validation, schema validation |
| Service | Least privilege, mTLS/service identity, audit logs |
| Data | Encryption, access control, backups, retention |
| Operations | Secrets management, deploy controls, monitoring |

### Authorization

Separate authentication from authorization:
- Authentication: Who are you?
- Authorization: What are you allowed to do?

Common models:
- RBAC for roles.
- ABAC for attribute/policy-based decisions.
- Tenant-scoped permissions for B2B SaaS.

### Secrets

Do not store secrets in code or plain environment dumps.

Use:
- Secret manager.
- Rotation.
- Separate secrets per environment.
- Short-lived credentials when possible.

### Audit Logs

Audit logs are required for sensitive systems:
- Who did what?
- To which resource?
- When?
- From where?
- Was it allowed or denied?

Store audit logs append-only where possible.

---

## 34. Reliability Architecture

Reliable systems assume things fail.

### Failure Modes

- Service instance crashes.
- DB primary fails.
- Replica lag increases.
- Cache is unavailable.
- Queue backlog grows.
- Third-party API times out.
- Network partition.
- Bad deploy.
- Region outage.
- Data corruption or accidental deletion.

### Resilience Patterns

| Pattern | Purpose |
|---|---|
| Timeout | Avoid waiting forever |
| Retry with backoff/jitter | Recover transient failures |
| Circuit breaker | Stop hammering unhealthy dependency |
| Bulkhead/Error Boundary | Isolate resources to prevent cascade failure |
| Fallback | Return degraded but useful response |
| Backpressure | Slow producers when consumers cannot keep up |
| Load shedding | Drop low-priority work under overload |
| Health checks | Remove unhealthy instances |
| Idempotency | Make retries safe |

### Graceful Degradation

Example e-commerce:
- Checkout must work.
- Product recommendations can disappear.
- Reviews can be stale.
- Search autocomplete can be disabled.
- Analytics events can buffer or drop if non-critical.

Senior point:
- Define which features are critical and which can degrade.

---

## 35. Availability and Disaster Recovery

### Availability Targets

| Target | Downtime per Year | Architecture Implication |
|---|---|---|
| 99% | ~3.65 days | Basic redundancy |
| 99.9% | ~8.8 hours | Multi-AZ, monitoring, tested deploys |
| 99.99% | ~52.6 minutes | Strong failover automation |
| 99.999% | ~5.3 minutes | Multi-region and serious operational maturity |

Higher availability is expensive. Ask whether the product needs it.

### Multi-AZ

Multi-AZ is the common default for production:
- App instances across zones.
- Database primary/standby or replicated cluster.
- Load balancer health checks.
- Zone failure should not take down the system.

### Multi-Region

Patterns:

| Pattern | Description | Trade-off |
|---|---|---|
| Backup/restore | Restore in another region | Cheapest, slowest recovery |
| Pilot light | Minimal standby infra | Lower cost, slower failover |
| Warm standby | Scaled-down full stack | Faster recovery, higher cost |
| Active-passive | One live region, one standby | Simpler consistency, failover needed |
| Active-active | Multiple live regions | Best latency/availability, hardest consistency |

### RTO and RPO

- **RTO**: How long can the system be down?
- **RPO**: How much data can be lost?

Architecture depends on these numbers.

Examples:
- Social likes may tolerate minutes of RPO.
- Bank transfers may tolerate near-zero RPO.

---

## 36. Data Migration and Backfills

Senior engineers plan for change.

### Safe Schema Migration Pattern

```text
1. Add new nullable column/table.
2. Deploy code that writes old + new.
3. Backfill old data into new shape.
4. Deploy code that reads new.
5. Stop writing old.
6. Drop old column/table later.
```

### Backfill Design

Backfills should:
- Run in batches.
- Be resumable.
- Be idempotent.
- Avoid overwhelming production DB.
- Track progress.
- Have pause/rollback controls.
- Emit metrics.

### Dual-Write Migration

During migration, you may write to old and new systems.

Risks:
- One write succeeds and the other fails.
- Data diverges.

Mitigations:
- Outbox/CDC.
- Reconciliation jobs.
- Checksums/count comparisons.
- Read shadowing before cutover.

---

## 37. Observability and Operations

A system is not production-ready if you cannot understand it.

### The Three Pillars

- **Metrics**: What is happening numerically?
- **Logs**: What happened in specific events?
- **Traces**: Where did time go across services?

### Golden Signals

- Latency.
- Traffic.
- Errors.
- Saturation (CPU, memory, disk, network).

### Architecture Metrics

Track:
- API p50/p95/p99 latency.
- Error rate by endpoint.
- QPS by endpoint.
- DB query latency.
- Cache hit rate.
- Queue depth.
- Oldest message age.
- Consumer lag.
- Worker success/failure rate.
- External dependency latency/error rate.
- CPU/memory/disk/network saturation.

### Health Checks

Use:
- Liveness check: should the process be restarted?
- Readiness check: should it receive traffic?
- Dependency checks: can it reach required systems?

Be careful:
- Do not make readiness depend on optional systems.
- Avoid expensive health checks.

---

## 38. Deployment Architecture

Deployment strategy affects reliability.

### Common Strategies

| Strategy | Description | Use When |
|---|---|---|
| Rolling deploy | Replace instances gradually | Common default |
| Blue/green | Switch traffic between two environments | Fast rollback needed |
| Canary | Send small percent to new version | Risky changes, high traffic |
| Feature flags | Control behavior independently of deploy | Gradual rollout |
| Shadow traffic | Send copied production traffic to new system | Validate without user impact |

### Compatibility Rules

In distributed systems:
- New clients may talk to old servers.
- Old clients may talk to new servers.
- New services may consume old event schemas.
- Old consumers may see new fields.

Prefer additive changes:
- Add fields.
- Add endpoints.
- Add event versions.

Avoid breaking changes without migration windows.

---

## 39. Configuration and Feature Flags

Configuration changes behavior without code changes.

Use config for:
- Rate limits.
- Feature thresholds.
- Provider endpoints.
- Experiment assignments.
- Kill switches.

Use feature flags for:
- Gradual rollout.
- A/B tests.
- Emergency disable.
- Tenant-specific features.

Design concerns:
- Defaults must be safe.
- Config changes need audit logs.
- Flags should be cleaned up.
- Critical flags should be cached locally if config service fails.

---

## 40. Cost and Simplicity

Architecture is constrained by cost and team capacity.

### Cost Drivers

- Cross-region traffic.
- Always-on compute.
- Large data retention.
- High-cardinality metrics/logs.
- Search clusters.
- Kafka operations.
- CDN egress.
- Object storage lifecycle.
- Over-sharding too early.

### Simplicity Questions

Ask:
- Can one database handle this for now?
- Can managed services reduce operational burden?
- Can async work be a simple queue instead of Kafka?
- Can a modular monolith handle the domain?
- Can we cache or precompute instead of sharding?
- What is the first bottleneck likely to be?

Senior point:
- Simplicity is not laziness. It is controlled complexity.

---

## 41. Common Architecture Blueprints

### Read-Heavy CRUD System

```text
Client -> API Gateway -> Service -> Redis Cache -> DB Read Replica
                                      |
                                      +-> Primary DB on writes
```

Use for:
- Product catalog.
- User profiles.
- Public pages.

Key points:
- Cache hot reads.
- Invalidate cache on writes.
- Use replicas for read scale.
- Read from primary when freshness matters.

### Write-Heavy Ingestion System

```text
Client/Device -> Ingestion API -> Queue/Stream -> Consumers -> Storage
                                           |
                                           +-> real-time processor
                                           +-> warehouse
```

Use for:
- Logs.
- Metrics.
- Clickstream.
- IoT events.

Key points:
- Validate and enqueue quickly.
- Partition by stable key.
- Batch writes downstream.
- Monitor lag and dropped events.

### Event-Driven Microservices

```text
Service A -> DB + Outbox -> Event Bus -> Service B Consumer -> Service B DB
                                  |
                                  +-> Service C Consumer
```

Use for:
- Independent domains.
- Async workflows.
- Derived views.

Key points:
- Services own their data.
- Events are contracts.
- Consumers are idempotent.
- Expect eventual consistency.

### Large File Upload System

```text
Client -> API -> Pre-signed URL
Client -> Object Storage
Object Event -> Queue -> Processor -> Metadata DB -> CDN
```

Use for:
- Photos.
- Videos.
- Documents.
- Exports/imports.

Key points:
- Direct upload avoids app bottleneck.
- Multipart for large files.
- Process asynchronously.
- Store metadata in DB.

### Search System

```text
Primary DB -> CDC/Outbox -> Indexer -> Search Index
Client -> Search API -> Search Index
```

Key points:
- Search index is derived.
- Reindexing plan matters.
- Search may be stale.

### Notification System

```text
Domain Event -> Notification Queue -> Notification Workers
                                      |-> Push
                                      |-> Email
                                      |-> SMS
                                      |-> In-app
```

Key points:
- Preferences and dedupe.
- Channel-specific retries.
- Provider failures should not block core workflows.

### Real-Time Chat

```text
Client -> WebSocket Gateway -> Chat Service -> Message Store
                              |
                              +-> Pub/Sub -> recipient connection server
```

Key points:
- Persist message before delivery ack.
- Track connections.
- Handle reconnects.
- Backpressure slow clients.

### Scheduled Reports

```text
Scheduler -> Queue -> Report Worker -> Warehouse/DB -> Object Storage
                                             |
                                             +-> Notification when ready
```

Key points:
- Heavy reports should not run in request path.
- Store generated file in object storage.
- Expose job status.

---

## 42. Architecture Decision Tree

```text
Start:
  Need user-facing API?
    -> API Gateway/LB + stateless service

Need durable business state?
    -> Primary database

Read-heavy?
    -> Cache/CDN/read replicas/read model

Write-heavy?
    -> Partitioning, batching, async ingestion, queue/stream

Slow work in request path?
    -> Queue + workers

Many consumers need the same event?
    -> Stream/event bus

Need reliable DB write -> event publish?
    -> Outbox + CDC

Need large files?
    -> Object storage + metadata DB + pre-signed upload

Need full-text search?
    -> Search index fed from source of truth

Need real-time client updates?
    -> SSE/WebSocket + connection manager + pub/sub

Need periodic work?
    -> Scheduler/cron + queue + idempotent workers

Need multi-step long-running process?
    -> Workflow engine

Need high availability?
    -> Multi-AZ first; multi-region only with clear RTO/RPO

Need strict correctness?
    -> Transactions, constraints, primary reads, idempotency, audit
```

---

## 43. How to Present the Final Design

A strong final architecture explanation follows data flow.

### Template

```text
For writes:
1. Client sends request through API Gateway.
2. Gateway authenticates, rate limits, and routes to service.
3. Service validates request and writes to source-of-truth DB.
4. Service writes an outbox event in the same transaction.
5. CDC/event publisher sends event to queue/stream.
6. Workers update derived systems: cache/search/notifications/analytics.

For reads:
1. Client requests data through API Gateway.
2. Service checks cache/read model.
3. On miss, reads DB or search index.
4. Response is paginated and cacheable if appropriate.

For failures:
1. Timeouts and retries protect transient failures.
2. Idempotency prevents duplicate side effects.
3. DLQ captures poison messages.
4. Monitoring tracks latency, errors, queue depth, consumer lag.
```

### What to Say Out Loud

- "The database is the source of truth; cache/search/feed tables are derived."
- "This operation needs strong consistency, so it stays in a transaction."
- "This operation can be eventually consistent, so I move it async."
- "This is likely the first bottleneck."
- "I would start simple and add this only when scale requires it."
- "The main trade-off is lower latency at the cost of staleness."

---

## 44. Common Pitfalls

- Adding microservices without explaining service boundaries.
- Adding Kafka when a queue is enough.
- Putting slow third-party calls in the critical request path.
- Forgetting idempotency for retries, payments, workers, and webhooks.
- Treating cache/search as source of truth.
- Ignoring hot keys and celebrity users.
- Ignoring data migrations and backfills.
- Designing active-active multi-region without explaining consistency.
- Forgetting observability and failure recovery.
- Sharding before estimating whether one DB can handle the load.
- Using cron without preventing duplicate execution.
- Uploading large files through app servers unnecessarily.
- Not distinguishing read path from write path.
- Forgetting tenant isolation in B2B systems.

---

## 45. Senior-Level Checklist

Before finishing an interview answer, make sure you covered:

- Requirements and explicit assumptions.
- Back-of-the-envelope scale.
- High-level architecture.
- API surface for core flows.
- Data model and source of truth.
- Read path and write path.
- Caching strategy and invalidation.
- Async processing strategy.
- Consistency model.
- Idempotency and retry behavior.
- Failure modes and graceful degradation.
- Scaling bottlenecks.
- Observability.
- Security and authorization.
- Deployment/migration considerations.
- Trade-offs and evolution path.

---

## 46. Practice Prompt Framework

For any system design prompt, fill this in:

```text
Problem:
  Design ...

Core requirements:
  1.
  2.
  3.

Scale:
  Users:
  QPS:
  Read/write ratio:
  Storage:
  Latency:
  Availability:

Data:
  Source of truth:
  Derived data:
  Retention:

Architecture:
  Edge:
  Services:
  Storage:
  Cache:
  Async:
  Search:
  Object storage:
  Realtime:

Critical flows:
  Write path:
  Read path:
  Background path:

Trade-offs:
  Consistency:
  Latency:
  Cost:
  Complexity:

Failures:
  Dependency failure:
  Duplicate requests:
  Backlog:
  Region/AZ failure:

Evolution:
  MVP:
  First bottleneck:
  Next scaling step:
```

---

## 47. Final Mental Model

Most system design architectures are combinations of a few repeatable ideas:

```text
Synchronous path for immediate user work.
Asynchronous path for slow or decoupled work.
Source-of-truth store for correctness.
Derived stores for speed and specialized queries.
Cache/CDN for latency and load reduction.
Object storage for large blobs.
Schedulers/workers for time-based and background work.
Events/streams for propagation and replay.
Observability and recovery for production reality.
```

The best interview answers are not the most complex. They are the ones where every component has a job, every trade-off is named, and every important failure has a credible response.
