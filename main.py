from flask import Flask, request
app = Flask(__name__)

print("Teamprojekt")


@app.route('/')
def hello_world():
    return "Teamprojekt"
