# Description: This is the main file that runs the Flask server and handles the API requests. Used for demo purposes.

from flask import Flask, jsonify, render_template
import os
import speech_recognition as sr
from gtts import gTTS
from supabase import create_client
from manualmode import ManualDataEntry 
from gptmode import GPTMode

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI() # See OpenAI documentation for how to set up chatGPT key

app = Flask(__name__)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL") # See Supabase documentation for how to set up Supabase URL and key
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)


# Creating classes of each librarian mode 
gpt = GPTMode()
manual = ManualDataEntry()


@app.route('/')
def index():
    return render_template('index.html')


# Get all current books in the database
@app.route('/get_books')
def get_books():
    books_with_authors = get_the_books_with_authors()
    return jsonify({"books": books_with_authors})


# Run manual mode
@app.route('/run_manual', methods=['POST'])
def run_manual():
    
    manual.main()
    # main()
    return jsonify({"message": "success"}) 


#Run gpt mode
@app.route('/run_main', methods=['POST'])
def run_main():
    
    gpt.main()
    # main()
    return jsonify({"message": "success"}) 


# Get all author names and their id's and put inside a key-value pair
def get_the_author():
    authors = supabase.table('authors').select('author_id', 'author_name').execute().data
    author_dict = {}
    for author in authors:
        author_dict[author['author_id']] = author['author_name']

    return author_dict


# Get the corresponding authors in the book_authors connecting table
def get_authors_for_book(book_id):
    authors = supabase.table('book_authors').select('author_id').eq('book_id', book_id).execute().data
    author_dict = get_the_author()
    author_names = [author_dict.get(author['author_id']) for author in authors]
    return author_names


# Get the book that belongs to the respective author
def get_the_books_with_authors():
    books = supabase.table('books').select('book_id', 'title', 'description').execute().data
    books_with_authors = []
    for book in books:
        book_id = book['book_id']
        book_title = book['title']
        description = book['description']
        authors = get_authors_for_book(book_id)
        books_with_authors.append({"title": book_title, "intro": description, "authors": authors})
    
    return books_with_authors



if __name__ == "__main__":
    app.run(debug=True)
    # main()
    # val = ManualDataEntry()
    # val.main()
