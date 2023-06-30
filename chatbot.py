#!/usr/bin/python3

import os

from CHATBOT_LSA import lsa

while True:
    input_text = input("User says > ")

    print(input_text)
    lsa_response = lsa(input_text)
    print("Bot says > ", lsa_response)

    file_path = os.getcwd() + '/fallback_sentences.txt'
    with open(file_path, 'a') as file:
        file.write(input_text + "\n")
