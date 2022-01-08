from lib.selenium_config import init_driver
from twitter import log_search_page, keep_scroling
from selenium.common.exceptions import TimeoutException, InvalidSessionIdException, NoSuchElementException, \
    WebDriverException

import datetime
from time import sleep
from const import *

iocs = []

from lib.logger import init_log

logger = init_log()


def scrape(since, until=None, words=None, to_account=None, from_account=None, mention_account=None, interval=5,
           lang=None,
           headless=True, limit=float("inf"), proxy=None, hashtag=None,
           show_images=False, save_images=False):
    # until = (datetime.datetime.now()).strftime('%Y-%m-%d')
    until = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    since = (datetime.datetime.now() - datetime.timedelta(days=380)).strftime('%Y-%m-%d')
    if until is None:
        until = datetime.date.today().strftime("%Y-%m-%d")
    # set refresh at 0. we refresh the page for each <interval> of time.
    # until = "2020-10-17"
    until = "2021-11-08"
    since = "2021-01-01"

    # initiate the driver
    driver = init_driver(headless, proxy, show_images)
    logger.info("Selenium is started")
    if type(since) != str:
        since = datetime.datetime.strftime(since, '%Y-%m-%d')

    logger.info("Scraping by Words is Started")

    for user in from_account:
        temp_until = until
        temp_since = since
        keep = True
        if user:
            while keep:
                result, last_tweet_date = get_search_data(driver=driver, since=temp_since, until=temp_until,
                                                          to_account=to_account,
                                                          from_account=user, mention_account=mention_account,
                                                          hashtag=hashtag,
                                                          lang=lang, limit=limit,
                                                          )
                temp_until = datetime.datetime.strptime(temp_until, "%Y-%m-%d")
                temp_since = datetime.datetime.strptime(temp_since, "%Y-%m-%d")
                if last_tweet_date:
                    last_tweet_date = datetime.datetime.strptime(last_tweet_date, "%Y-%m-%d")
                    _diff = temp_until - last_tweet_date
                    _diff_since = temp_since - last_tweet_date
                    if temp_since == last_tweet_date:
                        keep = False
                        logger.info("Scrolling is Disabled ")
                    else:
                        temp_until = (last_tweet_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                        temp_since = datetime.datetime.strftime(temp_since, '%Y-%m-%d')
                        print("New Until Time: " + temp_until)
                        logger.info("New Until Time: " + temp_until)
                else:
                    if temp_until != temp_since:
                        temp_until = (temp_until - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                        temp_since = datetime.datetime.strftime(temp_since, '%Y-%m-%d')
                        print("New Until Time: " + temp_until)
                        logger.info("New Until Time: " + temp_until)
                    else:
                        keep = False
                        logger.info("Scrolling is Disabled ")





    keep = True
    while keep:
        if words:
            result, last_tweet_date = get_search_data(driver=driver, words=words, since=since, until=until,
                                                      to_account=to_account,
                                                      mention_account=mention_account, hashtag=hashtag,
                                                      lang=lang, limit=limit,
                                                      )
            until = datetime.datetime.strptime(until, "%Y-%m-%d")
            since = datetime.datetime.strptime(since, "%Y-%m-%d")
            last_tweet_date = datetime.datetime.strptime(last_tweet_date, "%Y-%m-%d")
            _diff = until - last_tweet_date
            _diff_since = since - last_tweet_date

            if since == last_tweet_date:
                keep = False
                logger.info("Scrolling is Disabled ")
            else:
                until = (last_tweet_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                since = datetime.datetime.strftime(since, '%Y-%m-%d')
                print("New Until Time: " + until)
                logger.info("New Until Time: " + until)

            # if _diff_since.days > -1:
            # #     until = (until - _diff).strftime("%Y-%m-%d")
            #     since = datetime.datetime.strftime(since, '%Y-%m-%d')
            #     if until == since:
            #         keep = False
            #         logger.info("Scrolling is Disabled ")
            #     print("New Until Time: " + until)
            #     logger.info("New Until Time: " + until)
            # elif _diff.days != 0:
            #     until = (until - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            #     since = datetime.datetime.strftime(since, '%Y-%m-%d')
            #     print("New Until Time: " + until)
            #     logger.info("New Until Time: " + until)
            # else:
            #     keep = False
            #     until = until.strftime("%Y-%m-%d")
            #     print("Exit New Until Time: " + until)
            #     print(until)
            #     logger.info("Scrolling is Disabled ")

    # close the web driver
    driver.close()
    return True


def get_search_data(driver, since, until=None, words=None, to_account=None, from_account=None,
                    mention_account=None, interval=5, lang=None,
                    headless=True, limit=float("inf"), proxy=None, hashtag=None,
                    show_images=False, save_images=False):
    # list that contains all data
    # unique tweet ids
    tweet_ids = set()

    path = log_search_page(words=words, since=since,
                           until=until, to_account=to_account,
                           from_account=from_account, mention_account=mention_account, hashtag=hashtag,
                           lang=lang)
    try:
        driver.get(path)
    except InvalidSessionIdException as e:
        logger.info(str(e))
        driver = init_driver(headless, proxy, show_images)
        driver.get(path)
    # number of logged pages (refresh each <interval>)
    last_position = driver.execute_script("return window.pageYOffset;")
    # should we keep scrolling ?
    scrolling = True
    print("looking for tweets between " + str(since) + " and " + str(until) + " ...")
    print(" path : {}".format(path))
    logger.info("Requesting {}".format(path))
    tweet_parsed = 0
    sleep(3)

    # start scrolling and get tweets
    driver, tweet_ids, scrolling, tweet_parsed, last_position, last_tweet_date = \
        keep_scroling(driver, tweet_ids, scrolling, tweet_parsed, limit, last_position)

    # print('[+]' + str(len(tweet_parsed))+ 'Tweets ware saved in database')
    return True, last_tweet_date


def isEmptyIOC(ioc):
    if not ioc['md5']:
        if not ioc['sha1']:
            if not ioc['sha256']:
                if not ioc['ip']:
                    if not ioc['domain']:
                        if not ioc['url']:
                            if not ioc['mail']:
                                return False
    return True


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
minreplies = get_minreplies()
minlikes = get_minlikes()
minretweets = get_minlikes()


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
    users = []
    f.close()
    return userslist


def getWords():
    words = []
    with open("keywords.txt", "r") as f:
        words = f.read().splitlines()

    return words


words = getWords()
from_account = getUserList()

logger.info("Scraping is Started")
data = scrape(since=since, until=until, words=words, to_account=to_account, from_account=from_account,
              mention_account=mention_account,
              hashtag=hashtag, interval=interval, lang=lang, headless=headless, limit=limit,
              proxy=proxy)

x = get_since()
print(get_since())
print()
