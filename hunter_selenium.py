from lib.tscrape import scrape_word, scrape_user
from lib.const import *
from lib.logger import init_log
from lib.utils import *
import schedule
import time
import datetime

logger = init_log()

words = (get_words().split())
until = get_until()
since = get_since()
interval = int(get_interval())
lang = get_lang()
headless = get_headless()
limit = int(get_limit())
from_account = get_from_account()
to_account = get_to_account()
mention_account = get_mention_account()
hashtag = get_hashtag()
proxy = get_proxy()
proximity = get_proximity()
geocode = get_geocode()


def getUserList():
    userslist = []
    users = []
    user_count = 0
    f = open('users.txt', 'r')
    for i in f.readlines():
        if i != '\n':
            users.append(i.rstrip())
            user_count += 1
            if user_count == 5:
                userslist.append(users)
                users = []
                user_count = 0
    userslist.append(users)
    f.close()
    return userslist


def getWords():
    with open("keywords.txt", "r") as f:
        words = f.read().splitlines()
    return words


words = getWords()
from_account = getUserList()


def start():
    #1 day before and 2 days after
    since = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y-%m-%d')
    until = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime('%Y-%m-%d')
    #since = "2022-12-19"
    #until = "2022-12-21"
    logger.info("Scraping is Started")

    data = scrape_user(since=since, until=until, to_account=to_account, from_account=from_account,
                       mention_account=mention_account,
                       hashtag=hashtag, interval=interval, lang=lang, headless=headless, limit=limit,
                       proxy=proxy)

    data = scrape_word(since=since, until=until, words=words, to_account=to_account,
                  mention_account=mention_account,
                  hashtag=hashtag, interval=interval, lang=lang, headless=headless, limit=limit,
                  proxy=proxy)



    deleteDuplicatedTweets(since=since, until=until)
    dashboard_ioc_count()
    dashboard_monthly()
    dashboard_daily()
    dashboard_hashtag_daily()
    dashboard_hashtag_all()
    dashboard_ioctype_daily()
    dashboard_researcher_yearly()
    dashboard_researcher_month()
    #dashboard_researcher_daily()

    logger.info("Scraping is Done")


start()
# schedule.every().day.at("00:01").do(start)
# schedule.every().minute.do(start)
# schedule.every(30).minutes.do(start())
# while True:
#     schedule.run_pending()
#     time.sleep(50)
