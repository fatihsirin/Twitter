from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options

from fake_useragent import UserAgent

ua = UserAgent()
userAgent = ua.random

def init_driver(headless=True, proxy=None, show_images=False, option=None):

    # create instance of web driver
    chromedriver_path = chromedriver_autoinstaller.install()
    # options
    options = Options()
    if headless is True:
        print("Scraping on headless mode.")
        options.add_argument('--disable-gpu')
        options.headless = True
    else:
        options.headless = False
    options.add_argument('log-level=3')
    if proxy is not None:
        options.add_argument('--proxy-server=%s' % proxy)
        print("using proxy : ", proxy)
    if show_images == False:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    if option is not None:
        options.add_argument(option)

    options.add_argument('--headless')

    #options.add_argument("--incognito")
    #options.add_argument("--nogpu")
    #options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1000,5000")
    #options.add_argument("--no-sandbox")
    #options.add_argument("--enable-javascript")
    #options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #options.add_experimental_option('useAutomationExtension', False)
    #options.add_argument('--disable-blink-features=AutomationControlled')

    options.add_argument("--start-maximized")
    options.add_argument(
        'user-agent={Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36}')

    driver = webdriver.Chrome(options=options, executable_path=chromedriver_path)
    #driver.set_window_size(100, 5000)
    driver.set_page_load_timeout(100)
    return driver




