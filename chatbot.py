#!/usr/bin/python3

import os

from LsaChatbot import LsaChatbot

stopword_path = os.getcwd() + '/stopword.txt'
dataset_path = os.getcwd() + '/dataset/dataset.csv'

lsaChatbot = LsaChatbot(stopword_path, dataset_path)

while True:
    input_text = input("User says > ")

    print(input_text)
    lsa_response = lsaChatbot.lsa(input_text)
    print("Bot says > ", lsa_response)

    file_path = os.getcwd() + '/fallback_sentences.txt'
    with open(file_path, 'a') as file:
        file.write(input_text + "\n")
