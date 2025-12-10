'''
Example script for submitting a batch generation job to the LLM Gateway.
'''

import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEYS", "").split(",")[0]  # Use the first API key from .env

def submit_batch_job():
    '''
    Submit a batch generation job to the LLM Gateway.
    '''
    print("--- Batch Generation Example ---")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Define batch tasks
    payload = {
        "model": "llama-7b",
        "tasks": [
            {
                "id": "profile-1",
                "messages": [
                    {"role": "system", "content": "Generate synthetic user profiles for testing."},
                    {"role": "user", "content": "Create a realistic fitness client profile with name, age, goals, and experience level."}
                ]
            },
            {
                "id": "profile-2",
                "messages": [
                    {"role": "system", "content": "Generate synthetic user profiles for testing."},
                    {"role": "user", "content": "Create a realistic cardiology patient profile with medical history."}
                ]
            },
            {
                "id": "profile-3",
                "messages": [
                    {"role": "system", "content": "Generate synthetic user profiles for testing."},
                    {"role": "user", "content": "Create a realistic software developer profile with skills and experience."}
                ]
            }
        ],
        "max_tokens": 300,
        "temperature": 0.8,
        "batch_metadata": {
            "project": "synthetic_data_generation",
            "version": "v1"
        }
    }

    # Submit the batch job
    print("Submitting batch job...")
    response = requests.post(f"{BASE_URL}/v1/batch/generate", json=payload, headers=headers)

    if response.status_code != 200:
        print(f"Error submitting batch job: {response.text}")
        return

    job_data = response.json()
    job_id = job_data["job_id"]
    print(f"Batch job submitted successfully!")
    print(f"Job ID: {job_id}")
    print(f"Status: {job_data['status']}")
    print(f"Task Count: {job_data['task_count']}")

    # Poll for job completion
    print("\nPolling for job completion...")
    while True:
        time.sleep(3)  # Wait 3 seconds between checks

        status_response = requests.get(f"{BASE_URL}/v1/batch/{job_id}", headers=headers)

        if status_response.status_code != 200:
            print(f"Error checking job status: {status_response.text}")
            break

        status_data = status_response.json()
        current_status = status_data["status"]
        print(f"Current status: {current_status} (Completed: {status_data['completed_count']}/{status_data['task_count']})")

        if current_status in ["completed", "failed"]:
            break

    # Display results
    if current_status == "completed":
        print("\n--- Batch Results ---")
        for result in status_data["results"]:
            print(f"\nTask ID: {result['id']}")
            print(f"Output:\n{result['output']}")
            print(f"Tokens Used: {result['usage']['total_tokens']}")
            if result.get("error"):
                print(f"Error: {result['error']}")
    else:
        print(f"\nBatch job failed: {status_data.get('error', 'Unknown error')}")

if __name__ == "__main__":
    submit_batch_job()
