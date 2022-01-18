import lib.db as db
import datetime

from lib.logger import init_log

logger = init_log()

db = db.MongoDB(db="Tweettioc")


def deleteDuplicatedTweets(since=datetime.date(2000, 1, 1), until=datetime.datetime.now()):
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
        for item in doc["unique_ids"]:
            response.append(item)

    delete_query = {"_id": {"$in": response}}
    db.delete_many(collection="tweets", query=delete_query)
    logger.debug("Deleted Duplicate Tweets Count: " + str(len(response)))
    logger.debug('DeleteDuplicatedTweets is done')


# def dashboard_monthly():
#     data = {}
#     query = [
#         {"$group": {
#             "_id": {"month": {"$month": {"$toDate": "$date"}}},
#             "count": {"$sum": 1}
#         }
#         }, {"$sort": {"_id.month": 1}}
#     ]
#     cursor = db.aggregate(collection="tweets", query=query)
#     for item in cursor:
#         month = datetime.date(1900, item["_id"]["month"], 1).strftime('%B')
#         data[month] = item["count"]
#     data = {"type": "monthly", "data": data, "date": datetime.datetime.now()}
#     db.insert(collection="dashboards", data=data)

def dashboard_monthly():
    data = {}
    query = [
        {"$group": {
            "_id": {"month": {"$month": {"$toDate": "$date"}},
                    "year" : {"$year" : {"$toDate": "$date"}}
                    },
            "count": {"$sum": 1}
        }
        },
        {
            "$sort":{
                 "_id.year":-1,"_id.month":-1
            }
        },
        {"$project": {
            "name": "$_id",
            "count": 1,
            "_id":0 }
        },
    ]
    cursor = db.aggregate(collection="tweets", query=query)
    data = list(cursor)
    data = {"type": "monthly", "data": data, "date": datetime.datetime.now()}
    db.insert(collection="dashboards", data=data)



def dashboard_daily(days=30):
    since = (datetime.datetime.now() - datetime.timedelta(days=days))
    query = [
        {
            "$match": {"date": {"$gte": since}}
        },
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                    "count": {"$sum": 1}}},

        {"$project": {
            "name": "$_id",
            "count": 1, }
        },
        {
            "$sort": {"_id": +1}
        }
    ]

    cursor = db.aggregate(collection="tweets", query=query)
    cursor = list(cursor)
    data = {"type": "daily", "data": cursor, "date": datetime.datetime.now()}
    db.insert(collection="dashboards", data=data)


def dashboard_ioc_count():
    query = [
        {
            "$group": {
                "_id": None,
                "md5": {"$addToSet": "$md5"},
                "sha1": {"$addToSet": "$sha1"},
                "sha256": {"$addToSet": "$sha256"},
                "ip": {"$addToSet": "$ip"},
                "domain": {"$addToSet": "$domain"},
                "url": {"$addToSet": "$url"},
                "mail": {"$addToSet": "$mail"}
            }
        },
        {
            "$project": {
                "_id": False,
                "md5": {"$size": "$md5"},
                "sha1": {"$size": "$sha1"},
                "sha256": {"$size": "$sha256"},
                "ip": {"$size": "$ip"},
                "domain": {"$size": "$domain"},
                "url": {"$size": "$url"},
                "mail": {"$size": "$mail"}
            }
        }
    ]

    cursor = list(db.aggregate(collection="tweets", query=query))
    data = {"type": "iocCounts", "data": cursor, "date": datetime.datetime.now()}
    db.insert(collection="dashboards", data=data)


def dashboard_hashtag_all():
    query = [
        {
            "$match": {
                "hashtags": {"$not": {"$size": 0}}
            }
        },
        {"$unwind": "$hashtags"},
        {
            "$group": {
                "_id": {"$toLower": '$hashtags'},
                "count": {"$sum": 1}
            }
        },
        {
            "$match": {
                "count": {"$gte": 2}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 15},
        {"$project": {"count": 1, "_id": 0, "id": {"$trim": {"input": "$_id", "chars": "#"}}}}
    ]

    cursor = list(db.aggregate(collection="tweets", query=query))
    data = {"type": "hashtagsAll", "data": cursor, "date": datetime.datetime.now()}
    db.insert(collection="dashboards", data=data)


def dashboard_hashtag_daily(days=20):
    since = (datetime.datetime.now() - datetime.timedelta(days=days))
    query = [
        {
            "$match": {
                "hashtags": {"$not": {"$size": 0}}
            }
        },
        {
            "$match": {"date": {"$gte": since}}
        },
        {"$unwind": "$hashtags"},
        {
            "$group": {
                "_id": {"$toLower": '$hashtags'},
                "count": {"$sum": 1}
            }
        },

        {"$sort": {"count": -1}},
        {"$limit": 15},
        {"$project": {"count": 1, "_id": 0, "id": {"$trim": {"input": "$_id", "chars": "#"}}}}
    ]

    cursor = list(db.aggregate(collection="tweets", query=query))
    data = {"type": "hashtagsDaily", "data": cursor, "date": datetime.datetime.now()}
    db.insert(collection="dashboards", data=data)

#
# deleteDuplicatedTweets(since = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
#                        until = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime('%Y-%m-%d'))

dashboard_monthly()