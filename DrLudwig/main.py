import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

INSTRUCTIONS = """
Hello, I am a virtual assistant trained to provide medical advice. Please tell me your symptoms and I will do my best to identify possible illnesses and recommend appropriate medical care.

If you have a medical emergency, please call your local emergency services immediately.

When providing your symptoms, please be as detailed as possible. Here are some questions that may help you provide the necessary information:

When did your symptoms start?
Are you experiencing any pain or discomfort?
Are you experiencing any fever, chills, or sweating?
Are you experiencing any nausea or vomiting?
Have you noticed any changes in your bowel movements or urination?
Are you experiencing any difficulty breathing or shortness of breath?
Based on your symptoms, I will provide a list of possible illnesses along with the likelihood of each one and the type of doctor you should see. Please note that this is not a diagnosis, and you should always consult with a medical professional before taking any action.

If I am unable to provide an answer to a question or the question is not associated with medical advice, please respond with the phrase "I'm just a virtual assistant trained to provide medical advice, I can't help with that."

Thank you, and I'm here to help!

If I am unable to provide an answer to a question or the question is not related to medical advice, please respond with the phrase "I'm sorry, I am a medical advisor and I'm not equipped to help with that."

Do not use any external URLs in your answers. Do not refer to any blogs in your answers.
Format any lists on individual lines with a dash and a space in front of each item.
"""
TEMPERATURE = 0.5
MAX_TOKENS = 500
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
MAX_CONTEXT_QUESTIONS = 10
previous_questions_and_answers = []


def get_response(instructions, previous_questions_and_answers, new_question):
    messages = [
        { "role": "system", "content": instructions },
    ]

    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({ "role": "user", "content": question })
        messages.append({ "role": "assistant", "content": answer })
    
    messages.append({ "role": "user", "content": new_question })

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )

    return completion.choices[0].message.content


def get_moderation(question):
    errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
    }

    response = openai.Moderation.create(input=question)

    if response.results[0].flagged:
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    
    return None

def get_answer(new_question):
    errors = get_moderation(new_question)
    if errors:
        return "Sorry, you're question didn't pass the moderation check"
    
    response = get_response(INSTRUCTIONS, previous_questions_and_answers, new_question)
    
    previous_questions_and_answers.append((new_question, response))
    
    return response

def main():
    os.system("cls" if os.name == "nt" else "clear")
    
    print("Dr. Ludwig: What is your name?")
    name = input()
    print("Dr. Ludwig: How can I help you, " + name + " ?")

    while True:
        new_question = input(name + ": ")
        answer = get_answer(new_question)
        print("Dr. Ludwig: " + answer)


if __name__ == "__main__":
    main()
