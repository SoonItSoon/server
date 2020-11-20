from flask import Flask, render_template

app = Flask("Hello World!")

@app.route("/")
def home():
    print("[S_sendServerData] REST request : '/'")
    return render_template("home.html")


app.run(host="203.253.25.184", port=8080)

