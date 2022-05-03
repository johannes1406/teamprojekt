from flask import app

print("Teamprojekt")

@app.route('/')
def hello_world():
    return "Teamprojekt"