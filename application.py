
import os, requests, json
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, escape
from models import *
from sqlalchemy import exc

app = Flask(__name__)
app.secret_key = "any random string"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.route("/")
def index():
    if "user_id" in session:
        session.pop("user_id", None)
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    return render_template("register.html")


@app.route("/registrationcomplete", methods=["POST"])
def registrationcomplete():
   
    username = request.form.get("username")
    password = request.form.get("password")

    u = User(username = username, password = password)
    db.session.add(u)
    db.session.commit()

    return render_template("registrationcomplete.html")


@app.route("/login", methods=["POST"])
def login():
    
    return render_template("login.html")


@app.route("/search", methods=["POST"]) 
def search():
    if "user_id" not in session:
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username = username).first()
   
        if user == None:
            return render_template("error.html", message="Username or password does not match.")
        if user.password != password:
            return render_template("error.html", message="Username or password does not match.")
       
        session["user_id"] = user.id

    books = Book.query.all()

    return render_template("search.html", books=books)


@app.route("/book", methods=["POST"])
def book():
    
    try:
        book_id = int(request.form.get("book_id"))
    except ValueError:
        return render_template("error.html", message="Invalid book.")

    book = Book.query.get(book_id)
    if book is None:
        return render_template("error.html", message="No such book.")

    title = book.title
    author = book.author
    publicationyear = book.publicationyear
    isbn = book.isbn
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "pzaPV2a2PfX3QQmrXqWeQ", "isbns": book.isbn})
    book_dict = res.json()
    book_list = book_dict.get("books")
    rating_count = book_list[0].get("ratings_count")
    average_rating = book_list[0].get("average_rating")

    global the_id
    the_id = book_id
    
    reviews = Review.query.filter_by(book_id = book.id).all()

    return render_template("book.html", average_rating=average_rating, rating_count=rating_count, reviews=reviews, book=book, title=title, author=author, publicationyear=publicationyear, isbn=isbn)


@app.route("/review", methods=["POST"])
def review():
      
    book_id = the_id 
    rating = request.form.get("rating")  
    textreview = request.form.get("review")
    
    if "user_id" in session:
        user_id = int(session["user_id"])
    
    user = User.query.filter_by(id = user_id).first() 
    
    check_user = Review.query.filter_by(user_id = user.id).filter_by(book_id = book_id).first()

    if check_user != None:
        if rating != None:
            if check_user.rating != None:
                return render_template("error.html", message="You have already rated this book.")
        if textreview != None:
            if check_user.textreview != None:
                return render_template("error.html", message="You have already reviwed this book.")

    review = Review(user_id=user_id, book_id=book_id, textreview=textreview, rating=rating, username=user.username)
    db.session.add(review)
    db.session.commit()

    return render_template ("review.html")


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("user_id", None)
    return render_template("index.html")


@app.route("/api/<string:book_isbn>")
def book_api(book_isbn):

    book = Book.query.filter_by(isbn = book_isbn).first()

    if book is None:
        return jsonify({"error": "Invalid book_isbn"}), 404
    
    reviews = Review.query.filter_by(book_id = book.id)

    review_count = 0

    for review in reviews:
        if review.textreview != None:
            review_count = review_count + 1

    avg_score = float(0)
    sum = float(0)
    rating_count = float(0)

    for review in reviews:
        if review.rating != None:
            sum = sum + review.rating
            rating_count = rating_count + 1
    
    avg_score = sum/rating_count

    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.publicationyear,
        "isbn": book.isbn,
        "review_count": review_count,
        "average_score": avg_score
    })




