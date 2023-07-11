from flask import Flask, render_template

# Instancia de Flask
app = Flask(__name__)

# rutas
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", username=name)

# Errores
# Invalid URL

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Server Exception

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500