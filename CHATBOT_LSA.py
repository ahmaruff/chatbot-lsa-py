import pandas as pd
import os
import random
import string
import gensim
from gensim import corpora, models, similarities
from bahasa.stemmer import Stemmer
from Sastrapy.WordTokenize.Tokenize import tokenize
from Sastrapy.Corpus.SlangConverter import SlangConverterMachine
from Sastrapy.Corpus.StopwordRemover import StopwordRemoverMachine

import warnings
warnings.simplefilter('ignore')

# PRE PROCESSING
print('loading data sources')
data_path = os.getcwd() + '/dataset/dataset.csv'
print('Data source : ' + data_path)
data = pd.read_csv(data_path)
data.head()

temp_data = pd.read_csv(data_path)
question_data = temp_data['MESSAGE']


# Inisialisasi STOPWORD
stopwordMachine = StopwordRemoverMachine()
stopword_path = os.getcwd() + '/stopword.txt'
stopwordMachine.importDictionary(stopword_path)

# Inisialisasi fitur slang converter
slangMachine = SlangConverterMachine()

# Inisiasi stemmer
stemmer = Stemmer()

def pre_process(text: str):
    text = text.lower()
    tokens = tokenize(text)
    tokens = slangMachine.convertSlang(tokens)
    tokens = stopwordMachine.removeStopword(tokens)
    tokens = [stemmer.stem(t) for t in tokens]
    # print(tokens)
    return(tokens)


GREETING_INPUTS = ("halo", "hi", "hello", "hai", "hai saya butuh bantuan", "selamat siang", "selamat pagi", "selamat malam", "saya butuh bantuan")
GREETING_RESPONSES = ["halo, ada yang bisa saya bantu?", "halo", "hai, kamu sedang bicara denganku"]      

def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

# PRE PROCESS QUESTION COLUMN
data['MESSAGE'] = data['MESSAGE'].apply(pre_process)

# DEFINE QUESTION
question = data['MESSAGE']

dictionary = corpora.Dictionary(question)
corpus = [dictionary.doc2bow(a) for a in question]
tfidf = models.TfidfModel(corpus)
    
corpus_tfidf = tfidf[corpus]
lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=50) # Threshold A
corpus_lsi = lsi[corpus_tfidf]
index = similarities.MatrixSimilarity(corpus_lsi)

# CHATBOT DEFINITION

def talk_to_tau(question: str):
    tokens = pre_process(question)
    texts = " ".join(tokens)

    # ---------------Find and Sort Similarity -------------------------------#
    vec_bow = dictionary.doc2bow(texts.lower().split())
    vec_tfidf = tfidf[vec_bow]
    vec_lsi = lsi[vec_tfidf]

    if not(vec_lsi):
         # not_understood = "Apology, I do not understand. Can you rephrase?"
        not_understood = "maaf, saya tidak paham yang anda maksud, bisa anda ulangi?"
        return not_understood, 999
    
    else:
        # sort similarity
        sims = index[vec_lsi]
        sims = sorted(enumerate(sims),key=lambda item: -item[1])

        index_s = []
        score_s = []
        for i in range(len(sims)):
            x = sims[i][1]

            # is similarity is less than 0.5
            if x<=0.8: # thereshold B
                index_s.append(str(sims[i][0]))
                score_s.append(str(sims[i][1]))
                reply_indexes = pd.DataFrame({'index': index_s,'score': score_s})

                r_index = int(reply_indexes['index'].loc[0])
                r_score = float(reply_indexes['score'].loc[0])

                if(r_index < len(question_data) - 3):
                    return {
                        'result' : {
                            'messages' : {
                                'payload' : {
                                    'text' : 'Maaf, bisakah anda lebih spesifik lagi?, ini beberapa pertanyaan yang relevan',
                                    'quick_replies': [
                                        {
                                        'content_type' : 'text',
                                        'title' : question_data[r_index],
                                        'payload' : question_data[r_index]
                                        },{
                                        'content_type' : 'text',
                                        'title' : question_data[r_index+1],
                                        'payload' : question_data[r_index+1]   
                                        },{
                                        'content_type' : 'text',
                                        'title' : question_data[r_index+2],
                                        'payload' : question_data[r_index+2]  
                                        }
                                    ]
                                }
                            }
                        }
                    }, 999
                else:
                    # not_understood = "Apology, I do not understand. Can you rephrase?"
                    not_understood = "maaf, saya tidak paham yang anda maksud, bisa anda ulangi?"
                    return not_understood, 999
            else:
                index_s.append(str(sims[i][0]))
                score_s.append(str(sims[i][1]))
                reply_indexes = pd.DataFrame({'index': index_s,'score': score_s})
            
            #Find Top Questions and Score  
            r_index = int(reply_indexes['index'].loc[0])
            r_score = float(reply_indexes['score'].loc[0])
            reply = str(data.iloc[:,1][r_index])
        
            return reply, r_score
        
def lsa(sentence):
    if(sentence.lower() != 'bye'):
        if(greeting(sentence.lower()) != None):
            return greeting(sentence.lower())
        else:
            reply = []
            score = []
            reply, score = talk_to_tau(str(sentence))

            return reply