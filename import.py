#this is like import1.py
#uses python classes instead of sql

import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, publicationyear in reader:
        db.execute("INSERT INTO books (isbn, title, author, publicationyear) VALUES (:isbn, :title, :author, :publicationyear)",
                   {"isbn": isbn, "title": title, "author": author, "publicationyear": publicationyear})
        print(f"Added book isbn {isbn} title {title} author {author} publicationyear {publicationyear}.")
    db.commit()

if __name__ == "__main__":
    main()
