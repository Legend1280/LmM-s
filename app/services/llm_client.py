"""
LLM client service for communicating with different model backends.
Supports OpenAI and OpenAI-compatible APIs.
"""

import time
import uuid
from typing import Dict, Any, List, Optional
from openai import OpenAI, AsyncOpenAI
from app.models.schemas import Message, ChatCompletionResponse, ChatChoice, UsageInfo
from app.config import model_registry, settings


class LLMClient:
    """Client for interacting with LLM backends."""
    
    def __init__(self):
        self.clients: Dict[str, AsyncOpenAI] = {}
    
    def _get_client(self, model_id: str) -> AsyncOpenAI:
        """Get or create an OpenAI client for the specified model."""
        if model_id in self.clients:
            return self.clients[model_id]
        
        model_config = model_registry.get_model(model_id)
        if not model_config:
            raise ValueError(f"Unknown model: {model_id}")
        
        backend_type = model_config.get('backend_type', 'openai_compatible')
        base_url = model_config.get('base_url')
        
        # Determine API key based on backend type
        if backend_type == 'openai':
            api_key = settings.openai_api_key or "dummy-key"
        else:
            # For OpenAI-compatible backends, use a dummy key if not specified
            api_key = "dummy-key"
        
        # Create async client
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None,
            timeout=model_config.get('timeout', 60.0)
        )
        
        self.clients[model_id] = client
        return client
    
    async def chat_completion(
        self,
        model_id: str,
        messages: List[Message],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stream: bool = False
    ) -> ChatCompletionResponse:
        """
        Execute a chat completion request.
        
        Args:
            model_id: Logical model identifier
            messages: List of conversation messages
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            stream: Whether to stream the response
            
        Returns:
            ChatCompletionResponse with the model's output
        """
        model_config = model_registry.get_model(model_id)
        if not model_config:
            raise ValueError(f"Unknown model: {model_id}")
        
        client = self._get_client(model_id)
        backend_model_name = model_config['model_name']
        
        # Convert messages to dict format
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        # Call the model
        start_time = time.time()
        
        try:
            response = await client.chat.completions.create(
                model=backend_model_name,
                messages=messages_dict,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=stream
            )
            
            # Convert response to our schema
            completion_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
            created_at = int(start_time)
            
            choice = ChatChoice(
                index=0,
                message=Message(
                    role="assistant",
                    content=response.choices[0].message.content or ""
                ),
                finish_reason=response.choices[0].finish_reason
            )
            
            usage = UsageInfo(
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0
            )
            
            return ChatCompletionResponse(
                id=completion_id,
                model=model_id,
                created=created_at,
                choices=[choice],
                usage=usage
            )
            
        except Exception as e:
            raise RuntimeError(f"Error calling model {model_id}: {str(e)}")
    
    async def batch_chat_completion(
        self,
        model_id: str,
        tasks: List[Dict[str, Any]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple chat completion requests.
        
        Args:
            model_id: Logical model identifier
            tasks: List of tasks, each with 'id' and 'messages'
            max_tokens: Maximum tokens per task
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            
        Returns:
            List of results, each with 'id', 'output', 'usage', and optional 'error'
        """
        results = []
        
        for task in tasks:
            task_id = task['id']
            messages = task['messages']
            
            try:
                response = await self.chat_completion(
                    model_id=model_id,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p
                )
                
                results.append({
                    'id': task_id,
                    'output': response.choices[0].message.content,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    'error': None
                })
                
            except Exception as e:
                results.append({
                    'id': task_id,
                    'output': '',
                    'usage': {
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'total_tokens': 0
                    },
                    'error': str(e)
                })
        
        return results


# Global client instance
llm_client = LLMClient()
