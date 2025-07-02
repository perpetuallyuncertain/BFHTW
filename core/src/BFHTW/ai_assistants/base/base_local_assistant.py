"""
Module: base_local_assistant.py
Purpose: Defines a base contract for creating local AI assistants using Hugging Face pipelines.
          This abstract class facilitates integration of various pipeline types with a standard
          response model interface for structured output.

Classes:
    BaseLocalAssistant: Generic class that wraps Hugging Face pipelines and enforces a contract
                        for converting raw output into a Pydantic response model.
"""

from typing import TypeVar, Generic, Type
from pydantic import BaseModel
from transformers import pipeline

AnyResponseModel = TypeVar('AnyResponseModel', bound=BaseModel)

class BaseLocalAssistant(Generic[AnyResponseModel]):
    """
    A base class for local AI assistants built on Hugging Face pipelines.
    Enforces a standard contract for model execution and response conversion.

    Args:
        name (str): Unique identifier or label for the assistant instance.
        model_name (str): Name or path of the Hugging Face model to load.
        pipeline_type (str): Type of Hugging Face pipeline to use (e.g., 'text-generation').
        response_model (Type[BaseModel]): A Pydantic model to standardize the assistant's output.
        **pipeline_kwargs: Additional keyword arguments to pass to the Hugging Face pipeline.

    Attributes:
        name (str): Name of the assistant.
        model_name (str): The Hugging Face model name or path.
        response_model (Type[BaseModel]): Class for output structure.
        pipe: Hugging Face pipeline instance initialized with the given model.

    Methods:
        run(text: str, **kwargs) -> BaseModel:
            Abstract method. Must be implemented by subclasses to run the pipeline and return
            a structured response using the specified response_model.
    """

    def __init__(
        self,
        name: str,
        model_name: str,
        pipeline_type: str,
        response_model: Type[AnyResponseModel],
        **pipeline_kwargs
    ):
        self.name = name
        self.model_name = model_name
        self.response_model = response_model
        self.pipe = pipeline(pipeline_type, model=model_name, **pipeline_kwargs)

    def run(self, text: str, **kwargs) -> AnyResponseModel:
        """
        Run the assistant pipeline and return a structured response.

        This method must be overridden in subclasses to define how the raw model output
        is transformed into the response_model format.

        Args:
            text (str): Input prompt to pass to the model.
            **kwargs: Optional keyword arguments passed to the pipeline call.

        Returns:
            AnyResponseModel: Parsed model output.

        Raises:
            NotImplementedError: Always, unless overridden in a subclass.
        """
        raise NotImplementedError("Subclasses must implement how to convert raw output into response_model")
