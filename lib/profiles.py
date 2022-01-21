from lib.selenium_config import init_driver
from selenium.common.exceptions import InvalidSessionIdException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


import datetime
from time import sleep

import lib.db as db
db = db.MongoDB(db="Tweettioc")

from lib.logger import init_log
logger = init_log()


def parser_photo(driver,user,url=None):
    if url is None:
        url = "https://twitter.com/{username}/photo".format(username=user)
    try:
        driver.get(url)
        # element_present = EC.presence_of_element_located((By.ID, 'element_id'))
        element_present = EC.presence_of_element_located(
            (By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/img'))
        WebDriverWait(driver, 10).until(element_present)
        link = driver.find_elements_by_xpath(
            '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/img')
        photo = link[0].get_attribute('src')
        print(photo)

        data = {"username": user, "photo": photo, "date": datetime.datetime.now()}
        db.insert(collection="profiles", data=data)
        sleep(1)
    except InvalidSessionIdException:
        driver = init_driver()
        sleep(2)
    except TimeoutException:
        #parser_photo(driver=driver,user=user,url="https://twitter.com/Twitter/photo")
        data = {"username": user, "photo": "https://pbs.twimg.com/profile_images/1354479643882004483/Btnfm47p_400x400.jpg",
                "date": datetime.datetime.now()}
        db.insert(collection="profiles", data=data)

def get_user_profile_photo():
    driver = init_driver()
    users = list(db.distinct(collection="tweets",query="username"))
    saved_users = list(db.distinct(collection="profiles",query="username"))
    users_missing = list(set(users) - set(saved_users))
    for user in users_missing:
        parser_photo(driver=driver,user=user)



get_user_profile_photo()