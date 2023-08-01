# OpenAI GPT-3.5 Virtual Assistant

This code defines a virtual assistant named "Dr. Ludwig" that provides medical advice using the GPT-3.5 language model. Here's a brief explanation of each function and the main part of the code:

**get_response(instructions, previous_questions_and_answers, new_question)**: This function takes the instructions for the conversation, a list of previous questions and answers, and a new user question as input. It then uses the OpenAI GPT-3.5 model to generate a response based on the conversation history and the new question.

**get_moderation(question)**: This function checks if the user question violates any moderation rules. It sends the question to OpenAI's Moderation API, which flags content that may contain inappropriate or harmful material. If the question is flagged, it returns a list of categories that were violated. Otherwise, it returns None.

**get_answer(new_question)**: This function uses **get_moderation** to check if the question is appropriate. If the question passes the moderation check, it calls **get_response** to obtain a response from the virtual assistant. It then updates the conversation history with the new question and response.

**main()**: The main function sets up the conversation loop with the virtual assistant. It starts by asking the user's name and then continues to take user questions as input. It passes the user's question to **get_answer**, gets the response, and prints it as the virtual assistant's reply.

## Global variables for the virtual assistant

**INSTRUCTIONS**: This is a multiline string variable that contains the initial instructions given to the virtual assistant, "Dr. Ludwig." The instructions provide guidance on how users should interact with the assistant and what kind of information they should provide when seeking medical advice. These instructions will be used in the get_response function to set the context for the conversation with the language model.

**TEMPERATURE**: This variable sets the temperature for the language model's output. Temperature controls the randomness of the model's responses. A lower temperature (e.g., close to 0) makes the responses more focused and deterministic, while a higher temperature (e.g., close to 1) allows for more randomness and diversity in the responses. Here, **TEMPERATURE = 0.5** strikes a balance between maintaining coherence and introducing some variation.

**MAX_TOKENS**: This variable defines the maximum number of tokens allowed in the generated response. Tokens are chunks of text used by the language model to process and generate text. Setting **MAX_TOKENS = 500** means that the virtual assistant's response will be limited to 500 tokens, helping to control the length of the response.

**FREQUENCY_PENALTY**: This variable represents the frequency penalty used during response generation. A higher penalty value (e.g., > 0) reduces the likelihood of the model repeating the same response or generating repetitive content. However, in this case, **FREQUENCY_PENALTY = 0**, meaning there is no penalty for frequency, and the model may potentially generate more repetitive responses.

**PRESENCE_PENALTY**: This variable sets the presence penalty during response generation. The presence penalty discourages the model from generating responses that match input phrasings too closely. A higher penalty value (e.g., > 0) will lead to more diverse responses. Here, **PRESENCE_PENALTY = 0.6** indicates a moderate penalty to promote some level of response diversity.

**MAX_CONTEXT_QUESTIONS**: This variable specifies the maximum number of previous questions and answers that will be considered in the conversation history while generating a new response. It helps the model maintain context and relevance to the current user question. **MAX_CONTEXT_QUESTIONS = 10** limits the number of previous interactions to 10.

**previous_questions_and_answers**: This is an empty list that will be used to store previous questions and their corresponding responses during the conversation with the virtual assistant. As the user interacts with the assistant, their questions and the model's responses will be appended to this list, and it will be utilized to provide context for future responses.

*These settings and variables are crucial for fine-tuning the behavior of the virtual assistant and ensuring it provides relevant and helpful medical advice to users in a controlled and context-aware manner.*

## IMPORTANT: ❗❗❗API Key❗❗❗

An API key is a unique identifier or a secret code that grants access to a specific API (Application Programming Interface) provided by a service or platform. It acts as a security token and allows the owner to make authenticated requests to the API.

In this code, the API key is used to authenticate and authorize access to the OpenAI API. It allows the virtual assistant to communicate with the GPT-3.5 language model provided by OpenAI. Without a valid API key, the assistant wouldn't be able to access the language model and generate responses.

Here's how the API key is used in the code:

**import os** and **from dotenv import load_dotenv**: These lines import the necessary libraries to work with environment variables (such as the API key) stored in a file named "**.env**".

**load_dotenv()**: This function loads the environment variables from the "**.env**" file, making them accessible to the script.

**openai.api_key = os.getenv("OPENAI_API_KEY")**: This line retrieves the API key from the environment variables using the os.getenv function. The API key is expected to be stored under the name "**OPENAI_API_KEY**" in the "**.env**" file. It then sets the API key as the value for openai.api_key, allowing the virtual assistant to use it for making authenticated requests to the OpenAI API.

By using environment variables to store sensitive information like the API key in a separate file, developers can maintain a higher level of security and keep their credentials private. The "**.env**" file is usually not shared in version control systems like Git to prevent accidental exposure of the API key.

## Version of the OpenAI API

The virtual assistant uses the openai.ChatCompletion.create() method from the OpenAI API to perform the conversation with GPT-3.5 Turbo, which is a variant of the language model optimized for chat-like interactions.
