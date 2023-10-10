from gensim.models import Word2Vec
from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200/'])
#init

queries = ["multimodal travel services" , "Big Data for Mobility","European logistics applications","Architectures for Big Data Analytics","Architecture for Industrial IoT",
           "Mobility-as-a-Service tools","fragmentation of IoT through federation","Seamless Efficient European Travelling","cross-domain orchestration of services","communal organisation of network infrastucture"]

answer_file="ResultsElasticW2V50simple.txt"

index_w2v = "index_nostem"  
index_correct="index_analyzer_correct"
word2vec_model = Word2Vec.load("word2vecSimple.model")
min_sim=0.7
num_results=50


def analyze_w2v(query_text):
    analysis = es.indices.analyze(index=index_w2v, body={
        "text": query_text
        })
    analyzed_terms = [token["token"] for token in analysis["tokens"]]
    return analyzed_terms


    


def find_similar_words(word,word2vec_model,top_max_n=2):

    try:
        word_vector=word2vec_model.wv[word]
        similar_words = word2vec_model.wv.similar_by_vector(word_vector, topn=top_max_n)
        similar_words = [(token, score) for token, score in similar_words if score >= min_sim]
        similar_words = [token for token, _ in similar_words if token != word]

        return similar_words
    except KeyError:
        return []
    
def search_documents(query, index_name):
    
    response = es.search(index=index_name, body={
        "query": {
            "match": {
                "text": query
            }
        },
        "size": num_results
    })
    
    matching_documents = []
    for hit in response['hits']['hits']:
        doc = {
            'doc_id': hit['_id'],
            'score': hit['_score'],
            'text': hit['_source']['text']
        }
        matching_documents.append(doc)
    return matching_documents

with open(answer_file, "w") as file:
    
    query_number=1

    print(query_number)
    print("-------------------")

    for query in queries:
        keywords = analyze_w2v(query)
        expanded_keywords = []
        for keyword in keywords:
            similar_words = find_similar_words(keyword, word2vec_model)
            expanded_keywords.extend(similar_words)
            print("adding : " + ", ".join(similar_words))

        expanded_query = " ".join(keywords + expanded_keywords)
        analyzed_query = es.indices.analyze(index=index_correct, body={
            "analyzer": "rebuilt_english",
            "text": expanded_query
        })

        analyzed_terms = [token["token"] for token in analyzed_query["tokens"]]
        analyzed_query_text = " ".join(analyzed_terms)
        print(analyzed_query_text)

        #print(analyzed_query)
        search_results = es.search(index=index_correct, body={
            "query": {
                "match": {
                    "text_field": analyzed_query_text
                }
            },
            "size": num_results  # Retrieve the top n results
        })

        
        for rank, hit in enumerate(search_results['hits']['hits'], start=1):
            doc_id = hit['_id']
            score = hit['_score']
            line = f"Q0{query_number}\t0\t{doc_id}\t0\t{score}\tSearcherProject\n"
            if query_number==10:
                line = f"Q{query_number}\t0\t{doc_id}\t0\t{score}\tSearcherProject\n"
            file.write(line)

            
        query_number+=1
        print(query_number)
        print("Searching for ")
        print(query)
        print("     plus    : " +expanded_query)
        print("----------")

print(f"Results written to {answer_file}.")

        
        
        

