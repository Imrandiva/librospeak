import os
import time
import re
import playsound
import speech_recognition as sr
from gtts import gTTS
from supabase import create_client
from openai import OpenAI


# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)



bookID = 0

class BookEntry:
    book_title = 'No title added'
    book_author = 'No author added'
    book_info = 'No information added.'
    book_ID = -1
    def __init__(self, ID):
        self.book_ID = ID
    def add_book(self, title):
        self.book_title = title
    def add_author(self, author):
        self.book_author = author
    def add_info(self,info):
        self.book_info = info

recognizer = sr.Recognizer()

class ManualDataEntry:

    def __init__(self):
        self.client = OpenAI()
        
    def speak(self,text): #success
        tts = gTTS(text=text,lang='en')
        filename = 'outputvoice.mp3'
        tts.save(filename)
        playsound.playsound(filename)
        if os.path.exists(filename):
            os.remove(filename)
        else:
            print("The file does not exist")

    # OpenAI TTS
    def openai_speak(self, to_speak):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=to_speak
        )
        audio_data = response.content
        with open("temp.mp3", "wb") as f:
            f.write(audio_data)
        playsound.playsound("temp.mp3")
        os.remove("temp.mp3")

    # Get the audio input using the microphone
    def get_audio(self):
        with sr.Microphone() as source:
            print("Start speaking...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source,  phrase_time_limit=20)
            said = ""
            try:
                said = recognizer.recognize_google(audio)
                print(f"You said: {said}")
            except Exception as e:
                print("Exception: " + str(e))
        return said

    # Connect to the database
    def insert_to_database(self, booktemp):

        book_title = booktemp.book_title
        authors = booktemp.book_author
        abstract = booktemp.book_info

        # Insert book
        book = supabase.table('books').insert({'title': book_title, 'description': abstract}).execute()
        book_id = book.data[0]['book_id']
        
        # Insert authors
        author_ids = []

        authors = authors.split(' and ')

        print(authors)
        for author_name in authors:
            
            author = supabase.table('authors').select('author_id').eq('author_name', author_name).execute()
            if len(author.data) == 0:    
                author = supabase.table('authors').insert({'author_name': author_name}).execute()
            
            print(author.data[0]['author_id'])
            author_ids.append(author.data[0]['author_id'])
        
        # Link authors with book
        for author_id in author_ids:
            supabase.table('book_authors').insert({'author_id': author_id, 'book_id': book_id}).execute()


        print("Data inserted successfully.")



    # Extract the book title and author from the input
    def extract(self,text):
        words = []
        author_match = False
        title_match = False
        title_exist = re.search(r'title', text)
        author_exist = re.search(r'author', text)
        if title_exist and author_exist:
            if title_exist.start() < author_exist.start():
                title_match = re.search(r'title (of the book )?(is|should be) (.+) (((and)? (the )?author(s)?)|,)', text) # allows "and" in title and author
                author_match = re.search(r'author(s)? (of the book )?(is|are|should be) (.+)', text)
            else:
                title_match = re.search(r'title (of the book )?(is|should be) (.+)', text)
                author_match = re.search(r'author(s)? (of the book)?(is|are|should be) (.+) (((and)? (the )?title)|,)', text)
        elif title_exist:
            title_match = re.search(r'title (of the book )?(is|are|should be) (.+)( not| rather than)?', text)
        elif author_exist:
            author_match = re.search(r'author(s)? (of the book )?(is|are|should be) (.+)', text)
        else:
            self.speak("Sorry I don't understand what you said")
        title = title_match.group(3) if title_match else 'None Book Title'
        author = author_match.group(4) if author_match else 'None Book Author'
        words = (title,author)

        return words

    # Listen to the user's input
    def listen(self,bookID):
        # connection = self.connect_to_database()
        status = -3

        ## TO-DO: handle RFID tag and update the bookID

        # if capable of reading RFID
        booktemp = BookEntry(bookID) ## TO-DO: find the book in DB that is the ID so that we can modify the entry accordingly, or create a new one
        ## TO-DO: Check whether the book has already been added. If added, read out the information and tells already added.
        said = ""
        start_time = time.time()
        elapsed_time = 0

        while said == "" and elapsed_time < 10: ###  handle long blank waiting
            said = self.get_audio()  
            end_time = time.time()
            elapsed_time = end_time - start_time
        if elapsed_time >30 and said == "":
            self.speak("Are you still there?")
            said_temp = self.get_audio()
            if "yes" not in said_temp:
                return -2
            
        if said == "":
            return -1
        # work on non-information text
        if "quit"in said:
            return 0

        # work on book information
        if "title" in said:
            current_title, current_author = self.extract(said)
            booktemp.add_book(current_title)
            if "author" in said:
                booktemp.add_author(current_author)
            else:
                self.speak("Please tell me the author of the book "+current_title)
                ## Problem: what if this one still don't get an author? --> may be just leave it blank, or 
                ## may be return a status that will lead back to listen with corresponding ID, and add author.
                said = ""
                said = self.get_audio()  
                _, current_author = self.extract(said)
                booktemp.add_author(current_author)

            # confirm + store the book in database
            self.speak("Do you want to add book "+current_title+ "written by "+current_author +"?")
            said = self.get_audio()
            if "yes" in said:
                #Request book abstract/ introduction requestinfo()
                self.speak("Do you want to add an abstract or introduction of the book "+current_title+"?")
                said = self.get_audio() 
                if "yes" in said:
                    self.speak("Okay, say the abstract or introduction now.")
                    intro = self.get_audio() 
                    booktemp.add_info(intro)
                else:
                    self.speak("No introduction is added.")

                print(booktemp)
                self.insert_to_database(booktemp)
                self.speak("You has successfully added "+current_title+ "written by "+current_author)
                return 1
            else:
                # retry collect book title or author
                self.speak("Sorry for not collecting right information, please update book title or author you want.")
                said = self.get_audio()
                temp_title, temp_author = self.extract(said)
                if temp_title != 'None Book Title':
                    booktemp.add_book(temp_title)
                if temp_author != 'None Book Author':
                    booktemp.add_author(temp_author)
                self.speak("Do you want to add "+booktemp.book_title+ "written by "+booktemp.book_author+"?")
                said = self.get_audio()
                if "no" in said:
                    return 2

                #Request book abstract/ introduction requestinfo()
                self.speak("Do you want to add an abstract or introduction of the book "+current_title+"?")
                said = self.get_audio() 
                if len(said.split()) > 8 or "no" not in said:
                    booktemp.add_info(said)
                else:
                    self.speak("No introduction is added.")

                self.insert_to_database(booktemp)
                self.speak("You has successfully added "+current_title+ "written by "+current_author)
                return 1
        

        else:
            #fail extracting title
            return -1



    def main(self):

        ### example
        # "The author is JK ROwling and the title is Harry Porter"))
        # "the title of the book is Harry Porter and the author is JK Rowling"))
        # "The title is Harry porter and the author of the book is JK Rowling"))
        ###
        bookID = 0
        self.speak("Hello, Please tell me the title and author of the book you want to add.")
        status = 1
        
        while status!= 0:
            
            status = self.listen(bookID)

            if status == 1: # successfully added book
                bookID += 1
                self.speak("Thank you. Do you want to add another book? If no, say quit. If yes, tell me the title and author of the book.")
            elif status == 2:
                self.speak("Sorry for hearing you wrong, please tell me again with the correct title and book.")
            elif status == 0:
                self.speak("Thank you for using Librospeak system, bye bye.")
            elif status == -1:
                self.speak("Sorry. I don't get the book information. Do you want to continue or quit? If continue, tell me the title and author of the book.")
            elif status == -2: # long time waiting and not hearing anything
                self.speak("Thank you for using Librospeak and Good bye.")
                status = 0
            else:
                print("Unknown status"+str(status))
                self.speak("Please tell me again the book you are adding.")
        