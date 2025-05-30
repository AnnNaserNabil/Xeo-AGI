"""
Models module for the Xeo Framework.

This module defines the base Model class and ModelRegistry for managing
various AI/ML models used by agents.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic


class ModelType(Enum):
    """Represents different types of models."""
    LLM = auto()  # Large Language Model
    EMBEDDING = auto()
    CLASSIFICATION = auto()
    GENERATION = auto()
    REINFORCEMENT_LEARNING = auto()


@dataclass
class ModelConfig:
    """Configuration for a model."""
    name: str
    model_type: ModelType
    version: str = "1.0.0"
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_resources: Dict[str, Any] = field(default_factory=dict)


class Model(ABC):
    """
    Base class for all models in the framework.
    
    Models are used by agents to perform various tasks such as
    language understanding, generation, decision making, etc.
    """
    
    def __init__(self, config: ModelConfig):
        """
        Initialize the model with the given configuration.
        
        Args:
            config: Configuration for the model
        """
        self.config = config
        self._is_loaded = False
    
    @abstractmethod
    async def load(self) -> None:
        """Load the model and any required resources."""
        pass
    
    @abstractmethod
    async def unload(self) -> None:
        """Unload the model and release any resources."""
        pass
    
    @abstractmethod
    async def predict(self, input_data: Any, **kwargs) -> Any:
        """
        Make a prediction using the model.
        
        Args:
            input_data: Input data for the prediction
            **kwargs: Additional arguments for the prediction
            
        Returns:
            The model's prediction
        """
        pass
    
    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready for inference."""
        return self._is_loaded
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "name": self.config.name,
            "type": self.config.model_type.name,
            "version": self.config.version,
            "description": self.config.description,
            "is_loaded": self._is_loaded,
            "parameters": self.config.parameters
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.config.name}', type={self.config.model_type.name})"


class ModelRegistry:
    """
    Registry for managing models in the framework.
    
    The registry provides a central place to register, retrieve, and manage
    different model implementations.
    """
    
    def __init__(self):
        """Initialize the model registry."""
        self._models: Dict[str, Model] = {}
        self._model_classes: Dict[str, Type[Model]] = {}
    
    def register_model_class(self, model_class: Type[Model], name: Optional[str] = None) -> None:
        """
        Register a model class with the registry.
        
        Args:
            model_class: The model class to register
            name: Optional name to register the class under. If not provided,
                  the class's __name__ will be used.
        """
        name = name or model_class.__name__
        self._model_classes[name] = model_class
    
    def create_model(self, config: ModelConfig, model_class_name: Optional[str] = None) -> Model:
        """
        Create a new model instance.
        
        Args:
            config: Configuration for the model
            model_class_name: Name of the model class to use. If not provided,
                            the model type from config will be used.
                            
        Returns:
            A new model instance
            
        Raises:
            ValueError: If the model class is not found
        """
        if model_class_name is None:
            # Default model class based on model type
            model_class_name = f"{config.model_type.name}Model"
        
        model_class = self._model_classes.get(model_class_name)
        if model_class is None:
            raise ValueError(f"Model class '{model_class_name}' not found in registry.")
        
        return model_class(config)
    
    async def load_model(self, config: ModelConfig) -> Model:
        """
        Create and load a model.
        
        Args:
            config: Configuration for the model
            
        Returns:
            The loaded model instance
        """
        model = self.create_model(config)
        await model.load()
        self._models[config.name] = model
        return model
    
    def get_model(self, name: str) -> Optional[Model]:
        """
        Get a model by name.
        
        Args:
            name: Name of the model to retrieve
            
        Returns:
            The model instance, or None if not found
        """
        return self._models.get(name)
    
    async def unload_model(self, name: str) -> None:
        """
        Unload a model.
        
        Args:
            name: Name of the model to unload
        """
        model = self._models.get(name)
        if model is not None:
            await model.unload()
            del self._models[name]
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered models.
        
        Returns:
            List of model information dictionaries
        """
        return [{"name": name, "class": cls.__name__} 
               for name, cls in self._model_classes.items()]
    
    def list_loaded_models(self) -> List[Dict[str, Any]]:
        """
        Get information about all loaded models.
        
        Returns:
            List of loaded model information dictionaries
        """
        return [{"name": name, "info": model.get_info()} 
               for name, model in self._models.items()]
