'''
Example script for making a simple chat completion request to the LLM Gateway.
'''

import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI client to point to the local gateway
client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key=os.getenv("API_KEYS", "").split(",")[0]  # Use the first API key from .env
)

def simple_chat_example():
    '''
    Demonstrates a basic chat completion call.
    '''
    print("--- Simple Chat Completion Example ---")

    try:
        response = client.chat.completions.create(
            model="llama-7b",  # Or "gpt-4-mini", "gemini-flash"
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise answers."},
                {"role": "user", "content": "What is the primary function of a CPU in a computer?"}
            ],
            max_tokens=150,
            temperature=0.7
        )

        print("Model Response:")
        print(response.choices[0].message.content)

        print("\nUsage Stats:")
        print(f"  Prompt Tokens: {response.usage.prompt_tokens}")
        print(f"  Completion Tokens: {response.usage.completion_tokens}")
        print(f"  Total Tokens: {response.usage.total_tokens}")

    except openai.APIError as e:
        print(f"An API error occurred: {e}")

if __name__ == "__main__":
    simple_chat_example()
