import lib.db as db
import datetime


db = db.MongoDB(db="Threatintelligence")
db_ioc = db.MongoDB(db="ioctest")





def deleteDuplicatedTweets():
    db.logger.debug('deleteDuplicatedTweets is started')

    query = [
        {"$group": {"_id": "$tweet_id", "unique_ids": {"$addToSet": "$_id"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 2}}}
    ]

    cursor = db.aggregate(collection="tweets", query=query)
    response = []
    for doc in cursor:
        del doc["unique_ids"][0]
        for id in doc["unique_ids"]:
            response.append(id)

    delete_query = {"_id": {"$in": response}}
    #db.delete_many(collection="tweets",query=delete_query)
    db.logger.debug("Deleted Duplicate Tweets Count: " + str(len(response)))
    db.logger.debug('DeleteDuplicatedTweets is done')


