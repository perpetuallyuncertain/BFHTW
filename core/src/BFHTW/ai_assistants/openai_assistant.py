'''
OpenAI-specific assistant class for making structured and unstructured
requests to the OpenAI chat completion API.

Provides request formatting, error handling, cost estimation, and parsing of
API responses into structured output using Pydantic models.
'''

from collections import namedtuple
from dotenv import load_dotenv
from openai import OpenAI, APIError
from openai.types.chat import ChatCompletion
import os
import time
from typing import Optional, Type

from BFHTW.ai_assistants.base_assistant import BaseAIAssistant, AnyResponseModel
from BFHTW.utils.logs import get_logger
L = get_logger()

load_dotenv()
DEFAULT_API_KEY = os.environ.get('OPENAI_API_KEY')

# Consistent way to transport results
# Output is expected to be an instance of a ResponseModel
Completion = namedtuple(
    'Completion',
    ['output', 'prompt_tokens', 'prompt_tokens_cached', 'completion_tokens'] )

class OpenAIAssistant(BaseAIAssistant[AnyResponseModel]):
    '''OpenAI-backed assistant for generating structured outputs via OpenAI's
    chat completions API. Subclass of BaseAIAssistant.'''

    # Class-level defaults
    max_tokens = 10000
    temperature = 0.5
    frequency_penalty = 0
    presence_penalty = 0

    # Null result from analyse
    null_comp = Completion(None, 0, 0, 0)

    # Cost per 1M tokens as of: 2025-05-06
    PRICING = {
        'gpt-4o-mini': {
            'input': 0.15,
            'cached_input': 0.075,
            'output': 0.60 },
        'gpt-4.1-mini': {
            'input': 0.40,
            'cached_input': 0.10,
            'output': 1.60 },
        'gpt-4.1-nano': {
            'input': 0.10,
            'cached_input': 0.025,
            'output': 0.40 } }

    def __init__(self,
        name: str,
        sys_content: str,
        response_model: Type[AnyResponseModel],
        api_key: Optional[str] = None,
        default_model: Optional[str] = 'gpt-4o-mini' ):
        '''Initialise an OpenAIAssistant instance with credentials, a system
        prompt, and a structured response model.

        prompt string should be like: You are a helpful assistant... '''
        super().__init__(name, sys_content, response_model)
        self.client = OpenAI(api_key=(api_key or DEFAULT_API_KEY))
        self.tokens = 0
        self.default_model = default_model

        # Make sure we can price the calls
        assert default_model in self.PRICING
        self.null_output = response_model.null_response()

    @classmethod
    def from_file(cls,
        name: str,
        prompt_path: str,
        response_model: Type[AnyResponseModel],
        api_key: Optional[str] = None ):
        '''Create a new assistant by loading the system prompt from a file.'''
        base = super().from_file(name, prompt_path, response_model)
        if base:
            return cls(base.name, base.sys_content, response_model, api_key)
        return None

    def confirm_model(self, model: str) -> str:
        '''Validate and normalise the model name, ensuring it is present
        in the pricing table.'''
        if model is None:
            model = getattr(self, 'default_model', 'gpt-4o-mini')
        assert model in self.PRICING
        return model

    @staticmethod
    def response_2_completion(
        response: ChatCompletion,
        structured_output: Optional[bool]=True) -> Completion:
        '''Convert an OpenAI ChatCompletion response to a Completion namedtuple.'''
        usage = response.usage
        if structured_output:
            output = response.choices[0].message.parsed or None
        else:
            output = response.choices[0].message.content or None

        return Completion(
            output=output,
            prompt_tokens=usage.prompt_tokens,
            # Some older models do not report cahced input tokens
            prompt_tokens_cached=getattr(usage, 'prompt_tokens_cached', 0),
            completion_tokens=usage.completion_tokens )

    def _make_request_kwargs(self,
        usr_content: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        structured_output: Optional[bool] = True ) -> dict:
        '''Build the request payload (as kwargs) for an OpenAI API call.

        Adds appropriate model, prompt, and optional structured output schema.
        '''
        # make sure the model string is valid
        model = self.confirm_model(model)

        if frequency_penalty is None:
            frequency_penalty = getattr(
                self,
                'frequency_penalty',
                OpenAIAssistant.frequency_penalty )

        if presence_penalty is None:
            presence_penalty = getattr(
                self,
                'presence_penalty',
                OpenAIAssistant.presence_penalty )

        if max_tokens is None:
            max_tokens = getattr(self, 'max_tokens', OpenAIAssistant.max_tokens)

        if temperature is None:
            temperature = getattr(self, 'temperature', OpenAIAssistant.temperature)

        kwargs = dict(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            messages=[
                { 'role': 'system', 'content': self.sys_content },
                { 'role': 'user', 'content': usr_content }
            ] )
        if structured_output:
            kwargs['response_format'] = self.response_model
        else:
            kwargs['response_format'] = {'type': 'json_object'}

        return kwargs

    def submit_completion(self,
        request_kwargs: dict,
        structured_output: Optional[bool]=True ) -> Completion:
        '''Submit the API request to OpenAI and return a structured Completion
        object with token counts and the output.'''
        try:
            if structured_output:
                response = self.client.beta.chat.completions.parse(**request_kwargs)
                msg_wrapper = 'parsed'
            else:
                response = self.client.chat.completions.create(**request_kwargs)
                msg_wrapper = 'content'
        except APIError as e:
            L.error(f"API Error: {e}")
            return OpenAIAssistant.null_comp

        message = response.choices[0].message

        # Check for refusal
        if message.refusal:
            L.warning(f'Request refused {message.refusal}')
            return OpenAIAssistant.null_comp

        if not getattr(message, msg_wrapper):
            L.error('Model responded, but parsing failed unexpectedly')
            return OpenAIAssistant.null_comp

        return self.response_2_completion(
            response,
            structured_output=structured_output )

    @staticmethod
    def estimate_completion_cost(completion: Completion, model: str) -> float:
        '''Estimate the API usage cost based on token counts and model pricing.

        Accounts for cached input tokens. Returns the estimated cost in USD.
        '''
        try:
            prices = OpenAIAssistant.PRICING[model.lower()]
        except KeyError:
            raise ValueError(f'Model "{model}" not found in pricing table.')

        # Convert to cost per token
        per_token_input = prices['input'] / 1_000_000
        per_token_cached = prices['cached_input'] / 1_000_000
        per_token_output = prices['output'] / 1_000_000

        billed_input_tokens = completion.prompt_tokens - completion.prompt_tokens_cached

        return (
            billed_input_tokens * per_token_input +
            completion.prompt_tokens_cached * per_token_cached +
            completion.completion_tokens * per_token_output )

    def analyse(self,
        usr_content: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        structured_output: Optional[bool] = True ) -> tuple[AnyResponseModel, float]:
        '''Run a full analysis cycle: submit user content to the LLM, capture
        structured output, and estimate API cost.

        Returns a parsed response model and the estimated cost.
        '''
        start_time = time.time()

        if structured_output:
            NULL = self.null_output
        else:
            NULL = None

        if not usr_content.strip():
            L.warning('No user content supplied. Skipping...')
            return NULL, 0.

        # make sure the model string is valid
        model = self.confirm_model(model)

        # Make the call to the LLM API
        completion = self.submit_completion(
            self._make_request_kwargs(
                usr_content,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                structured_output=structured_output ),
            structured_output=structured_output )

        if completion.output is None:
            L.warning('Model responded, but no results were returned')
            return NULL, 0.

        estimated_cost = self.estimate_completion_cost(
            completion=completion,
            model=model )

        processing_time = int(time.time() - start_time)
        L.info(' : --- : '.join([
            f'Assistant: {self.name}',
            f'Processing time = {processing_time}',
            (
                f'Tokens used = {completion.prompt_tokens} '
                f'({completion.prompt_tokens_cached} cached):'
                f'{completion.completion_tokens}' ),
            f'Estimated cost = {estimated_cost}' ]) )

        return completion.output, estimated_cost
