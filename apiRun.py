#from lib.utils import *
#import lib.dashboardData as dashboardData
#import lib.hashtags as hashtags
import datetime
import tweepy
import pymongo
from lib import twitter
from lib.logger import init_log
import lib.parser as parser
logger = init_log()

connection = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = connection["ioctest"]
ioc = mydb["ioc"]



def tweepylogin():
    consumer_key = 'dM6lo6TKjzkY1QHdIFCoxhxGd'
    consumer_secret = 'TYFvslFiYTNLBt8LgHFERTtPSEKi89IVqlFeYeSswbxFoZMeAm'
    access_token = '320948193-cjsOagxsgO3aLxzZqeTFO53RUQCcMsez3sX9Qdz4'
    access_token_secret = 'aAIrUH0lKaPuz96YVcKY9MoYIWkoe4yqz6d6FDmwfMIf4'
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    print("[+] Api Auth Succeed")
    return api


def getCriteria(users, word, since, until):
  query = ''
  if word.strip() != '':
    query += word
  if len(users) == 1:
    query += ' from:' + users[0]
  elif len(users) > 1:
    query += ' from:' + ' OR from:'.join(users)
  if query == '':
    return query
  else:
    try:
      if since != None:
        #since_day = dateutil.parse(since).strftime('%Y-%m-%d')
        query += ' since:' + since
      if until != None:
        #until_day = dateutil.parse(until).strftime('%Y-%m-%d')
        query += ' until:' + until
    except ValueError:
      print('[-] Date Format Error')
  #query = urllib.parse.quote_plus(query)
  return query



def startApp(api,max_count, word='', users='',since='', until=''):
    _api = api
    query = getCriteria(users, word, since, until)
    # max_count = args.max_count
    print('[+] Your Query is: ' + query)
    print('[+] You can Check your Results in the following URL.')
    print('[+] https://twitter.com/search?f=tweets&vertical=news&q={q}&src=typd&'.format(q=query))
    print('[+] Gathering Tweets. Please Wait...')
    #(tweets, statuscode) = getTweet(query, 'min_pos', max_count, [])
    tweets = twitter.apiGetTweet(_api, query, 'min_pos', max_count, [])
    print('[+] Get {num} Tweets '.format(num=str(len(tweets))))
    print('[+] Save Twitter Search Result')
    ioc_pattaern = twitter.getIoCPattern()
    json_result = []
    for t in tweets:
        iocs = parser.extractIoC(t['text'], ioc_pattaern)
        iocs.update(t)
        #iocs['tweet'] = t
        json_result.append(iocs)
        ioc.insert_one(iocs)

    print('[+] Tweets ware saved in database')


def main():
    word = 'virustotal.com OR app.any.run OR hybrid-analysis.com OR reverseit.com OR virusbay.io OR tria.ge'
    max_count = 1000000

    def start():
        api = tweepylogin()
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

        logger.info('starting data gathering -'+ str(datetime.datetime.now().strftime('%Y-%m-%d')))
        since = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        until = (datetime.datetime.now()).strftime('%Y-%m-%d')

        for user in userslist:
            if user:
                startApp(api=api,max_count=max_count, users=user, since=since, until=until)
        startApp(api=api,max_count=max_count, word=word, since=since, until=until)
        logger.info('finished data gathering -'+ str(datetime.datetime.now().strftime('%Y-%m-%d')))


    start()
    #schedule.every().day.at("00:01").do(start)
    # schedule.every().minute.do(start)
    #while True:
    #    schedule.run_pending()
    #    time.sleep(50)


if __name__ == "__main__":
    main()