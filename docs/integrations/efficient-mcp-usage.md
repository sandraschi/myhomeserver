# Efficient MCP Server Usage: Best Practices for Stability and Performance

## 🎯 Overview

This guide outlines proven strategies for efficiently and stably using existing local MCP servers in MyHomeServer. The goal is to maximize reliability while minimizing resource usage and ensuring consistent user experience.

## 🔧 Connection Management

### Connection Pooling Strategy

```python
# backend/services/mcp_pool.py
from typing import Dict, Optional
import httpx
from dataclasses import dataclass

@dataclass
class McpConnection:
    client: httpx.AsyncClient
    server_url: str
    last_used: datetime
    health_status: str

class McpConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.pool: Dict[str, McpConnection] = {}
        self.max_connections = max_connections

    async def get_connection(self, server_name: str, server_url: str) -> httpx.AsyncClient:
        """Get or create connection to MCP server"""
        if server_name in self.pool:
            conn = self.pool[server_name]
            # Check if connection is still healthy
            if await self._check_health(conn):
                conn.last_used = datetime.now()
                return conn.client

        # Create new connection
        if len(self.pool) >= self.max_connections:
            await self._evict_oldest()

        client = httpx.AsyncClient(
            base_url=server_url,
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5)
        )

        self.pool[server_name] = McpConnection(
            client=client,
            server_url=server_url,
            last_used=datetime.now(),
            health_status="healthy"
        )

        return client
```

### Health Monitoring

```python
# backend/services/health_monitor.py
import asyncio
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class McpHealthMonitor:
    def __init__(self, mcp_servers: Dict[str, str]):
        self.servers = mcp_servers
        self.health_status: Dict[str, dict] = {}
        self.monitoring = True

    async def start_monitoring(self):
        """Start continuous health monitoring"""
        while self.monitoring:
            await self._check_all_servers()
            await asyncio.sleep(30)  # Check every 30 seconds

    async def _check_all_servers(self):
        """Check health of all MCP servers"""
        tasks = []
        for name, url in self.servers.items():
            tasks.append(self._check_server_health(name, url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for name, result in zip(self.servers.keys(), results):
            if isinstance(result, Exception):
                self.health_status[name] = {
                    "status": "error",
                    "error": str(result),
                    "last_check": datetime.now(),
                    "response_time": None
                }
                logger.warning(f"MCP server {name} health check failed: {result}")
            else:
                self.health_status[name] = result

    async def _check_server_health(self, name: str, url: str) -> dict:
        """Check individual server health"""
        start_time = datetime.now()

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                response_time = (datetime.now() - start_time).total_seconds() * 1000

                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "last_check": datetime.now(),
                        "response_time": response_time,
                        "version": response.json().get("version")
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "last_check": datetime.now(),
                        "response_time": response_time,
                        "error": f"HTTP {response.status_code}"
                    }

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return {
                "status": "error",
                "last_check": datetime.now(),
                "response_time": response_time,
                "error": str(e)
            }
```

## 📊 Caching Strategy

### Multi-Level Caching

```python
# backend/services/cache_manager.py
from typing import Any, Optional
import json
from datetime import datetime, timedelta
import redis.asyncio as redis

class McpCacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
        self.local_cache: Dict[str, dict] = {}

    async def get_cached_data(self, key: str, max_age: int = 300) -> Optional[Any]:
        """Get data from cache with TTL check"""
        # Try Redis first
        cached = await self.redis.get(f"mcp:{key}")
        if cached:
            data = json.loads(cached)
            if self._is_fresh(data, max_age):
                return data["value"]

        # Fallback to local cache
        if key in self.local_cache:
            data = self.local_cache[key]
            if self._is_fresh(data, max_age):
                return data["value"]

        return None

    async def set_cached_data(self, key: str, value: Any, ttl: int = 300):
        """Cache data with TTL"""
        data = {
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "ttl": ttl
        }

        # Store in Redis
        await self.redis.setex(f"mcp:{key}", ttl, json.dumps(data))

        # Also store locally for faster access
        self.local_cache[key] = data

    def _is_fresh(self, data: dict, max_age: int) -> bool:
        """Check if cached data is still fresh"""
        timestamp = datetime.fromisoformat(data["timestamp"])
        age = (datetime.now() - timestamp).total_seconds()
        return age < max_age
```

### Smart Cache Invalidation

```python
# backend/services/cache_invalidator.py
class CacheInvalidator:
    def __init__(self, cache_manager: McpCacheManager):
        self.cache = cache_manager

    async def invalidate_on_change(self, server_name: str, resource_type: str):
        """Invalidate cache when data changes"""
        patterns = {
            "camera": [f"cameras:*", f"{server_name}:cameras:*"],
            "energy": [f"energy:*", f"{server_name}:energy:*"],
            "weather": [f"weather:*", f"{server_name}:weather:*"],
            "security": [f"security:*", f"{server_name}:security:*"]
        }

        if resource_type in patterns:
            for pattern in patterns[resource_type]:
                await self.cache.invalidate_pattern(pattern)

    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        keys = await self.redis.keys(f"mcp:{pattern}")
        if keys:
            await self.redis.delete(*keys)
```

## 🔄 Request Optimization

### Batch Requests

```python
# backend/services/batch_processor.py
from typing import List, Dict, Any
import asyncio

class McpBatchProcessor:
    def __init__(self, connection_pool: McpConnectionPool):
        self.pool = connection_pool

    async def batch_camera_status(self, camera_ids: List[str]) -> Dict[str, Any]:
        """Batch multiple camera status requests"""
        async def fetch_camera(camera_id: str):
            client = await self.pool.get_connection("tapo-camera", "http://localhost:7778")
            response = await client.get(f"/api/cameras/{camera_id}/status")
            return camera_id, response.json()

        tasks = [fetch_camera(cid) for cid in camera_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        status_map = {}
        for result in results:
            if isinstance(result, Exception):
                # Handle individual failures gracefully
                continue
            camera_id, status = result
            status_map[camera_id] = status

        return status_map
```

### Request Deduplication

```python
# backend/services/request_deduplicator.py
from typing import Dict, Any, Optional
import asyncio
import hashlib

class RequestDeduplicator:
    def __init__(self):
        self.pending_requests: Dict[str, asyncio.Future] = {}

    def _generate_key(self, method: str, url: str, params: dict = None) -> str:
        """Generate unique key for request"""
        key_data = f"{method}:{url}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def deduplicate_request(self, method: str, url: str, params: dict = None) -> Any:
        """Execute request or return pending result"""
        key = self._generate_key(method, url, params)

        if key in self.pending_requests:
            return await self.pending_requests[key]

        future = asyncio.Future()
        self.pending_requests[key] = future

        try:
            result = await self._execute_request(method, url, params)
            future.set_result(result)
            return result
        except Exception as e:
            future.set_exception(e)
            raise
        finally:
            # Clean up after short delay
            asyncio.create_task(self._cleanup_request(key))

    async def _cleanup_request(self, key: str):
        await asyncio.sleep(0.1)  # Brief delay to allow other waiters
        self.pending_requests.pop(key, None)
```

## 🛡️ Error Handling & Resilience

### Circuit Breaker Pattern

```python
# backend/services/circuit_breaker.py
from enum import Enum
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class McpCircuitBreaker:
    def __init__(self, server_name: str, failure_threshold: int = 5, timeout: int = 60):
        self.server_name = server_name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenException(self.server_name)

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            logger.info(f"Circuit breaker for {self.server_name} reset to CLOSED")

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker for {self.server_name} opened after {self.failure_count} failures")

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True

        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.timeout
```

### Graceful Degradation

```python
# backend/services/graceful_degradation.py
from typing import Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class GracefulDegradationManager:
    def __init__(self):
        self.fallbacks: Dict[str, Callable] = {}
        self.degraded_features: set = set()

    def register_fallback(self, feature: str, fallback_func: Callable):
        """Register fallback function for a feature"""
        self.fallbacks[feature] = fallback_func

    async def execute_with_fallback(self, feature: str, primary_func: Callable, *args, **kwargs) -> Any:
        """Execute primary function with fallback on failure"""
        try:
            return await primary_func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary function for {feature} failed: {e}")

            if feature not in self.degraded_features:
                self.degraded_features.add(feature)
                logger.info(f"Entering degraded mode for {feature}")

            if feature in self.fallbacks:
                try:
                    return await self.fallbacks[feature](*args, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback for {feature} also failed: {fallback_error}")

            # Return minimal/default data
            return self._get_default_data(feature)

    def _get_default_data(self, feature: str) -> Any:
        """Return default/minimal data for degraded features"""
        defaults = {
            "cameras": [],
            "energy": {"devices": [], "usage": 0},
            "weather": {"temperature": None, "status": "unavailable"},
            "security": {"events": [], "alerts": []}
        }
        return defaults.get(feature, None)
```

## 📈 Performance Monitoring

### Metrics Collection

```python
# backend/services/metrics_collector.py
from typing import Dict, List
import time
import logging

logger = logging.getLogger(__name__)

class McpMetricsCollector:
    def __init__(self):
        self.metrics: Dict[str, List[dict]] = {}

    def record_request(self, server_name: str, endpoint: str, method: str,
                      response_time: float, status_code: int, success: bool):
        """Record API request metrics"""
        metric = {
            "timestamp": time.time(),
            "server": server_name,
            "endpoint": endpoint,
            "method": method,
            "response_time": response_time,
            "status_code": status_code,
            "success": success
        }

        if server_name not in self.metrics:
            self.metrics[server_name] = []

        self.metrics[server_name].append(metric)

        # Keep only last 1000 metrics per server
        if len(self.metrics[server_name]) > 1000:
            self.metrics[server_name] = self.metrics[server_name][-1000:]

    def get_server_stats(self, server_name: str) -> dict:
        """Get performance statistics for a server"""
        if server_name not in self.metrics:
            return {}

        metrics = self.metrics[server_name]
        if not metrics:
            return {}

        response_times = [m["response_time"] for m in metrics]
        success_count = sum(1 for m in metrics if m["success"])

        return {
            "total_requests": len(metrics),
            "success_rate": success_count / len(metrics),
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "last_request": max(m["timestamp"] for m in metrics)
        }
```

## 🚀 Best Practices

### 1. Connection Management
- Use connection pooling to avoid overhead
- Implement proper connection timeouts
- Monitor connection health continuously
- Handle connection failures gracefully

### 2. Caching Strategy
- Cache frequently accessed data
- Implement smart cache invalidation
- Use Redis for distributed caching
- Set appropriate TTL values

### 3. Request Optimization
- Batch similar requests when possible
- Deduplicate concurrent identical requests
- Implement request prioritization
- Use compression for large payloads

### 4. Error Handling
- Implement circuit breakers for failing services
- Provide graceful degradation
- Log errors comprehensively
- Alert on critical failures

### 5. Monitoring & Observability
- Track response times and success rates
- Monitor resource usage
- Implement health checks
- Set up alerting for anomalies

### 6. Configuration Management
- Make timeouts configurable
- Allow cache TTL adjustments
- Support different environments
- Enable feature flags for testing

## 📊 Performance Benchmarks

Expected performance with these optimizations:

- **Response Time**: <500ms for cached data, <2s for fresh data
- **Success Rate**: >99.5% under normal conditions
- **Resource Usage**: <200MB memory per MCP server connection
- **Concurrent Users**: Support 100+ simultaneous users
- **Uptime**: >99.9% with proper failover

## 🔧 Troubleshooting

### Common Issues & Solutions

1. **Slow Response Times**
   - Check cache hit rates
   - Monitor MCP server performance
   - Optimize database queries

2. **Connection Failures**
   - Verify MCP server URLs
   - Check network connectivity
   - Review firewall settings

3. **Memory Leaks**
   - Monitor connection pool size
   - Implement proper cleanup
   - Check for circular references

4. **Cache Inconsistencies**
   - Verify cache invalidation logic
   - Check TTL settings
   - Monitor cache hit/miss ratios

This guide provides the foundation for stable, efficient MCP server integration. Regular monitoring and optimization based on real usage patterns will further improve performance over time.