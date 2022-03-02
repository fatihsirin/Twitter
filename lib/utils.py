import lib.db as db
import datetime

from lib.logger import init_log

logger = init_log()

db = db.MongoDB(db="Tweettioc")


def deleteDuplicatedTweets(since=datetime.date(2000, 1, 1), until=datetime.datetime.now()):
    logger.info('deleteDuplicatedTweets is started')
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
    logger.info("Deleted Duplicate Tweets Count: " + str(len(response)))
    logger.info('DeleteDuplicatedTweets is done')


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
                    "year": {"$year": {"$toDate": "$date"}}
                    },
            "count": {"$sum": 1}
        }
        },
        {
            "$sort": {
                "_id.year": -1, "_id.month": -1
            }
        },
        {"$project": {
            "name": "$_id",
            "count": 1,
            "_id": 0}
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


def dashboard_ioctype_daily(days=30):
    since = (datetime.datetime.now() - datetime.timedelta(days=days))
    names = ['md5', 'sha1', 'sha256', 'ip', 'domain', 'url', 'mail']
    for name in names:
        query = [
            {
                "$match": {name: {"$regex": ".+"}},
            },
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

        query_totalcount = [
            {
                "$match": {name: {"$regex": ".+"}},
            },
            {"$unwind": "$" + name},
            {"$group": {"_id": 0, "count": {"$sum": 1}}}
        ]

        cursor = list(db.aggregate(collection="tweets", query=query))
        totalcount = list(db.aggregate(collection="tweets", query=query_totalcount))
        totalcount = totalcount[0]["count"]
        data = {"type": name, "data": cursor, "totalcount": totalcount, "date": datetime.datetime.now()}
        db.insert(collection="dashboards", data=data)


def dashboard_researcher_month():
    date = datetime.datetime.now()
    query = [
        {"$group": {
            "_id": {"username": "$username",
                    "month": {"$month": {"$toDate": "$date"}},
                    "year": {"$year": {"$toDate": "$date"}},
                    },
            "count": {"$sum": 1}
        }
        },
        {"$lookup":
            {
                "from": "twitterprofiles",
                "localField": "_id.username",
                "foreignField": "username",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {"$project": {
            "_id": 0,
            "count": 1,
            "photo": "$user.photo",
            "username": "$_id.username",
            "month": "$_id.month",
            "year": "$_id.year",
        }},

        {"$match": {
            "$and": [{"month": date.month}, {"year": date.year}]}
        },
        {"$sort": {"count": -1}},
    ]

    cursor = list(db.aggregate(collection="tweets", query=query))
    data = {"type": "researchersMonthly", "data": cursor, "date": datetime.datetime.now()}
    db.insert(collection="dashboards", data=data)


def dashboard_researcher_daily(days=1):
    since = (datetime.datetime.now() - datetime.timedelta(days=days))
    date = datetime.datetime.now()
    query = [
        {
            "$match": {"date": {"$gte": since}}
        },
        {"$group": {
            "_id": {"username": "$username",
                    "month": {"$month": {"$toDate": "$date"}},
                    "year": {"$year": {"$toDate": "$date"}},
                    "day": {"$dayOfMonth": {"$toDate": "$date"}},
                    },
            "count": {"$sum": 1}
        }
        },
        {"$lookup":
            {
                "from": "twitterprofiles",
                "localField": "_id.username",
                "foreignField": "username",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {"$project": {
            "_id": 0,
            "count": 1,
            "photo": "$user.photo",
            "username": "$_id.username",
            "month": "$_id.month",
            "year": "$_id.year",
            "day": "$_id.day",
        }},

        {"$match": {
            "$and": [{"day": date.day}, {"month": date.month}, {"year": date.year}]}
        },
        {"$sort": {"count": -1}},
    ]

    cursor = list(db.aggregate(collection="tweets", query=query))
    data = {"type": "researchersDaily", "data": cursor, "date": datetime.datetime.now()}
    db.insert(collection="dashboards", data=data)


def dashboard_researcher_yearly():
    date = datetime.datetime.now()
    query = [
        {"$group": {
            "_id": {"username": "$username",
                    "year": {"$year": {"$toDate": "$date"}},
                    },
            "count": {"$sum": 1}
        }
        },
        {"$lookup":
            {
                "from": "twitterprofiles",
                "localField": "_id.username",
                "foreignField": "username",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {"$project": {
            "_id": 0,
            "count": 1,
            "photo": "$user.photo",
            "username": "$_id.username",
            "year": "$_id.year",
        }},

        {"$match": {"year": date.year}},
        {"$sort": {"count": -1}},
    ]

    cursor = list(db.aggregate(collection="tweets", query=query))
    data = {"type": "researchersYearly", "data": cursor, "date": datetime.datetime.now()}
    db.insert(collection="dashboards", data=data)


dashboard_researcher_yearly()
dashboard_researcher_month()
dashboard_researcher_daily()
#
# deleteDuplicatedTweets(since = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
#                        until = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime('%Y-%m-%d'))
