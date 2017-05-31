from pymongo import MongoClient

def connect(ip, port):
    client = MongoClient(ip + ":" + port)
    return client
    
def initilize_collection(client, db, collection):
    client[db][collection]

def remove_document(client, db, collection, doc_key, doc_value):
    client.db.collection.delete_many({doc_key: doc_value})
    
def remove_database(client, db):
    client.drop_database(db)
    
def insert_data(client, db, collection, data):
    _collection = client.db.collection
    for d in data:
        _collection.save(d)

def read_document(client, db, collection, document):
    return client.db.collection.find(document)