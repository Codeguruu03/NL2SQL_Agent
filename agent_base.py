# agent_base.py
"""
Base class for all agents in the multi-agent system.
Provides common functionality for LLM interaction.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from openrouter_client import get_openrouter_client, OpenRouterClient


class Agent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, role: str):
        """
        Initialize agent.
        
        Args:
            name: Agent name (e.g., "SQL Agent")
            role: Agent role description (e.g., "Generates SQL queries")
        """
        self.name = name
        self.role = role
        self.client: OpenRouterClient = get_openrouter_client()
        self.conversation_history: List[Dict[str, str]] = []
    
    @abstractmethod
    def process(self, input_data: Any, **kwargs) -> Any:
        """
        Process input and return output.
        Each agent implements its own logic.
        
        Args:
            input_data: Input data for the agent
            **kwargs: Additional parameters specific to agent
            
        Returns:
            Processed output
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        Defines the agent's behavior and capabilities.
        
        Returns:
            System prompt string
        """
        pass
    
    def call_llm(
        self,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        use_history: bool = False
    ) -> Optional[str]:
        """
        Call LLM with a message.
        
        Args:
            user_message: User message to send
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            use_history: Whether to include conversation history
            
        Returns:
            LLM response or None on failure
        """
        messages = []
        
        # Add system prompt
        system_prompt = self.get_system_prompt()
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history if requested
        if use_history:
            messages.extend(self.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Call LLM
        response = self.client.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Update conversation history
        if response and use_history:
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def reset_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.role})"
