# Networking Essentials for System Design Interviews

## OSI Model & TCP/IP Stack

### OSI Model (7 Layers)
- **Layer 7 - Application**: HTTP, HTTPS, DNS, SMTP, FTP
- **Layer 6 - Presentation**: Encryption, compression, serialization
- **Layer 5 - Session**: Session management, authentication
- **Layer 4 - Transport**: TCP, UDP
- **Layer 3 - Network**: IP, routing
- **Layer 2 - Data Link**: MAC addresses, switches
- **Layer 1 - Physical**: Cables, signals

### TCP/IP Model (4 Layers)
- Application Layer: HTTP, DNS, SMTP
- Transport Layer: TCP, UDP
- Internet Layer: IP
- Link Layer: MAC

![](../images/System%20Design/Networking/OSI.jpg)


---

## Network Layer (Layer 3): IP

The Network Layer is responsible for logical addressing and routing packets across multiple networks.

### Core Responsibilities
- Logical addressing with IP addresses (source and destination)
- Packet forwarding between networks via routers
- Path selection (routing) from sender network to receiver network
- Fragmentation/reassembly behavior (primarily relevant in IPv4)

### IPv4 vs IPv6
- **IPv4**: 32-bit address space (e.g., `192.168.1.10`), limited address pool
- **IPv6**: 128-bit address space (e.g., `2001:db8::1`), massive scale and simplified header design
- IPv6 reduces dependence on NAT and supports better end-to-end connectivity

### Routing Basics
- Routers forward packets using routing tables
- Route decision is based on **longest prefix match**
- Common routing protocols: OSPF, BGP
- TTL (IPv4) / Hop Limit (IPv6) prevents infinite routing loops

### Subnetting and CIDR
- CIDR notation: `IP/prefix` (example: `10.0.0.0/24`)
- Larger prefix length means smaller subnet (e.g., `/24` > `/16` in specificity)
- Subnetting helps isolate traffic, improve security boundaries, and control broadcast domains

### NAT (Network Address Translation)
- Translates private IPs to public IPs for internet access
- Conserves public IPv4 addresses
- Common in home networks and cloud VPC egress paths
- Trade-off: breaks true end-to-end addressing and complicates some protocols

### How IPv4 Ranges Are Allocated
- Internet IPv4 space is globally managed by IANA
- IANA gives big blocks to regional registries (RIRs)
- RIRs allocate to ISPs, cloud providers, and companies
- Companies split their block into smaller subnets (for offices, VPCs, VLANs)

### Subnets
- Think of a subnet as a street of addresses.
- In a **/24** subnet (like `192.168.1.0/24`):
  - `192.168.1.0` = subnet/network address (reserved)
  - `192.168.1.255` = broadcast address (reserved)
  - Usable host range = `192.168.1.1` to `192.168.1.254`
- Router is usually set to `.1` (for example `192.168.1.1`) by convention, not because `.0` is the router address.
- Common private IPv4 ranges:
  - `10.0.0.0/8`
  - `172.16.0.0/12`
  - `192.168.0.0/16`
- Also useful to know:
  - `127.0.0.1` = loopback (your own machine)
  - `255.255.255.255` = local broadcast only

### System Design Relevance
- Multi-region systems rely on BGP and DNS to route users to healthy regions
- IP planning (subnets/CIDR) is critical in VPC/VNet design
- Layer 3 issues often appear as packet loss, high latency, or asymmetric routing

---

## 4. Transportation Layer (layer 4) Protocols

### TCP (Transmission Control Protocol)

- Connection-oriented protocol
- Reliable, ordered delivery of bytes
- Uses acknowledgments (ACKs), retransmissions, and sequence numbers
- Flow control with sliding window
- Congestion control (slow start, congestion avoidance)
- Three-way handshake: `SYN -> SYN-ACK -> ACK`
- Four-step close with `FIN/ACK`
- Common use cases: HTTP/1.1, HTTP/2, HTTPS, SSH, databases

![](../images/System%20Design/Networking/TCP.jpg)

### UDP (User Datagram Protocol)

- Connectionless protocol
- Best-effort delivery (no built-in retransmission)
- No ordering guarantees
- Lower overhead and lower latency than TCP
- No flow or congestion control at protocol level
- Common use cases: DNS queries, VoIP, live streaming, online gaming

![](../images/System%20Design/Networking/UDP.jpg)

### QUIC (Quick UDP Internet Connections)

- Modern transport protocol built on top of UDP
- Provides reliability, encryption (TLS 1.3), and multiplexed streams
- Faster handshakes than TCP+TLS (supports 0-RTT and 1-RTT)
- Avoids head-of-line blocking across independent streams
- Connection migration support (helps when network changes, e.g., Wi-Fi to mobile)
- Common use cases: HTTP/3, latency-sensitive web/mobile workloads

### TCP vs UDP (Interview Lens)

- **Reliability**: TCP = high, UDP = low
- **Latency**: TCP = higher, UDP = lower
- **Ordering**: TCP = guaranteed, UDP = not guaranteed
- **Overhead**: TCP = higher, UDP = lower
- **When to use TCP**: Correctness and complete delivery matter
- **When to use UDP**: Speed matters more than perfect delivery

### TCP vs UDP vs QUIC (Quick Recall)

- **Transport base**: TCP = native transport, UDP = native transport, QUIC = over UDP
- **Reliability**: TCP = yes, UDP = no, QUIC = yes
- **Encryption**: TCP = optional (via TLS), UDP = optional (app-level), QUIC = built-in (TLS 1.3)
- **Handshake cost**: TCP+TLS = higher, UDP = minimal, QUIC = lower than TCP+TLS
- **Best for**: TCP = strict reliability, UDP = ultra-low overhead, QUIC = fast + secure modern web transport

---


## HTTP & HTTPS (Application Layer) - Layer 7

Request:
````
GET /posts/1 HTTP/1.1
Host: myserveristhebest.com
Accept: application/json
User-Agent: Mozilla/5.0 (Windows 10)

````

Response:
````
HTTP/1.1 200 OK
Date: Wed, 26 Feb 2025 12:34:56 GMT
Content-Type: application/json; charshet=utf-8
Content-Length: 292

{
    "userId": 1,
    "id": 1,
    "title": "Mypost title",
    "body": "Interesting content of the post"
}
````

### HTTP (HyperText Transfer Protocol)

- **Stateless** protocol built on TCP
- Default port: **80**
- Request-response model
- Methods / HTTP verb: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS
- Headers: Key-value metadata such as `Host`, `Authorization`, `Content-Type`, `Accept`, `Cache-Control`, and `User-Agent`
- Status codes:
  - 1xx: Informational
  - 2xx: Success (200 OK, 201 Created)
  - 3xx: Redirection (301, 302, 304)
  - 4xx: Client Error (400, 401, 403, 404)
  - 5xx: Server Error (500, 502, 503)

### HTTPS (HTTP Secure)
- HTTP over TLS/SSL encryption
- Default port: **443**
- Provides confidentiality, integrity, and authentication
- Certificate-based authentication

### HTTP/2
- Multiplexing: Multiple requests over single connection
- Server push capability
- Header compression
- Binary framing

### HTTP/3
- Built on QUIC protocol
- Faster connection establishment
- Better performance over unreliable networks


## DNS (Domain Name System)
Domain Name System (DNS) is best understood as a hierarchical, distributed, and eventually consistent database that abstracts network addressing. It’s essentially a globally scaled service discovery mechanism that translates human-readable hostnames into wire-protocol addresses (IPv4/IPv6). 

![](../images/System%20Design/Networking/DNS.jpeg)

### DNS Resolution Process
1. Client queries local DNS resolver
2. Recursive resolver queries **Root nameserver**
3. Root nameserver directs to **TLD (Top-level Domain) nameserver**
4. TLD nameserver directs to **authoritative nameserver**
5. Authoritative nameserver returns IP address

### DNS Records
- **A**: IPv4 address (`93.184.216.34`)
- **AAAA**: IPv6 address (`2606:2800:220:1:248:1893:25c8:1946`)
- **CNAME**: Alias for another domain, used for subdomains (`blog.myblog.com. → myblog.wordpress.com`)
- **MX**: Mail exchange server
- **NS**: Nameserver (e.g., `mywebsite.com ask to ns1.cloudflare.com`)
- **SOA**: Start of Authority
- **TXT**: Text records
- **SRV**: Service records 

### DNS Caching & TTL
- TTL (Time To Live): Controls cache duration
- Lower TTL = more queries, faster updates
- Higher TTL = fewer queries, slower propagation

### DNS Issues
- Single point of failure without redundancy
- DNS spoofing/hijacking attacks
- Cache poisoning
- Slow propagation


## 5. Load Balancing
A load balancer is a critical component in distributed systems that distributes incoming network traffic across multiple backend servers to ensure high availability, reliability, and scalability.

There are: 
- Client-side load balancers, mainly used in internal facing microservices for service discovery and load distribution.
- Server-side load balancers, they sit in front of a pool of servers to distribute incoming requests.

### Load Balancer Types
- **Hardware**: Expensive, dedicated boxes
- **Software**: Nginx, HAProxy, AWS ELB
- **Cloud-based**: AWS ALB, Google Cloud LB, Azure LB

### Load Balancing Algorithms
- **Round Robin**: Rotate through servers
- **Least Connections**: Direct to server with fewest connections
- **IP Hash**: Route based on client IP
- **Weighted**: Distribute based on server capacity
- **Least Response Time**: Route to fastest server
- **Random**: Random selection

### Layer 4 vs Layer 7 Load Balancing
- **L4 (TCP/UDP)**: Fast, less context, only looks at IP/port
- **L7 (HTTP/HTTPS)**: Slower, can inspect content (cookies, headers) and make routing decisions based on application data

### Sticky Sessions
- Route client to same backend server
- Use session cookies or IP hashing
- Can cause uneven load distribution

---

## 7. Caching Strategies

### HTTP Caching Headers
- **Cache-Control**: `public, private, max-age=3600`
- **ETag**: Entity tag for conditional requests
- **Last-Modified**: For conditional requests
- **Expires**: Absolute expiration time
- **Vary**: Cache variant based on header

### Caching Layers
- **Browser Cache**: Client-side
- **CDN Cache**: Edge networks
- **Server Cache**: Redis, Memcached
- **Database Cache**: Query results

### Cache Invalidation Strategies
- **TTL-based**: Time-based expiration
- **Event-based**: Invalidate on data change
- **LRU (Least Recently Used)**: Remove least used items
- **Manual**: Explicit cache clearing

---

## 8. Content Delivery Networks (CDN)

### How CDNs Work
1. User requests content
2. DNS resolves to nearest edge server
3. Edge server serves cached content or fetches from origin

### Benefits
- Reduced latency
- Decreased server load
- Improved availability
- Protection against DDoS

### Popular CDNs
- Cloudflare
- AWS CloudFront
- Akamai
- Fastly

---

## 9. Security & Authentication

### CORS (Cross-Origin Resource Sharing)
- Allows cross-origin requests safely
- Preflight requests (OPTIONS)
- Access-Control headers

### OAuth 2.0
- Authorization framework
- Access tokens, refresh tokens
- Grant types: Authorization code, Implicit, Client credentials

### JWT (JSON Web Tokens)
- Self-contained tokens
- Header.Payload.Signature
- Stateless authentication
- Vulnerable to XSS if stored in localStorage

### SSL/TLS
- Encryption protocol
- Certificate-based
- Handshake process
- Forward secrecy with Perfect Forward Secrecy (PFS)

---

## 10. Bandwidth & Latency

### Bandwidth
- Amount of data transmitted per unit time
- Measured in Mbps, Gbps
- Affects throughput
- Often the limiting factor

### Latency
- Time for data to travel from source to destination
- Network latency = propagation + transmission + queuing + processing
- RTT (Round Trip Time): Time for request and response
- P95, P99 latencies important for SLAs

### Optimizations
- Connection pooling
- Keep-alive connections
- Compression (gzip, brotli)
- Protocol selection (HTTP/2, HTTP/3)

---

## 11. Network Topologies

### Topologies
- **Star**: All connected to central hub
- **Mesh**: Every node connected to every other
- **Ring**: Nodes in circular arrangement
- **Bus**: All connected to central line
- **Hybrid**: Combination of topologies

### Data Center Networks
- **Tier Architecture**: Core, Distribution, Access
- **Spine-Leaf**: Scalable, non-blocking
- **Fat Tree**: High bandwidth, low latency

---

## 12. Recovering from Failures (Resilience):

### Timeout, Backoff & Retry Strategies

After a failure, clients should implement retry logic with exponential backoff to avoid overwhelming the server and to increase the chances of success on subsequent attempts.

![](../images/System%20Design/Networking/Retries.jpg)

- **Exponential Backoff**: Wait time increases exponentially with each retry (e.g., 1s, 2s, 4s, 8s)
- **Jitter**: Add randomness to backoff to prevent thundering herd problem (e.g., 1s ± 0.5s, 2s ± 1s)

### Cascade Failures
When one service failure causes a chain reaction of failures in dependent services, which can be agravated by retry storms.
For example, if Service A calls Service B, and Service B fails because service C is down, Service A will retry. If many clients are calling Service A, this can lead to a surge of retries that overwhelms Service B and C, causing a cascade failure.

Mitigation strategies:
- **Circuit Breaker**: Stop calls to failing service after threshold is reached.
- **Bulkhead**: Isolate resources for different services
- **Fallbacks**: Provide default response when service is unavailable   
 

---

## 13. Monitoring & Observability

### Key Metrics
- **Throughput**: Requests per second (TPS)
- **Latency**: Response time (p50, p95, p99)
- **Error Rate**: Failed requests percentage (failed requests / total requests)
- **Saturation**: Resource utilization (CPU, memory, disk, network)

### Tools
- Prometheus: Metrics collection
- Grafana: Visualization
- ELK Stack: Logging
- Jaeger: Distributed tracing
- New Relic, Datadog: APM

---

## 14. Common Interview Scenarios

### Designing a URL Shortener
- DNS resolution
- Load balancing
- Database indexing
- Caching strategy
- Rate limiting

### Designing a Chat System
- WebSocket for real-time
- Message persistence
- Presence detection
- Scalability considerations

### Designing an API Gateway
- Routing logic
- Rate limiting
- Authentication
- Request/response transformation
- Load balancing

### Designing a Video Streaming Service
- CDN for distribution
- Adaptive bitrate streaming (HLS, DASH)
- Bandwidth optimization
- Error handling

### Designing a Real-time Notification System
- WebSocket vs polling
- Message queues (Kafka, RabbitMQ)
- Fan-out architecture
- Rate limiting

---

## Other useful resources
- https://www.hellointerview.com/learn/system-design/core-concepts/networking-essentials

--
