import random
from time import sleep
import lib.regex as regex
import lib.parser as parser
import lib.db as db
import tweepy

import datetime
from lib.const import get_username, get_password
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from pathlib import Path
# logging
from lib.logger import init_log
logger = init_log()


#db connection
db = db.MongoDB(db="Tweettioc")


from lib.regex import *
import os


wl_ip = []
wl_dom = []
path_whitelist = os.getcwd() + "/whitelist.txt"
if os.path.exists(path_whitelist):
    (wl_ip, wl_dom) = loadWhitelist(path_whitelist)
elif os.path.exists(os.path.dirname(__file__) +'../whitelist'): #windows çalıştırmasından kaynaklı hatadan eklendi
    (wl_ip, wl_dom) = loadWhitelist(os.path.dirname(__file__) +'../whitelist.txt')
else:
    print('whitelist file couldnt find')
    exit()



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


def get_data(card, save_images=False, save_dir=None):
    """Extract data from tweet card"""
    image_links = []
    tweet = {}

    try:
        tweet["name"] = card.find_element_by_xpath('.//span').text
    except:
        return

    try:
        tweet["username"] = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
        tweet["username"] = tweet["username"].replace("@", "")
    except:
        return

    try:
        tweet["postdate"] = card.find_element_by_xpath('.//time').get_attribute('datetime')
        tweet['timestamp'] = datetime.datetime.strptime(tweet["postdate"], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
        tweet['date'] = datetime.datetime.fromtimestamp(tweet['timestamp'])
    except:
        return

    try:
        text = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    except:
        text = ""

    # make readable tweets
    text = text.replace('# ', '#')
    text = text.replace('@ ', '@')
    text = text.replace('[.] ', '.')
    text = text.replace('].', '] .')
    text = text.replace(',', '.')
    text = text.replace('[dot]', '.')
    text = text.replace(' dot ', '.')
    text = text.replace(']', '')
    text = text.replace('[', '')
    # text = text.replace('=', '= ')
    text = text.replace(' com ', 'com ')
    text = text.replace('https://', ' https://')
    text = text.replace('http://', ' http://')
    text = text.replace(' net', 'net')
    text = text.replace('pic.twitter.com', ' pic.twitter.com')
    text = text.replace('..', '.')
    text = text.replace(' .', '.')

    tweet["text"] = text

    tweet["mentions"] = re.compile('(@\\w+)').findall(text)
    tweet["hashtags"] = re.compile('(#\\w+)').findall(text)

    try:
        elements = card.find_elements_by_xpath('.//div[2]/div[2]//img[contains(@src, "https://pbs.twimg.com/")]')
        for element in elements:
            image_links.append(element.get_attribute('src'))
    except:
        image_links = []
    tweet["images"] = image_links

    # tweet url
    try:
        element = card.find_element_by_xpath('.//a[contains(@href, "/status/")]')
        tweet_url = element.get_attribute('href')
        tweet["link"] = tweet_url
    except:
        tweet["link"] = ""
        return

    # Tweet id
    tweet_id = tweet_url.split("/")[5]
    tweet["tweet_id"] = tweet_id

    return tweet


def log_in(driver, timeout=10):
    username = get_username()  # const.USERNAME
    password = get_password()  # const.PASSWORD

    driver.get('https://twitter.com/i/flow/login')
    username_css = 'label input'
    password_css = 'label input[type="password"]'

    username_el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, username_css)))
    sleep(3)
    username_el.send_keys(username)
    sleep(3)
    username_el.send_keys(Keys.RETURN)
    sleep(3)
    password_el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, password_css)))
    sleep(3)
    password_el.send_keys(password)
    password_el.send_keys(Keys.RETURN)


def keep_scroling(driver, tweet_ids, scrolling, tweet_parsed, limit, last_position, save_images=False):
    """ scrolling function for tweets crawling"""

    save_images_dir = "./images"
    last_tweet_date = None
    temp_tweet_count = 0
    scroll_up_attempt_count = 0
    # regex pattern
    ioc_pattaern = regex.getIoCPattern()

    if save_images:
        if not os.path.exists(save_images_dir):
            os.mkdir(save_images_dir)
    try:
        while scrolling and tweet_parsed < limit:
            sleep(random.uniform(0.5, 1.5))
            # get the card of tweets
            page_cards = driver.find_elements_by_xpath('//article[@data-testid="tweet"]')  # changed div by article
            for card in page_cards:
                tweet = get_data(card, save_images, save_images_dir)
                if tweet:
                    # check if the tweet is unique
                    if tweet["tweet_id"] not in tweet_ids:
                        ioc = parser.extractIoC(tweet['text'], ioc_pattaern)
                        tweet_ids.add(tweet["tweet_id"])
                        if isEmptyIOC(ioc=ioc):
                            # inserting data to DB
                            ioc.update(tweet)
                            db.insert(collection="tweets", data=ioc)
                        tweet_parsed += 1
                        print('\rParsed Tweet Count [%d] - Last Tweet Date [%s]' % (tweet_parsed, tweet["postdate"]),
                              end="")
                        if tweet_parsed >= limit:
                            break
                        # last_tweet_date = datetime.datetime.strptime(tweet["postdate"],
                        #                                              '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d")
                        # return driver, tweet_ids, scrolling, tweet_parsed, last_position, last_tweet_date

                    last_tweet_date = datetime.datetime.strptime(tweet["postdate"],
                                                                 '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d")

            # scrolling events
            scroll_attempt = 0
            if tweet_parsed == temp_tweet_count:
                scroll_up_attempt_count += 1
            else:
                scroll_up_attempt_count = 0
                temp_tweet_count = tweet_parsed

            while tweet_parsed < limit:
                # check scroll position
                sleep(random.uniform(0.5, 1.5))
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                sleep(3)
                curr_position = driver.execute_script("return window.pageYOffset;")
                sleep(1)
                if last_position == curr_position:
                    scroll_attempt += 1
                    # end of scroll region
                    logger.info("Scrolling Attempt. Parsed Tweet Count [%d]"
                                % tweet_parsed)
                    if scroll_attempt >= 3 or scroll_up_attempt_count > 2:
                        scrolling = False
                        logger.info("Scrolling is disabled. Parsed Tweet Count [%d]"
                                    % tweet_parsed)
                        break
                    elif scroll_attempt > 1:
                        driver.execute_script("window.scroll(0, 0);")
                        sleep(2)  # attempt another scroll
                        print("\nScrolled Up")
                        logger.info("Scrolling Up Attempt. Parsed Tweet Count [%d]"
                                    % tweet_parsed)
                        # last_position = driver.execute_script("return window.pageYOffset;")
                else:
                    last_position = curr_position
                    break
        return driver, tweet_ids, scrolling, tweet_parsed, last_position, last_tweet_date
    except WebDriverException as e:
        logger.info(str(e))
        return driver, tweet_ids, scrolling, tweet_parsed, last_position, last_tweet_date


def log_search_page(since, until, lang, words, to_account, from_account, mention_account, hashtag):
    """ Search for this query between since and until"""
    # format the <from_account>, <to_account> and <hash_tags>
    to_account = "(to%3A" + to_account + ")%20" if to_account is not None else ""
    mention_account = "(%40" + mention_account + ")%20" if mention_account is not None else ""
    hash_tags = "(%23" + hashtag + ")%20" if hashtag is not None else ""

    if from_account is not None:
        if len(from_account) == 1:
            from_account = "(from:" + str(''.join(from_account)) + ")%20"
        else:
            from_account = "(from:" + str(' from:'.join(from_account)) + ") "
            from_account = from_account.split(" ")
            from_account = str(' OR ').join(from_account)[:-3]
    else:
        from_account = ""

    if words is not None:
        if len(words) == 1:
            words = "(" + str(''.join(words)) + ")%20"
        else:
            words = "(" + str('%20OR%20'.join(words)) + ")%20"
    else:
        words = ""

    if lang is not None:
        lang = 'lang%3A' + lang
    else:
        lang = ""

    until = "until%3A" + until + "%20"
    since = "since%3A" + since + "%20"

    # latest tweets
    display_type = "&f=live"

    path = 'https://twitter.com/search?q={0}{1}{2}{3}{4}{5}{6}{7}&src=typed_query{8}'.format(words, from_account,
                                                                                             to_account,
                                                                                             mention_account, hash_tags,
                                                                                             until, since, lang,
                                                                                             display_type)
    return path



def apiGetTweet(tweepyapi,query, min_pos, max_count, tweets,tweet_count=0):
  tweetslist = []
  txt=''
  tweets = tweepy.Cursor(tweepyapi.search_tweets,
                         q=query,
                         result_type="recent", tweet_mode="extended").items(5000)
  for tweet in tweets:
    t = {}
    txt =''
    if 'retweeted_status' in tweet._json:
      # t['favorites'] = tweet._json['retweeted_status']['favorite_count']
      # if 'extended_tweet' in tweet._json['retweeted_status']:
      #   t['user'] = tweet._json['retweeted_status']['user']['screen_name']
      #   txt = tweet._json['retweeted_status']['full_text']
      # else:
      #   t['user'] = tweet._json['retweeted_status']['user']['screen_name']
      #   txt = 'RT @' + tweet._json['retweeted_status']['user']['screen_name'] + ':' + tweet._json['retweeted_status']['full_text']
      #
      # kisaltilmis linklerin expand edilmesi
      # for i in tweet._json['retweeted_status']['entities']['urls']:
      #   if i['url'] in txt:
      #     txt = txt.replace(i['url'], i['expanded_url'])
      pass
    else:
      if 'extended_tweet' in tweet._json:
        txt = tweet._json['extended_tweet']['full_text']
      else:
        txt = tweet._json['full_text']
        t['username'] = tweet._json['user']['screen_name']
        t['name'] = tweet._json['user']['name']

        # kisaltilmis linklerin expand edilmesi
        if len(tweet._json['entities']['urls']) != 0:
          for i in tweet._json['entities']['urls']:
            if i['url'] in txt:
              txt = txt.replace(i['url'], i['expanded_url'])

        if 'extended_entities' in tweet._json:
          if len(tweet._json['extended_entities']['media']) != 0:
            for i in tweet._json['extended_entities']['media']:
              if i['url'] in txt:
                txt = txt.replace(i['url'], i['expanded_url'])

      txt = txt.replace('# ', '#')
      txt = txt.replace('@ ', '@')
      txt = txt.replace('].', '] .')
      txt = txt.replace(',', '.')
      txt = txt.replace('[dot]', '.')
      txt = txt.replace(' dot ', '.')
      txt = txt.replace(']', '')
      txt = txt.replace('[', '')
      #txt = txt.replace('=', '= ')
      txt = txt.replace(' com ', 'com ')
      txt = txt.replace('https://', ' https://')
      txt = txt.replace('http://', ' http://')
      txt = txt.replace(' net', 'net')
      txt = txt.replace('pic.twitter.com', ' pic.twitter.com')
      txt = txt.replace('..', '.')

      t['text'] = txt
      t['tweet_id'] = tweet._json['id_str']
      #t['retweets'] = tweet._json['retweet_count']
      t['link'] = 'https://twitter.com/' + t['username'] + '/status/' + t['tweet_id']
      t['mentions'] = re.compile('(@\\w+)').findall(t['text'])
      t['hashtags'] = re.compile('(#\\w+)').findall(t['text'])
      t['date'] = str(tweet.created_at)
      t['date'] = t['date'][:19]
      t['postdate'] = t['date'][:19]
      _date = datetime.datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S')
      #_date = datetime.datetime.strptime(t['date'], "%Y-%m-%d %H:%M:%S+%z")
      t['timestamp'] =int(datetime.datetime.timestamp(_date))
      t['date'] = datetime.datetime.fromtimestamp(t['timestamp'])

      tweetslist.append(t)
  return tweetslist

