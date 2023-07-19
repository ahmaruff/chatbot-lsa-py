import pandas as pd
import random
from Sastrapy.WordTokenize.Tokenize import tokenize
from Sastrapy.Corpus.SlangConverter import SlangConverterMachine
from Sastrapy.Corpus.StopwordRemover import StopwordRemoverMachine
from bahasa.stemmer import Stemmer
from gensim import corpora, models, similarities

class LsaChatbot:
    # Inisiasi objek LSA
    def __init__(self, stopword_path: str, dataset_path: str):
        # lokasi/alamat path dataset (dataset/dataset.csv)
        self.dataset_path = dataset_path
        # lokasi alamat path stopword (stopword.txt)
        self.stopword_path = stopword_path

        self.stopwordMachine = StopwordRemoverMachine()
        self.slangMachine = SlangConverterMachine()
        self.stemmer = Stemmer()
        self.stopwordMachine.importDictionary(self.stopword_path)

        # mengambil data dataset
        self.dataset = self.load_data()

        # variable yang berisi data hasil training
        self.trained = None
        self.train()
            
    # load/mengambil dataset dari CSV
    def load_data(self):
        return pd.read_csv(self.dataset_path)
    
    # PREPROCESSING DATASET
    def pre_process(self, text):
        # CASE FOLDING - ubah text menjadi lowecase/huruf kecil
        text = text.lower() 
        # TOKENIZE - membuat token kata (kalimat dipecah menjadi list kata)
        tokens = tokenize(text)
        # SLANG CONVERTER - konversi bahasa gaul menjadi bahasa baku pada token
        tokens = self.slangMachine.convertSlang(tokens)
        # FILTERING STOPWORD - penghapusan stopword pada token
        tokens = self.stopwordMachine.removeStopword(tokens)
        # STEMMING token kata
        tokens = [self.stemmer.stem(t) for t in tokens]
        # output/hasil preprocess
        return (tokens)

    def train(self):
        # reset data training sebelumnya
        data = self.load_data()
        self.trained = None

        # preprocess untuk setiap baris "message" pada dataset >> LIHAT PRE_PROCESS DIATAS
        data['MESSAGE'] = data['MESSAGE'].apply(self.pre_process)
        # kumpulan data pertanyaan yang telah di pre-process
        question = data['MESSAGE'] 

        # ===== PERHITUNGAN LSA ========
        # Mapping kata/token unik menjadi id angka
        dictionary = corpora.Dictionary(question)
        # DOCUMENT-TERM MATRIX
        corpus = [dictionary.doc2bow(q) for q in question]

        # TF-IDF
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]

        # model LSA (proses SVD ada didalam model ini)        
        lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=50)
        corpus_lsi = lsi[corpus_tfidf]

        # SIMILIARITY
        index = similarities.MatrixSimilarity(corpus_lsi)
    
        # output model training LSA
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
    
    # proses di chatbot ( input pertanyaan, cari data jawaban terdekat dengan model LSA yang dibuat sebelumnya)
    def talk(self, question:str):
        # PRE-PROCESS PERTANYAAN
        tokens = self.pre_process(question)
        text = " ".join(tokens)

        # DEFINE HASIL TRAINING DATA MODEL SEBELUMNYA
        dictionary = self.trained['dictionary']
        tfidf = self.trained['tfidf']
        lsi = self.trained['lsi']
        index = self.trained['index']

        # === PROSES LSA dari input pertanyaan ====
        # document-term matrix
        vec_bow = dictionary.doc2bow(tokens)
        # TF-IDF
        vec_tfidf = tfidf[vec_bow]
        # LSA/SVD
        vec_lsi = lsi[vec_tfidf]

        # jika tidak ditemukan hasilnya
        if not(vec_lsi):
            not_understood = "maaf, saya tidak paham yang anda maksud, bisa anda ulangi?"
            payload = not_understood
        else:
            # lihat urutan index terdekat (hasil perhitungan LSA)
            sims = index[vec_lsi]
            sims = sorted(enumerate(sims), key=lambda item: -item[1])
            index_s = []
            score_s = []
            for i in range(len(sims)):
                x = sims[i][1]

                # JIKA Similiarity < 0.8 (muncul 3 opsi pertanyaan terdekat)
                if x <= 0.8:
                    index_s.append(str(sims[i][0]))
                    score_s.append(str(sims[i][1]))
                    reply_indexes = pd.DataFrame({'index': index_s, 'score': score_s})

                    r_index = int(reply_indexes['index'].loc[0])
                    r_score = float(reply_indexes['score'].loc[0])

                    question_data = self.dataset['MESSAGE']

                    if (r_index < len(question_data) - 3):
                        payload = [
                            {
                                'message' : question_data[r_index],
                            },{
                                'message' : question_data[r_index+1],   
                            },{
                                'message' : question_data[r_index+2],
                            }
                        ]
                    else:
                        not_understood = "maaf, saya tidak paham yang anda maksud, bisa anda ulangi?"
                        payload = not_understood
                # jika similiarity lebih dari 0.8
                else:
                    question_data = self.dataset['MESSAGE']
                    index_s.append(str(sims[i][0]))
                    score_s.append(str(sims[i][1]))
                    # jawaban terbaik            
                    reply_indexes = pd.DataFrame({'index': index_s,'score': score_s})
                
                # find top question and answer
                r_index = int(reply_indexes['index'].loc[0])
                r_score = float(reply_indexes['score'].loc[0])
                # jawaban terbaik
                question = question_data[r_index]
                reply = str(self.dataset.iloc[:,1][r_index])

                payload = {
                    'question'  : question,
                    'reply'     : reply,
                }

        return {
            'status' : 200,
            'result' : {
                'payload' : payload
            }
        }
    
    def lsa(self, sentence):
        reply = []
        reply = self.talk(str(sentence))        
        return reply


                