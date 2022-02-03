from bson.objectid import ObjectId
from flask import Flask, render_template, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "moneyfull"
app.config["MONGO_URI"] = "mongodb+srv://surelis:rootUser@myfirstcluster-1cswe.mongodb.net/moneyfull?retryWrites=true"

mongo = PyMongo(app)


@app.route('/')
def get_landing_page():
    return render_template('landing.html')

@app.route('/register')
def get_register_page():
    return render_template('register.html', Categories=mongo.db.Categories.find())

@app.route('/login')
def get_login_page():
    return render_template('login.html')

@app.route('/tracker')
def get_tracker_page():
    return render_template('tracker.html')

@app.route('/budget')
def get_budget_page():
    return render_template('budget.html')

@app.route('/trends')
def get_trends_page():
    return render_template('trends.html')

@app.route('/targets')
def get_targets_page():
    return render_template('targets.html')

@app.route('/settings')
def get_settings_page():
    return render_template('settings.html')

@app.route('/help')
def get_help_page():
    return render_template('help.html')

@app.route('/error')
def get_error_page():
    return render_template('error.html')

#@app.route('/add_test')
#def add_test():
#    mongo.db.Categories.insert_one({'title': "Rent"})
#    return jsonify(message="success")


# Main function for running the app

if __name__ == "__main__":
    app.run(port=7000, host='0.0.0.0', debug=True)
    #app.run(
            #host=os.environ.get('0.0.0.0'),
            #port=int(os.environ.get(5000)),
            #debug=True)
