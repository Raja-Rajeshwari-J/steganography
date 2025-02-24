from flask import Flask, render_template
from encrypt import encrypt_route
from decrypt import decrypt_route

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/encrypt", methods=["POST"])
def encrypt():
    return encrypt_route()

@app.route("/decrypt", methods=["POST"])
def decrypt():
    return decrypt_route()

if __name__ == "__main__":
    app.run(debug=True)
