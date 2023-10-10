from elasticsearch.helpers import bulk,BulkIndexError
from elasticsearch import Elasticsearch
import re

es = Elasticsearch(['http://localhost:9200/'] )


index_name = "index_analyzer_correct"
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)


index_mapping = {
  "settings": {
    "analysis": {
      "filter": {
        "english_stop": {
          "type":       "stop",
          "stopwords":  "_english_" 
        },
        "english_stemmer": {
          "type":       "stemmer",
          "language":   "english"
        },
        "english_possessive_stemmer": {
          "type":       "stemmer",
          "language":   "possessive_english"
        }
      },
      "analyzer": {
        "rebuilt_english": {
          "tokenizer":  "standard",
          "filter": [
            "english_possessive_stemmer",
            "lowercase",
            "english_stop",
            "english_stemmer"
          ]
        }
      }
    }
  },
  "mappings": {
        "properties": {
            "text_field": {
                "type": "text",
                "analyzer": "rebuilt_english"  
          }
      }
  }
}
es.indices.create(index=index_name, body=index_mapping)


def index_documents(file_path, index_name):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        doc_id = None
        content = ""
        for line in file:
            line = line.strip()
            if line.startswith('///'):
                # End of document, yield Elasticsearch bulk action
                if doc_id and content:
                    yield {
                        '_index': index_name,
                        '_id': doc_id,
                        "text_field" : content
                    }
                doc_id = None
                content = ""
            else:
                if doc_id is None:
                    doc_id = line
                else:
                    content += line

try:
    success = bulk(es, index_documents('documents.txt', index_name=index_name))
    if success:
        print("Indexing completed successfully.")
    else:
        print("Indexing failed.")
except BulkIndexError as e:
    print(f"Bulk indexing failed with {len(e.errors)} errors.")
    for error in e.errors:
        print(error)
es.indices.refresh(index=index_name)