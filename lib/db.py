import pymongo


class MongoDB(object):
    URI = "mongodb://localhost:27017"
    db = None
    DATABASE = None


    def __init__(self,db):
        self.db = db
        try:
            client = pymongo.MongoClient(MongoDB.URI)
            MongoDB.DATABASE = client[self.db]
        except Exception:
            print("Fatal error in main loop")


    @staticmethod
    def insert(collection, data):
        MongoDB.DATABASE[collection].insert_one(data)

    @staticmethod
    def insertmany(collection, data):
        MongoDB.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection,query):
        return MongoDB.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return MongoDB.DATABASE[collection].find_one(query)

    @staticmethod
    def aggregate(collection, query):
        return MongoDB.DATABASE[collection].aggregate(query)

    @staticmethod
    def delete_many(collection, query):
        return MongoDB.DATABASE[collection].delete_many(query)

    @staticmethod
    def delete_one(collection, query):
        return MongoDB.DATABASE[collection].delete_one(query)

    @staticmethod
    def distinct(collection, query):
        return MongoDB.DATABASE[collection].distinct(query)

