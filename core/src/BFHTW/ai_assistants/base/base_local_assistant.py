from typing import TypeVar, Generic, Type
from pydantic import BaseModel
from transformers.pipelines import pipeline

AnyResponseModel = TypeVar('AnyResponseModel', bound=BaseModel)

class BaseLocalAssistant(Generic[AnyResponseModel]):
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
            raise NotImplementedError("Subclasses must implement how to convert raw output into response_model")
