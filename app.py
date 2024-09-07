from flask import Flask, render_template, session, redirect, request, url_for, flash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from functools import wraps
import random
from geturls import geturls
from openai import OpenAI
from scrapedata import scrape_data
import time

load_dotenv()

uri = os.getenv("MONGO_URI_STRING")
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["Accounts"]
userinfo = db["Users"]
logindb = db["Login"]
app = Flask(__name__)
openAIClient = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

app.secret_key= "3405gorfejiu84tgfnje2i30rf9joed23rifu90ehoirj49getb8fvu7yd8h3ut4oig9tebifv8dwc7ey80h3ut4og5itu9b0evfdc"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in") or not session.get("username"):
            flash("You need to be logged in to access this page.")
            return redirect(url_for("login"))
        user = logindb.find_one({"username": session.get("username")})
        if not user:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def ask_gpt(prompt):
    completion = openAIClient.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Answer the following question to the best of your ability. Put no text before and after the answer, just provide the answer."},
        {
            "role": "user",
            "content": prompt
        }
    ]
    )
    return(completion.choices[0].message.content)

def gen_random_id():
    rand_id = random.randint(1, 10000)
    if userinfo.find_one({"id": rand_id}):
        return gen_random_id()
    return rand_id

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form.get("username").strip()
            password = request.form.get("password").strip()
            user = logindb.users.find_one({"username": username})
            if not user:
                logindb.insert_one({
                    "username": username,
                    "password": password,
                })
                return redirect(url_for("login"))
            else:
                return(render_template("error.html"))
        except Exception as e:
            print(e)
            return render_template("error.html")
    return render_template("signup.html", error=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get("username").strip()
            password = request.form.get("password").strip()
            user = logindb.find_one({"username": user})
            if not user:
                return render_template("login.html", error="User not found.")
            if user["password"] == password:
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("search"))
            else:
                return render_template("login.html", error="Wrong username or password.")
        except Exception as e:
            return render_template("error.html")
    return render_template("login.html", error=None)

@app.route("/search", methods=["POST", "GET"])
@login_required
def search():
    if request.method == "POST":
        query = request.form.get('query')
        if query:
            symptoms = []
            titles = []
            urls = geturls(query)
            if not urls:
                return "No results found.", 404

            search_results = []
            for url in urls:
                response, title = scrape_data(url)
                symptom_str = ask_gpt("I have a following page. There will be some header text, IGNORE it. What I want you to do is gather up symptoms from the page, then put them in this format. NO TEXT BEFORE OR AFTER THE ANSWER, JUST THE ANSWER. Here's the format: | Symptom | Symptom | Symptom |... Here's the page:  "+ response)
                symptom_list = [s.strip() for s in symptom_str.split('|') if s.strip()]
                search_results.append({"url": url, "title": title, "symptoms": symptom_list})
                
            return render_template("search_results.html", search_results=search_results)
        else:
            return 'No query provided', 400
    else:
        return render_template("index.html")


@app.route("/scrape/<path:url>")
@login_required
def scrape_and_process(url):
    modified_url = url.replace("symptoms-causes", "diagnosis-treatment")
    
    response, realtitle = scrape_data(modified_url)
    
    def ask_for_titles():
        title_str = ask_gpt("I have a following page. There will be some header text, IGNORE it. What I want you to do is gather up the steps to recovery from the page, then put them in this format. Each step should be listed with a title. NO TEXT BEFORE OR AFTER THE ANSWER, JUST THE ANSWER. Here's the format: | Step1 Title | Step2 Title |... Here's the page: " + response)
    
        titles = []
        for title in title_str.split('|'):
            if title.strip():
                titles.append({"title": title.strip()})
        return titles

    titles = ask_for_titles()
    while not titles or len(titles) == 0:
        print("No titles found, retrying...")
        titles = ask_for_titles()
    
    elaborations = []
    for title in titles:
        elaboration = ask_gpt(f"So here I have a step to recovering from an injury. Here's the step: {title['title']} and here's the injury: {realtitle}. Can you give me a 1-2 sentence elaboration on what exactly to do here?")
        elaborations.append(elaboration)
        
    return render_template("progress_map.html", title=realtitle, titles=titles, elaborations=elaborations)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3945, debug = True)
