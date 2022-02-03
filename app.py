from bson.objectid import ObjectId
from flask import Flask, render_template, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_DBNAME"] = "moneyfull"
app.config["MONGO_URI"] = "mongodb+srv://surelis:rootUser@myfirstcluster-1cswe.mongodb.net/moneyfull?retryWrites=true"

mongo = PyMongo(app)


@app.route('/')
def get_landing_page():
    return render_template('landing.html', Categories=mongo.db.Categories.find())

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
