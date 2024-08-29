from flask import Flask, redirect, render_template, url_for, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

import os
from markdown import markdown

load_dotenv('.env')
genai.configure(api_key="AIzaSyAgxBM2LpvW4bNmtM8MNWSI1KSOJyTTymI")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=safety_settings,
    generation_config=generation_config,
    system_instruction="You are \"The Wellbeing Assistant\" for Our Own High School. Maintain a conversational tone. do not overwhelm with too much information. If a student comes with a problem, first comfort them and then ask them thier name followed by the grade and section. if they are anxious about something that is unlikely to happen. ask them to check out \"Zycho - The Anxiety Analyzer\". and if they need to talk to a real person recommend them to a counsellor. and when ONLY JUST said \"rel\". make a list in the format [name,grade&section,problem(in one word),severity(out of 5)] AND DO NOT SAY ANYTHING ELSE. Example: [John,10A,Bullying,3].",
)

chat_model = model.start_chat(history=[])  # chat based on history

img_model = genai.GenerativeModel('gemini-pro-vision')

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


# Text to text
fh = open("xyz.txt","a")


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        query = request.json['query']
        if (len(query.strip()) == 0):
            return jsonify("Please enter something!")

        gemini_response = chat_model.send_message(query).text
        if "[" in gemini_response:
            fh.write(gemini_response + "\n")
            # Send message based on the chat his


        return jsonify(markdown(gemini_response))
    else:
        return render_template("chats.html")


# Image to text


@app.route("/image_chat", methods=['POST', 'GET'])
def image_chat():
    if request.method == 'POST':
        img = request.files['image']  # Loads the file
        q = request.form['query']  # Loads the query

        image = Image.open(img)  # Read the image in PIL format
        try:
            response = img_model.generate_content(
                [q, image])  # Generate content for the image
        except:
            return jsonify("Something went wrong!")
        return jsonify(markdown(response.text))
    else:
        return render_template("image_upload.html")


if __name__ == "__main__":
    app.run(port=8080, debug=True)
