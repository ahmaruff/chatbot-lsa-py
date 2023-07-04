import pandas as pd
import random
from Sastrapy.WordTokenize.Tokenize import tokenize
from Sastrapy.Corpus.SlangConverter import SlangConverterMachine
from Sastrapy.Corpus.StopwordRemover import StopwordRemoverMachine
from bahasa.stemmer import Stemmer
from gensim import corpora, models, similarities

class LsaChatbot:
    def __init__(self, stopword_path: str, dataset_path: str):
        self.dataset_path = dataset_path
        self.stopword_path = stopword_path
        self.stopwordMachine = StopwordRemoverMachine()
        self.slangMachine = SlangConverterMachine()
        self.stemmer = Stemmer()
        self.stopwordMachine.importDictionary(self.stopword_path)

        # for data training
        self.dataset = self.load_data()

        self.trained = None
        self.train()
            
    def load_data(self):
        return pd.read_csv(self.dataset_path)
    
    def pre_process(self, text):
        text = text.lower()
        tokens = tokenize(text)
        tokens = self.slangMachine.convertSlang(tokens)
        tokens = self.stopwordMachine.removeStopword(tokens)
        tokens = [self.stemmer.stem(t) for t in tokens]
        return (tokens)

    def train(self):
        # reset
        data = self.load_data()
        self.trained = None
        # preprocess
        data['MESSAGE'] = data['MESSAGE'].apply(self.pre_process)
        question = data['MESSAGE']

        # LSA
        dictionary = corpora.Dictionary(question)
        corpus = [dictionary.doc2bow(q) for q in question]
        tfidf = models.TfidfModel(corpus)

        corpus_tfidf = tfidf[corpus]
        lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=50)
        corpus_lsi = lsi[corpus_tfidf]
        index = similarities.MatrixSimilarity(corpus_lsi)
    
        self.trained = {
            'dictionary'    : dictionary,
            'corpus'        : corpus,
            'tfidf'         : tfidf,
            'corpus_tfidf'  : corpus_tfidf,
            'lsi'           : lsi,
            'corpus_lsi'    : corpus_lsi,
            'index'         : index, 
        }

        # update dataset
        self.dataset = self.load_data()
        
        return self.trained
    
    def talk(self, question:str):
        tokens = self.pre_process(question)
        text = " ".join(tokens)

        # define trained data
        dictionary = self.trained['dictionary']
        tfidf = self.trained['tfidf']
        lsi = self.trained['lsi']
        index = self.trained['index']

        # find and sort similarity
        vec_bow = dictionary.doc2bow(text.lower().split())
        vec_tfidf = tfidf[vec_bow]
        vec_lsi = lsi[vec_tfidf]

        if not(vec_lsi):
            not_understood = "maaf, saya tidak paham yang anda maksud, bisa anda ulangi?"
            return not_understood
        else:
            sims = index[vec_lsi]
            sims = sorted(enumerate(sims), key=lambda item: -item[1])
            index_s = []
            score_s = []
            for i in range(len(sims)):
                x = sims[i][1]

                # is similarity is less than 0.5 
                if x <= 0.8:
                    index_s.append(str(sims[i][0]))
                    score_s.append(str(sims[i][1]))
                    reply_indexes = pd.DataFrame({'index': index_s, 'score': score_s})

                    r_index = int(reply_indexes['index'].loc[0])
                    r_score = float(reply_indexes['score'].loc[0])

                    question_data = self.dataset['MESSAGE']

                    if (r_index < len(question_data) - 3):
                        return {
                            'status' : 200,
                            'result' : {
                                'payload' : {
                                    'quick_replies': [
                                        {
                                            'content_type' : 'text',
                                            'message' : question_data[r_index],
                                        },{
                                            'content_type' : 'text',
                                            'message' : question_data[r_index+1],   
                                        },{
                                            'content_type' : 'text',
                                            'message' : question_data[r_index+2],
                                        }
                                    ]
                                }
                            }
                        }
                    else:
                        not_understood = "maaf, saya tidak paham yang anda maksud, bisa anda ulangi?"
                        return not_understood
                else:
                    index_s.append(str(sims[i][0]))
                    score_s.append(str(sims[i][1]))
                    reply_indexes = pd.DataFrame({'index': index_s,'score': score_s})
                
                # find top question and answer
                r_index = int(reply_indexes['index'].loc[0])
                r_score = float(reply_indexes['score'].loc[0])
                reply = str(self.dataset.iloc[:,1][r_index])

                return reply
            
    def lsa(self, sentence):
        reply = []
        reply = self.talk(str(sentence))        
        return reply


                