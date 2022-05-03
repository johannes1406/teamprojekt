from flask import Flask, request
app = Flask(__name__)
@app.route('/')  # this is the home page route
def hello_world():  # this is the home page function that generates the page code
    return "Teamprojekt"