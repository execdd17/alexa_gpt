# Alexa GPT Skill

## Overview

This project demonstrates how to integrate OpenAI’s language models (such as GPT) into an Alexa skill. The skill asks for the user’s age, then tailors its responses accordingly. For instance, if the user is under 10, the skill provides fun, simplified answers; if the user is older, it offers more detailed explanations. Essentially, it's an Alexa front-end for GPT-based Q&A with an age-based “personality.”

## How It Works

1. **User Launches the Skill**  
   When the skill is launched, it prompts the user to provide their age.

2. **Age Intent**  
   After capturing the user’s age, the skill stores it in session attributes and delegates control to the `QueryIntent`.

3. **Query Intent**  
   The user can then ask any question. The skill contacts OpenAI’s API (using an API key stored securely in AWS Secrets Manager) and returns a text response geared towards the user’s age bracket. If GPT ends its reply with a question, Alexa will use that as a reprompt to encourage more conversation.

4. **Conversation Memory**  
   The skill retains conversation history in session attributes for coherent follow-up questions and context.

## Architecture

### 1. Skill Configuration in the Alexa Developer Console
You (or any developer) must create a custom skill in the [Alexa Developer Console](https://developer.amazon.com/alexa/console). This project provides the necessary skill configuration files (e.g., `en-US.json`) that define the interaction model. **However**, each user must manually import these files or replicate the settings for their own skill in the console so the Lambda function’s intents match the interaction model.

### 2. Skill Metadata / Interaction Models
Your repository includes metadata like `en-US.json` to specify the utterances, sample phrases, and dialog rules. These files are **critical**—without them, Alexa won’t know how to route user queries to the correct intents. Make sure to align the Lambda code and interaction model (for example, the **AgeIntent** and **QueryIntent** in your code must exist in your Alexa console config).

### 3. Hosting Your Own Lambda & Using AWS Secrets Manager
- **Lambda Hosting**: This skill requires a custom AWS Lambda, rather than an Alexa-hosted one, to leverage AWS Secrets Manager.  
- **AWS Secrets Manager**: The code fetches an OpenAI API key stored in Secrets Manager, so you’ll need to:
  1. Create a secret in Secrets Manager (e.g., “prod/openai/tokens”).  
  2. Grant your Lambda function permission to retrieve it.  
  3. Provide that secret name in your code (default: `prod/openai/tokens`).  

### 4. Lambda Layers for Dependency Management
Managing Python dependencies in Lambda can be tedious. [I used this guide to create two lambda layers](https://github.com/syedfaiqueali/aws-lambda-layer-openai?tab=readme-ov-file#step-2-list-your-dependencies-in-requirementstxt):

1. **Alexa Layer** containing the Alexa Skills Kit SDK dependencies (e.g., `ask-sdk-core`, `ask-sdk-model`, etc.).  
2. **OpenAI Layer** containing the `openai` library and any related dependencies.  

By keeping these dependencies in layers, your main Lambda code (i.e., `lambda_function.py` or equivalent) can remain small. Simply attach these layers to your Lambda function, and everything “just works” without needing to bundle all libraries in a single zip.

## Prerequisites & Setup

1. **Python 3.8+**  
2. **AWS Account** (with permissions to create and manage Lambda functions, Layers, and Secrets).  
3. **Alexa Developer Console Account** (for skill creation).

### Steps

1. **Create a Custom Alexa Skill**  
   - Go to the Alexa Developer Console, create a new custom skill.  
   - Set up the invocation name, language model, and interaction model. Import the `en-US.json` (or other locale .json if applicable) from this repository into your Alexa skill’s console.

2. **Set Up Lambda**  
   - In the AWS Console, create a Lambda function.  
   - Attach two Lambda Layers (one for Alexa’s SDK dependencies, one for OpenAI’s dependencies).  
   - Copy or upload your main code file (`lambda_function.py` or similar) into the Lambda.  
   - Adjust the environment variables or code references to point to your AWS Secrets Manager secret name if you changed it from the default.

3. **Configure AWS Secrets Manager**  
   - Store your OpenAI API key in AWS Secrets Manager under the name `prod/openai/tokens` (or whatever name you prefer).  
   - Ensure your Lambda role has the necessary IAM policy (e.g., `secretsmanager:GetSecretValue`) to retrieve this secret.

4. **Link the Skill to Lambda**  
   - In the Alexa Developer Console, set the endpoint to your Lambda’s ARN.  
   - Under “Account Linking,” “Permissions,” or the relevant sections, ensure everything is aligned so Alexa can call your Lambda.

5. **Testing the Skill**  
   - Use the Alexa Developer Console’s “Test” tab or an actual Echo device (with your skill enabled) to launch the skill.  
   - It will ask for your age, then wait for your question.  
   - Check the CloudWatch logs if anything isn’t working as expected.

## Usage

1. **Invoke the Skill**: “Open [your skill invocation name].”  
2. **Provide Age**: When prompted “Hello. How old are you?”, say a number.  
3. **Ask a Question**: “Search for why the sky is blue” or “Explain how rainbows form.”  
4. **Response**: The skill uses GPT to respond according to the user’s age bracket. If GPT’s last sentence is a question, Alexa will prompt for follow-up.

## Code Highlights

- **`AgeIntentHandler`**: Captures the user’s age and delegates to `QueryIntent`.  
- **`QueryIntentHandler`**:  
  - Dynamically selects a “personality” based on the user’s age.  
  - Queries GPT with a system prompt.  
  - Stores conversation in session attributes to maintain context.  
- **`get_last_sentence_and_check_question()`**: Determines if GPT’s last sentence is a question.  
- **`get_secret_from_extension()`**: Fetches the OpenAI key from AWS Secrets Manager.

## Contributing

Feel free to open an issue or a pull request if you see areas for improvement or would like to add new features.

## License

This project uses a [PERSONAL USE LICENSE](LICENSE), which restricts commercial usage. For more details, please refer to the [LICENSE](LICENSE) file in this repository.