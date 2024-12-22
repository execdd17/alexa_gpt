# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import os
import urllib.request
import json
import ask_sdk_core.utils as ask_utils
from openai import OpenAI


from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_intent_name
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AgeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # Check if this is a NameIntent request
        return is_intent_name("AgeIntent")(handler_input)

    def handle(self, handler_input):
        # Get the user's name from the slot
        age = handler_input.request_envelope.request.intent.slots["age"].value
        
        # Store the user's name in session attributes
        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes['age'] = age

        logger.debug(f"Inside AgeIntentHandler with age: {age} from the session")
        
        age_echo = f"You are {age} years old, got it. "
        query_echo = f"What do you want to know? Say, 'search for' and then your question."
        return (
            handler_input.response_builder
                .speak(age_echo + query_echo)
                .ask(query_echo)
                .response
        )


class QueryIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("QueryIntent")(handler_input)
    
    def handle_user_query(self, age: int, user_query: str, session_attributes):
        secret = QueryIntentHandler.get_secret_from_extension()
        api_key = json.loads(secret)['api-key']
        logger.info(f"api_key length: {len(api_key)}")
        
        client = OpenAI(api_key=api_key)

        if age < 10:
            system_prompt = "You are a friendly assistant who explains things in a simple, fun, and easy-to-understand way. Use clear language and short sentences, and focus on keeping the conversation engaging. Avoid using difficult words and make sure your explanations are interesting by adding examples or fun comparisons. Imagine explaining things to someone who loves to learn but still needs things broken down clearly and simply. Keep your answers concise, limited to one or two short paragraphs, as kids have short attention spans."
        elif age <= 15:
            system_prompt = "You are an assistant who explains things in a fun and informative way for a curious 10-12-year-old. Use language that’s a little more advanced than for younger children, but still make sure the information is easy to follow. Provide some more details and examples to help them understand complex ideas, and try to make the explanations interesting and relatable by connecting them to things they might already know, like hobbies, games, or school subjects."
        else:
            system_prompt = "You are a knowledgeable assistant who provides thorough, well-explained responses suited for an adult. Your tone should be professional, but friendly, and you should use complete sentences with appropriate vocabulary. Avoid being overly casual, and aim to deliver clear, informative responses that assume the reader has a general level of education."

        return QueryIntentHandler.query_openai(client, system_prompt, session_attributes, user_prompt=user_query)

    @staticmethod
    def query_openai(client: OpenAI, system_prompt: str, session_attributes, 
                     user_prompt: str, model: str = "gpt-4o-mini") -> str:
        logger.info(f"Using system prompt: {system_prompt}")
        logger.info(f"Using user prompt: {user_prompt}")

        if session_attributes.get("convo"):
            session_attributes["convo"].append({ "role": "user", "content": user_prompt })
        else:
            session_attributes["convo"] = [
                { "role": "system", "content": system_prompt },
                { "role": "user", "content": user_prompt }
            ]

        completion = client.chat.completions.create(
            model=model,
            max_tokens=250,
            messages=session_attributes["convo"]
        )

        response = completion.choices[0].message.content

        session_attributes["convo"].append(
            {"role": "assistant", "content": response}
        )

        logger.info(f"Conversation history: {session_attributes['convo']}")
        return response
    
    @staticmethod
    def get_secret_from_extension() -> str:
        """
        Retrieve a secret string from the AWS Secrets Manager extension.

        This method uses the local AWS Secrets Manager extension to fetch a secret. 
        It requires an active AWS session token available in the environment variables.

        Returns:
            str: The secret string retrieved from the AWS Secrets Manager.

        Raises:
            Exception: If the AWS_SESSION_TOKEN is not found in the environment variables.
            Exception: If the secret cannot be retrieved successfully, or the HTTP response 
                       from the AWS Secrets Manager extension is not 200.

        Notes:
            - The secret name is hardcoded as "prod/openai/tokens".
            - The method assumes the AWS Secrets Manager extension is running locally 
              on port 2773.

        """
        secret_name = "prod/openai/tokens"
        endpoint = f"http://localhost:2773/secretsmanager/get?secretId={secret_name}"

        # Get the AWS session token from environment variables
        session_token = os.getenv('AWS_SESSION_TOKEN')

        if not session_token:
            raise Exception("AWS_SESSION_TOKEN not found in environment variables")

        # Set the necessary headers, including the session token
        headers = {
            "X-Aws-Parameters-Secrets-Token": session_token
        }

        req = urllib.request.Request(endpoint, headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                secret = json.loads(response.read().decode())
                return secret['SecretString']
            else:
                raise Exception(f"Failed to retrieve secret. Status: {response.status}")

    def handle(self, handler_input):
        user_query = handler_input.request_envelope.request.intent.slots["query"].value

        session_attributes = handler_input.attributes_manager.session_attributes
        age = session_attributes.get("age")

        logger.debug(f"user_query is {user_query}")
        logger.debug(f"age is {age}")

        if not age:
          raise Exception("I do not know the age!")
        
        age = int(age)
        
        if not user_query:
          raise Exception("I do not know the user query!")

        # Proceed with the query logic
        gpt_response = self.handle_user_query(age, user_query, session_attributes)
        return (
            handler_input.response_builder
                .speak(gpt_response)
                .ask("If you want to keep talking, then say 'search for' first.")
                .response
        )


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "How old are you?" 

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
    

class ZigZagIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ZigZagIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Who is the dog that likes to play? Zig Zag, Zig Zag!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )
    


# class HelloWorldIntentHandler(AbstractRequestHandler):
#     """Handler for Hello World Intent."""
#     def can_handle(self, handler_input):
#         # type: (HandlerInput) -> bool
#         return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

#     def handle(self, handler_input):
#         # type: (HandlerInput) -> Response
#         speak_output = "Hello, dude!"

#         return (
#             handler_input.response_builder
#                 .speak(speak_output)
#                 # .ask("add a reprompt if you want to keep the session open for the user to respond")
#                 .response
#         )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye, dude!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AgeIntentHandler())
sb.add_request_handler(QueryIntentHandler())
# sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(ZigZagIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
