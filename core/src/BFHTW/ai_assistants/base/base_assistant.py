'''
Base class for creating AI assistant implementations.

Provides common logic for loading system prompts and binding response schemas.
Intended to be subclassed by specific assistant implementations.
'''

import os
from pydantic import BaseModel
from typing import TypeVar, Generic, Type, Optional

from BFHTW.utils.logs import get_logger
L = get_logger()

# Declare a TypeVar for any ResponseModel that's a subclass of BaseModel
# Then we can support typing but allow the schema to be provided at runtime
AnyResponseModel = TypeVar('AnyResponseModel', bound=BaseModel)

# This is the default filename for the system content
DEFAULT_PROMPT_FILENAME = 'system_prompt.txt'

class BaseAIAssistant(Generic[AnyResponseModel]):
    '''Base class for creating AI assistants.

    Subclasses should supply a system prompt and a response model. This class
    provides helpers for prompt loading and response parsing.
    '''
    def __init__(self,
        name: str,
        sys_content: str,
        response_model: Type[AnyResponseModel] ):
        self.name = name
        self.sys_content: Optional[str | None] = sys_content
        self.response_model = response_model

    @classmethod
    def from_file(cls,
        name: str,
        prompt_path: str,
        response_model: Type[AnyResponseModel] ) -> Optional['BaseAIAssistant[AnyResponseModel]']:
        '''Create an assistant using a system prompt loaded from a file'''
        if not os.path.exists(prompt_path):
            L.error(f'Could not locate prompt at: "{prompt_path}"')
            return None
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return cls(name, f.read(), response_model)

    @staticmethod
    def safe_load_prompt(search_path: str, raw_prompt_path: str) -> Optional[str]:
        '''Safely load a prompt file, resolving the path in dynamic environments.

        In Azure Functions and similar environments, the current working directory
        may not match the source folder — this function corrects for that.
        '''
        prompt_path = os.path.join(
            search_path,
            os.path.basename(raw_prompt_path) )
        if not os.path.exists(prompt_path):
            L.error(f'Could not locate prompt file at: "{prompt_path}"')
            return None
        with open(prompt_path, 'r', encoding='utf-8') as fh:
            return fh.read().strip()

    @staticmethod
    def load_default_prompt(search_path: str) -> str:
        '''Load and return the default system prompt using the standard filename.'''
        sys_content = BaseAIAssistant.safe_load_prompt(
            search_path,
            DEFAULT_PROMPT_FILENAME
        )
        if sys_content is None:
            raise ValueError('Could not load default system prompt')
        return sys_content

    @staticmethod
    def ensure_sys_content(sys_content: str, search_path: str) -> str:
        '''Ensure that a valid system prompt is available.

        Returns the given system prompt if non-empty, or attempts to load
        the default. Raises ValueError if no valid prompt can be found.
        '''
        if sys_content is None or len(sys_content) == 0:
            sys_content = BaseAIAssistant.load_default_prompt(search_path)
            if sys_content is None:
                raise ValueError('Could not load a system prompt')
        return sys_content