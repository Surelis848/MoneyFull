from bson.objectid import ObjectId
from flask import Flask, render_template, request, url_for, redirect, session
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)
app.secret_key = "testing" #change

#change - Make safe
app.config["MONGO_DBNAME"] = "moneyfull"
app.config["MONGO_URI"] = "mongodb+srv://surelis:rootUser@myfirstcluster-1cswe.mongodb.net/moneyfull?retryWrites=true"

mongo = PyMongo(app)


@app.route('/')
def get_landing_page():
    return render_template('landing.html')

@app.route('/register', methods=['post', 'get'])
def get_register_page(): #change - mix up for plagiarism
    message = ''
    if "email" in session:
        return redirect(url_for("get_tracker_page"))
    if request.method == 'POST':
        user = request.form.get("fullname")
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user_found = mongo.db.Users.find_one({"name": user})
        email_found = mongo.db.Users.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('register.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('register.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('register.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            mongo.db.Users.insert_one(user_input)

            user_data = mongo.db.Users.find_one({"email": email})
            session["email"] = user_data['email']

            return redirect(url_for('get_tracker_page'))
    return render_template('register.html')

   # return render_template('register.html', Categories=mongo.db.Categories.find())

@app.route('/login', methods=["POST", "GET"])
def get_login_page():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("get_tracker_page"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        email_found = mongo.db.Users.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']

            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('get_tracker_page'))
            else:
                if "email" in session:
                    return redirect(url_for("get_tracker_page"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        message = 'You are signed out!'
        return render_template("landing.html", message=message)
    else:
        return render_template('landing.html')

@app.route('/tracker')
def get_tracker_page():
    if "email" in session:
        email = session["email"]
        return render_template('tracker.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route('/budget')
def get_budget_page():
    if "email" in session:
        email = session["email"]
        return render_template('budget.html')
    else:
        return redirect(url_for("login"))

@app.route('/trends')
def get_trends_page():
    if "email" in session:
        email = session["email"]
        return render_template('trends.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route('/targets')
def get_targets_page():
    if "email" in session:
        email = session["email"]
        return render_template('targets.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route('/settings')
def get_settings_page():
    if "email" in session:
        email = session["email"]
        return render_template('settings.html', email=email)
    else:
        return redirect(url_for("login"))

@app.route('/help')
def get_help_page():
    if "email" in session:
        email = session["email"]
        return render_template('help.html', email=email)
    else:
        return redirect(url_for("login"))

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
