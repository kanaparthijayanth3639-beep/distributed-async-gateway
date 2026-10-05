# Asynchronous Layer-7 Proxy Gateway & Traffic Orchestrator

A custom, low-level Layer-7 API Gateway, Load Balancer, and Web Application Firewall (WAF) engineered in Python using raw asynchronous socket pipelines. Designed to handle stateful concurrency, low-overhead active health checking, and baseline traffic isolation policies at the ingress interface without external networking packages.

## Core Features

* **Asynchronous Socket Concurrency:** Uses Python's native `asyncio` networking framework to pipe non-blocking data conduits concurrently.
* **Round-Robin Load Balancing:** Features a state-aware load broker managed by an isolated background task tracking server health via active TCP handshakes.
* **Layer-7 Content Firewall:** Analyzes inbound streams to isolate and drop requests carrying illegal payloads (SQLi / XSS footprints) or blacklisted script scanner user-agents.
* **Sliding-Window Rate Limiter:** Features granular IP-based rate controls tracking client frequency bounds to yield clean `429 Too Many Requests` HTTP blocks.
* **Dynamic Stream Assembly:** Safely reads dynamic multi-part streaming byte content by analyzing `Content-Length` fields prior to dispatch.

## Repository Layout

```text
├── gateway/
│   ├── core.py          # Asynchronous Socket Transport Core
│   ├── router.py        # Health Daemon & Load Balance Routing Strategy
│   └── middleware.py    # Request Validation Filters & WAF Engine
├── backend/
│   └── microservice.py  # Targeted application microservices (mock output)
├── docker-compose.yml   # Multi-tier container configuration metrics
└── launch.bat           # Environment bootstrapping verification script
```
