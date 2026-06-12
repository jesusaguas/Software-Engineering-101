# Databases for System Design Interviews

A database is a system for storing, querying, updating, and managing data reliably.


## 1. Data Modeling
Data modeling is the process of defining how your application’s data is structured, stored, and related. In practice, this means deciding what entities exist, how they’re identified, and how they connect to one another.

![](../images/System%20Design/Databases/DataModeling.jpg)


- **Primary keys**: Unique identifiers for each record. Often an auto-incrementing integer or a UUID.
- **Foreign keys**: Points to a primary key in another table to define relationships between tables. For example, an `orders` table might have a `user_id` foreign key that references the `users` table. They enforce referential integrity, ensuring that relationships between tables remain consistent - The database will prevent you from creating an order with a user_id that doesn't exist in the users table.
- **Constraints**: Rules that ensure data integrity and consistency (correctness). For example:
    - `NOT NULL` constraint ensures that a column cannot have a null value.
    - `UNIQUE` constraint ensures that all values in a column are unique.
    - `CHECK` constraint ensures that values in a column satisfy a specific condition (e.g., `CHECK (age >= 0)` to prevent negative ages).
    - `DEFAULT` constraint provides a default value for a column when no value is specified (e.g., `DEFAULT CURRENT_TIMESTAMP` for a created_at column).

### Normalization vs. Denormalization
- **Normalization**: The process of organizing data to minimize redundancy and improve data integrity. This typically involves splitting data into multiple related tables and using foreign keys to link them. Normalization can lead to more complex queries (joins) but ensures consistency and reduces storage costs.
- **Denormalization**: The process of intentionally introducing redundancy into a database to improve read performance. This often involves combining related tables into a single table, which can reduce the need for joins and speed up read queries at the cost of increased storage, complex writes, and potential data inconsistency.

![](../images/System%20Design/Databases/Normalization.jpg)

## 2. Types of Databases

| Type | Best For | Avoid When |
|---|---|---|
| [Relational](#relational-databases-sql) | Transactions, joins, correctness | Horizontal scaling, schema changes |
| [Document](#document-databases-nosql) | Flexible nested objects (JSON) | Complex joins and strict ACID properties |
| [Key-value](#key-value-stores) | Fast lookup by key | Ad hoc queries or relationships |
| [Wide-column](#wide-column-databases) | Huge write scale | Flexible querying or joins |
| [Graph](#graph-databases) | Relationship traversal | Simple CRUD workloads |
| [Search](#search-databases) | Full-text search and ranking | Source-of-truth transactions |
| [Time-series](#time-series-databases) | Timestamped metrics/events | General-purpose business data |
| [Warehouse](#warehouse-databases) | Analytics and reporting | Low-latency app transactions |
| [Object storage](#object-storage) | Large files and blobs | Small relational records |

### Relational Databases (SQL)

| Description | Best For | Cons | Examples |
|---|---|---|---|
| Structured data in tables with rows and columns, using SQL to query and manage relationships between entities. | Clear structure, relationships, constraints, and correctness requirements (ACID). Examples: users, orders, payments, inventory, billing, permissions. | Horizontal scaling, schema changes | PostgreSQL, MySQL, Oracle, SQL Server, MariaDB |

#### PostgreSQL
- Open-source, feature-rich relational database
- Supports advanced data types (JSONB, arrays)
- Strong ACID transactions, constraints, joins, and complex SQL queries.
- Extensible (PostGIS -> geospatial / TimescaleDB -> time-series)
- Table data is stored as unordered rows in pages (8KB)
- Uses B-tree indexes by default, with support for other index types (GIN, GiST)
- High single-node performance, but can be scaled with read replicas (eventually consistent) and sharding (+ complexity):
  - 32TB of data per table (1KB row -> 32 billion rows)
  - 160TB of data per database
  - 10k - 100k QPS on a single node


### Document Databases (NoSQL)

| Description | Best For | Cons | Examples |
|---|---|---|---|
| Stores data as flexible, nested documents (JSON-like) without a fixed schema. | Semi-structured data, simple relationships, schema flexibility, horizontal scaling, and nested data. Use cases: user profiles, content management, analytics. | Limited joins, weak ACID properties | MongoDB, CouchDB, Amazon DocumentDB, Firebase Firestore. |


### Key-Value Stores
| Description | Best For | Cons | Examples |
|---|---|---|---|
| Simple database that stores data as key-value pairs. | Fast lookups by key and don't require complex querying or relationships. Horizontal scaling. Examples: caching, sessions, real-time data. | Limited querying, no joins | Redis, Memcached, DynamoDB (can also be document store) |

#### DynamoDB
- Fully managed, serverless key-value and document database by AWS
- Single-digit millisecond latency at any scale, with built-in replication and high availability
- Supports both key-value and document data models, with flexible schema design
- Offers tunable consistency (eventual or strong) and automatic scaling based on traffic
- Ideal for applications that require low-latency access to data, such as gaming, IoT, and mobile backends

### Wide-Column Databases
| Description | Best For | Cons | Examples |
|---|---|---|---|
| Stores data in tables with rows and dynamic columns grouped into column families. | Massive horizontal scale and high write throughput. For Big Data (Time-series data, logs, metrics, analytics) | Limited querying, no joins | HBase, Cassandra, Google BigTable |

### Graph Databases
| Description | Best For | Cons | Examples |
|---|---|---|---|
| Stores data as nodes and edges to represent entities and their relationships. | Complex relationships and traversals, such as social networks, recommendation engines, and knowledge graphs. | Not suitable for traditional CRUD workloads (lookups not optimized) | Neo4j, ArangoDB, Amazon Neptune |

### Search Databases
| Description | Best For | Cons | Examples |
|---|---|---|---|
| Uses inverted index that maps terms (tokenized text) to documents. | Optimized for full-text search, indexing, and ranking of unstructured data (Logs, search functionality, analytics) | Cannot be Source-of-truth (no correctness, eventual consistency) | Elasticsearch, OpenSearch, Solr | 

### Time-Series Databases
| Description | Best For | Cons | Examples |
|---|---|---|---|
| Data is stored as time-ordered records: `(timestamp, metric/value, tags)`. | Optimized for fast writes, time-range queries, compression, retention, and downsampling. (Metrics, events, IoT data, and any data that is primarily indexed by time) | Not suitable for general-purpose business data | InfluxDB, TimescaleDB, Prometheus |

### Warehouse Databases
| Description | Best For | Cons | Examples |
|---|---|---|---|
| Optimized for analytical queries on large datasets, often using columnar storage and MPP (Massively Parallel Processing) architecture. | Analytics and reporting on large datasets, where query performance is more important than low-latency transactions. | Not for low-latency transactions | Snowflake, Google BigQuery, Amazon Redshift, ClickHouse |


## 3. ACID Properties

### Atomicity
All or nothing. All operations in a transaction succeed or fail together. Achieved through transaction commit/rollback.
```
BEGIN;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

COMMIT;
```


#### Distributed Transactions: 
This is where atomicity gets expensive. If a transaction spans multiple microservices or database shards, you cannot rely on a single WAL. You must discuss coordination patterns:
  - **Two-Phase Commit (2PC)**: A coordinator node manages the transaction. In the first phase, it asks all participants to prepare and vote. If all vote yes, it commits; if any vote no, it rolls back. **This can lead to blocking if the coordinator fails**, so it's not commonly used. Need to support the XA protocol for distributed transactions or use a distributed DB like Google Spanner.
  - **Saga Pattern**: Instead of a single transaction, you break it into a series of smaller transactions with compensation logic. If one step fails, you execute compensating transactions to undo the previous steps. This is more resilient and better for microservices, but introduces **eventual consistency**. See Dual-write problem -> Transactional Outbox pattern for more details.
    - **Coreography**: Each service manages its own transaction and triggers the next step through events. This is more decoupled but can be harder to manage. Good for simple workflows.
    - **Orchestration** [PREFERRED]: A central orchestrator manages the workflow and calls each service in sequence. This is easier to manage but introduces a single point of failure. Example: AWS Step Functions, Temporal.


### Consistency
Transactions transition the database from one valid state to another, maintaining data integrity. Enforced through constraints, triggers, and application logic. The application developer is ultimately responsible for defining what "consistent" means.

Example: A balance cannot become negative if the schema or business rules forbid it.


### Isolation
Isolation defines how concurrent transactions interact. Implemented through locking mechanisms and isolation levels. Higher isolation levels (e.g., Serializable) can lead to increased contention and reduced concurrency, while lower levels (e.g., Read Uncommitted) can lead to phenomena like dirty reads.

#### The Four Concurrency Anomalies
When two concurrent transactions (Transaction A and Transaction B) overlap, the following nightmares can occur if isolation is too weak:

- **Dirty Read**: Transaction A reads uncommitted changes from Transaction B. If Transaction B rolls back, Transaction A has read invalid data.
  - You made decisions using uncommitted data.
- **Non-Repeatable Read**: Transaction A reads the same data twice, but Transaction B modifies it in between. Transaction A gets different results on each read.
  - The transaction did not operate on a stable view of the row.
- **Phantom Read**: Transaction A reads a set of rows that satisfy a condition. Transaction B inserts or deletes rows that satisfy the same condition. Transaction A sees different sets of rows on subsequent reads.
  - The set of matching rows changed during the transaction.
- **Write Skew**: Two transactions read overlapping data and make decisions based on that data, but when they commit, they violate a constraint. For example, two transactions read the same account balance and both decide to withdraw money, leading to an overdraft.
  - The transactions made decisions based on stale data, leading to an inconsistent state.

#### Isolation Levels
- **Read Uncommitted**: Allows dirty reads, non-repeatable reads, and phantom reads. Lowest isolation level, highest concurrency.
- **Read Committed**: Prevents dirty reads, but allows non-repeatable reads and phantom reads. Default in many databases.
- **Repeatable Read**: Prevents dirty reads and non-repeatable reads, but allows phantom reads. Suitable for many applications.
- **Serializable**: Prevents all anomalies, but can lead to significant contention and reduced concurrency. Use when strict consistency is required.

| Isolation Level | Dirty Reads | Non-Repeatable Reads | Phantom Reads | Real-World Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Read Uncommitted** | Permitted | Permitted | Permitted | Almost never used. It is effectively no isolation. |
| **Read Committed** | Prevented | Permitted | Permitted | The default for Postgres, SQL Server, and Oracle. Fast, prevents reading bad data, but requires application-level care for repeated reads. |
| **Repeatable Read** | Prevented | Prevented | Permitted | The default for MySQL (InnoDB). Good for complex reporting queries that need a consistent snapshot of data over time. |
| **Serializable** | Prevented | Prevented | Prevented | Financial ledgers or extremely strict inventory systems. Prevents all anomalies but causes massive locking contention and transaction rollbacks. |

#### Locks and Deadlocks:
- **Locks**: Databases use locks to manage concurrent access to data. Types include row locks, table locks, and intent locks. Locking can lead to contention and reduced concurrency.
- **Deadlocks**: Occur when two or more transactions are waiting on each other to release locks, resulting in a cycle of dependencies.
```
Transaction A locks row 1, wants row 2
Transaction B locks row 2, wants row 1
```
The database detects deadlocks and typically resolves them by aborting one of the transactions, which can lead to retries and increased latency.

#### MVCC (Multi-Version Concurrency Control):
Instead of locking reads, the database keeps multiple versions of rows.
Benefits:
- Readers do not block writers
- Writers do not block readers
- Better concurrency

Costs:
- Storage overhead
- Cleanup needed
- Long transactions can prevent cleanup


### Durability
Once a transaction is committed, it will survive system failures. Ensured through Write-Ahead Logging and [Replication](#replication).


#### WAL (Write-Ahead Log):
Before any changes are made to the actual data files on disk, the intended changes are written to an append-only log (sequential writes are fast, not random access memory) called WAL. 

If the system crashes before the changes are applied, the database can replay the WAL to restore the database to a consistent state. This ensures that committed transactions are not lost, even in the event of a crash.

![](../images/System%20Design/Databases/WAL.jpg)


## 4. CAP Theorem
CAP says a distributed system cannot fully guarantee all three at once during a network partition.

- **Consistency**: Every read sees the latest write. All replicas have same data
- **Availability**: Every request receives a non-error response. System always responds to requests
- **Partition Tolerance**: The system continues despite network failures (called **partitions**) -> nodes cannot communicate with each other.

Because fault tolerance is a must in distributed systems, you can only guarantee 2 of the 3 properties:

### Consistency vs. Availability
- **Consistency**: Correctness over availability. All replicas see the same data immediately. If a partition occurs, the system will reject requests to maintain consistency. This leads to higher latency and lower availability during partitions.
  - Use cases: Banking, critical systems where correctness is paramount.

- **Availability**: Availability over immediate consistency. The system continues to respond to requests even during partitions, but may return stale data. This leads to lower latency and higher availability, but temporary inconsistency.
  - Use cases: Social media, caches, systems where eventual consistency is acceptable.

### PACELC Theorem
An extension of CAP that also considers latency when there is no partition -> **P**artion **A**vailability **C**onsistency **E**lse **L**atency **C**onsistency
- **If Partition**: Choose Availability or Consistency
- **Else (no Partition)**: Choose Latency or Consistency

Example: 
```
Low latency:
  Read from the nearest replica.
  Fast response.
  But data may be slightly stale.

Consistency:
  Coordinate with the latest/leader replica.
  Slower response.
  But fresher data.
```



---

## 5. Indexing & Query Optimization
When executing a query in a database, the query planner will determine how to efficiently retrieve the data. 

It may choose (Use EXPLAIN or EXPLAIN ANALYZE to inspect execution):

- **Sequential scan**: Scan entire table row by row (1 item in 1M rows -> 1s) 
- **Index scan**: When querying/filtering on selective columns, an index locate matching rows more efficiently (1 item in 1M rows -> 1ms)
- **Nested loop join**: For each row in the outer table, look up matching rows in the inner table. This works well for small datasets or when the inner lookup is indexed.
- **Hash join**: Build a hash table on the smaller dataset and probe it with the larger dataset (good for large datasets without indexes)
- **Merge join**: Sort both datasets and merge them (good for large sorted datasets)

### Indexes
An index speeds up reads by maintaining an auxiliary data structure that makes values faster to find, filter, sort, or join on.

> Indexes improve reads but hurt writes.

Every insert, update, or delete must update indexes too. Too many indexes cause:
- Slower writes
- More storage / memory usage
- More complex query planning

Create indexes for real query patterns, not for every column.

Indexes will be different depending on the nature of the fields that we want to look up:

#### **B-tree**: 
A B-tree is a self-balancing tree that maintains sorted data and allows for efficient insertions, deletions, and searches O(log n). B-tree nodes can have multiple children - typically hundreds in practice. Each node contains an ordered array of keys and pointers, structured to minimize disk reads. Nodes are optimized to fit on a single disk page.

![](../images/System%20Design/Databases/BTree.jpg)


Great for:

- Equality queries
```
WHERE user_id = 123
```
- Range queries
```
WHERE created_at > now() - interval '7 days'
```
- Sorting
```
ORDER BY created_at DESC
```
- Prefix lookups
```
WHERE name LIKE 'John%'
```

PostgresSQL uses B+ Trees, which store all values in the leaf nodes and use internal nodes only for indexing (no data). This allows for efficient range queries and better cache performance.


#### **Hash Index**: 
Uses a hash function to compute the location of the data based on the indexed field. 
It provides O(1) average-case complexity for lookups, making it very fast for exact match queries. However, it does not support range queries or sorting, as the hash function does not preserve any order, so it mostly used for in-memory key-value stores or for specific use cases where only equality lookups are needed.

![](../images/System%20Design/Databases/HashIndex.jpg)


#### **Inverted Index**: 
An inverted index maps terms (tokenized text) to the documents that contain those terms. It is optimized for full-text search, allowing for fast lookups of documents based on keywords. Inverted indexes are commonly used in search engines and databases that support full-text search capabilities (e.g., Elasticsearch, OpenSearch).

![](../images/System%20Design/Databases/InvertedIndex.jpg)

#### **Geospatial Index**: 
B-tree indexes are designed for linear data (1 dimension), they don't perform well for geospatial queries (2 dimensions -> latitude/longitude), since you need to perform an expensive merge operation to find overlapping regions. See example:

![](../images/System%20Design/Databases/Geospatial.jpg)

So databases use specialized spatial indexes like Geohashing (Redis), R-trees (PostGIS) to index Spatial data (latitude/longitude)

##### **Geohashing**:
- Divides the world into a grid and encodes latitude and longitude into a single string (e.g., "u4pruydqqvj")
- Similar geohashes represent nearby locations
- Fast lookups for nearby points, but less precise for complex shapes (consider hexagonal grid)
![](../images/System%20Design/Databases/Geohashing.jpg)


#### **Bitmap Index**:
A bitmap index uses a bitmap (array of bits) to represent the presence or absence of a value in a column. Each bit corresponds to a row in the table, and the position of the bit indicates whether the row contains the indexed value. Bitmap indexes are particularly efficient for low-cardinality columns (columns with few distinct values, such as boolean flags or categorical data). They allow for fast bitwise operations to combine multiple conditions, making them ideal for complex queries on low-cardinality data. Ideal for read-heavy workloads with few updates, like Datawarehousing and OLAP systems.

![](../images/System%20Design/Databases/Bitmap.jpg)


#### **Bloom Filters**: 
A Bloom filter is a probabilistic data structure that provides a space-efficient (compared to Hash Tables) way to test whether an element is a member of a set:
- Firm NO
- Probable YES (with false positives)

It uses multiple hash functions to map elements to a bit array. When an element is added, the corresponding bits are set to 1. To check for membership, the same hash functions are applied, and if any of the corresponding bits are 0, the element is definitely not in the set. If all bits are 1, the element may be in the set (with a possibility of false positives). 


![](../images/System%20Design/Databases/BloomFilter.jpg)

Bloom filters are commonly used for fast negative checks, such as in caching systems or databases to quickly determine if a key does not exist before performing a more expensive lookup.

#### Composite Indexes
A composite index covers multiple columns, such as:
```
CREATE INDEX idx_orders_user_created_at ON orders(user_id, created_at);

SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC;
```

The order of the columns in the index matters, as it determines how the index can be used for queries. A composite index on (A, B) can efficiently support queries that filter on A alone or on both A and B, but not on B alone.

#### Covering Indexes
A covering index includes all the columns needed by a query, allowing the database to retrieve results directly from the index without accessing the main table. This can significantly improve query performance, as it reduces the number of disk reads required.

```
CREATE INDEX idx_orders_user_status_total ON orders(user_id, status, total);

SELECT status, total FROM orders WHERE user_id = ?;
```

### Materialized Views
A materialized view is a precomputed result set that is stored as a physical table. It is defined by a query and can be refreshed periodically or on demand. Materialized views can significantly improve query performance for complex aggregations or joins, as the results are computed in advance and stored for fast retrieval. At the cost of storage and potential staleness of data, since the view may not reflect the most recent changes until it is refreshed.

For example: A materialized view that aggregates total sales by day:



## 6. Scaling: Replication and Partitioning 
When data or traffic grows beyond the capacity of a single machine, we will need to scale up.
- **Vertical scaling**: Upgrade to a more powerful machine (CPU, RAM, disk). Simple but limited by hardware constraints and can be expensive.
- **Horizontal scaling**: Add more machines to distribute the load. More complex (ACID constraints) but can handle much larger scale.

To horizontally scale a database:
- **Replication**: Add copies for read scaling and fault tolerance
- **Partitioning**: Split data across multiple machines.


### Replication: 
The process of keeping a copy of the same data on multiple machines connected via a network. This also provides high availability, low latency, and fault tolerance.
The biggest design decision is determining which nodes are allowed to accept new data:

- **Single-Leader (Master-Slave)**: One node is designated the Leader. All writes must go to the Leader. The Leader writes the data to its local log and then sends that log to the Followers. Followers only accept reads. Can be async or sync, depending on consistency requirements (Strict or Eventual).(Ex. Postgres, MySQL, MongoDB).
    ```
    Master (writes)
      ↓
    Replica 1, Replica 2 (reads)
    ```
    - **Pros**: Simple, easy to understand, read scaling
    - **Cons**: Write bottleneck, replica lag, failover complexity

- **Multi-Leader (Master-Master)**: Multiple nodes can accept writes. Each node writes to its local log and replicates to the others. This allows for higher availability and distributed writes, but introduces complexity in conflict resolution and eventual consistency.
  ```
  Master 1 ↔ Master 2
  ```
    - **Pros**: No single point of failure, distributed writes
    - **Cons**: Conflict resolution complexity, eventual consistency

- **Leaderless (Quorum-Based)**: Writes must be acknowledged by a majority of nodes (W), and reads must read from a majority of nodes (R). This ensures that if W + R > N (total replicas), you can guarantee consistency. (Ex. DynamoDB and Cassandra).
  ```
  Node 1 ↔ Node 2 ↔ Node 3
   \       |       /
    \      |      /
     \     |     /
      Quorum (W + R > N)
  ```
    - **Pros**: No single point of failure, tunable consistency
    - **Cons**: Higher latency, more complex to manage


### Partitioning:
Partitioning is the process of splitting a large database into smaller, more manageable pieces called partitions or shards. 

- **Vertical partitioning**: Split by columns (Separate user info vs. user activity). Isolating frequently accessed or critical data from rarely used, large, or heavily updated columns, which reduces unnecessary disk I/O and improves caching.
- **Horizontal partitioning**: Split by rows (User ID 1-1000 → Partition 1, User ID 1001-2000 → Partition 2). This allows for horizontal scaling and faster queries, but introduces complexity in query routing and joins across partitions.


### Sharding:
When horizontal partitioning is applied across multiple machines, it is called sharding. Each shard is a separate database instance that holds a subset of the data. Sharding allows for massive horizontal scaling, but requires careful design of the shard key and query routing logic.

#### Choice of Shard Key:
The shard key determines how data is distributed across shards. A good shard key should have:
- High cardinality (many unique values), like *user_id* or *order_id*
- Evenly distributed to avoid hotspots.
- Align with query patterns, to minimize cross-shard queries.

#### How we distribute data across shards:

##### Range-based:
Shard by key range.
```
Shard 1 → User IDs 1–1M
Shard 2 → User IDs 1M–2M
Shard 3 → User IDs 2M–3M
```
- **Pros**: Simple implementation, good for range queries
- **Cons**: Uneven distribution, hotspots (e.g., new users all go to the same shard)

##### Hash-based [PREFERRED]:
Shard by hash(key) % num_shards
```
shard = hash(user_id) % 4

User 42  → hash(42) % 4 = Shard 2
User 99  → hash(99) % 4 = Shard 3
User 123 → hash(123) % 4 = Shard 1
```
- **Pros**: Even distribution
- **Cons**: Resharding (adding/removing shards) is complex (requires consistent hashing), full scan required

##### Directory-based:
Maintain a lookup table that maps key ranges to shards. The application queries the directory to determine which shard to access.
```
user_to_shard
---------------
User 15   → Shard 1
User 87   → Shard 4
User 204  → Shard 2
```
- **Pros**: Flexible, easy resharding (just update the directory)
- **Cons**: Lookup overhead, single point of failure


#### Challenges of Sharding:
Data is now distributed across multiple machines, which means you have to deal with uneven load, queries that span shards, and maintaining consistency across databases. 

##### Hot spots:
Even with a good shard key, some shards can end up handling way more traffic than others and become your bottleneck.

The most common cause is the celebrity problem. If you shard users by user_id, Taylor Swift's shard handles 1000x more traffic than a normal user's shard. Also Time-based sharding all new updates could go to the newest shard, creating a hot spot.

Solutions:
- **Isolate hot keys to dedicated shards**: If Taylor Swift's account generates too much traffic, move it to a dedicated shard that only handles celebrity accounts. This is why directory-based sharding can be useful for specific cases, though you probably wouldn't start there.
- **Use compound shard keys**: Instead of sharding just by user_id, combine it with another dimension like hash(user_id + date). This spreads a single user's data across multiple shards over time, distributing the load evenly at the cost of worst cross-shard queries for that user.
- **Dynamic shard splitting**: Some databases support automatically splitting a shard when it gets too large or too hot. (Example MongoDB)

##### Cross-shard queries:
Queries that need to access data from multiple shards (e.g., joins, aggregates) become more complex and less efficient.

Solutions:
- **Cache the results of common cross-shard queries**: For example, "top 10 most popular posts". Trading latency for consistency and staleness of data.
- **Denormalization**: Duplicate data across shards to avoid cross-shard joins. This can lead to data inconsistency, increased storage costs and writes more complex, but improves read performance.

##### Maintaining consistency:
When data is distributed across shards, ensuring ACID properties becomes more difficult, especially for transactions that span multiple shards. You need to coordinate commits across shards to maintain atomicity and consistency. Like a bank transfer between one account on Shard A and another on Shard B.

Solutions:
- Use distributed transactions (2PC, Saga pattern) to ensure atomicity across shards, though this can be complex and impact performance.
- Design to avoid cross-shard transactions when possible, by carefully choosing shard keys and denormalizing data, like keeping a user's profile and their posts in the same shard.
- Accept eventual consistency for certain operations, especially if they are not critical (e.g., user profile updates can be eventually consistent, but financial transactions should be strongly consistent).

---

## 7. CDC, Outbox, and Data Movement
Modern systems often need to move data from the main database to other systems, such as queues, search indexes, caches, analytics platforms, or other services.

The main challenge is doing this reliably. This is known as the **dual-write problem**: if you write to the database and then to the downstream system, you risk inconsistency if one write succeeds and the other fails.

### CDC: Change Data Capture
CDC is a software design pattern that captures changes to the database (inserts, updates, deletes) and streams them to downstream systems in real-time. 
This allows is done by reading the database's transaction log (WAL) or by using an outbox table that the application writes to as part of the same transaction.

Examples: Dynamodb Streams, Postgres Logical Decoding, Debezium (open-source CDC platform)

### Outbox Pattern
Instead of writing to the database and publishing an event separately, the application writes both the business data and the event into the same database transaction.

Example:
```
orders table       → stores the order
outbox_events table → stores `OrderCreated` event
```

### Outbox + CDC
You can use CDC alone or combine it with the Outbox pattern to be explicit about the business intent (events you want to capture and avoid noise from other database changes).

A common production setup combines both patterns:

Application writes an event to the outbox table within a database transaction
        ↓
CDC reads the outbox change
        ↓
Event is published to Kafka or another broker


These systems usually provide *at-least-once* delivery.

That means an event should be delivered, but it might be delivered more than once.

Because of that, consumers should be idempotent -> Processing the same event multiple times has the same result as processing it once.

### Common Uses
- Keep search indexes (Elasticsearch) in sync with the source-of-truth database.
- Feed analytics pipelines and data warehouses.
- Propagate events to microservices reliably (Kafka, RabbitMQ).
- Invalidate caches (Redis) when data changes.


## 8. Data Lifecycle and Governance
Data should not live forever without a plan. A good database design should define how data is created, stored, used, archived, and eventually deleted.

This is called the data lifecycle.

Create → Store → Use → Share → Archive → Delete

### Data Encryption
Most production databases should use encryption at rest and in transit by default.
- **At rest**: Encrypt data on disk to protect against physical theft. Use AES-256 or similar strong encryption algorithms. Key management is critical.
- **In transit**: Use TLS to encrypt data between clients and the database, and between database nodes in a cluster. This prevents eavesdropping and man-in-the-middle attacks.

### Data Classification
| Type | Examples |
|---|---|
| Public | Public product catalog |
| Internal | Internal metrics or logs |
| Confidential | Business reports, contracts |
| Sensitive | Personal data (PII), payment data, credentials |

### Retention Policies
A retention policy defines how long data should be kept.

Example:
Keep application logs for 30 days. Keep invoices for 7 years. Delete inactive user sessions after 24 hours. Archive old orders after 2 years.


### Data Deletion Strategies
- **Hard delete**: Permanently remove data from the database. This is simple but irreversible. Use when data must be removed for compliance or privacy reasons.
- **Soft delete**: Mark data as deleted (e.g., `is_deleted` flag) without actually removing it. This allows for recovery and auditing, but requires filtering out deleted records in queries and can lead to storage bloat.
- **Tombstone**: Similar to soft delete, but also includes metadata about the deletion (e.g., deletion timestamp, reason). This can be useful for auditing and debugging, but adds complexity to the data model and queries.
- **Anonymization**: Remove identifying fields while keeping aggregate data for analysis.

---

## 9. Backup & Recovery

### Backup Types
- **Full backup**: Complete database copy
- **Incremental backup**: Only changes since last backup
- **Differential backup**: Changes since last full backup

### Recovery objectives
- **RTO (Recovery Time Objective)**: Time to recover to a functional state after failure.
- **RPO (Recovery Point Objective)**: Data loss tolerance (time between last backup and failure)

Example: If you can tolerate losing up to 1 hour of data, your RPO is 1 hour. If you need to be back up within 30 minutes, your RTO is 30 minutes.

### Recovery mechanisms
- **Backups**: Restore from a backup file. Can be slow, especially for large databases.
- **Replication**: Failover to a replica. Faster than restoring from backup, but may have some data loss if replication lag exists.
- **Failover**: Automatic or manual switch to a standby replica in case of primary failure. Requires careful planning and testing to ensure it works correctly.
- **Snapshots**: Some databases support taking snapshots of the data at a point in time, which can be used for quick recovery.

### Recovery capabilities
- **Point-in-time recovery**: Restore the database to a specific point in time, using a combination of backups and transaction logs. Specially useful for recovering from logical errors (e.g., accidental data deletion) or to a known good state after a failure.
- **Continuous backup**: Some databases support continuous backup to cloud storage, allowing for near-instant recovery to any point in time within the retention period.


## 10. Monitoring & Observability

### Key Metrics
| Metric | Why it matters |
|---|---|
| CPU usage | High CPU may indicate expensive queries or database overload |
| Memory usage | Low memory can cause more disk reads and slower queries |
| Disk usage | Full disks can cause outages |
| Disk I/O | Slow reads/writes can slow the database |
| Query latency (p50, p99) | Shows how long queries take |
| Query throughput (QPS) | Shows how many queries are running |
| Connection count | Too many connections can overload the database |
| Lock waits | Shows queries waiting on other queries |
| Deadlocks | Indicates conflicting transactions |
| Replication lag | Shows how far replicas are behind the primary |
| Backup status | Ensures recovery is possible |
| Error rate | Shows failed queries or database errors |

### Alerting
- High latency, error rates
- Replication lag threshold
- Disk space running out
- Connection pool exhaustion


## 11. System Design Example Decision Tree

```
START
  ↓
Consistency critical?
  ├─ YES → Relational DB (PostgreSQL), Strong consistency
  └─ NO → NoSQL option, check data model
       ↓
High read volume?
  ├─ YES → Read replicas + cache (Redis)
  └─ NO → Direct DB access
       ↓
High write volume?
  ├─ YES → Sharding strategy
  └─ NO → Single instance or master-slave
       ↓
Complex queries?
  ├─ YES → Relational DB, complex joins
  └─ NO → NoSQL, consider document or key-value
       ↓
Real-time requirements?
  ├─ YES → Cache + message queue
  └─ NO → Standard approach sufficient
```

---

## 12. Common Interview Questions

1. **Design a URL shortening service**: Distributed ID generation, sharding by hash
2. **Design a social media feed**: Materialized views, cache, read replicas
3. **Design a ride-sharing system**: Geospatial indexes, strong consistency for payments
4. **Design a search engine**: Inverted indexes, caching, distributed search
5. **Design an analytics platform**: Time-series DB, columnar storage, batch processing
