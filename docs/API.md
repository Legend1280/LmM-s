> **Note:** This is an automatically generated document. Please do not edit it manually.

# LLM Gateway API Reference

This document provides a detailed reference for the LLM Gateway API. All endpoints are available under the `/v1` prefix.

## Authentication

All API requests must be authenticated using a bearer token in the `Authorization` header.

`Authorization: Bearer <YOUR_API_KEY>`

## Endpoints

### Chat Completions

This endpoint generates a response for a given chat conversation.

`POST /v1/chat/completions`

#### Request Body

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | The ID of the model to use for this request. |
| `messages` | array | Yes | A list of messages comprising the conversation so far. |
| `max_tokens` | integer | No | The maximum number of tokens to generate in the chat completion. |
| `temperature` | number | No | What sampling temperature to use, between 0 and 2. |
| `top_p` | number | No | An alternative to sampling with temperature, called nucleus sampling. |
| `stream` | boolean | No | If set, partial message deltas will be sent, like in ChatGPT. |
| `metadata` | object | No | A JSON object to store any additional information. |

#### Response Body

The response body is an object with the following fields:

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | A unique identifier for the chat completion. |
| `model` | string | The model used for the chat completion. |
| `created` | integer | The Unix timestamp (in seconds) of when the chat completion was created. |
| `choices` | array | A list of chat completion choices. |
| `usage` | object | Usage statistics for the completion request. |

### Batch Generation

This endpoint submits a batch of generation tasks for asynchronous processing.

`POST /v1/batch/generate`

#### Request Body

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | Yes | The ID of the model to use for this request. |
| `tasks` | array | Yes | A list of tasks to be processed in the batch. |
| `max_tokens` | integer | No | The maximum number of tokens to generate in the chat completion. |
| `temperature` | number | No | What sampling temperature to use, between 0 and 2. |
| `top_p` | number | No | An alternative to sampling with temperature, called nucleus sampling. |
| `batch_metadata` | object | No | A JSON object to store any additional information about the batch. |

#### Response Body

The response body is an object with the following fields:

| Field | Type | Description |
| --- | --- | --- |
| `job_id` | string | A unique identifier for the batch job. |
| `status` | string | The status of the batch job. |
| `submitted_at` | integer | The Unix timestamp (in seconds) of when the batch job was submitted. |
| `task_count` | integer | The number of tasks in the batch job. |

### Batch Status

This endpoint retrieves the status of a batch job.

`GET /v1/batch/{job_id}`

#### Path Parameters

| Field | Type | Description |
| --- | --- | --- |
| `job_id` | string | The ID of the batch job. |

#### Response Body

The response body is an object with the following fields:

| Field | Type | Description |
| --- | --- | --- |
| `job_id` | string | A unique identifier for the batch job. |
| `status` | string | The status of the batch job. |
| `submitted_at` | integer | The Unix timestamp (in seconds) of when the batch job was submitted. |
| `started_at` | integer | The Unix timestamp (in seconds) of when the batch job started processing. |
| `completed_at` | integer | The Unix timestamp (in seconds) of when the batch job was completed. |
| `task_count` | integer | The number of tasks in the batch job. |
| `completed_count` | integer | The number of completed tasks in the batch job. |
| `failed_count` | integer | The number of failed tasks in the batch job. |
| `results` | array | A list of results for each task in the batch job. |
| `error` | string | An error message if the batch job failed. |

### Models

This endpoint lists the available models.

`GET /v1/models`

#### Response Body

The response body is an object with the following fields:

| Field | Type | Description |
| --- | --- | --- |
| `models` | array | A list of available models. |

### Health Check

This endpoint checks the health of the service.

`GET /health`

#### Response Body

The response body is an object with the following fields:

| Field | Type | Description |
| --- | --- | --- |
| `status` | string | The status of the service. |
| `service` | string | The name of the service. |
| `version` | string | The version of the service. |
| `timestamp` | integer | The Unix timestamp (in seconds) of when the health check was performed. |
