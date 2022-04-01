from datetime import datetime
from bson.objectid import ObjectId
from flask import Flask, render_template, request, url_for, redirect, session
from flask_pymongo import PyMongo
import bcrypt
import json
from bson import json_util

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

        currentDate = datetime.now().strftime("%Y-%m-%d")
        salaryPeriod = request.form.get("salaryPeriod")
        salary = request.form.get("salary")
        otherIncome = request.form.get("otherIncome")
        savings = request.form.get("savings")
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
                          'otherIncome': otherIncome, 'savings': savings, 'investments': investments,
                          'target': target, 'amountNeeded': amountNeeded, 'targetProgress': '0',
                          'due': due, 'budgetingSystem': budgetingSystem, 'enteredDate': currentDate}
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
        current_month = int(datetime.now().strftime('%m'))
        budgetingSystem = user['budgetingSystem']
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
                 "November", "December"];
        if budgetingSystem == 'moneyfullSystem':
            categories = mongo.db.Categories_MoneyFull.find()
        elif budgetingSystem == '50/30/20':
            categories = mongo.db.Categories_50_30_20.find()
        elif budgetingSystem == '70/20/10':
            categories = mongo.db.Categories_70_20_10.find()
        elif budgetingSystem == 'custom':
            categories = mongo.db.user.categories.find()
        tracker = mongo.db.Tracker
        spending = tracker.find({"email": email}).sort('date', -1)
        spending_list = []
        for entry in spending:
            date = entry["date"]
            datem = datetime.strptime(date, "%Y-%m-%d")
            day = int(datem.day)
            month = int(datem.month)
            year = int(datem.year)
            spend = {'year': year, 'month': month, 'day': day, 'amount': entry['amount'], 'description': entry['description'],
                     'category': entry['category']}
            spending_list.append(spend)
        date = request.form.get('date')
        if date != None:
            add_item = {
                'date': date,
                'amount': request.form.get('amount'),
                'description': request.form.get('description'),
                'category': request.form.get('category'),
                'email': email
            }
            tracker.insert_one(add_item)
        return render_template('tracker.html', email=email, user=user, categories=categories, spending=spending_list, current_month=current_month,
                               months=months)
    else:
        return redirect(url_for("get_login_page"))


@app.route('/delete_purchase/<purchase_id>')
def delete_purchase(purchase_id):
    mongo.db.Tracker.delete_one({'_id': ObjectId(purchase_id)})
    return redirect(url_for("get_tracker_page"))


@app.route('/edit_purchases')
def edit_purchases():
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
        elif budgetingSystem == 'custom':
            categories = mongo.db.user.categories.find()
        categories_list = []
        for c in categories:
            categories_list.append(c['title'])
        tracker = mongo.db.Tracker
        spending = tracker.find({"email": email}).sort('date', -1)
        date = request.form.get('date')
        if date != None:
            add_item = {
                'date': date,
                'amount': request.form.get('amount'),
                'description': request.form.get('description'),
                'category': request.form.get('category'),
                'email': email
            }
            tracker.insert_one(add_item)
        return render_template('tracker_edit.html', email=email, user=user, spending=spending, categories=categories_list)
    else:
        return redirect(url_for("get_login_page"))


@app.route('/update_purchases/<purchase_id>', methods=["POST"])
def update_purchases(purchase_id):
    if "email" in session:
        email = session["email"]
        spending = mongo.db.Tracker
        spending.replace_one({'_id': ObjectId(purchase_id)},
                        {
                            'date': request.form.get('date'),
                            'amount': request.form.get('amount'),
                            'description': request.form.get('description'),
                            'category': request.form.get('category'),
                            'email': email
                        })
        return redirect(url_for('get_tracker_page'))
    else:
        return redirect(url_for('get_login_page'))


@app.route('/budget')
def get_budget_page():
    if "email" in session:
        email = session["email"]
        user = mongo.db.Users.find_one({"email": email})
        salary = int(user['salary'])
        salaryf = f'{salary:,}'
        current_month = int(datetime.now().strftime('%m'))
        budgetingSystem = user['budgetingSystem']
        if budgetingSystem == 'moneyfullSystem':
            categories = mongo.db.Categories_MoneyFull.find()
        elif budgetingSystem == '50/30/20':
            categories = mongo.db.Categories_50_30_20.find()
        elif budgetingSystem == '70/20/10':
            categories = mongo.db.Categories_70_20_10.find()
        elif budgetingSystem == 'custom':
            categories = mongo.db.user.categories.find()
        categories_list = []
        for c in categories:
            category = {'title': c['title'], 'percentage': int(c['percentage']), 'catsalary': salary*int(c['percentage'])/100}
            categories_list.append(category)
        tracker = mongo.db.Tracker.find({"email": email})
        spending_list = []
        for entry in tracker:
            date = entry["date"]
            datem = datetime.strptime(date, "%Y-%m-%d")
            month = int(datem.month)
            spend = {'date': month, 'category': entry['category'], 'amount': entry['amount']}
            spending_list.append(spend)
        categoryShare = 0
        categoryPercentage = 0
        return render_template('budget.html', email=email,
                                            user=user,
                                            categories_list=categories_list,
                                            budgetingSystem=budgetingSystem,
                                            salary=salary,
                                            spending=spending_list,
                                            categoryShare=categoryShare,
                                            categoryPercentage=categoryPercentage,
                                            currentMonth=current_month,
                                            salaryf=salaryf)
    else:
        return redirect(url_for("get_login_page"))


@app.route('/edit_categories')
def edit_categories():
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
        elif budgetingSystem == 'custom':
            categories = mongo.db.user.categories.find()
        return render_template('budget_edit.html', email=email, user=user, categories=categories)
    else:
        return redirect(url_for("get_login_page"))


@app.route('/trends')
def get_trends_page():
    if "email" in session:
        email = session["email"]
        tracker = mongo.db.Tracker.find_one({"email": email})
        message = "You currently have no spending tracked. Please add your purchases in the 'Tracker' tab"
        return render_template('trends.html', email=email, tracker=tracker, message=message)
    else:
        return redirect(url_for("get_login_page"))


@app.route('/moneyfull/Tracker')
def get_moneyfull_Tracker():
    email = session["email"]
    tracker = mongo.db.Tracker.find({"email": email})
    json_spending = []
    for spend in tracker:
        json_spending.append(spend)
    json_spending = json.dumps(json_spending, default=json_util.default)
    return json_spending


@app.route('/targets', methods=["POST", "GET"])
def get_targets_page():
    if "email" in session:
        email = session["email"]
        user = mongo.db.Users
        particularUser = user.find_one({"email": email})
        target = particularUser["target"]
        targetProgress = int(particularUser["targetProgress"])
        startedDate = datetime.strptime(particularUser["enteredDate"], "%Y-%m-%d")
        startedDateNoTime = startedDate.date()
        amountNeeded = f'{int(particularUser["amountNeeded"]):,}'
        due = datetime.strptime(particularUser["due"], "%Y-%m-%d")
        dueNoTime = due.date()
        currentDate = datetime.now().strftime("%Y-%m-%d")
        currentDated = datetime.strptime(currentDate, "%Y-%m-%d")
        difference = due - currentDated
        daysLeft = difference.days
        monthsLeft = (due.year - currentDated.year) * 12 + (due.month - currentDated.month)
        monthsFromBegining = (due.year - startedDate.year) * 12 + (due.month - startedDate.month)
        monthsPassed = monthsFromBegining - monthsLeft
        monthlyAmountNeeded = int(particularUser["amountNeeded"]) / int(monthsFromBegining)
        amountProgress = int(particularUser["amountNeeded"]) * targetProgress / 100
        amountProgressF = f'{int(amountProgress):,}'

        if int(amountProgress) >= int(particularUser["amountNeeded"]):
            status = "Target Reached"
        elif amountProgress > monthsPassed * monthlyAmountNeeded:
            status = "Ahead"
        elif amountProgress == monthsPassed * monthlyAmountNeeded:
            status = "On Target"
        elif amountProgress < monthsPassed * monthlyAmountNeeded:
            status = "Behind"

        return render_template('targets.html', email=email, target=target, amountNeeded=amountNeeded,
                               due=dueNoTime, daysLeft=daysLeft, monthsLeft=monthsLeft, monthlyAmountNeeded=monthlyAmountNeeded,
                               targetProgress=targetProgress, startedDate=startedDateNoTime, status=status, amountProgress=amountProgressF)
    else:
        return redirect(url_for("get_login_page"))


@app.route('/update_goal_progress/', methods=["POST"])
def update_goal_progress():
    if "email" in session:
        email = session["email"]
        user = mongo.db.Users
        particularUser = user.find_one({"email": email})
        objectID = particularUser["_id"]
        targetProgress = int(particularUser["targetProgress"])
        amountProgress = int(particularUser["amountNeeded"]) * targetProgress / 100

        addProgress = request.form.get('addProgress')
        newProgress = (amountProgress + float(addProgress)) * 100 / int(particularUser["amountNeeded"])

        user.update_one({'_id': objectID}, {"$set": {'targetProgress': newProgress}})

        return redirect(url_for('get_targets_page'))
    else:
        return redirect(url_for('get_login_page'))


@app.route('/update_goal_date/', methods=["POST"])
def update_goal_date():
    if "email" in session:
        email = session["email"]
        user = mongo.db.Users
        particularUser = user.find_one({"email": email})
        objectID = particularUser["_id"]

        currentDate = datetime.now().strftime("%Y-%m-%d")

        user.update_one({'_id': objectID}, {"$set": {'enteredDate': currentDate}})

        return redirect(url_for('get_targets_page'))
    else:
        return redirect(url_for('get_login_page'))


@app.route('/update_goal_progress_zero/', methods=["POST"])
def update_goal_progress_zero():
    if "email" in session:
        email = session["email"]
        user = mongo.db.Users
        particularUser = user.find_one({"email": email})
        objectID = particularUser["_id"]

        user.update_one({'_id': objectID}, {"$set": {'targetProgress': '0'}})

        return redirect(url_for('get_targets_page'))
    else:
        return redirect(url_for('get_login_page'))


@app.route('/settings')
def get_settings_page():
    if "email" in session:
        email = session["email"]
        user = mongo.db.Users.find_one({"email": email})
        name = user['name']
        password = user['password']
        savings = user['savings']
        salaryPeriod = user['salaryPeriod']
        salary = user['salary']
        otherIncome = user['otherIncome']
        investments = user['investments']
        target = user['target']
        targetProgress = user['targetProgress']
        amountNeeded = user['amountNeeded']
        due = user['due']
        enteredDate = user["enteredDate"]
        budgetingSystem = user['budgetingSystem']
        salaryPeriods = mongo.db.salaryPeriods.find()
        savingTargets = mongo.db.savingTargets.find()
        Categories = mongo.db.Categories.find()
        return render_template('settings.html', email=email,
                                                user=user,
                                                budgetingSystem=budgetingSystem,
                                                name=name,
                                                password=password,
                                                savings=savings,
                                                salaryPeriod=salaryPeriod,
                                                salary=salary,
                                                otherIncome=otherIncome,
                                                investments=investments,
                                                target=target,
                                                targetProgress=targetProgress,
                                                amountNeeded=amountNeeded,
                                                due=due,
                                                enteredDate=enteredDate,
                                                salaryPeriods=salaryPeriods,
                                                savingTargets=savingTargets,
                                                Categories=Categories)
    else:
        return redirect(url_for("get_login_page"))


@app.route('/update_user/', methods=["POST"])
def update_user():
    if "email" in session:
        email = session["email"]
        user = mongo.db.Users.find_one({"email": email})

        name = user['name']
        password = user['password']
        savings = user['savings']
        salaryPeriod = user['salaryPeriod']
        salary = user['salary']
        otherIncome = user['otherIncome']
        investments = user['investments']
        target = user['target']
        targetProgress = user['targetProgress']
        amountNeeded = user['amountNeeded']
        due = user['due']
        enteredDate = user["enteredDate"]
        budgetingSystem = user['budgetingSystem']
        salaryPeriods = mongo.db.salaryPeriods.find()
        savingTargets = mongo.db.savingTargets.find()
        Categories = mongo.db.Categories.find()

        currentPassword = user['password']
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        password3 = request.form.get("password3")

        if password1 == '' and password2 == '' and password3 == '':
            password = user['password']
        elif not bcrypt.checkpw(password1.encode('utf-8'), currentPassword):
            message = 'Wrong current password'
            return render_template('settings.html', email=email,
                                   user=user,
                                   budgetingSystem=budgetingSystem,
                                   name=name,
                                   password=password,
                                   savings=savings,
                                   salaryPeriod=salaryPeriod,
                                   salary=salary,
                                   otherIncome=otherIncome,
                                   investments=investments,
                                   target=target,
                                   targetProgress=targetProgress,
                                   amountNeeded=amountNeeded,
                                   due=due,
                                   enteredDate=enteredDate,
                                   salaryPeriods=salaryPeriods,
                                   savingTargets=savingTargets,
                                   Categories=Categories,
                                   message=message)
        elif password2 == '' and password3 == '':
            password = user['password']
        elif password2 != password3:
            message = 'Passwords should match!'
            return render_template('settings.html', email=email,
                                   user=user,
                                   budgetingSystem=budgetingSystem,
                                   name=name,
                                   password=password,
                                   savings=savings,
                                   salaryPeriod=salaryPeriod,
                                   salary=salary,
                                   otherIncome=otherIncome,
                                   investments=investments,
                                   target=target,
                                   targetProgress=targetProgress,
                                   amountNeeded=amountNeeded,
                                   due=due,
                                   enteredDate=enteredDate,
                                   salaryPeriods=salaryPeriods,
                                   savingTargets=savingTargets,
                                   Categories=Categories,
                                   message=message)
        else:
            password = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())

        user_id = user["_id"]
        mongo.db.Users.replace_one({'_id': user_id},
                        {
                            'name': user['name'],
                            'email': email,
                            'password': password,
                            'salaryPeriod': request.form.get('salaryPeriod'),
                            'salary': request.form.get('salary'),
                            'otherIncome': request.form.get('otherIncome'),
                            'savings': request.form.get('savings'),
                            'investments': request.form.get('investments'),
                            'target': request.form.get('target'),
                            'targetProgress': targetProgress,
                            'amountNeeded': request.form.get('amountNeeded'),
                            'due': request.form.get('due'),
                            'enteredDate': enteredDate,
                            'budgetingSystem': request.form.get('budgetingSystem')
                        })
        return redirect(url_for('get_settings_page'))
    else:
        return redirect(url_for('get_login_page'))


@app.route('/help', methods=["POST", "GET"])
def get_help_page():
    if "email" in session:
        email = session["email"]
        return render_template('help.html', email=email)
    else:
        return redirect(url_for("get_login_page"))


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
