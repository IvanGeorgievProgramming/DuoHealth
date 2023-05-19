from flask import Flask, render_template, request, make_response, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib
import os
from email.message import EmailMessage
import ssl
import smtplib
import random
import requests
from bs4 import BeautifulSoup
import json
from newsapi.newsapi_client import NewsApiClient
import string
from urllib.parse import urlparse
from cryptography.fernet import Fernet, InvalidToken
import openai
from dotenv import load_dotenv

# ********** 2FA ********** #

load_dotenv()

# ********** OpenAI ********** #

openai.api_key = os.getenv("OPENAI_API_KEY")

INSTRUCTIONS = """Hello, I am a virtual assistant trained to only provide medical advice. Please tell me your symptoms and I will do my best to identify possible illnesses and recommend appropriate medical care. If you have a medical emergency, please call your local emergency services immediately. When providing your symptoms, please be as detailed as possible. Here are some questions that may help you provide the necessary information: When did your symptoms start? Are you experiencing any pain or discomfort? Are you experiencing any fever, chills, or sweating? Are you experiencing any nausea or vomiting? Have you noticed any changes in your bowel movements or urination? Are you experiencing any difficulty breathing or shortness of breath? Based on your symptoms, I will provide a list of possible illnesses along with the likelihood of each one and the type of doctor you should see. Please note that this is not a diagnosis, and you should always consult with a medical professional before taking any action. If I am unable to provide an answer to a question or the question is not associated with medical advice, please I will respond with the phrase "I'm just a virtual assistant trained to provide medical advice, I can't help with that." Thank you, and I'm here to help! Do not use any external URLs in your answers. Do not refer to any blogs in your answers. Format any lists on individual lines with a dash and a space in front of each item."""
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

# ********** Email ********** #

email_sender = os.environ.get('EMAIL_SENDER')
email_password = os.environ.get('EMAIL_PASSWORD')

# **********  App  ********** #

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db = SQLAlchemy(app)
key = Fernet.generate_key()
crypter = Fernet(key)

# ********** Database ********** #	

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key = True)
    email = db.Column(db.String(), unique = True, nullable = False)
    username = db.Column(db.String(), unique = True, nullable = False)
    password = db.Column(db.String(), nullable = False)
    
class Item(db.Model):
    __tablename__ = 'password'
    id = db.Column(db.Integer(), primary_key = True)
    email = db.Column(db.String(), nullable = False)
    username = db.Column(db.String(), nullable = False)
    user_password = db.Column(db.String(), nullable = False)
    website = db.Column(db.String(), nullable = False)

# ********** Routes ********** #

# Landing page
@app.route('/')
@app.route('/landing')
def home():
    email = session.get('email')
    if email:
        return redirect(url_for('Index'))
    newsapi = NewsApiClient(api_key= os.getenv('NEWS_API_KEY'))
    topheadlines = newsapi.get_everything(q='cybersecurity', language='en', sort_by = 'publishedAt', page_size=5)
                                        
    articles = topheadlines['articles']

    desc = []
    news = []
    link = []
    img = []

    for i in range(len(articles)):
        myarticles = articles[i]

        news.append(myarticles['title'])
        desc.append(myarticles['content'])
        img.append(myarticles['urlToImage'])
        link.append(myarticles['url'])

    mylist = zip(news, desc, link, img)

    return render_template('landing.html', context = mylist)

# Register page
@app.route('/register', methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        psw = request.form.get("password")
        psw_confirm = request.form.get("confirm_password")
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('register.html', message="Another account is using this email.")
        elif len(email) < 4:
            return render_template('register.html', message="Email must be longer than 3 characters.")
        elif len(username) < 2:
            return render_template('register.html', message="Username must be longer than 2 characters.")
        elif psw != psw_confirm:
            return render_template('register.html', message="The passwords do not match.")
        elif len(psw) < 7:
            return render_template('register.html', message="The password must be at least 7 characters")
        else:
            hash_object = hashlib.sha256(psw.encode('utf-8'))
            hex_dig = hash_object.hexdigest()
            user = User(email=email, username=username, password = hex_dig)
            db.session.add(user)
            db.session.commit()
            flash('Account created!', category='success')
            return redirect(url_for('login'))
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    email = session.get('email')
    if email:
        return redirect(url_for('verification'))
    if request.method == 'POST':
        email = request.form['email']
        email_receiver = email
        code = random.randint(100000, 999999)
        session['code'] = code  # store code in session

        subject = 'Verification Code'
        body = f'Your verification code is: \n----------\n{code}\n----------'

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_receiver, em.as_string())
        password = request.form['password']
        remember = request.form.get('remember', False)
        session['remember'] = remember
        user = User.query.filter_by(email=email).first()
        if user is None:
            return render_template('login.html', message="Invalid Credentials")
        hash_password = hashlib.sha256(password.encode()).hexdigest()
        if hash_password == user.password:
            session['email'] = email
            session['password'] = password
            if remember:
                session.permanent = True
            return redirect(url_for('verification'))
        else:
            return render_template('login.html', message="Invalid Credentials")
    else:
        return render_template('login.html')

# Verification page
@app.route('/verification', methods=['GET', 'POST'])
def verification():
    email = session.get('email')
    remember = session.get('remember')
    if email is None:
            if remember != True:
                return redirect(url_for('login'))    
    print("hello world")
    if request.method == 'POST':
        code= int(request.form['code'])
        if code == (session['code']):
            return redirect(url_for('Index'))
        else:   
            flash('Invalid Code')
            return render_template('auth.html')
    else:
        return render_template('auth.html')

# Logout page
@app.route('/logout')
def left():
    session.pop("email", None)
    session.pop("remember", None)
    session.pop("password", None)
    return redirect('/')
    
# Index page
@app.route('/home', methods= ['POST', 'GET'])
def Index():
    user = User.query.get(4) #! Get Current User id

    newsapi = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY'))
    topheadlines = newsapi.get_everything(q='healthcare, medicine, articles', language='en', sort_by = 'publishedAt', page_size=6)
                                        
    articles = topheadlines['articles']

    desc = []
    news = []
    link = []
    img = []

    for i in range(len(articles)):
        myarticles = articles[i]

        news.append(myarticles['title'])
        desc.append(myarticles['content'])
        img.append(myarticles['urlToImage'])
        link.append(myarticles['url'])

    mylist = zip(news, desc, link, img)

    if request.method == 'POST':
        question = request.form.get('question')
        if not question:
            return render_template('home.html', context = mylist, user = user)
        answer = get_answer(question)
        if question and answer:
            return render_template('home.html', question = question, answer=answer, context = mylist, user = user)
    else :return render_template('home.html', context = mylist, user = user)

    return render_template('home.html', context = mylist, user = user)

# ********** Main **********

if __name__ == "__main__":
    app.run(debug=True)