from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Reemplaza 'index.html' con el nombre de tu template

# Otras rutas y funciones pueden ir aquí

if __name__ == '__main__':
    app.run(debug=True)