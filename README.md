# High-Availability Asynchronous API Gateway & Traffic Orchestrator

A lightweight, production-grade Layer-7 API Gateway, Load Balancer, and Web Application Firewall (WAF) engineered completely from scratch in Python utilizing asynchronous socket multiplexing. Built to demonstrate low-level systems engineering, network routing topologies, and programmatic cybersecurity constraints without relying on external enterprise frameworks.

## 🚀 Key Architectural Features

* **Asynchronous Socket Multiplexing:** Utilizes Python's native `asyncio` event loop to handle concurrent traffic conduits streams seamlessly with zero-blocking CPU performance degradation.
* **Health-Aware Load Balancing:** Implements a thread-safe Round-Robin routing matrix driven by an active background daemon executing continuous low-overhead TCP pings to automatically evict dead servers and restore recovering nodes.
* **Inline Security Shielding (WAF):** Employs deep-packet heuristic checking to inspect Layer-7 payloads, instantly dropping requests carrying known malicious signatures (SQL Injection, XSS scripting patterns) or blacklisted security scraping user-agents.
* **Dynamic Token Rate Limiting:** Mitigates Denial-of-Service (DoS) vectors by running an IP-based sliding window request tracker, automatically enforcing a `429 Too Many Requests` threshold constraint.
* **Automated Cluster Orchestration:** Containerized via Docker & Docker-Compose to support immediate multi-node deployment, accompanied by a local development orchestration engine (`.bat`) for rapid local testing loops.

## 📁 System Architecture & Directory Topology

```text
distributed-gateway/
│
├── gateway/
│   ├── core.py          # Asynchronous Layer-7 TCP Socket Engine
│   ├── router.py        # Advanced Path Routing & Health Monitoring Daemon
│   ├── middleware.py    # Security Firewall Engine & Token Rate Limiter
│   └── Dockerfile       # Container blueprint for the Gateway node
│
├── backend/
│   ├── microservice.py  # Asynchronous JSON application service target
│   └── Dockerfile       # Container blueprint for application cluster nodes
│
├── docker-compose.yml   # Production container environment mesh layout
└── launch.bat           # Automated development environment bootstrap script
```

## 🛠️ Local Infrastructure Initialization

To initialize the distributed environment grid locally on Windows, execute the automated bootstrap batch script from your command line or double-click the file in your workspace:

```bash
# Launch the cluster via the automated orchestrator
launch.bat
```

The script automatically provisions environment parameters, binds structural nodes to assigned network ports (`8001` and `8002`), introduces initialization buffers, and ignites the core Proxy Gateway routing hub on `http://127.0.0.1:8080`.
