"""
Knowledge module for the Agentic Framework.

This module defines the knowledge management system used by agents to
store, retrieve, and reason about information.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import json
from datetime import datetime


class KnowledgeType(Enum):
    """Types of knowledge that can be stored."""
    FACT = "fact"
    RULE = "rule"
    PROCEDURE = "procedure"
    CONCEPT = "concept"
    RELATIONSHIP = "relationship"


@dataclass
class KnowledgeItem:
    """Represents a single piece of knowledge."""
    id: str
    content: Any
    knowledge_type: KnowledgeType
    source: str = "system"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0  # 0.0 to 1.0
    tags: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the knowledge item to a dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "knowledge_type": self.knowledge_type.value,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "confidence": self.confidence,
            "tags": list(self.tags)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeItem':
        """Create a knowledge item from a dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            knowledge_type=KnowledgeType(data["knowledge_type"]),
            source=data.get("source", "system"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.utcnow().isoformat())),
            metadata=data.get("metadata", {}),
            confidence=data.get("confidence", 1.0),
            tags=set(data.get("tags", []))
        )


class KnowledgeBase(ABC):
    """
    Abstract base class for knowledge bases.
    
    Knowledge bases store and retrieve structured knowledge that agents
    can use for reasoning and decision-making.
    """
    
    @abstractmethod
    async def add(self, item: KnowledgeItem) -> bool:
        """
        Add a knowledge item to the knowledge base.
        
        Args:
            item: The knowledge item to add
            
        Returns:
            True if the item was added successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get(self, item_id: str) -> Optional[KnowledgeItem]:
        """
        Retrieve a knowledge item by ID.
        
        Args:
            item_id: The ID of the item to retrieve
            
        Returns:
            The knowledge item, or None if not found
        """
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10, **filters) -> List[KnowledgeItem]:
        """
        Search for knowledge items matching the query and filters.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            **filters: Additional filters to apply
            
        Returns:
            List of matching knowledge items, ordered by relevance
        """
        pass
    
    @abstractmethod
    async def update(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a knowledge item.
        
        Args:
            item_id: The ID of the item to update
            updates: Dictionary of fields to update
            
        Returns:
            True if the update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        """
        Delete a knowledge item.
        
        Args:
            item_id: The ID of the item to delete
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def relate(self, source_id: str, target_id: str, relation_type: str, **properties) -> bool:
        """
        Create a relationship between two knowledge items.
        
        Args:
            source_id: ID of the source item
            target_id: ID of the target item
            relation_type: Type of relationship
            **properties: Additional properties of the relationship
            
        Returns:
            True if the relationship was created successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_related(self, item_id: str, relation_type: Optional[str] = None) -> List[Tuple[KnowledgeItem, str, Dict]]:
        """
        Get items related to a given item.
        
        Args:
            item_id: ID of the source item
            relation_type: Optional filter for relation type
            
        Returns:
            List of tuples containing (related_item, relation_type, properties)
        """
        pass


class InMemoryKnowledgeBase(KnowledgeBase):
    """
    In-memory implementation of a knowledge base.
    
    This implementation stores all knowledge in memory and is suitable
    for testing and small-scale applications. For production use, consider
    using a persistent storage backend.
    """
    
    def __init__(self):
        """Initialize the in-memory knowledge base."""
        self._items: Dict[str, KnowledgeItem] = {}
        self._relations: Dict[Tuple[str, str, str], Dict] = {}
    
    async def add(self, item: KnowledgeItem) -> bool:
        """Add a knowledge item to the knowledge base."""
        if item.id in self._items:
            return False
        
        self._items[item.id] = item
        return True
    
    async def get(self, item_id: str) -> Optional[KnowledgeItem]:
        """Retrieve a knowledge item by ID."""
        return self._items.get(item_id)
    
    async def search(self, query: str, limit: int = 10, **filters) -> List[KnowledgeItem]:
        """
        Search for knowledge items.
        
        Note: This is a simple implementation that only supports exact matches.
        A production implementation would use a proper search engine.
        """
        results = []
        
        for item in self._items.values():
            # Check if item matches all filters
            matches = True
            for key, value in filters.items():
                if key == 'knowledge_type':
                    if item.knowledge_type != value:
                        matches = False
                        break
                elif key == 'tag':
                    if value not in item.tags:
                        matches = False
                        break
                elif hasattr(item, key):
                    if getattr(item, key) != value:
                        matches = False
                        break
                elif key in item.metadata:
                    if item.metadata[key] != value:
                        matches = False
                        break
                    
            if matches:
                results.append(item)
        
        # Simple relevance sorting (in a real implementation, this would use the query)
        results.sort(key=lambda x: x.confidence, reverse=True)
        
        return results[:limit]
    
    async def update(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """Update a knowledge item."""
        if item_id not in self._items:
            return False
        
        item = self._items[item_id]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(item, key):
                setattr(item, key, value)
            else:
                item.metadata[key] = value
        
        # Update timestamp
        item.updated_at = datetime.utcnow()
        
        return True
    
    async def delete(self, item_id: str) -> bool:
        """Delete a knowledge item."""
        if item_id not in self._items:
            return False
        
        # Remove the item
        del self._items[item_id]
        
        # Remove any relationships involving this item
        self._relations = {
            (s, t, r): props
            for (s, t, r), props in self._relations.items()
            if s != item_id and t != item_id
        }
        
        return True
    
    async def relate(self, source_id: str, target_id: str, relation_type: str, **properties) -> bool:
        """Create a relationship between two knowledge items."""
        if source_id not in self._items or target_id not in self._items:
            return False
        
        key = (source_id, target_id, relation_type)
        self._relations[key] = properties
        return True
    
    async def get_related(self, item_id: str, relation_type: Optional[str] = None) -> List[Tuple[KnowledgeItem, str, Dict]]:
        """Get items related to a given item."""
        if item_id not in self._items:
            return []
        
        results = []
        
        for (source_id, target_id, rel_type), props in self._relations.items():
            if source_id == item_id and (relation_type is None or rel_type == relation_type):
                target = self._items.get(target_id)
                if target:
                    results.append((target, rel_type, props))
            
            # For bidirectional relationships, we could also check target_id == item_id
            # if the relationship is bidirectional
        
        return results


class KnowledgeManager:
    """
    Manages multiple knowledge bases and provides a unified interface.
    """
    
    def __init__(self):
        """Initialize the knowledge manager."""
        self._knowledge_bases: Dict[str, KnowledgeBase] = {}
        self._default_kb: Optional[KnowledgeBase] = None
    
    def add_knowledge_base(self, name: str, kb: KnowledgeBase, set_as_default: bool = False) -> None:
        """
        Add a knowledge base to the manager.
        
        Args:
            name: Name to identify the knowledge base
            kb: The knowledge base instance
            set_as_default: Whether to set this as the default knowledge base
        """
        self._knowledge_bases[name] = kb
        if set_as_default or self._default_kb is None:
            self._default_kb = kb
    
    def get_knowledge_base(self, name: Optional[str] = None) -> Optional[KnowledgeBase]:
        """
        Get a knowledge base by name.
        
        Args:
            name: Name of the knowledge base, or None for the default
            
        Returns:
            The knowledge base, or None if not found
        """
        if name is None:
            return self._default_kb
        return self._knowledge_bases.get(name)
    
    def set_default_knowledge_base(self, name: str) -> bool:
        """
        Set the default knowledge base.
        
        Args:
            name: Name of the knowledge base to set as default
            
        Returns:
            True if successful, False if the knowledge base doesn't exist
        """
        if name not in self._knowledge_bases:
            return False
        
        self._default_kb = self._knowledge_bases[name]
        return True
    
    async def add(self, item: KnowledgeItem, kb_name: Optional[str] = None) -> bool:
        """Add a knowledge item to the specified knowledge base."""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            return False
        return await kb.add(item)
    
    async def get(self, item_id: str, kb_name: Optional[str] = None) -> Optional[KnowledgeItem]:
        """Retrieve a knowledge item by ID from the specified knowledge base."""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            return None
        return await kb.get(item_id)
    
    async def search(self, query: str, limit: int = 10, kb_name: Optional[str] = None, **filters) -> List[KnowledgeItem]:
        """Search for knowledge items in the specified knowledge base."""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            return []
        return await kb.search(query, limit=limit, **filters)
    
    async def update(self, item_id: str, updates: Dict[str, Any], kb_name: Optional[str] = None) -> bool:
        """Update a knowledge item in the specified knowledge base."""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            return False
        return await kb.update(item_id, updates)
    
    async def delete(self, item_id: str, kb_name: Optional[str] = None) -> bool:
        """Delete a knowledge item from the specified knowledge base."""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            return False
        return await kb.delete(item_id)
    
    async def relate(self, source_id: str, target_id: str, relation_type: str, 
                    kb_name: Optional[str] = None, **properties) -> bool:
        """Create a relationship between two knowledge items in the specified knowledge base."""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            return False
        return await kb.relate(source_id, target_id, relation_type, **properties)
    
    async def get_related(self, item_id: str, relation_type: Optional[str] = None, 
                         kb_name: Optional[str] = None) -> List[Tuple[KnowledgeItem, str, Dict]]:
        """Get items related to a given item in the specified knowledge base."""
        kb = self.get_knowledge_base(kb_name)
        if kb is None:
            return []
        return await kb.get_related(item_id, relation_type=relation_type)
