import asyncio
import json
import redis
import httpx
from typing import Dict, Any,AsyncIterable, Optional, Callable, List


from dataclasses import dataclass
from enum import Enum
import uuid
import structlog

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response" 
    NOTIFICATION = "notification"
    ERROR = "error"

@dataclass
class A2AMessage:
    """Agent-to-Agent message structure following JSON-RPC 2.0"""
    id: str
    method: str
    params: Dict[str, Any]
    message_type: MessageType = MessageType.REQUEST
    source_agent: Optional[str] = None
    target_agent: Optional[str] = None
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": self.id,
            "method": self.method,
            "params": self.params,
            "metadata": {
                "message_type": self.message_type.value,
                "source_agent": self.source_agent,
                "target_agent": self.target_agent,
                "timestamp": self.timestamp
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        metadata = data.get("metadata", {})
        return cls(
            id=data["id"],
            method=data["method"], 
            params=data.get("params", {}),
            message_type=MessageType(metadata.get("message_type", "request")),
            source_agent=metadata.get("source_agent"),
            target_agent=metadata.get("target_agent"),
            timestamp=metadata.get("timestamp")
        )

class A2ACommunicationBus:
    """Message bus for Agent-to-Agent communication"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.logger = structlog.get_logger(component="a2a_bus")
        self.message_handlers: Dict[str, Callable] = {}
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
    
    def register_agent(self, agent_name: str, agent_info: Dict[str, Any]):
        """Register an agent in the communication bus"""
        self.agent_registry[agent_name] = {
            **agent_info,
            "last_seen": asyncio.get_event_loop().time()
        }
        self.logger.info("Agent registered", agent=agent_name, info=agent_info)
    
    def register_message_handler(self, method: str, handler: Callable):
        """Register a handler for specific message method"""
        self.message_handlers[method] = handler
        self.logger.info("Message handler registered", method=method)
    
    async def send_message(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """Send message to target agent"""
        try:
            # Add timestamp
            message.timestamp = str(asyncio.get_event_loop().time())
            
            # Determine routing strategy
            if message.target_agent:
                return await self._send_direct_message(message)
            else:
                return await self._broadcast_message(message)
                
        except Exception as e:
            self.logger.error("Failed to send A2A message", 
                            message_id=message.id, error=str(e))
            raise
    
    async def _send_direct_message(self, message: A2AMessage) -> Optional[Dict[str, Any]]:
        """Send message directly to specific agent"""
        target_agent = message.target_agent
        
        # Check if agent is registered
        if target_agent not in self.agent_registry:
            raise ValueError(f"Target agent {target_agent} not registered")
        
        agent_info = self.agent_registry[target_agent]
        
        # Try HTTP endpoint first
        if "http_endpoint" in agent_info:
            return await self._send_http_message(message, agent_info["http_endpoint"])
        
        # Fall back to message queue
        queue_name = f"agent_{target_agent}_queue"
        await self._send_queue_message(message, queue_name)
        
        return {"status": "queued", "queue": queue_name}
    
    async def _send_http_message(self, message: A2AMessage, endpoint: str) -> Dict[str, Any]:
        """Send message via HTTP to agent endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json=message.to_dict(),
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def _send_queue_message(self, message: A2AMessage, queue_name: str):
        """Send message via Redis queue"""
        message_data = json.dumps(message.to_dict())
        self.redis_client.lpush(queue_name, message_data)
        
        self.logger.info("Message queued", 
                        message_id=message.id,
                        queue=queue_name,
                        target=message.target_agent)
    
    async def _broadcast_message(self, message: A2AMessage) -> Dict[str, Any]:
        """Broadcast message to all registered agents"""
        results = {}
        
        for agent_name in self.agent_registry:
            if agent_name != message.source_agent:  # Don't send to self
                message.target_agent = agent_name
                try:
                    result = await self._send_direct_message(message)
                    results[agent_name] = result
                except Exception as e:
                    results[agent_name] = {"error": str(e)}
        
        return {"broadcast_results": results}
    
    async def receive_messages(self, agent_name: str) -> AsyncIterable[A2AMessage]:
        """Receive messages for specific agent"""
        queue_name = f"agent_{agent_name}_queue"
        
        while True:
            try:
                # Non-blocking pop from queue
                message_data = self.redis_client.brpop([queue_name], timeout=1)
                
                if message_data:
                    _, raw_message = message_data
                    message_dict = json.loads(raw_message.decode())
                    message = A2AMessage.from_dict(message_dict)
                    
                    self.logger.info("Message received",
                                   agent=agent_name,
                                   message_id=message.id,
                                   method=message.method)
                    
                    yield message
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                self.logger.error("Error receiving message",
                                agent=agent_name, error=str(e))
                await asyncio.sleep(1)  # Longer delay on error

class A2AAgent:
    """Mixin class to add A2A communication capabilities to agents"""
    
    def __init__(self, agent_name: str, communication_bus: A2ACommunicationBus):
        self.agent_name = agent_name
        self.communication_bus = communication_bus
        self.logger = structlog.get_logger(agent=agent_name)
        
        # Register this agent
        self.communication_bus.register_agent(agent_name, {
            "name": agent_name,
            "type": getattr(self, "agent_type", "unknown"),
            "http_endpoint": f"/api/v1/agents/{agent_name}/a2a"
        })
    
    async def call_agent(self, target_agent: str, method: str, 
                        params: Dict[str, Any]) -> Dict[str, Any]:
        """Call another agent directly (A2A)"""
        message = A2AMessage(
            id=str(uuid.uuid4()),
            method=method,
            params=params,
            source_agent=self.agent_name,
            target_agent=target_agent,
            message_type=MessageType.REQUEST
        )
        
        self.logger.info("Calling agent A2A",
                        target=target_agent, method=method)
        
        response = await self.communication_bus.send_message(message)
        
        self.logger.info("A2A call completed",
                        target=target_agent, method=method, 
                        response=response)
        
        return response
    
    async def notify_agent(self, target_agent: str, event: str, 
                          data: Dict[str, Any]):
        """Send notification to another agent"""
        message = A2AMessage(
            id=str(uuid.uuid4()),
            method="notify",
            params={"event": event, "data": data},
            source_agent=self.agent_name,
            target_agent=target_agent,
            message_type=MessageType.NOTIFICATION
        )
        
        await self.communication_bus.send_message(message)
    
    async def broadcast_event(self, event: str, data: Dict[str, Any]):
        """Broadcast event to all agents"""
        message = A2AMessage(
            id=str(uuid.uuid4()),
            method="broadcast_event",
            params={"event": event, "data": data},
            source_agent=self.agent_name,
            message_type=MessageType.NOTIFICATION
        )
        
        await self.communication_bus.send_message(message)
    
    async def start_message_listener(self):
        """Start listening for incoming A2A messages"""
        async for message in self.communication_bus.receive_messages(self.agent_name):
            try:
                await self._handle_a2a_message(message)
            except Exception as e:
                self.logger.error("Error handling A2A message",
                                message_id=message.id, error=str(e))
    
    async def _handle_a2a_message(self, message: A2AMessage):
        """Handle incoming A2A message"""
        method = message.method
        
        if hasattr(self, f"a2a_{method}"):
            handler = getattr(self, f"a2a_{method}")
            await handler(message.params)
        else:
            self.logger.warning("No handler for A2A method",
                              method=method, source=message.source_agent)