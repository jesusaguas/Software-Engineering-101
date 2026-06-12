# API Concepts for Systems Design Interviews

**API (Application Programming Interface)**: 
- Contract between client and server for data exchange
- Enables communication between different software systems
- Abstracts implementation details, exposing only necessary functionality

## Types of APIs
- **REST (Representational State Transfer)**: HTTP-based, stateless, resource-oriented
- **GraphQL**: Query language allowing clients to request exact data needed
- **gRPC**: High-performance, binary protocol using Protocol Buffers
- **SSE (Server-Sent Events)**: One-way server-to-client streaming
- **WebSocket**: Bidirectional communication for real-time applications
- **WebRTC**: Real-time communication for browsers (audio/video)
- **SOAP**: XML-based, complex but reliable for enterprise systems
- **Message Queues**: Asynchronous communication (RabbitMQ, Kafka)


### REST API
`````
GET /api/v1/users/123 HTTP/1.1
Host: api.example.com
Accept: application/json
`````    
- Resource-oriented design
- Uses HTTP methods semantically
- Stateless interactions
- Supports caching and layered system design

### GraphQL
````
POST /graphql HTTP/1.1
Host: api.example.com
Content-Type: application/json
{
  "query": "query { 
        user(id: 123) { 
            name, 
            email 
        },
        posts { 
            title, 
            content 
        }
    }"
}
```` 
- Query language for APIs
- Many client, different shapes, single endpoint (`/graphql`)
- Clients specify exactly what data they need
- Reduces over-fetching and under-fetching (deep nested reads in one trip)


- More complex server implementation
- HTTP caching is harder
- N+1 query problem (where ) if not optimized (e.g., DataLoader)
### gRPC (Google Remote Procedure Call)
`````
service UserService {
  rpc GetUser (GetUserRequest) returns (GetUserResponse);
}
`````
- High-performance RPC framework, low latency, language-agnostic
- Uses Protocol Buffers for serialization (binary format, smaller and faster than JSON)
- HTTP/2 based transport
- Supports streaming (unary, server, client, bidirectional)
- Common in internal microservices

- Hard to debug (binary format)
- Not browser-friendly (requires gRPC-Web)

### Server Sent Events (SSE)
- Unidirectional real-time updates from server to client
- Uses HTTP connection, keeps it open for streaming, when connections are severed, SSE will automatically reconnect.
- Simpler than WebSockets for certain use cases (e.g., live scores, notifications)

#### Step 1: Client initiates connection
The browser sends an HTTP GET request, including `Accept: text/event-stream` header to indicate it wants an SSE stream.
````
GET /live-updates HTTP/1.1
Host: example.com
Accept: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
Last-Event-ID: 42  <-- (Only sent if reconnecting)
````

#### Step 2: Server responds.
The server must acknowledge this by setting the Content-Type to text/event-stream. It also usually disables buffering so that data is sent to the client immediately.

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
Transfer-Encoding: chunked
```

#### Step 3: The data payload. 

Once the connection is established, the body of the HTTP response remains unfinished/open, and the server can send multiple events over time. Each event is formatted as follows:
```
id: 101
event: price-update
data: {"symbol": "BTC", "price": "65000"}

: this is a comment (heartbeat) to keep the connection alive

id: 102
data: User "Alice" joined the chat

retry: 10000
```

---

### WebSockets
- Full-duplex communication over a single TCP connection
- Starts with HTTP handshake, then upgrades to WebSocket protocol
- Lower latency than HTTP for real-time applications
- Use cases: chat apps, live notifications, gaming
```
wss://yahoofinance.com/ticker (WebSocket URL)
```

Sent:
```
{
    "type": "subscribe",
    "symbol": "AAPL"
}
```

Received:
```
{
    "symbol": "AAPL",
    "price": 150.25,
    "timestamp": "2024-06-01T12:34:56Z"
}
```
```
{
    "symbol": "AAPL",
    "price": 151.45,
    "timestamp": "2024-06-01T12:35:05Z"
}
```

### WebRTC
WebRTC (Web Real-Time Communication) is an open-source technology that enables browsers and mobile apps to exchange audio, video, and data directly with each other, mostly without needing intermediate servers.
- Peer-to-peer communication protocol for real-time media and data
- Used for video conferencing, Live Broadcasting, file sharing, and online gaming
- Supports NAT traversal with STUN/TURN servers     

![](../images/System%20Design/APIs/WebRTC.jpg)



---

## 2. REST API Design Principles

### RESTful Constraints
1. **Client-Server**: Separation of concerns
2. **Statelessness**: Each request contains all information needed
3. **Cacheability**: Responses marked as cacheable/non-cacheable
4. **Uniform Interface**: Consistent API design
5. **Layered System**: Client unaware of intermediate layers
6. **Code on Demand**: Optional, server can extend client functionality

### HTTP Methods
- **GET**: Retrieve data (safe, idempotent)
- **POST**: Create new resource (non-idempotent)
- **PUT**: Replace entire resource (idempotent)
- **PATCH**: Partial update (may/may not be idempotent)
- **DELETE**: Remove resource (idempotent)
- **HEAD**: Like GET but no response body
- **OPTIONS**: Describe communication options

### Status Codes
- **2xx (Success)**: 200 OK, 201 Created, 202 Accepted (Async work), 204 No Content
- **3xx (Redirection)**: 301 Moved Permanently, 304 Not Modified
- **4xx (Client Error)**: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 429 Too Many Requests
- **5xx (Server Error)**: 500 Internal Server Error, 503 Service Unavailable

### Resource-Oriented Design
- Resources identified by URIs: `/users/123/posts/456`
- Versioning strategies: URL path (`/v1/`), header, query parameter
- Represent resources as JSON/XML with meaningful structure
- Use plural nouns: `/users` not `/user`

---

## 3. API Authentication & Authorization

### Authentication Methods
- **API Keys**: API keys are long, randomly generated strings, should be used only for server-to-server communication, not for user authentication.
- **OAuth 2.0**: Industry standard for delegated authentication. Ex. Sign in with Google/Facebook.
  - Human user -> Authorization Code Flow: User -> Google login -> Client sends code to backend -> backend gets token.
  - Machine-to-machine -> Client Credentials Flow: Service A -> auth server -> token -> Service B
- **JWT (JSON Web Tokens)**: Encode user information directly into the token itself rather than storing session state on your server.
  - Header.Payload.Signature format
- **mTLS**: Mutual TLS for service-to-service authentication using certificates
- **Basic Auth**: Username:password in Base64 (use only over HTTPS, not recommended for production)

### Authorization Patterns
- **Role-Based Access Control (RBAC)**: Users assigned roles with permissions
- **Attribute-Based Access Control (ABAC)**: Fine-grained policies based on attributes
- **Scopes**: OAuth scopes limiting token permissions. Example: `scope=read:users write:posts`

---

## 4. Rate Limiting & Throttling

### Rate Limiting Strategies
- **Token Bucket** [*PREFERRED*]: Refill tokens at fixed rate, burst allowed
- **Leaky Bucket**: Fixed output rate, smooths traffic (avoid bursts, good for fragile downstream services)
- **Sliding Window**: Track requests in time window, most complex but fair
- **Fixed Window**: Simplest, but vulnerable to bursts at boundaries

### Implementation Considerations
- **Per-user/per-IP**: Different limits for different clients
- **Distributed rate limiting**: Shared state across servers (Redis)
- **Response headers**: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
- **429 Too Many Requests**: Proper HTTP status

---

## 5. Caching Strategies

### HTTP Caching Headers
- **Cache-Control**: max-age=3600, no-cache, no-store, public, private
- **ETag**: Entity tag, identifier for a specific version of a resource
- **Last-Modified**: Timestamp for cache validation
- **Expires**: Absolute expiration time

### Caching Levels
- **Client-side**: Browser cache reduces round trips, like HTTP cache or localStorage for API responses.
- **CDN**: Distribute content geographically, edge networks.
- **Server-side**: External cache (Redis, Memcached) or in-process cache (local memory).


### Cache Invalidation / Eviction policies: 
  - LRU (Least Recently Used) [*PREFERRED*]: Linked list / ring buffer to track usage, good for general-purpose caching
  - LFU (Least Frequently Used): Good for popular keys, like trending videos
  - TTL (Time To Live): Expire items after a certain time, good for time-sensitive data

### Cache Busting (force cache refresh)
- Query parameters: `/resource?v=123`
- File naming: Include version in filename (Ex: `app.9f3c.js`)
- Time-based: Change URLs on content updates

### Cache architectures
- **Cache-aside**: Read cache; on miss, client fetches from DB and updates cache (most common)
- **Write-through**: Write to cache; cache immediately writes to DB (sync) (strong consistency, slower writes + dual-write complexity)
- **Write-back**: Write to cache; cache flushes to DB later (async) (high write throughput, risk of data loss)
- **Read-through**: Read cache; on miss, cache fetches from DB (simplifies client logic, but can increase latency on cache miss)

### Common Caching Problems
- **Cache Stampede**: When a popular cache entry (Homepage feed) expires and many requests try to rebuild it at the same time, the spike can overwhelm the database and cause cascading failures. Solution:
    - **Request coalescing** / **Locking**: Only one request rebuilds cache, others wait. Prevent multiple rebuilds with distributed locks (e.g., Redis SETNX)
    - **Early recomputation / cache warming**: Refresh cache before it expires
- **Cache Inconsistency**: Cache and database out of sync. Mitigation: 
   - **Cache invalidation on writes**: Delete the cache entry after updating the database  
   - **Eventual consistency**: Accept stale reads for a short period, use background jobs to update cache.
    - **Write-through caching**: Ensure cache is always updated on writes, but this can increase latency and complexity.
    - **Short TTLs**: Reduce the window of inconsistency, but can lead to more cache misses and higher load on the database.
- **Hot Keys**: Certain keys receive disproportionate traffic, leading to cache overload (User: Messi). Mitigation: 
  - **Replication**: Store the same value on multiple cache nodes and load balance reads across them.
  - **Rate limiting**: Apply stricter rate limits to known hot keys to prevent cache overload.
  - **Local caching**: Keep hot keys in memory on the application server to reduce load on the cache


---

## 6. Pagination & Filtering

### Pagination Patterns
- **Offset-Limit**: `?offset=10&limit=20` (simple but inefficient for large datasets, also can lead to duplicates/missing items if data changes/shifts)
- **Cursor-Based**: `?cursor=eyJjcmVh==&limit=20` The cursor is typically an encoded reference to a specific record (like an ID or timestamp).  (efficient, handles insertions/deletions, it's harder to implement features like "jump to page 5.")


### Sorting & Filtering
- Query parameters: `?sort=name&order=asc&filter[status]=active`
- Full-text search support for text fields (e.g., `?q=football`, reverse index in database)
- Range queries: `?price_min=10&price_max=100`


---

## 7. Error Handling

### Error Categories
- **Client Errors (4xx)**: Validation (400), authentication (401), authorization (403), not found (404), rate limit exceeded (429). 
- **Server Errors (5xx)**: Internal failures(500), service unavailable(503). 

### Idempotency
- **Idempotent endpoints**: `GET`, `PUT`, `DELETE` are naturally idempotent. `POST` is non‑idempotent unless you add server‑side deduplication (Idempotency-Key).
- **Idempotency Keys**: Client-provided unique (UUID) identifier for deduplication. The server stores (cache) the key and response for a certain period, returning the same result for duplicate requests with the same key. For example: Place checkout order.

### Retry Strategies
- **Exponential backoff with jitter**: baseDelay * 2^attempt ± jitter prevents synchronized retries. Example: base=100ms + 100, 200, 400ms ± random(0,100ms).
- **When to retry**: transient 5xx, network errors, 429 (respect `Retry-After`), `Retryable`. Do not retry 4xx validation errors or business rejections.
  - Operational Errors (timeouts, capacity) -> NOT RETRYABLE
  - Business Errors  (insufficient funds, out-of-stock) -> RETRYABLE
- Use circuit breakers (resilience pattern) to fail fast when downstream is unhealthy.

## 8. Testing & Validation
| Test type | What it checks | Example |
|---|---|---|
| Unit tests | Small, isolated tests covering single functions and components. | A pricing function calculates tax correctly |
| Integration tests | Interaction with real dependencies (DB, cache, message broker) | API handler talks to database correctly |
| Contract tests | Service/API compatibility | Consumer expects `GET /users/{id}` to return `id`, `name`, `email` |
| Smoke tests | Basic deployment health | App starts, `/health` returns `200`, login works |
| End-to-end tests | Full user workflows | User signs up, pays, receives confirmation |
| Regression tests | Previously working behavior still works | A fixed bug does not come back |
| Acceptance tests | Feature meets business/user requirements | User can reset password via email |
| Load tests | Test under expected high traffic | Checkout works during peak usage |
| Stress tests | Behavior beyond normal limits | What happens at 5× expected traffic? |
| Soak tests | Long-running stability | Service runs under load for 24 hours without memory leaks |
| Security tests | Vulnerabilities and abuse cases | Auth bypass, injection, dependency scanning |
| Chaos tests | Resilience to failures | Inject latency, kill dependencies.. to validate circuit breakers, bulkheads (isolation), and graceful degradation (e.g., fallback responses). |
| Compatibility tests | Works across environments | Browser, OS, device, API version compatibility |
| Accessibility tests | Usable by people with disabilities | Keyboard navigation, screen reader labels, contrast |
| Usability tests | Real users can use it effectively | Users can complete onboarding without confusion |
| Canary tests | Validate a small production rollout | Send 1% of traffic to new version and monitor |
| Synthetic monitoring | Production-like checks on a schedule | Bot logs in every 5 minutes and checks checkout |

### Product and release validation
| Technique | What it validates | Example |
|---|---|---|
| Feature flags | Whether a change can be safely enabled, disabled, or targeted | Enable a new feature only for internal users |
| Canary releases | Whether a release behaves safely in production at small scale | Send 5% of traffic to the new version and monitor SLOs |
| A/B testing | Whether one product variant performs better than another | Compare two checkout flows by conversion rate |
| Synthetic monitoring | Whether critical user journeys keep working in production | Bot logs in every 5 minutes and checks checkout |


### CI/CD Pipelines
**CI/CD** is the practice of automating how software changes are tested, built, and released.
The goal of CI/CD is to make releases faster, safer, repeatable, and easier to recover from.
- **Continuous Integration**: Merge code frequently, run automated tests (linting, unit tests, integration tests) on every commit/PR to catch issues early.
- **Continuous Delivery**: Automatically deploy to staging after passing tests, with manual approval for production.
- **Continuous Deployment**: Automatically deploy to production after passing tests, no manual approval needed.

#### Mechanisms
- **Rollback**: Automatically revert to previous version on failure (e.g., failed health checks, SLO breaches).
- **Bake Time**: Wait for a certain period after deployment to monitor for issues before considering it successful.
- **Stages**: Separate pipelines for different environments (dev, staging, prod) with increasing levels of testing and validation.


---

## 9. Versioning & Backwards Compatibility

### Versioning Strategies
- **URL Versioning**: `/v1/users`, `/v2/users`
- **Header Versioning**: `Accept: application/vnd.api+json;version=2`
- **Query Parameter**: `?api_version=2`

### Backwards Compatibility
- **Additive Changes**: New fields, new endpoints (safe)
- **Deprecation Period**: Announce, support old version, migrate
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Feature Flags**: Roll out new features gradually
---

## 10. Performance & Scalability

### API Performance Metrics
- **Latency**: p50, p95, p99 response times
- **Throughput**: Requests per second
- **Availability**: Uptime percentage
- **Error Rate**: Percentage of failed requests

### Logging
- **Structured Logging**: JSON logs with correlation IDs
- **Log Levels**: DEBUG, INFO, WARN, ERROR
- **Sensitive Data**: Don't log passwords, tokens, PII

### Tools
- **Prometheus**: Metrics collection
- **ELK Stack**: Logging and analysis
- **Jaeger**: Distributed tracing
- **DataDog**: Comprehensive monitoring

### Optimization Techniques
- **Database Optimization**: Indexing, query optimization
- **Connection Pooling**: Reuse database connections
- **Batch Endpoints**: Multiple operations in single request
- **Compression**: gzip response bodies
- **Async Processing**: Long operations run asynchronously with job IDs
- **Load Balancing**: Distribute requests across servers

### Scalability Patterns
- **Horizontal Scaling**: Add more servers
- **Vertical Scaling**: More powerful hardware
- **Database Sharding**: Partition data by key
- **Read Replicas**: Distribute read traffic
- **Message Queues**: Decouple components

---

## 11. Security Best Practices

### Transport Security
- **HTTPS/TLS**: Encrypt data in transit
- **Certificate Pinning**: Prevent Man in the Middle attacks
- **Forward Secrecy**: Perfect Forward Secrecy in TLS

### Input Validation & Output Encoding
- **Input Validation**: Strict schema validation, type checking
- **SQL Injection Prevention**: Parameterized queries
- **XSS Prevention**: Output encoding/escaping, HTML sanitization
- **CSRF Protection**: CSRF tokens for state-changing operations

### API Security
- **CORS**: Whitelist allowed origins
- **Request Signing**: HMAC signing for authenticity
- **Rate Limiting**: Prevent brute force attacks
- **IP Whitelisting**: Restrict to known IPs
- **Audit Logging**: Track API access and changes

---

## 12. Async APIs & Long-Running Operations

### Patterns for Long Operations
- **Polling**: Client periodically checks status endpoint (Inefficient, but simple)
- **Webhooks**: External services (such as payment processors - Stripe) push updates to your server when paym
- **Server-Sent Events (SSE)**: One-way server-to-client push
- **WebSockets**: Bidirectional real-time communication

Example: A client initiates a purchase `api/pay`, and opens a WebSocket connection to the server to receive real-time payment status updates (processing, success, failure). 
Meanwhile the server initiate a Stripe payment, and listens for webhook events from Stripe on `/api/stripe/webhooks`, when the payment is confirmed, update the client through the WebSocket.

### Job Management
- **Job ID**: Return ID immediately, client queries status
- **Status Codes**: PENDING, PROCESSING, COMPLETED, FAILED
- **Callbacks**: Notify when complete via webhook
- **Timeout Handling**: Clear expectations on job lifetime

---

## 13. API Gateway & Service Mesh

### API Gateway
- **Routing**: Direct requests to correct backend services
- **Request/Response Transformation**: Modify headers, bodies
- **Authentication**: Centralized auth enforcement
- **Rate Limiting**: Global rate limit management
- **Logging & Monitoring**: Centralized observability
- **Examples**: Kong, AWS API Gateway, nginx

### Service Mesh
A service mesh is infrastructure that manages service-to-service communication inside a distributed system, usually microservices, as a sidecar proxy deployed alongside each service instance:
- **Service Discovery**: Automatic service location
- **Load Balancing**: Intelligent request distribution
- **Circuit Breaking**: Fail fast on unhealthy services
- **Retry Logic**: Automatic retries with backoff
- **Examples**: Istio, Linkerd

---

## 14. Common Pitfalls & Best Practices

### Design Anti-Patterns
- **Chatty APIs**: Too many small requests (use batching)
- **Inconsistent Errors**: Varying error formats across endpoints
- **Breaking Changes**: Without deprecation period
- **Tight Coupling**: API tightly coupled to backend
- **Ignoring Caching**: Missing opportunities for optimization

### Best Practices
- **Design for Change**: Plan for evolution
- **Be Explicit**: Clear naming, intent
- **Consistency**: Uniform design across API
- **Documentation**: Keep it updated and accurate
- **Testing**: Unit, integration, load testing
- **Monitoring**: Proactive observability
- **Security-First**: Build security in from start
- **User-Centric**: Design with client needs in mind

---

## Other resources
- https://www.hellointerview.com/learn/system-design/core-concepts/api-design
