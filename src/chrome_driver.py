# Import modules
from selenium import webdriver


def setup_chrome_driver():
    # Set option to Chrome headless.
    chrome_options = webdriver.ChromeOptions()

    # Tries to avoid bot detection.
    # chrome_options.add_argument('headless') # headless seems to fuck things up
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--no-proxy-server')

    # Do not load images to chrome browser.
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    # Sets up chrome driver with the additional options.
    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.implicitly_wait(10)
    return chrome_driver
