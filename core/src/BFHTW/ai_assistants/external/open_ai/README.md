# OpenAI RAG Assistant

This repository contains a Python implementation of an OpenAI-based assistant that utilizes various APIs to provide functionalities like news retrieval and web search. The assistant is designed to handle structured and unstructured requests while managing responses and function calls effectively.

## Contents

- **openai_rag_assistant.py**: The main file that defines the assistant's functionality, including event handling, function execution, and interaction with the OpenAI API.
- **openai_assistant.py**: This file contains the OpenAI-specific assistant class, which manages API requests, error handling, and response parsing.
- **core_utils.py**: A utility module (not provided in the snippet) likely containing helper functions and classes, such as `EnvManager` for managing environment variables.

## Structure

### EventHandler Class
- **Purpose**: Handles events from the OpenAI assistant, such as text responses and function calls.
- **Methods**:
  - `on_text_delta`: Streams text responses from the assistant.
  - `on_tool_call_created`: Manages function calls initiated by the assistant.
  - `on_run_step_delta`: Handles run step events related to message creation.

### Functions Class
- **Purpose**: Contains utility functions for fetching news and performing web searches.
- **Methods**:
  - `get_news`: Fetches news articles from the NewsAPI based on a specified topic and date range.
  - `web_search`: Conducts a web search using the Bing API, returning summarized results.
  - `research_tools`: Returns a list of research tools for market analysis.

### AssistantManager Class
- **Purpose**: Manages the interaction with the OpenAI assistant, including thread creation, message handling, and function calls.
- **Methods**:
  - `create_thread`: Initializes a new conversation thread.
  - `add_msg_to_thread`: Adds messages to the current thread.
  - `call_function`: Executes a specified function from the function map.
  - `process_message`: Processes and extracts the AI's response.
  - `run_assistant`: Orchestrates the assistant's operations, including waiting for tool calls and processing responses.

### OpenAIAssistant Class
- **Purpose**: Provides an interface for making requests to the OpenAI API, handling structured outputs and API response parsing.
- **Methods**:
  - `submit_completion`: Submits a request to OpenAI and returns a structured output.
  - `estimate_completion_cost`: Estimates the cost of API usage based on token counts.
  - `analyse`: Runs a full analysis cycle, submitting user content and capturing structured outputs.

## Installation

To set up this project, ensure you have Python installed and the required dependencies specified in a `requirements.txt` file (not provided in the snippet). You can install the dependencies using:

```bash
pip install -r requirements.txt
```

Make sure to set up the necessary environment variables for API keys and configurations.

## Usage

To use the assistant, instantiate the `AssistantManager` class and call its methods to create threads, send messages, and handle responses. The assistant can be customized further by modifying the parameters for the OpenAI API calls.

## License

This project is licensed under the MIT License. See the LICENSE file for details.