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
    if "email" in session:
        return redirect(url_for("get_tracker_page"))
    return render_template('landing.html')

@app.route('/register', methods=['post', 'get'])
def get_register_page():
    message = ''
    if "email" in session:
        return redirect(url_for("get_tracker_page"))
    if request.method == 'POST':
        user = request.form.get("fullname")
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        salaryPeriod = request.form.get("salaryPeriod")
        salary = request.form.get("salary")
        otherIncome = request.form.get("otherIncome")
        investments = request.form.get("investments")
        target = request.form.get("target")
        amountNeeded = request.form.get("amountNeeded")
        due = request.form.get("due")
        budgetingSystem = request.form.get("budgetingSystem")

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
            user_input = {'name': user, 'email': email, 'password': hashed,
                          'salaryPeriod': salaryPeriod, 'salary': salary,
                          'otherIncome': otherIncome, 'investments': investments,
                          'target': target, 'amountNeeded': amountNeeded,
                          'due': due, 'budgetingSystem': budgetingSystem}
            mongo.db.Users.insert_one(user_input)

            user_data = mongo.db.Users.find_one({"email": email})
            session["email"] = user_data['email']

            return redirect(url_for('get_tracker_page'))
    return render_template('register.html')

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


@app.route('/tracker', methods=['post', 'get'])
def get_tracker_page():
    if "email" in session:
        email = session["email"]
        user = mongo.db.Users.find_one({"email": email})
        budgetingSystem = user['budgetingSystem']
        if budgetingSystem == 'moneyfullSystem':
            categories = mongo.db.Categories_MoneyFull.find()
        elif budgetingSystem == '50/30/20':
            categories = mongo.db.Categories_50_30_20.find()
        elif budgetingSystem == '70/20/10':
            categories = mongo.db.Categories_70_20_10.find()
        tracker = mongo.db.Tracker
        spending = tracker.find({"email": email}).sort('date', -1)
        date = request.form.get('date')
        if date != None:
            add_item = {
                'date': date,
                # "{:%b, %d %Y}".format(datetime.now()),
                'amount': request.form.get('amount'),
                'description': request.form.get('description'),
                'category': request.form.get('category'),
                'email': email
            }
            tracker.insert_one(add_item)
        return render_template('tracker.html', email=email, user=user, categories=categories, spending=spending)
    else:
        return redirect(url_for("login"))


@app.route('/delete_purchase/<purchase_id>')
def delete_purchase(purchase_id):
    mongo.db.Tracker.delete_one({'_id': ObjectId(purchase_id)})
    return redirect(url_for("get_tracker_page"))


@app.route('/edit_purchase/<purchase_id>')
def edit_purchase(purchase_id):
    mongo.db.Tracker.delete_one({'_id': ObjectId(purchase_id)})
    return redirect(url_for("get_tracker_page"))


# @app.route('/insert_tracker', methods=['POST'])
# def insert_tracker():
#     if "email" in session:
#         email = session["email"]
#         user = mongo.db.Users.find_one({"email": email})
#         tracker = mongo.db.Tracker
#         add_item = {
#             'date': request.form.get('date'),
#         # "{:%b, %d %Y}".format(datetime.now()),
#             'amount': request.form.get('amount'),
#             'description': request.form.get('description'),
#             'category': request.form.get('category'),
#             'email': email
#         }
#         tracker.insert_one(add_item)
#         return render_template('tracker.html', email=email, user=user)
#     else:
#         return redirect(url_for("login"))

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
