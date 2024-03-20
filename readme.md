<!-- add image -->
![Demo](/header.png)

# LibroSpeak

LibroSpeak is an assistant program designed to help librarians efficiently add new books to a database using voice commands. This program utilizes speech recognition and text-to-speech capabilities to interact with users, facilitating the process of inputting book titles and authors into a database. t incorporates OpenAI's powerful language models to understand user input and provide helpful responses.

## Installation

To use LibroSpeak, follow these steps:

1. Clone the repository to your local machine:

2. Install playsound by by going to the playsound-master directory and running:
```git
python setup.py install
```

3. Install all other required dependencies using pip:

4. Make sure you have PostgreSQL installed and running on your machine. Modify the database connection details (`dbname`, `user`, `password`, `host`) in the `connect_to_database()` function to match your PostgreSQL configuration.

5. You will need to set up environment variables for OpenAI API and Supabase credentials as described in the comments within the code.


## Usage

1. Run the program by executing the following command in your terminal:

```git
python app.py
```

2. Once the program is running, go to your localhost that the app is running on, which will show a simple frontend showing the books in the database and two modes to add new ones. Choose one mode to add the title and author of the book you wish to add to the database. 


### Overview of the two modes

| GPT mode | Manual mode | 
|----------|----------|
| Powered by Open AIs LLM API | Powered by regular expressions | 
| Allows the user to speak more freely| The user needs to speak in a certain format | 


3. LibroSpeak will process your input, ensuring it understands the provided information correctly. If there are any issues or uncertainties, it will ask for clarification or provide guidance on how to proceed.

4. Once LibroSpeak has gathered the necessary details, it will confirm the information with you. If everything is correct, you can confirm, and the book will be added to the database. Otherwise, you can make corrections as needed.

5. The program will continue running, ready to assist you with adding more books as necessary.


## Contributing

Contributions to LibroSpeak are welcome! If you encounter any issues or have suggestions for improvements, feel free to open an issue or submit a pull request on the GitHub repository.

## Developers
This project was developed by Imran Diva, Xi Gong, and Nora Karaduman Sorsenger, as part of KTH course DT2112 Speech Technology

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code for your own purposes.


