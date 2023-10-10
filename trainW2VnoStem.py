from elasticsearch import Elasticsearch
from gensim.models import Word2Vec
import re



es = Elasticsearch(['http://localhost:9200/'])
file_path="documents.txt"
def analyze_words(words):
    analyzed_text = es.indices.analyze(index="index_nostem", body={
        "analyzer": "rebuilt_english_nostem",
        "text": words
    })
    analyzed_words = [token["token"] for token in analyzed_text["tokens"]]
    return analyzed_words
    

def create_sentences(file):
    doc_count = 0
    sentences = []
    current_sentence = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            line = line.strip()
            if line.startswith('///'):
                if current_sentence:
                    analyzed_sentence = analyze_words(current_sentence)
                    sentences.append(analyzed_sentence)
            
                    sentences.append(current_sentence)
                    doc_count += 1
                    if doc_count % 1000 == 0:
                        print(f"Analyzed {doc_count} documents")
                    
                current_sentence = []
            else:
                words = re.findall(r'\b\w+\b', line.lower())
                #mhn krathseis to doc_id tou document 
                if words and words[0].isdigit():
                    words = words[1:]
                current_sentence.extend(words)

    print(f"Finished analyzing {doc_count} documents")
    return sentences


sentences=create_sentences(file_path)

'''
    vector_size : int, optional
        Dimensionality of the word vectors.
    window : int, optional
         Maximum distance between the current and predicted word within a sentence.
    min_count : int, optional
        Ignores all words with total frequency lower than this.
    workers : int, optional
        Use these many worker threads to train the model (=faster training with multicore machines).
    sg : {0, 1}, optional
        Training algorithm: 1 for !!!!skip-gram; otherwise CBOW.!!!

'''
#100-5-3
VECTOR_SIZE=150
WINDOW=5
MIN_COUNT=4
SG=0
#1=skip-gram
#0=cbow
model = Word2Vec(sentences, 
                 vector_size=VECTOR_SIZE, 
                 window=WINDOW, 
                 min_count=MIN_COUNT,
                 sg=SG)
model.save("word2vecSimple.model")
print("done training")

 