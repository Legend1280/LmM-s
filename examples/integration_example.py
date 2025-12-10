'''
Example showing how to integrate the LLM Gateway into your existing applications.
This demonstrates creating a reusable LLM client class.
'''

import os
import openai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMGatewayClient:
    '''
    A reusable client for interacting with the LLM Gateway.
    This class can be integrated into your existing applications.
    '''

    def __init__(self, base_url: str = "http://localhost:8000/v1", api_key: Optional[str] = None):
        '''
        Initialize the LLM Gateway client.

        Args:
            base_url: The base URL of the LLM Gateway API
            api_key: Your API key for authentication
        '''
        self.base_url = base_url
        self.api_key = api_key or os.getenv("API_KEYS", "").split(",")[0]

        # Configure OpenAI client
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-7b",
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        '''
        Send a chat completion request.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use ('llama-7b', 'gpt-4-mini', 'gemini-flash')
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            The model's response as a string
        '''
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content

        except openai.APIError as e:
            raise RuntimeError(f"LLM Gateway API error: {e}")

    def ask(self, question: str, system_prompt: Optional[str] = None, model: str = "llama-7b") -> str:
        '''
        Ask a simple question to the LLM.

        Args:
            question: The question to ask
            system_prompt: Optional system prompt to set context
            model: Model to use

        Returns:
            The model's response
        '''
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": question})

        return self.chat(messages, model=model)

    def summarize(self, text: str, max_length: int = 200, model: str = "llama-7b") -> str:
        '''
        Summarize a piece of text.

        Args:
            text: The text to summarize
            max_length: Maximum length of the summary in words
            model: Model to use

        Returns:
            The summary
        '''
        system_prompt = f"You are a helpful assistant that summarizes text concisely. Limit your summary to approximately {max_length} words."
        user_prompt = f"Please summarize the following text:\n\n{text}"

        return self.ask(user_prompt, system_prompt=system_prompt, model=model)

    def extract_entities(self, text: str, entity_types: List[str], model: str = "llama-7b") -> str:
        '''
        Extract named entities from text.

        Args:
            text: The text to analyze
            entity_types: List of entity types to extract (e.g., ['person', 'organization', 'location'])
            model: Model to use

        Returns:
            Extracted entities as formatted text
        '''
        entity_list = ", ".join(entity_types)
        system_prompt = f"You are a helpful assistant that extracts named entities from text. Extract the following types: {entity_list}."
        user_prompt = f"Extract entities from this text:\n\n{text}"

        return self.ask(user_prompt, system_prompt=system_prompt, model=model)


# Example usage
def main():
    '''
    Demonstrate how to use the LLMGatewayClient in your application.
    '''
    print("--- LLM Gateway Integration Example ---\n")

    # Initialize the client
    client = LLMGatewayClient()

    # Example 1: Simple question
    print("Example 1: Simple Question")
    response = client.ask("What are the benefits of using a unified LLM API?")
    print(f"Response: {response}\n")

    # Example 2: Summarization
    print("Example 2: Text Summarization")
    long_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural
    intelligence displayed by humans and animals. Leading AI textbooks define the field as the study of
    "intelligent agents": any device that perceives its environment and takes actions that maximize its
    chance of successfully achieving its goals. Colloquially, the term "artificial intelligence" is often
    used to describe machines (or computers) that mimic "cognitive" functions that humans associate with
    the human mind, such as "learning" and "problem solving".
    """
    summary = client.summarize(long_text, max_length=50)
    print(f"Summary: {summary}\n")

    # Example 3: Entity extraction
    print("Example 3: Entity Extraction")
    text_with_entities = "Apple Inc. was founded by Steve Jobs in Cupertino, California in 1976."
    entities = client.extract_entities(text_with_entities, ["person", "organization", "location", "date"])
    print(f"Entities: {entities}\n")


if __name__ == "__main__":
    main()
