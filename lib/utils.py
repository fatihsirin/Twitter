import lib.db as db
import datetime

from lib.logger import init_log

logger = init_log()

db = db.MongoDB(db="Tweettioc")


def deleteDuplicatedTweets(since, until):
    logger.debug('deleteDuplicatedTweets is started')
    since = datetime.datetime.strptime(since, "%Y-%m-%d")
    until = datetime.datetime.strptime(until, "%Y-%m-%d")

    query = [
        {"$group": {"_id": {"tweet_id": "$tweet_id", "date": "$date"}, "unique_ids": {"$addToSet": "$_id"},
                    "count": {"$sum": 1}}},
        {"$match": {
            "$and": [
                {"count": {"$gte": 2}},
                {"_id.date": {
                    '$lt': until,
                    '$gt': since
                }
                },
            ]
        }
        }
    ]

    cursor = db.aggregate(collection="tweets", query=query)
    response = []
    for doc in cursor:
        del doc["unique_ids"][0]
        for id in doc["unique_ids"]:
            response.append(id)

    delete_query = {"_id": {"$in": response}}
    # db.delete_many(collection="tweets",query=delete_query)
    logger.debug("Deleted Duplicate Tweets Count: " + str(len(response)))
    logger.debug('DeleteDuplicatedTweets is done')


def data_monthly():
    data = {}
    query = [
        {"$group": {
            "_id": {"month": {"$month": {"$toDate": "$date"}}},
            "count": {"$sum": 1}
        }
        }, {"$sort": {"_id.month": 1}}
    ]
    cursor = db.aggregate(collection="tweets", query=query)
    for item in cursor:
        month = datetime.date(1900, item["_id"]["month"], 1).strftime('%B')
        data[month] = item["count"]
    data = {"type": "monthly", "data": data}
    db.insert(collection="dashboards", data=data)


def data_weekly():
    since = (datetime.datetime.now() - datetime.timedelta(days=7))
    data = {}
    query = [
        {
            "$match": {"date": {"$gte": since}}
        },
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}}, "count": {"$sum": 1}}},
        {
            "$sort": {"_id": +1}
        }
    ]

    cursor = db.aggregate(collection="tweets", query=query)
    cursor = list(cursor)
    for item in cursor:
        pass

    data = {"type": "monthly", "data": data}
    db.insert(collection="dashboards", data=data)


data_weekly()

#
# deleteDuplicatedTweets(since = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
#                        until = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime('%Y-%m-%d'))
