"""
Model Orchestrator for Agent Zero.
Manages multiple LLM models and provides a unified interface for model selection and usage.
"""

import os
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from enum import Enum
import asyncio
import models
from models import ModelType, ModelProvider
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.language_models.llms import BaseLLM
from python.helpers.call_llm import call_llm


class ModelCapability(Enum):
    """Capabilities that models can have."""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    TRANSLATION = "translation"
    CREATIVE = "creative"
    FACTUAL = "factual"


class ModelProfile:
    """Profile for a model with its capabilities and performance metrics."""
    
    def __init__(
        self,
        provider: ModelProvider,
        model_name: str,
        model_type: ModelType,
        capabilities: List[ModelCapability] = None,
        cost_per_1k_tokens: float = 0.0,
        max_tokens: int = 4096,
        typical_latency_ms: int = 500,
        description: str = "",
    ):
        self.provider = provider
        self.model_name = model_name
        self.model_type = model_type
        self.capabilities = capabilities or []
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.max_tokens = max_tokens
        self.typical_latency_ms = typical_latency_ms
        self.description = description
        self._model_instance = None
        
    def get_model(self, **kwargs) -> Union[BaseChatModel, BaseLLM]:
        """Get or create the model instance."""
        if not self._model_instance:
            self._model_instance = models.get_model(
                self.model_type, 
                self.provider, 
                self.model_name, 
                **kwargs
            )
        return self._model_instance
    
    def has_capability(self, capability: ModelCapability) -> bool:
        """Check if the model has a specific capability."""
        return capability in self.capabilities
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the model profile to a dictionary."""
        return {
            "provider": self.provider.value,
            "model_name": self.model_name,
            "model_type": self.model_type.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "max_tokens": self.max_tokens,
            "typical_latency_ms": self.typical_latency_ms,
            "description": self.description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelProfile":
        """Create a model profile from a dictionary."""
        return cls(
            provider=ModelProvider(data["provider"]),
            model_name=data["model_name"],
            model_type=ModelType(data["model_type"]),
            capabilities=[ModelCapability(cap) for cap in data.get("capabilities", [])],
            cost_per_1k_tokens=data.get("cost_per_1k_tokens", 0.0),
            max_tokens=data.get("max_tokens", 4096),
            typical_latency_ms=data.get("typical_latency_ms", 500),
            description=data.get("description", ""),
        )


class ModelOrchestrator:
    """
    Orchestrates multiple LLM models, providing a unified interface for model selection and usage.
    """
    
    def __init__(self):
        self.models: Dict[str, ModelProfile] = {}
        self.default_model_id: Optional[str] = None
        
    def register_model(self, model_id: str, model_profile: ModelProfile) -> None:
        """Register a model with the orchestrator."""
        self.models[model_id] = model_profile
        if not self.default_model_id:
            self.default_model_id = model_id
            
    def set_default_model(self, model_id: str) -> None:
        """Set the default model."""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not registered")
        self.default_model_id = model_id
        
    def get_model(self, model_id: Optional[str] = None, **kwargs) -> Union[BaseChatModel, BaseLLM]:
        """Get a model by ID or the default model."""
        model_id = model_id or self.default_model_id
        if not model_id or model_id not in self.models:
            raise ValueError(f"Model {model_id} not registered")
        return self.models[model_id].get_model(**kwargs)
    
    def get_model_profile(self, model_id: Optional[str] = None) -> ModelProfile:
        """Get a model profile by ID or the default model profile."""
        model_id = model_id or self.default_model_id
        if not model_id or model_id not in self.models:
            raise ValueError(f"Model {model_id} not registered")
        return self.models[model_id]
    
    def find_models_with_capability(self, capability: ModelCapability) -> List[Tuple[str, ModelProfile]]:
        """Find all models with a specific capability."""
        return [(model_id, profile) for model_id, profile in self.models.items() 
                if profile.has_capability(capability)]
    
    def find_best_model_for_capability(
        self, 
        capability: ModelCapability,
        prefer_low_cost: bool = False,
        prefer_low_latency: bool = False,
    ) -> Optional[Tuple[str, ModelProfile]]:
        """Find the best model for a specific capability based on preferences."""
        models_with_capability = self.find_models_with_capability(capability)
        if not models_with_capability:
            return None
        
        if prefer_low_cost:
            return min(models_with_capability, key=lambda x: x[1].cost_per_1k_tokens)
        elif prefer_low_latency:
            return min(models_with_capability, key=lambda x: x[1].typical_latency_ms)
        
        # Default to the first model with the capability
        return models_with_capability[0]
    
    async def call_model(
        self,
        system: str,
        message: str,
        model_id: Optional[str] = None,
        examples: List[Dict[str, str]] = None,
        callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> str:
        """Call a model with a system prompt and message."""
        model = self.get_model(model_id, **kwargs)
        examples = examples or []
        return await call_llm(system, model, message, examples, callback)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models."""
        return [
            {"id": model_id, **profile.to_dict()}
            for model_id, profile in self.models.items()
        ]
    
    def save_to_file(self, filepath: str) -> None:
        """Save the model registry to a file."""
        import json
        with open(filepath, "w") as f:
            json.dump({
                "default_model_id": self.default_model_id,
                "models": {
                    model_id: profile.to_dict()
                    for model_id, profile in self.models.items()
                }
            }, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "ModelOrchestrator":
        """Load a model registry from a file."""
        import json
        orchestrator = cls()
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                for model_id, model_data in data.get("models", {}).items():
                    orchestrator.register_model(
                        model_id, ModelProfile.from_dict(model_data)
                    )
                default_model_id = data.get("default_model_id")
                if default_model_id and default_model_id in orchestrator.models:
                    orchestrator.default_model_id = default_model_id
        return orchestrator