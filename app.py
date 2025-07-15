from flask import Flask,render_template,request
import requests
from bs4 import BeautifulSoup
import re
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

load_dotenv()

SERPAPI_KEY = os.getenv("SERP_API_KEY")

app = Flask(__name__)



def get_business_website(business_name, location):
    query = f"{business_name} {location}"
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": 1
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if "organic_results" in data and data["organic_results"]:
            return data["organic_results"][0].get("link", "Website not found")
        else:
            return "Website not found"

    except Exception as e:
        print("Website fetch error:", e)
        return "Website not found"


def extract_email_from_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "lxml")

        
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", soup.get_text())
        return emails[0] if emails else "Email not found"
    except Exception as e:
        print("Email scraping error:", e)
        return "Email not found"
    




client = InferenceClient(token=os.getenv("HF_API_KEY"))

def generate_outreach_email(business_name, location):
    prompt = (
        f"Write a short and polite outreach email to the business named {business_name} located in {location}. "
        "Keep it professional and end with 'Best regards'."
    )
    try:
        response = client.text_generation(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            prompt=prompt,
            max_new_tokens=200,
            temperature=0.7,
        )
        print("HF response:", response)
        return response.strip()
    except Exception as e:
        print("HF API error:", e)
        return "Could not generate email."



    

@app.route("/",methods =['GET'])
def home():
    return render_template("home.html")

@app.route("/submit",methods=['POST','GET'])
def submit():
    
    business_name = request.form.get('business_name')
    location = request.form.get('location')
        
    website = get_business_website(business_name, location)
    email = extract_email_from_website(website) if "http" in website else "Email not found"

    outreach_email = generate_outreach_email(business_name, location)

    return render_template("home.html", outreach_email=outreach_email)

if __name__=="__main__":
    app.run(host = '0.0.0.0',debug = True)
    