# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import os
import urllib.request
import json
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_intent_name


from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_secret_from_extension():
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

    try:
        req = urllib.request.Request(endpoint, headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                secret = json.loads(response.read().decode())
                return secret['SecretString']
            else:
                raise Exception(f"Failed to retrieve secret. Status: {response.status}")
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None


class NameIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # Check if this is a NameIntent request
        return is_intent_name("NameIntent")(handler_input)
        # return ask_utils.is_request_type("NameIntent")(handler_input)

    def handle(self, handler_input):
        # Get the user's name from the slot
        user_name = handler_input.request_envelope.request.intent.slots["name"].value
        
        # Store the user's name in session attributes
        session_attributes = handler_input.attributes_manager.session_attributes
        session_attributes['userName'] = user_name
        
        speak_output = f"Nice to meet you, {user_name}! How can I help you today?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "What is your name?" 

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
    


class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello, dude!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


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
sb.add_request_handler(NameIntentHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(ZigZagIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()


# def lambda_handler(event, context):
#     # secret = get_secret()
#     secret = get_secret_from_extension()
#     return json.dumps({"secret": secret})

# def lambda_handler(event, context):
#     secret_name = "prod/openai/tokens-LTn7P9"
#     endpoint = f"http://localhost:2773/secretsmanager/get?secretId={secret_name}"
#     headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN", "N/A")}

#     # Logging the environment variable to ensure it's set
#     print(f"Session Token: {headers['X-Aws-Parameters-Secrets-Token']}")

#     req = urllib.request.Request(endpoint, headers=headers)
    
#     try:
#         with urllib.request.urlopen(req) as response:
#             if response.status == 200:
#                 secret = json.loads(response.read().decode())
#                 print(f"Secret retrieved: {secret['SecretString']}")
#                 return {
#                     "statusCode": 200,
#                     "body": f"Secret retrieved: {secret['SecretString']}"
#                 }
#             else:
#                 print(f"Failed to retrieve secret. Status: {response.status}")
#                 return {
#                     "statusCode": response.status,
#                     "body": f"Failed to retrieve secret. Status: {response.status}"
#                 }
#     except urllib.error.URLError as e:
#         print(f"Error retrieving secret: {e.reason}")
#         return {
#             "statusCode": 500,
#             "body": f"Error retrieving secret: {e.reason}"
#         }