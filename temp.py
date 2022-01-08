from lib.selenium_config import init_driver
from lib.twitter import log_search_page, keep_scroling

import datetime
from time import sleep
from lib.const import *


def scrape(since, until=None, words=None, to_account=None, from_account=None, mention_account=None, interval=5,
           lang=None,
           headless=True, limit=float("inf"), display_type="Top", proxy=None, hashtag=None,
           show_images=False, save_images=False, filter_replies=False, proximity=False,
           geocode=None, minreplies=None, minlikes=None, minretweets=None):
    """
    scrape data from twitter using requests, starting from <since> until <until>. The program make a search between each <since> and <until_local>
    until it reaches the <until> date if it's given, else it stops at the actual date.
    return:
    data : df containing all tweets scraped with the associated features.
    save a csv file containing all tweets scraped with the associated features.
    """
    # ------------------------- Variables :
    # header of csv
    header = ['UserScreenName', 'UserName', 'Timestamp', 'Text', 'Embedded_text', 'Emojis', 'Comments', 'Likes',
              'Retweets',
              'Image link', 'Tweet URL']
    # list that contains all data
    data = []
    # unique tweet ids
    tweet_ids = set()
    # start scraping from <since> until <until>
    # add the <interval> to <since> to get <until_local> for the first refresh
    until = (datetime.datetime.now()).strftime('%Y-%m-%d')
    until_local = datetime.datetime.strptime(until, '%Y-%m-%d') - datetime.timedelta(days=interval)
    # if <until>=None, set it to the actual date
    since = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    if until is None:
        until = datetime.date.today().strftime("%Y-%m-%d")
    # set refresh at 0. we refresh the page for each <interval> of time.
    refresh = 0

    # initiate the driver
    driver = init_driver(headless, proxy, show_images)

    # log search page for a specific <interval> of time and keep scrolling unltil scrolling stops or reach the <until>
    while until_local <= datetime.datetime.strptime(until, '%Y-%m-%d'):
        scroll = 0

        if type(since) != str:
            since = datetime.datetime.strftime(since, '%Y-%m-%d')
        if type(until_local) != str:
            until_local = datetime.datetime.strftime(until_local, '%Y-%m-%d')
        # log search page between <since> and <until_local>
        path = log_search_page(driver=driver, words=words, since=since,
                               until_local=until_local, to_account=to_account,
                               from_account=from_account, mention_account=mention_account, hashtag=hashtag,
                               lang=lang,
                               display_type=display_type, filter_replies=filter_replies, proximity=proximity,
                               geocode=geocode, minreplies=minreplies, minlikes=minlikes, minretweets=minretweets)
        # number of logged pages (refresh each <interval>)
        refresh += 1
        last_position = driver.execute_script("return window.pageYOffset;")
        # should we keep scrolling ?
        scrolling = True
        print("looking for tweets between " + str(since) + " and " + str(until_local) + " ...")
        print(" path : {}".format(path))
        # number of tweets parsed
        tweet_parsed = 0
        # sleep
        sleep(3)
        # start scrolling and get tweets
        driver, data, tweet_ids, scrolling, tweet_parsed, scroll, last_position = \
            keep_scroling(driver, data, tweet_ids, scrolling, tweet_parsed, limit, scroll, last_position)

        # keep updating <start date> and <end date> for every search
        if type(since) == str:
            since = datetime.datetime.strptime(since, '%Y-%m-%d') + datetime.timedelta(days=interval)
        else:
            since = since + datetime.timedelta(days=interval)
        if type(since) != str:
            until_local = datetime.datetime.strptime(until_local, '%Y-%m-%d') + datetime.timedelta(days=interval)
        else:
            until_local = until_local + datetime.timedelta(days=interval)

    # close the web driver
    driver.close()
    return data


words = (get_words().split())
until = get_until()
since = get_since()
interval = int(get_interval())
lang = get_lang()
headless = get_headless()
limit = int(get_limit())
display_type = get_display_type()
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

data = scrape(since=since, until=until, words=words, to_account=to_account, from_account=from_account,
              mention_account=mention_account,
              hashtag=hashtag, interval=interval, lang=lang, headless=headless, limit=limit,
              display_type=display_type, proxy=proxy, filter_replies=False, proximity=proximity,
              geocode=geocode, minreplies=minreplies, minlikes=minlikes, minretweets=minretweets)

x = get_since()
print(get_since())
print()
