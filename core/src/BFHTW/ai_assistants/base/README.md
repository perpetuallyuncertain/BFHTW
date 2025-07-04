# AI Assistant Framework

This repository provides a framework for creating local AI assistants using Hugging Face pipelines. It includes base classes for defining assistants and a factory for instantiating specific models.

## Purpose
The primary goal of this framework is to standardize the development of AI assistants by providing a base structure for integrating various Hugging Face models with a consistent response format using Pydantic models.

## Contents
The folder includes the following main files:

- **base_local_assistant.py**: Defines the `BaseLocalAssistant` class, which serves as a generic wrapper around Hugging Face pipelines. This class enforces a contract for converting raw output into a structured response model.
- **base_assistant.py**: Contains the `BaseAIAssistant` class, which provides common logic for loading system prompts and binding response schemas. This class is intended to be subclassed for specific assistant implementations.
- **factory.py**: Implements a factory function `get_assistant` that creates instances of specific assistant classes based on the model name and task type.

## Structure
The structure of the folder is as follows:

```
/
├── base_local_assistant.py   # Base class for local AI assistants
├── base_assistant.py          # Base class for AI assistant implementations
└── factory.py                 # Factory for creating specific AI assistants
```

## Classes Overview
### `BaseLocalAssistant`
- **Purpose**: Wraps Hugging Face pipelines and enforces a contract for model execution and response conversion.
- **Key Method**: `run(text: str, **kwargs) -> AnyResponseModel`

### `BaseAIAssistant`
- **Purpose**: Provides common logic for loading system prompts and response parsing.
- **Key Methods**:
  - `from_file(name: str, prompt_path: str, response_model: Type[AnyResponseModel])`
  - `safe_load_prompt(search_path: str, raw_prompt_path: str)`
  - `load_default_prompt(search_path: str)`
  - `ensure_sys_content(sys_content: str, search_path: str)`

### Factory Function
- **`get_assistant(model_name: str, task: str)`**: Instantiates the appropriate assistant based on the provided model name.

## Usage
To create a new assistant, subclass either `BaseLocalAssistant` or `BaseAIAssistant` and implement the necessary methods to define the behavior of your assistant. Use the factory function to easily instantiate the desired model based on the task requirements.

## Contribution
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.