"""
Memory module for the Xeo Framework.

This module defines the memory systems used by agents to store and retrieve
information over short and long time periods.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, Type
import json
import time


@dataclass
class MemoryItem:
    """Represents a single memory item with metadata."""
    content: Any
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0.0 to 1.0 scale
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the memory item to a dictionary."""
        return {
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "importance": self.importance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """Create a memory item from a dictionary."""
        return cls(
            content=data["content"],
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {}),
            importance=data.get("importance", 0.5)
        )


class Memory(ABC):
    """
    Abstract base class for all memory implementations.
    
    Memory classes handle the storage and retrieval of information
    that agents need to maintain state and learn from experience.
    """
    
    @abstractmethod
    async def store(self, content: Any, **metadata) -> str:
        """
        Store a piece of information in memory.
        
        Args:
            content: The content to store
            **metadata: Additional metadata about the memory
            
        Returns:
            A unique identifier for the stored memory
        """
        pass
    
    @abstractmethod
    async def retrieve(self, query: Optional[Any] = None, limit: int = 10, **filters) -> List[MemoryItem]:
        """
        Retrieve memories matching the query and filters.
        
        Args:
            query: Optional query to match against memory contents
            limit: Maximum number of memories to return
            **filters: Additional filters to apply
            
        Returns:
            List of matching memory items, ordered by relevance
        """
        pass
    
    @abstractmethod
    async def update(self, memory_id: str, content: Optional[Any] = None, **updates) -> bool:
        """
        Update an existing memory.
        
        Args:
            memory_id: ID of the memory to update
            content: New content (if updating content)
            **updates: Other fields to update
            
        Returns:
            True if the update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        pass


class ShortTermMemory(Memory):
    """
    Short-term memory for agents.
    
    This implementation uses an in-memory dictionary for fast access
    to recent memories. It's suitable for storing temporary information
    that doesn't need to persist between sessions.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize the short-term memory.
        
        Args:
            max_size: Maximum number of items to store before evicting old ones
        """
        self._memories: Dict[str, MemoryItem] = {}
        self.max_size = max_size
        self._counter = 0
    
    async def store(self, content: Any, **metadata) -> str:
        """Store a memory."""
        # Generate a unique ID
        memory_id = f"stm_{self._counter}"
        self._counter += 1
        
        # Create and store the memory
        memory_item = MemoryItem(
            content=content,
            metadata=metadata
        )
        
        self._memories[memory_id] = memory_item
        
        # Enforce max size
        if len(self._memories) > self.max_size:
            # Remove the oldest memory (FIFO)
            oldest_id = next(iter(self._memories))
            del self._memories[oldest_id]
        
        return memory_id
    
    async def retrieve(self, query: Optional[Any] = None, limit: int = 10, **filters) -> List[MemoryItem]:
        """Retrieve memories matching the query and filters."""
        # For short-term memory, we just return the most recent memories
        # In a more sophisticated implementation, we might do semantic search
        all_items = list(self._memories.values())
        
        # Apply filters
        if filters:
            filtered_items = []
            for item in all_items:
                match = all(
                    item.metadata.get(k) == v
                    for k, v in filters.items()
                )
                if match:
                    filtered_items.append(item)
            all_items = filtered_items
        
        # Sort by timestamp (newest first)
        all_items.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        return all_items[:limit]
    
    async def update(self, memory_id: str, content: Optional[Any] = None, **updates) -> bool:
        """Update a memory."""
        if memory_id not in self._memories:
            return False
        
        memory = self._memories[memory_id]
        
        if content is not None:
            memory.content = content
        
        # Update metadata
        if 'metadata' in updates:
            memory.metadata.update(updates['metadata'])
        else:
            memory.metadata.update(updates)
        
        return True
    
    async def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        if memory_id in self._memories:
            del self._memories[memory_id]
            return True
        return False


class LongTermMemory(Memory):
    """
    Long-term memory for agents.
    
    This implementation uses a file-based storage system to persist
    memories between sessions. It's suitable for storing important
    information that needs to be retained long-term.
    """
    
    def __init__(self, storage_path: str = "long_term_memory.json"):
        """
        Initialize the long-term memory.
        
        Args:
            storage_path: Path to the file where memories will be stored
        """
        self.storage_path = storage_path
        self._memories: Dict[str, Dict[str, Any]] = {}
        self._counter = 0
        self._load()
    
    def _load(self) -> None:
        """Load memories from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self._memories = data.get('memories', {})
                self._counter = data.get('counter', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            # File doesn't exist or is invalid, start with empty memory
            self._memories = {}
            self._counter = 0
    
    def _save(self) -> None:
        """Save memories to storage."""
        data = {
            'memories': {
                k: v.to_dict() if hasattr(v, 'to_dict') else v
                for k, v in self._memories.items()
            },
            'counter': self._counter
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def store(self, content: Any, **metadata) -> str:
        """Store a memory."""
        # Generate a unique ID
        memory_id = f"ltm_{self._counter}"
        self._counter += 1
        
        # Create and store the memory
        memory_item = MemoryItem(
            content=content,
            metadata=metadata
        )
        
        self._memories[memory_id] = memory_item.to_dict()
        self._save()
        
        return memory_id
    
    async def retrieve(self, query: Optional[Any] = None, limit: int = 10, **filters) -> List[MemoryItem]:
        """Retrieve memories matching the query and filters."""
        # Convert stored dicts back to MemoryItem objects
        all_items = [
            MemoryItem.from_dict(item_data)
            for item_data in self._memories.values()
        ]
        
        # Apply filters
        if filters:
            filtered_items = []
            for item in all_items:
                match = all(
                    item.metadata.get(k) == v
                    for k, v in filters.items()
                )
                if match:
                    filtered_items.append(item)
            all_items = filtered_items
        
        # Sort by importance and then by timestamp (most recent first)
        all_items.sort(key=lambda x: (-x.importance, -x.timestamp))
        
        # Apply limit
        return all_items[:limit]
    
    async def update(self, memory_id: str, content: Optional[Any] = None, **updates) -> bool:
        """Update a memory."""
        if memory_id not in self._memories:
            return False
        
        # Get the existing memory
        memory_data = self._memories[memory_id]
        memory = MemoryItem.from_dict(memory_data)
        
        # Update fields
        if content is not None:
            memory.content = content
        
        # Update metadata
        if 'metadata' in updates:
            memory.metadata.update(updates['metadata'])
        else:
            memory.metadata.update(updates)
        
        # Save back to storage
        self._memories[memory_id] = memory.to_dict()
        self._save()
        
        return True
    
    async def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        if memory_id in self._memories:
            del self._memories[memory_id]
            self._save()
            return True
        return False
