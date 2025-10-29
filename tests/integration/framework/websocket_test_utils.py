"""
WebSocket Test Utilities for Integration Testing.

Provides mock WebSocket connections with realistic latency and failure simulation.

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Integration Tests
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import asyncio
import json
import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)


@dataclass
class MockWebSocketConnection:
    """Mock WebSocket connection for testing."""
    
    client_id: str
    is_connected: bool = True
    latency_ms: float = 0.0
    failure_rate: float = 0.0
    messages_sent: List[dict] = field(default_factory=list)
    messages_received: List[dict] = field(default_factory=list)
    connection_time: float = field(default_factory=time.time)
    
    async def send(self, message: str) -> None:
        """Simulate sending a message with latency and potential failure."""
        if not self.is_connected:
            raise ConnectionClosed(1000, "Connection closed")
        
        # Simulate network latency
        if self.latency_ms > 0:
            await asyncio.sleep(self.latency_ms / 1000.0)
        
        # Simulate random failures
        import random
        if random.random() < self.failure_rate:
            self.is_connected = False
            raise ConnectionClosed(1006, "Simulated connection failure")
        
        # Record sent message
        try:
            msg_dict = json.loads(message)
            self.messages_sent.append(msg_dict)
        except json.JSONDecodeError:
            self.messages_sent.append({"raw": message})
    
    async def recv(self) -> str:
        """Simulate receiving a message."""
        if not self.is_connected:
            raise ConnectionClosed(1000, "Connection closed")
        
        # Simulate network latency
        if self.latency_ms > 0:
            await asyncio.sleep(self.latency_ms / 1000.0)
        
        # Return next message if available
        if self.messages_received:
            msg = self.messages_received.pop(0)
            return json.dumps(msg)
        
        # Wait for message
        await asyncio.sleep(0.1)
        return json.dumps({"type": "ping"})
    
    async def close(self, code: int = 1000, reason: str = "") -> None:
        """Close the connection."""
        self.is_connected = False
    
    def inject_message(self, message: dict) -> None:
        """Inject a message to be received."""
        self.messages_received.append(message)
    
    def get_sent_messages(self) -> List[dict]:
        """Get all sent messages."""
        return self.messages_sent.copy()
    
    def clear_messages(self) -> None:
        """Clear message history."""
        self.messages_sent.clear()
        self.messages_received.clear()


class MockWebSocket:
    """
    Mock WebSocket for testing ResilientWebSocketManager.
    
    Simulates realistic WebSocket behavior including:
    - Network latency
    - Connection failures
    - Message queuing
    - Connection state tracking
    """
    
    def __init__(
        self,
        client_id: str = "test_client",
        latency_ms: float = 0.0,
        failure_rate: float = 0.0
    ):
        """
        Initialize mock WebSocket.
        
        Args:
            client_id: Client identifier
            latency_ms: Simulated network latency in milliseconds
            failure_rate: Probability of connection failure (0.0-1.0)
        """
        self.connection = MockWebSocketConnection(
            client_id=client_id,
            latency_ms=latency_ms,
            failure_rate=failure_rate
        )
        self.remote_address = ("127.0.0.1", 12345)
    
    async def send(self, message: str) -> None:
        """Send a message through the mock connection."""
        await self.connection.send(message)
    
    async def recv(self) -> str:
        """Receive a message from the mock connection."""
        return await self.connection.recv()
    
    async def close(self, code: int = 1000, reason: str = "") -> None:
        """Close the mock connection."""
        await self.connection.close(code, reason)
    
    @property
    def closed(self) -> bool:
        """Check if connection is closed."""
        return not self.connection.is_connected
    
    def inject_message(self, message: dict) -> None:
        """Inject a message to be received."""
        self.connection.inject_message(message)
    
    def get_sent_messages(self) -> List[dict]:
        """Get all sent messages."""
        return self.connection.get_sent_messages()
    
    def clear_messages(self) -> None:
        """Clear message history."""
        self.connection.clear_messages()
    
    def simulate_disconnect(self) -> None:
        """Simulate connection disconnect."""
        self.connection.is_connected = False
    
    def simulate_reconnect(self) -> None:
        """Simulate connection reconnect."""
        self.connection.is_connected = True


def create_mock_websocket(
    client_id: str = "test_client",
    latency_ms: float = 0.0,
    failure_rate: float = 0.0
) -> MockWebSocket:
    """
    Create a mock WebSocket connection for testing.
    
    Args:
        client_id: Client identifier
        latency_ms: Simulated network latency in milliseconds
        failure_rate: Probability of connection failure (0.0-1.0)
    
    Returns:
        MockWebSocket instance
    
    Example:
        >>> ws = create_mock_websocket("client1", latency_ms=50.0)
        >>> await ws.send('{"type": "test"}')
    """
    return MockWebSocket(client_id, latency_ms, failure_rate)


async def simulate_connection_failure(
    websocket: MockWebSocket,
    delay_ms: float = 0.0
) -> None:
    """
    Simulate a connection failure after optional delay.
    
    Args:
        websocket: Mock WebSocket to fail
        delay_ms: Delay before failure in milliseconds
    
    Example:
        >>> ws = create_mock_websocket()
        >>> await simulate_connection_failure(ws, delay_ms=100.0)
    """
    if delay_ms > 0:
        await asyncio.sleep(delay_ms / 1000.0)
    
    websocket.simulate_disconnect()
    logger.info(f"Simulated connection failure for {websocket.connection.client_id}")


async def simulate_network_latency(
    websocket: MockWebSocket,
    latency_ms: float
) -> None:
    """
    Update network latency for a WebSocket connection.
    
    Args:
        websocket: Mock WebSocket to update
        latency_ms: New latency in milliseconds
    
    Example:
        >>> ws = create_mock_websocket()
        >>> await simulate_network_latency(ws, 200.0)  # 200ms latency
    """
    websocket.connection.latency_ms = latency_ms
    logger.info(f"Updated latency to {latency_ms}ms for {websocket.connection.client_id}")


async def create_multiple_mock_clients(
    count: int,
    latency_range: tuple = (0.0, 100.0),
    failure_rate: float = 0.0
) -> List[MockWebSocket]:
    """
    Create multiple mock WebSocket clients with varying latencies.
    
    Args:
        count: Number of clients to create
        latency_range: (min_ms, max_ms) for random latency
        failure_rate: Probability of connection failure
    
    Returns:
        List of MockWebSocket instances
    
    Example:
        >>> clients = await create_multiple_mock_clients(10, latency_range=(10.0, 50.0))
    """
    import random
    
    clients = []
    for i in range(count):
        latency = random.uniform(*latency_range)
        client_id = f"test_client_{i}"
        ws = create_mock_websocket(client_id, latency, failure_rate)
        clients.append(ws)
    
    logger.info(f"Created {count} mock clients with latency range {latency_range}ms")
    return clients

