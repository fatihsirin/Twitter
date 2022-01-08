###############
### Imports ###
###############

## Might need to install modules below
# !pip install selenium
# !pip install textblob
# !pip install dataframe_image
# !pip install wordcloud #or in anaconda prompt type: conda install -c https://conda.anaconda.org/conda-forge wordcloud

import os
import re
import sys
import csv
import time
import getpass
import pandas as pd
import datetime as dt
import dataframe_image as dfi
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

from time import sleep
from textblob import TextBlob
from selenium import webdriver
from wordcloud import WordCloud, STOPWORDS
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


###########################
# Scrape data from tweets #
###########################

def scrape_tweet(tweet, term):
    '''Extract the data from tweets related to the searched term'''

    # find username
    username = tweet.find_element_by_xpath('.//span').text

    # find twitter handle
    try:
        handle = tweet.find_element_by_xpath('.//span[contains(text(), "@")]').text
    except NoSuchElementException as error:
        handle = None

    # find datetime of tweet
    try:
        postdate = tweet.find_element_by_xpath('.//time').get_attribute('datetime')
    except NoSuchElementException as error:
        postdate = None

    # get the post's text
    try:
        text = tweet.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    except NoSuchElementException as error:
        text = None

    # get associated #'s
    associated_hashtags = []
    for word in text.split():
        if '#' in word and word.upper() != term.upper():
            associated_hashtags.append(word)

    # replies count
    replies = tweet.find_element_by_xpath('.//div[@data-testid="reply"]').text
    if replies == '':
        replies = 0

    # retweets count
    retweets = tweet.find_element_by_xpath('.//div[@data-testid="retweet"]').text
    if retweets == '':
        retweets = 0

    # likes count
    likes = tweet.find_element_by_xpath('.//div[@data-testid="like"]').text
    if likes == '':
        likes = 0

    try:
        link = ""
        links = tweet.find_elements_by_tag_name("a")
        for i in links:
            if "status" in i.get_attribute('href'):
                link = i.get_attribute('href')
                break
    except NoSuchElementException as error:
        link = None

    image_links = []
    try:
        elements = tweet.find_elements_by_xpath('.//div[2]/div[2]//img[contains(@src, "https://pbs.twimg.com/")]')
        for element in elements:
            image_links.append(element.get_attribute('src'))
    except:
        image_links = []

    #Tweet id
    tweet_id = link.split("/")[5]

    #fixing text from newlines and other not related data
    text = text.replace("\n"+replies, "")
    text = text.replace("\n"+retweets, "")
    text = text.replace("\n"+likes, "")

    # making tuple of the extracted tweet data
    data = (tweet_id, username, handle, postdate, text, associated_hashtags, replies, retweets, likes, link)
    return data


# initialize variables that will be the id used to login into the Twitter account
login_id = handle_or_phone = term = password = ''

# getting login id
login_id = "kayipoluyorum"
# handle_or_phone = input('Please enter your Twitter handle or phone: ')
term = "BTC"
password = "filizbenimaskim2021"
all_ids = [login_id, handle_or_phone, term, password]


options = Options()
options.add_argument('--headless')
options.add_argument("--incognito")
options.add_argument("--nogpu")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,1280")
options.add_argument("--no-sandbox")
options.add_argument("--enable-javascript")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')


driver = webdriver.Chrome(options=options,executable_path=r"/Users/fsirin/PycharmProjects/virustotalv1/chromedriver")
driver.maximize_window()  # window is maximized in order to have access to Twitter's search query

##Finding the term in the search query of Twitter
search_term = driver.get('http://www.twitter.com/search/')
sleep(4)
search_term = driver.find_element_by_xpath('(//input[@placeholder="Search Twitter"])[1]')
search_term.send_keys(term)
search_term.send_keys(Keys.RETURN)
sleep(2)

##Sorting by latest
# driver.find_element_by_link_text('Latest').click()

start = time.time()
##Get the desired number of tweets by scrolling the page to scrape new data
data = []  # create an empty list to store scraped tweets
unique_ids = set()  # make a set of unique ids to make sure no same tweets are scraped
last_position = driver.execute_script("return window.pageYOffset;")
scrolling = True
max_data = 100  # max number of data that will be scraped
complete = ''  # complete message for visual cue of the bot's scraping progress (will be updated as more data is being gathered)

while scrolling and len(data) < max_data:
    tweets = driver.find_elements_by_xpath('//article[@role="article"]')
    for t in tweets[-15:]:
        tweet = scrape_tweet(t, term)
        if tweet:
            unique_id = ''.join(tweet[3])  # making a unique id by joining the text of each tweet
            if unique_id not in unique_ids:  # append unique id in set of ids if it is not in there yet
                unique_ids.add(unique_id)
                data.append(tweet)

                # adding visual indication of how much data has been scraped at each 20% completion mark
                if (len(data) / max_data) < 0.2 and complete != ('0% complete...'):
                    complete = '0% complete...'
                    print('Scraping Starts... Now!\n' + complete)
                elif (len(data) / max_data) >= 0.2 and (len(data) / max_data) < 0.4 and complete != ('20% complete...'):
                    complete = '20% complete...'
                    print(complete)
                elif (len(data) / max_data) >= 0.4 and (len(data) / max_data) < 0.6 and complete != ('40% complete...'):
                    complete = '40% complete...'
                    print(complete)
                elif (len(data) / max_data) >= 0.6 and (len(data) / max_data) < 0.8 and complete != ('60% complete...'):
                    complete = '60% complete...'
                    print(complete)
                elif (len(data) / max_data) >= 0.8 and (len(data) / max_data) < 1.0 and complete != ('80% complete...'):
                    complete = '80% complete...'
                    print(complete)
                elif (len(data) / max_data) >= 1.0:
                    print('100% complete. Almost Done...')

    # check scroll position; making sure it isnt stuck or if it ever reach the end
    scroll_attempt = 0
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(1)
        curr_position = driver.execute_script("return window.pageYOffset;")
        if last_position == curr_position:
            scroll_attempt += 1

            # end of scroll region
            if scroll_attempt >= 3:
                scrolling = False
                break
            else:
                sleep(2)  # attempt another scroll
        else:
            last_position = curr_position
            break

