from html.entities import name2codepoint
from pickle import FALSE
import re
import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_mail import Mail, Message
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required
from cs50 import SQL
from base64 import b64encode

from werkzeug.utils import secure_filename
app = Flask(__name__)

app.config['MAIL_SERVER']= 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'makers.place@hotmail.com'
app.config['MAIL_PASSWORD'] = 'makersplace123' #os.environ["MAIL_PASSWORD"]
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_DEBUG'] = True
app.config['MAIL_SUPRESS_SEND'] = False
app.config['SECURECONNECTION']=FALSE


# db = SQL("sqlite:///makersplace.db")
db = SQL("postgresql://wkmuqbrtzfrpfj:4c599a25d03303fafca91c62b3f4acf2859d49fdf261cc85572e0a64d86e5c35@ec2-54-147-36-107.compute-1.amazonaws.com:5432/ddfu28nlqel0ts")


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mail = Mail(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    #set the session of user id to a variable
    id = session["user_id"]
 

    return render_template("index.html")

    # total_value = db.execute("SELECT sum(transaction_value) FROM transactions WHERE user_id = :user_id", user_id=session["user_id"])



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        email = request.form.get("email")
        description = request.form.get("description")
        location = request.form.get("location")
        number = request.form.get("number")

        if not username:
            flash("Must provide valid username", "alert-warning")
        elif not password or not confirmation:
            flash("Must provide valid password", "alert-warning")
        elif password != confirmation:
            flash("Password must match confirm password", "alert-warning")

        if password != confirmation:
            flash("Passwords do not match")

        if not email:
            flash("must provide valid email", "alert-warning")

        if not description:
            flash("must provide valid description", "alert-warning")

        if not location:
            flash("must provide valid location", "alert-warning")

        if not number:
            flash("must provide valid number", "alert-warning")


        hash = generate_password_hash(password)

        try:
            print("executing")
            db.execute("INSERT INTO users(username, hash, email, description, location, number) VALUES (?,?,?,?,?,?)", username, hash, email, description, location, number)
            return redirect("/")
        except Exception as e:
            print(e)
            flash("Username has already been registered!")


        return render_template("")


    else:
        return render_template("register.html")


@app.route("/listing")
@login_required
def listing():
    return render_template("listing.html")

@app.route("/listingproduct",methods=["GET", "POST"])
@login_required
def listingproduct():
    if request.method == "POST":
        id = session["user_id"]
        name = request.form.get("name")
        location = request.form.get("location")
        email = request.form.get("email")
        number = request.form.get("number")
        description = request.form.get("description")
        budget = request.form.get("budget")
        meetup = request.form.getlist("meetup")
        delivery = request.form.getlist("delivery")
        file = request.files['file']

        if (meetup == []):
            meetup = "No"

        if (delivery == []):
            delivery = "No"
        
        
        db.execute("INSERT INTO productlistings(id,name,location,email,number,description,budget,meetup,delivery,filename,data) VALUES(?,?,?,?,?,?,?,?,?,?,?)",id,name,location,email,number,description,budget,meetup,delivery,file.filename,file.read())
        return render_template("product.html")

        
    else:
        return render_template("listingproduct.html")

@app.route("/listingvendor", methods=["GET", "POST"])
@login_required
def listingvendor():
    if request.method == "POST":
        id = session["user_id"]
        name = request.form.get("name")
        location = request.form.get("location")
        email = request.form.get("email")
        number = request.form.get("number")
        website = request.form.get("website")
        description = request.form.get("description")
        meetup = request.form.getlist("meetup")
        delivery = request.form.getlist("delivery")
        file = request.files['file']


        if (meetup == []):
            meetup = "No"

        if (delivery == []):
            delivery = "No"


        db.execute("INSERT INTO vendorlistings (id,name,location,email,number,website,description,meetup, delivery,filename,data) VALUES(?,?,?,?,?,?,?,?,?,?,?)",id,name,location,email,number,website,description,meetup,delivery,file.filename,file.read())
        print(meetup)
        print(delivery)

        return render_template("vendor.html")

    else:
        return render_template("listingvendor.html")

@app.route("/account")
@login_required
def account():
    #set the session of user id to a variable

    users = db.execute("SELECT * FROM users WHERE id = :id",id=session["user_id"])[0]
    return render_template("account.html", users=users)


@app.route("/test")
@login_required
def test():
    #set the session of user id to a variable
    return render_template("test.html")

@app.route("/vendor")
@login_required
def vendor():
    vendorlistings = db.execute("SELECT * FROM vendorlistings")
    data_list=[]
    for data in vendorlistings:
        # Here we are encoding the image and then send this image sepatately like image=image to the templates
        try:
            image = b64encode(data['data']).decode("utf-8")
        except:
            image=''
        data_list.append(
            [data['id'],data['name'],data['location'],data['email'],
             data['number'],data['website'],data['description'],
             data['meetup'],data['delivery'],data['filename'],image
                          ])


    return render_template("vendor.html", vendorlistings=vendorlistings,data_list=data_list)

@app.route("/favourites")
@login_required
def favourites():
    return render_template("favourites.html")

@app.route("/product", methods=['GET','POST'])
@login_required
def product():

    if request.method == 'POST':
        title=request.form.get("title")
        email = request.form.get("email")
        body= request.form.get("body")
        
        msg = Message(title, sender = 'makers.place@hotmail.com', recipients = [email])
        msg.body = body
        mail.send(msg)
        return "Sent email."

        return render_template("product.html")

        # with app.open_resource('cat.jpeg') as cat:
        #     msg.attach('cat3.jpeg', 'image/jpeg', cat.read())
        # mail.send(msg)
        # return "Sent email."
    else:

        productlistings = db.execute("SELECT * FROM productlistings")
        data_list=[]
        for data in productlistings:
        # Here we are encoding the image and then send this image sepatately like image=image to the templates
            try:
                image = b64encode(data['data']).decode("utf-8")
            except:
                image=''
            data_list.append(
                [data['id'],data['name'],data['location'],data['email'],
                data['number'],data['description'],data['budget'],
                data['meetup'],data['delivery'],data['filename'],image
                          ])

        return render_template("product.html", productlistings=productlistings,data_list=data_list)



@app.route("/upload", methods=['GET','POST'])
def uploadFile():
    if request.method == 'POST':
        file = request.files['file']
        db.execute("insert into vendorlistings (filename,data) values(?,?)",file.filename,file.read())
        #upload = Upload(filename=file.filename, data=file.read())
        #db.session.add(upload)
        #db.session.commit()
        return f'Uploaded: {file.filename}'
    return render_template('upload.html')

@app.route("/mylistings")
@login_required
def mylistings():


    productlistings = db.execute("SELECT * FROM productlistings WHERE id = :id",id=session["user_id"])
    id = db.execute("SELECT id FROM users WHERE id = :id",id=session["user_id"])[0]
    print(id)


    try:
        db.execute("SELECT id FROM productlistings WHERE id = :id",id=session["user_id"])[0] or db.execute("SELECT id FROM vendorlistings WHERE id = :id",id=session["user_id"])[0]
    except:
        flash("You have no product listings or no vendor listings")



    from base64 import b64encode
    data_list_product=[]
    for data in productlistings:
        # Here we are encoding the image and then send this image sepatately like image=image to the templates
        try:
            image = b64encode(data['data']).decode("utf-8")
        except:
            image=''
        data_list_product.append(
            [data['id'],data['name'],data['location'],data['email'],
             data['number'],data['description'],data['budget'],
             data['meetup'],data['delivery'],data['filename'],image
                          ])


    vendorlistings = db.execute("SELECT * FROM vendorlistings WHERE id = :id",id=session["user_id"])
    from base64 import b64encode
    data_list_vendor=[]
    for data in vendorlistings:
        # Here we are encoding the image and then send this image sepatately like image=image to the templates
        try:
            image = b64encode(data['data']).decode("utf-8")
        except:
            image=''
        data_list_vendor.append(
            [data['id'],data['name'],data['location'],data['email'],
             data['number'],data['website'],data['description'],
             data['meetup'],data['delivery'],data['filename'],image
                          ])



    return render_template("mylistings.html", productlistings=productlistings,data_list_product=data_list_product, vendorlistings=vendorlistings,data_list_vendor=data_list_vendor)


@app.route("/delete", methods = ["POST"])
def delete():

    #Delete entry
    email = request.form.get("email")
    number = request.form.get("number")

    if number:
        db.execute("DELETE FROM productlistings WHERE number = ?", number)
    if email:
        db.execute("DELETE FROM vendorlistings WHERE email = ?", email)


    return redirect("/mylistings")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)