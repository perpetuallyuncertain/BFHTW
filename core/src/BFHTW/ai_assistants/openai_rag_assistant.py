from .core_utils import EnvManager
from openai import OpenAI, APIError, AssistantEventHandler
from typing_extensions import override
import json
import requests
from datetime import datetime, timedelta
import time
from newsapi import NewsApiClient
import os

class EventHandler(AssistantEventHandler):
    def __init__(self, update_callback):
        super().__init__()
        self.update_callback = update_callback
        self.function_calls = {}  # Cache function calls until processing

    @override
    def on_text_delta(self, delta, snapshot):
        """Handles assistant response streaming (text messages)."""
        if delta.value:
            print(f"DEBUG: Streaming Assistant Response - {delta.value}")
            self.update_callback({"value": delta.value})  #  Stream text as normal

    # @override
    # def on_tool_call_created(self, tool_call):
    #     """Handles function calls (when the assistant requests an external tool)."""
    #     print(f"DEBUG: Tool Call Created - {tool_call}")
    #     if tool_call.type == "function":
    #         function_name = tool_call.function.name
    #         parameters = json.loads(tool_call.function.arguments)
    #         self.function_calls[tool_call.id] = {
    #             "function_name": function_name,
    #             "parameters": parameters,
    #         }
    #         print(f"DEBUG: Cached Function Call - {function_name} with {parameters}")

    @override
    def on_tool_call_created(self, tool_call):
        """Handles function calls (when the assistant requests an external tool)."""
        print(f"DEBUG: Tool Call Created - {tool_call}")

        if tool_call.type == "function":
            function_name = tool_call.function.name
            arguments_str = tool_call.function.arguments

            # Handle empty or invalid JSON case
            if not arguments_str or arguments_str.strip() == "":
                print(f"WARNING: Empty function arguments for {function_name}")
                parameters = {}  # Default to empty parameters
            else:
                try:
                    parameters = json.loads(arguments_str)  # Parse only if valid
                except json.JSONDecodeError as e:
                    print(f"ERROR: Failed to parse JSON arguments for {function_name} - {e}")
                    parameters = {}  # Default to empty parameters

            self.function_calls[tool_call.id] = {
                "function_name": function_name,
                "parameters": parameters,
            }
            print(f"DEBUG: Cached Function Call - {function_name} with {parameters}")

    @override
    def on_run_step_delta(self, delta, snapshot):
        """Handles `thread.run_step.delta` events which contain function call execution details."""
        if delta.step_details and delta.step_details.type == "message_creation":
            message_id = delta.step_details.message_creation.message_id
            print(f"DEBUG: Assistant Message Created - Message ID {message_id}")


class Functions:

    def __init__(self):
        self.env_manager = EnvManager(environment="dev", local=True)
        self.news_api_key = self.env_manager.get_env_var("newsapi")
        self.newsapi = NewsApiClient(api_key=self.news_api_key)
        self.web_search_key = self.env_manager.get_env_var("bingapi")

    def get_news(self, topic, start_date=None, end_date=None):
        """
        Fetches news articles from NewsAPI based on a topic, always using a date range of:
        - Today - 25 days → Today
        - Returns a formatted list of articles with relevant details.
        """

        #  Always force the date range to the last 25 days
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=25)

        from_date_str = start_date.strftime("%Y-%m-%d")
        to_date_str = end_date.strftime("%Y-%m-%d")

        print(f" Overriding AI dates: Searching news from {from_date_str} to {to_date_str}")

        try:
            top_headlines = self.newsapi.get_top_headlines(q=f"bitcoin",
                                                            category='business',
                                                            language='en',
                                                            country='us',
                                                            page_size=10)

            news_data = top_headlines

            print(f"DEBUG: NewsAPI Response: {news_data}")

            if news_data.get("status") != "ok":
                print(" News API returned an error status!")
                return {"error": "Failed to fetch news", "details": news_data}

            articles = news_data.get("articles", [])

            if not articles:  #  No articles found, return an error
                print(f" No articles found for topic '{topic}'. Closing thread.")
                return {"error": f"No news found for topic '{topic}' in the last 25 days."}

            final_news = []

            # Loop through articles and format output
            for article in articles:
                source_name = article["source"]["name"]
                author = article["author"]
                title = article["title"]
                description = article["description"]
                url = article["url"]
                content = article["content"]

                title_description = f"""
                    Title: {title}, 
                    Author: {author},
                    Source: {source_name},
                    Description: {description},
                    URL: {url}
                """
                final_news.append(title_description)

            print(f"DEBUG: Formatted News for topic '{topic}': {final_news}")

            return f"""Summarise the news articles {final_news} and return the top 10 articles in the following format to the user:
                        Title: [title], Author: [author], Source: [source], Summary: [summary], URL: [url]"""

        except requests.exceptions.RequestException as e:
            print(f" NewsAPI request failed: {str(e)}")
            return {"error": "Error occurred during API request", "details": str(e)}

    import requests

    def web_search(self, query: str, region: str = None, language: str = "en"):
        """
        Performs a Bing web search with optional filtering by region and language.
        Returns a dictionary of summarized search results.
        """

        subscription_key = self.web_search_key
        endpoint = "https://api.bing.microsoft.com/v7.0/search"  # Ensure this is correct

        if not subscription_key:
            return {"error": "Missing Bing API Key."}

        try:
            # Construct query parameters
            params = {
                "q": query,
                "count": 5,  # Limit results
                "textDecorations": "true",
                "textFormat": "HTML",
            }

            if region:
                params["mkt"] = region  # Correct parameter for market
            if language:
                params["setLang"] = language  # Correct parameter for language

            # Set request headers
            headers = {
                "Ocp-Apim-Subscription-Key": subscription_key
            }

            # Make the GET request to Bing Search API
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
            response.raise_for_status()  # Raise an exception for 4xx/5xx responses

            web_data = response.json()

            if "webPages" not in web_data or "value" not in web_data["webPages"]:
                print(f"No web pages found for query: {query}")
                return {"error": f"No web pages found for '{query}'."}

            # Process search results
            web_results = {}

            for result in web_data["webPages"]["value"]:
                title = result.get("name", "No title")
                url = result.get("url", "No URL")
                snippet = result.get("snippet", "No summary available")

                # Attempt to fetch full webpage content
                try:
                    page_response = requests.get(url, timeout=5)  # Set timeout to prevent hanging
                    content = page_response.text if page_response.status_code == 200 else snippet
                except requests.exceptions.RequestException:
                    content = snippet  # Use snippet if request fails

                # Store results in JSON format
                web_results[title] = {
                    "content": content,
                    "url": url
                }

            print(f"Retrieved {len(web_results)} results for '{query}'")
            return {"query": query, "results": web_results}

        except requests.exceptions.RequestException as e:
            print(f"Bing API request failed: {str(e)}")
            return {"error": "Error occurred during API request", "details": str(e)}

            
    def research_tools(self, **kwargs):  # Accepts any arguments, ignores unexpected ones

        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'research_tools_descriptions.json')

        with open(file_path) as f:
            tools = json.load(f)

        return {
            "message": "Here is a list of research tools that can help with market analysis.",
            "tools": tools
        }


    def tools_helper(self, query: str):
        return {"error": "Not implemented"}
    
class AssistantManager:
    def __init__(self, environment: str, local: bool = True):
        self.environment = environment.lower()
        self.env_manager = EnvManager(environment=self.environment, local=local)
        self.openai_api_key = self.env_manager.get_env_var("OpenAIapiKey")
        self.assistantID = self.env_manager.get_env_var("AiAssistantID")

        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables.")

        self.client = OpenAI(api_key=self.openai_api_key)
        self.thread = None
        self.chat_history = []
        self.functions = Functions()

        # Define function mappings
        self.function_map = {
            "newsfeed_search": self.functions.get_news,
            "web_search": self.functions.web_search,
            "research_tools": self.functions.research_tools,
            # "tools_helper": self.tools_helper
        }

    def create_thread(self, thread_id=None):
        if thread_id:
            self.thread = self.client.beta.threads.retrieve(thread_id=thread_id)
        else:
            thread_obj = self.client.beta.threads.create()
            self.thread = thread_obj
            self.chat_history = []  # Reset chat history for a new thread

    def add_msg_to_thread(self, role, content):
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role=role,
            content=content
        )
        # Append user message to chat history
        self.chat_history.append({"role": role, "content": content})

    def call_function(self, function_name, parameters):
        func = self.function_map.get(function_name)
        if func:
            return func(**parameters)
        else:
            return {"error": f"Function {function_name} not found"}
    
    def process_message(self, update_callback):
        """Extracts the AI's last response message after it receives tool outputs and sends it to the UI."""
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)

        if messages.data:
            last_message = messages.data[0]  # Get the latest message
            response = last_message.content[0].text.value

            print(f" DEBUG: AI Summary Response - {response}")
            
            #  Send to the UI via update_callback
            update_callback({"value": response})  
        else:
            print(" DEBUG: No response message found from AI.")
    
    def wait_for_completion(self, run_id, update_callback):
        retry_count = 0
        max_retries = 3  #  Prevent infinite loop

        while True:
            time.sleep(2)  # Polling delay
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id, run_id=run_id
            )

            if run_status.status == "completed":
                print("DEBUG: Assistant has responded. Fetching message...")
                self.process_message(update_callback)  # Extract and print the AI's summary message
                break
            elif run_status.status == "requires_action":
                print(f"DEBUG: Assistant still needs function calls. Waiting... (Retry {retry_count}/{max_retries})")
                retry_count += 1

                if retry_count >= max_retries:
                    print("Assistant still needs tool calls after multiple retries. Forcing thread shutdown.")

                    #  Step 1: Explicitly submit an empty response to OpenAI
                    self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=self.thread.id,
                        run_id=run_id,
                        tool_outputs=[]
                    )

                    # Step 2: Cancel the run
                    self.client.beta.threads.runs.cancel(
                        thread_id=self.thread.id, run_id=run_id
                    )

                    # Step 3: Reset thread state
                    self.thread = None
                    print(" Thread forcefully closed.")
                    return


    def run_assistant(self, update_callback):
        """
        Runs the OpenAI Assistant, listens for tool calls, and executes them.
        If the function execution fails, the thread is closed.
        """
        try:
            with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistantID,
                event_handler=EventHandler(update_callback)
            ) as stream:

                for event in stream:
                    print(f"DEBUG: Full Event Received:\n{event}")

                    if event.event == "thread.run.requires_action":
                        required_action = event.data.required_action

                        if required_action and required_action.type == "submit_tool_outputs":
                            tool_calls = required_action.submit_tool_outputs.tool_calls
                            print(f"DEBUG: Tool Calls Detected: {tool_calls}")

                            tool_outputs = []  # Store function results

                            for tool_call in tool_calls:
                                function_name = tool_call.function.name
                                parameters = json.loads(tool_call.function.arguments)

                                print(f"DEBUG: Executing {function_name} with {parameters}")

                                # Call the function and handle failure
                                result = self.call_function(function_name, parameters)

                                if "error" in result:  # If function call failed, return an error response instead of closing
                                    print(f"Function {function_name} failed. Returning error response.")

                                    tool_outputs.append({
                                        "tool_call_id": tool_call.id,
                                        "output": json.dumps(result)  # Ensure OpenAI receives a response
                                    })

                                else:
                                    # Store successful result
                                    tool_outputs.append({
                                        "tool_call_id": tool_call.id,
                                        "output": json.dumps(result)
                                    })

                            # Ensure OpenAI gets a response even if an error occurs
                            print(f"DEBUG: Submitting tool outputs: {json.dumps(tool_outputs, indent=2)}")
                            self.client.beta.threads.runs.submit_tool_outputs(
                                thread_id=self.thread.id,
                                run_id=event.data.id,
                                tool_outputs=tool_outputs
                            )

                            # Wait for assistant to complete processing
                            run_id = event.data.id
                            self.wait_for_completion(run_id=run_id, update_callback=update_callback)

                stream.until_done()

        except Exception as e:
            print(f"Critical error in run_assistant: {str(e)}. Closing thread.")
            stream.close()


    def run_chat(self, question, update_callback):
        if not self.thread:
            self.create_thread()

        # Add user question to the thread
        self.add_msg_to_thread(role="user", content=question)

        # Run the assistant and process responses
        self.run_assistant(update_callback)

        return self.thread.id

