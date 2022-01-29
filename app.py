import os
from flask import Flask, render_template


app = Flask(__name__)


@app.route('/get_landing_page')
def get_landing_page():
    return render_template("index.html")


# Main function for running the app

if __name__ == "__main__":
    #app.secret_key = 'mysecret',
    app.debug = os.environ.get('FLASK_DEBUG', True)
    app.run(port=7000)
    #app.run(
            #host=os.environ.get('0.0.0.0'),
            #port=int(os.environ.get(5000)),
            #debug=True)
