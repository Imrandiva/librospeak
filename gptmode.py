import os
import playsound
import speech_recognition as sr
from gtts import gTTS
from supabase import create_client

from openai import OpenAI


recognizer = sr.Recognizer()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)






class GPTMode:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI()

        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.conversation = []


    def send_convo(self):
        return self.conversation
    
    # TTS function
    def speak(self, text):
        tts = gTTS(text=text, lang='en')
        filename = 'outputvoice.mp3'
        tts.save(filename)
        playsound.playsound(filename)
        if os.path.exists(filename):
            os.remove(filename)
        else:
            print("The file does not exist")

    # Get the audio input using the microphone
    def get_audio(self):
        with sr.Microphone() as source:
            print("Start speaking...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, phrase_time_limit=20)
            said = ""
            try:
                said = self.recognizer.recognize_google(audio)
                print(f"You said: {said}")
            except Exception as e:
                print("Exception: " + str(e))
        return said


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


    # Connect to OpenAI chatGPT API and set up the chat response
    def chat_response(self, input, previous_messages):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content":
                    """You are a helpful assistant to help the librarian add library books to a database.
                    The user will speak freely and it is up to you to help them. If they have any questions, help them using the knowledge that
                    you have already, as well as input from previous messages. Also, for example if the book is well known, suggest an author.

                    If you cannot understand the input, tell the user that you did not understand, help them.,

                    Redo until you have been given a title and all the authors. Separate the authors by comma if there are multiple authors. If the format and the input is correct, format the input
                    into a string in python in the format: Title, Author1, author2..., theinputisready2024".
                    
                    """
                 },
                {"role": "user", "content": previous_messages + "\n Latest input: " + input}
            ]
        )
        return response.choices[0].message.content



    # Insert the book and authors to the database
    def insert_to_database(self, objects):
        print(objects)
        print(objects)
        book_title = objects[0]
        authors = objects[1:-2]
        print(authors)
        abstract = objects[-1]

        # Insert book
        book = supabase.table('books').insert({'title': book_title, 'description': abstract}).execute()
        book_id = book.data[0]['book_id']
        
        # Insert authors
        author_ids = []

        for author_name in authors:
            
            author = supabase.table('authors').select('author_id').eq('author_name', author_name).execute()


            if len(author.data) == 0:    
                author = supabase.table('authors').insert({'author_name': author_name}).execute()
            
            print(author.data)
            author_ids.append(author.data[0]['author_id'])
        
        # Link authors with book
        for author_id in author_ids:
            supabase.table('book_authors').insert({'author_id': author_id, 'book_id': book_id}).execute()


        print("Data inserted successfully.")
   
    def main(self):

        
        multiple_insertions = False
        books_to_add = []
        self.speak("Welcome to LibroSpeak. Add the title and author of the book that you want to add to the database.")
        previous_messages = "Previous messages:"

        while True:

            if multiple_insertions:
                self.speak("Glad to help you again. Add the title and author of the book that you want to add to the database.")

            text = self.get_audio()
            
            if not text:
                print("Sorry... I didn't get that")
                self.speak("Sorry... I didn't get that")
                continue

            reply = self.chat_response(text, previous_messages)
            previous_messages += "\n" + text

            if 'theinputisready2024' in reply:
                reply = reply.split(",")
                author_saying = ""
                if len(reply) > 3:
                    for author in reply[1:-1]:
                        if author == reply[-2]:
                            author_saying += "and " + author
                        else:
                            author_saying += author + ","
                else:
                    author_saying = reply[1]

                output = "You want to add the book" + reply[0] + " written by " + author_saying + " to the database. Is that correct?"

                books_to_add = reply
                self.speak(output)
                print(output)
                text = self.get_audio()
                if "yes" in text:
                    books_to_add = reply
                    print("Done")

                    self.speak("Great! Do you want to add an abstract or an introduction as well?")
                    text = self.get_audio()
                    if "yes" in text:
                        self.speak("Great! Please say the abstract or introduction of the book.")
                        text = self.get_audio()
                        books_to_add.append(text)
                        self.speak("The abstract has been added to the database.")
                    else:
                        books_to_add.append("No abstract or introduction available.")

                    self.insert_to_database(books_to_add)

                    self.speak("The book has been added to the database. Do you want to add another book?")

                    text = self.get_audio()

                    if "yes" in text:
                        multiple_insertions = True
                        continue
                    self.speak("Thank you for using Librospeak")
                    return 
                    
                else:
                    self.speak("Ok. Fix it by saying your input again.")
                    continue
            else:
                self.speak(reply)
                continue



# if __name__ == "__main__":
#     system = GPTMode()
#     system.main()
