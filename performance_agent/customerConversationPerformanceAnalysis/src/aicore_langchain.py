"""
LangChain integration for SAP AI Core
This module provides LangChain-compatible LLM wrapper for AI Core services
"""

import logging
from typing import Any, Dict, List, Optional, Iterator
from langchain.llms.base import LLM
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.chat_models.base import BaseChatModel
from langchain.schema.messages import BaseMessage
from langchain.schema.output import ChatResult, ChatGeneration
from pydantic import Field

try:
    from .aicore_service import get_aicore_client, AICoreClient
except ImportError:
    # Fallback for direct execution
    from aicore_service import get_aicore_client, AICoreClient


class AICoreChat(BaseChatModel):
    """LangChain chat model wrapper for SAP AI Core"""
    
    client: Optional[AICoreClient] = Field(default=None, exclude=True)
    model_name: str = Field(default="gpt-4")
    temperature: float = Field(default=0.1)
    max_tokens: int = Field(default=4000)
    credentials_path: Optional[str] = Field(default=None)
    
    def __init__(self, **kwargs):
        """Initialize the AI Core chat model"""
        super().__init__(**kwargs)
        
        # Initialize AI Core client
        if not self.client:
            try:
                self.client = get_aicore_client(self.credentials_path)
                # Use module-level logger instead of instance attribute
                logger = logging.getLogger(__name__)
                logger.info("Successfully initialized AI Core client for LangChain")
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to initialize AI Core client: {e}")
                raise
    
    def _get_logger(self):
        """Get logger instance"""
        return logging.getLogger(__name__)
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM"""
        return "aicore-chat"
    
    def _convert_messages_to_aicore_format(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """
        Convert LangChain messages to AI Core format
        
        Args:
            messages: List of LangChain BaseMessage objects
            
        Returns:
            List of message dictionaries for AI Core API
        """
        aicore_messages = []
        system_content = None
        
        # First pass: extract system message content
        for message in messages:
            if isinstance(message, SystemMessage):
                system_content = message.content
                break
        
        # Second pass: convert messages, handling system messages specially
        for message in messages:
            if isinstance(message, HumanMessage):
                role = "user"
                content = message.content
                
                # If this is the first user message and we have system content,
                # prepend the system content to this message
                if system_content and len(aicore_messages) == 0:
                    content = f"{system_content}\n\n{content}"
                    system_content = None  # Only add it once
                
            elif isinstance(message, AIMessage):
                role = "assistant"
                content = message.content
            elif isinstance(message, SystemMessage):
                # Skip system messages as we handle them above
                continue
            else:
                # Default to user for unknown message types
                role = "user"
                content = message.content
            
            aicore_messages.append({
                "role": role,
                "content": content
            })
        
        # If we still have system content but no user messages, create a user message
        if system_content and not aicore_messages:
            aicore_messages.append({
                "role": "user",
                "content": system_content
            })
        
        return aicore_messages
    
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        """
        Generate chat completion using AI Core
        
        Args:
            messages: List of messages in the conversation
            stop: List of stop sequences (optional)
            **kwargs: Additional arguments
            
        Returns:
            ChatResult with generated response
        """
        try:
            # Convert messages to AI Core format
            aicore_messages = self._convert_messages_to_aicore_format(messages)
            
            # Extract parameters with fallbacks
            model = kwargs.get('model', self.model_name)
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            
            self._get_logger().debug(f"Generating chat completion with AI Core - Model: {model}, Temperature: {temperature}")
            
            # Make API call to AI Core
            response = self.client.chat_completion(
                messages=aicore_messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract the generated content
            # Note: Adjust this based on actual AI Core response format
            if 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0]['message']['content']
            else:
                # Fallback for different response formats
                content = response.get('content', response.get('text', ''))
            
            # Create ChatGeneration object
            message = AIMessage(content=content)
            generation = ChatGeneration(message=message)
            
            # Return ChatResult
            return ChatResult(generations=[generation])
            
        except Exception as e:
            self._get_logger().error(f"Error generating chat completion with AI Core: {e}")
            # Return an error message instead of failing completely
            error_message = AIMessage(content=f"Error: Unable to generate response - {str(e)}")
            error_generation = ChatGeneration(message=error_message)
            return ChatResult(generations=[error_generation])
    
    async def _agenerate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        """
        Async version of generate (currently just calls sync version)
        
        Args:
            messages: List of messages in the conversation
            stop: List of stop sequences (optional)
            **kwargs: Additional arguments
            
        Returns:
            ChatResult with generated response
        """
        # For now, just call the sync version
        # In the future, this could be implemented with async HTTP requests
        return self._generate(messages, stop, **kwargs)
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from AI Core
        
        Returns:
            List of available models
        """
        try:
            return self.client.get_available_models()
        except Exception as e:
            self._get_logger().error(f"Failed to get available models: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check
        
        Returns:
            Health status dictionary
        """
        try:
            return self.client.health_check()
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "unknown"
            }


class AICoreSimpleLLM(LLM):
    """Simple LLM wrapper for AI Core (for basic text completion)"""
    
    client: Optional[AICoreClient] = Field(default=None, exclude=True)
    model_name: str = Field(default="gpt-4")
    temperature: float = Field(default=0.1)
    max_tokens: int = Field(default=4000)
    credentials_path: Optional[str] = Field(default=None)
    
    def __init__(self, **kwargs):
        """Initialize the AI Core simple LLM"""
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI Core client
        if not self.client:
            try:
                self.client = get_aicore_client(self.credentials_path)
                self.logger.info("Successfully initialized AI Core client for simple LLM")
            except Exception as e:
                self.logger.error(f"Failed to initialize AI Core client: {e}")
                raise
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM"""
        return "aicore-simple"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        """
        Call the LLM with a prompt
        
        Args:
            prompt: Input prompt
            stop: List of stop sequences (optional)
            **kwargs: Additional arguments
            
        Returns:
            Generated text response
        """
        try:
            # Convert prompt to chat format
            messages = [{"role": "user", "content": prompt}]
            
            # Extract parameters with fallbacks
            model = kwargs.get('model', self.model_name)
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            
            self.logger.debug(f"Calling AI Core simple LLM - Model: {model}, Temperature: {temperature}")
            
            # Make API call to AI Core
            response = self.client.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract the generated content
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content']
            else:
                # Fallback for different response formats
                return response.get('content', response.get('text', ''))
            
        except Exception as e:
            self.logger.error(f"Error calling AI Core simple LLM: {e}")
            return f"Error: Unable to generate response - {str(e)}"


# Factory functions for easy instantiation
def create_aicore_chat_model(model_name: str = "gpt-4", 
                            temperature: float = 0.1,
                            max_tokens: int = 4000,
                            credentials_path: Optional[str] = None) -> AICoreChat:
    """
    Factory function to create AI Core chat model
    
    Args:
        model_name: Name of the model to use
        temperature: Temperature setting
        max_tokens: Maximum tokens to generate
        credentials_path: Path to credentials file (optional)
        
    Returns:
        AICoreChat instance
    """
    return AICoreChat(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        credentials_path=credentials_path
    )


def create_aicore_simple_llm(model_name: str = "gpt-4",
                            temperature: float = 0.1,
                            max_tokens: int = 4000,
                            credentials_path: Optional[str] = None) -> AICoreSimpleLLM:
    """
    Factory function to create AI Core simple LLM
    
    Args:
        model_name: Name of the model to use
        temperature: Temperature setting
        max_tokens: Maximum tokens to generate
        credentials_path: Path to credentials file (optional)
        
    Returns:
        AICoreSimpleLLM instance
    """
    return AICoreSimpleLLM(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        credentials_path=credentials_path
    )


# Convenience function to get the appropriate LLM based on use case
def get_aicore_llm(llm_type: str = "chat", **kwargs) -> Any:
    """
    Get AI Core LLM instance based on type
    
    Args:
        llm_type: Type of LLM ("chat" or "simple")
        **kwargs: Additional arguments for LLM initialization
        
    Returns:
        AI Core LLM instance
    """
    if llm_type.lower() == "chat":
        return create_aicore_chat_model(**kwargs)
    elif llm_type.lower() == "simple":
        return create_aicore_simple_llm(**kwargs)
    else:
        raise ValueError(f"Unknown LLM type: {llm_type}. Use 'chat' or 'simple'.")
