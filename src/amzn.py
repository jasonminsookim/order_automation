# Import libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
import time
import re
from src import chrome_driver


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def login(driver, email, password):
    logged_in = False

    while logged_in is False:
        # Open up amazon.com
        driver.get("https://www.amazon.com/")

        # Sign into amazon
        driver.find_element_by_xpath("//span[contains(text(),'Hello, Sign in')]").click()

        # Enter email address
        login_email_ele = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ap_email']")))
        login_email_ele.click()
        WebDriverWait(driver, 5).until(lambda browser: login_email_ele.get_attribute('value') == '')

        login_email_ele.send_keys(email)

        driver.find_element_by_xpath("//input[@id='continue']").click()

        # Enter password
        login_pw_ele = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='ap_password']")))
        login_pw_ele.click()
        WebDriverWait(driver, 5).until(lambda browser: login_pw_ele.get_attribute('value') == '')

        login_pw_ele.send_keys(password)
        driver.find_element_by_xpath("//input[@name='rememberMe']").click()
        driver.find_element_by_xpath("//input[@id='signInSubmit']").click()

        # Check if the Amazon account has been successfully logged in.
        logged_in = check_exists_by_xpath(driver, "//input[@id='twotabsearchtextbox']")

        # If Amazon requires an additional authentication, get the authenciation code from gmail API.
        if not logged_in:
            driver.find_element_by_xpath("//span[contains(text()" +
                                         ",'Email a one-time passcode to m********b@gmail.com')]").click()
            driver.find_element_by_xpath("//input[@id='continue']").click()

            gmail_driver = chrome_driver.setup()

            gmail_driver.get("https://mail.google.com/")
            gmail_driver.find_element_by_xpath("//input[@id='identifierId']").send_keys(email + u'\ue007')
            gmail_driver.find_element_by_xpath("//input[@name='password']").click()
            gmail_driver.send_keys(password)
            gmail_driver.send_keys(u'\ue007')

            driver.find_element_by_xpath("//input[@name='code']").click()


def search_product_id(driver, product_id):
    try:
        product_entered_to_search = False

        # Goes to amazon homepage, then clicks and clears anything in the search bar
        driver.get("https://www.amazon.com")
        search_bar = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='twotabsearchtextbox']")))
        search_bar.click()
        search_bar.clear()
        WebDriverWait(driver, 5).until(lambda browser: search_bar.get_attribute('value') == '')

        # Ensures that a product id is entered.
        while not product_entered_to_search:
            search_bar.click()
            search_bar.send_keys(product_id)
            if search_bar.get_attribute('value') == product_id:
                product_entered_to_search = True

        # Presses the enter key in the search bar.
        search_bar.send_keys(u'\ue007')

    except ValueError:
        print(f"The product_id {product_id} has no search results")


def get_num_results(driver):
    results_div = driver.find_element_by_xpath("//div[@class='a-section a-spacing-small a-spacing-top-small']")
    num_results_long = results_div.find_element_by_xpath("//span[contains(text(),'result')]").text
    num_results = int(num_results_long.split(" ")[-3].replace(',', ''))
    return num_results


def get_num_cart_items(driver):
    test = driver.find_element_by_xpath("//span[@id='nav-cart-count']").text.strip()
    return int(test)


# Selects the quantity.
def select_quantity(driver, quantity):
    select_quantity_num_avail = False
    string_quantity = str(quantity)

    select = Select(driver.find_element_by_xpath("//select[@id='quantity']"))

    option_list = list()
    for option in select.options:
        option_list.append(option.text.strip())

    if string_quantity in option_list:
        select_quantity_num_avail = True
        select.select_by_visible_text(string_quantity)

    return select_quantity_num_avail


def clear_cart(driver):
    print("Starting to clear cart ...")
    driver.get("https://www.amazon.com/gp/cart/view.html?ref_=nav_cart")
    xpath_for_multiple_items = "//div[3]//div[4]//div[1]//div[1]//div[1]//div[1]//div[2]//div[1]//span[2]//span[1]//input[1]"

    if check_exists_by_xpath(driver, "//span[@id='sc-subtotal-label-buybox']"):

        cart_total = get_num_cart_items(driver)
        start_cart_total = cart_total

        # While there is anything in the cart find a delete button and click it
        while cart_total > 0:
            if check_exists_by_xpath(driver, xpath_for_multiple_items):
                driver.find_element_by_xpath(xpath_for_multiple_items).click()

            else:
                driver.get("https://www.amazon.com/gp/cart/view.html?ref_=nav_cart")
                if check_exists_by_xpath(driver, "//span[2]//span[1]//input[1]"):
                    driver.find_element_by_xpath("//span[2]//span[1]//input[1]").click()

            cart_total = get_num_cart_items(driver)
            if cart_total == 0:
                print(f"Checkout cart has been cleared of {start_cart_total} items.")

    else:
        print("Checkout cart does not have any items to clear.")


def add_items_to_cart(orders_dict_list, driver, order_index, order_results_dict_list):

    # Iterates over each product for a given order.
    for product in orders_dict_list[order_index]['products']:

        # Initializes order specific tracking variables.
        went_to_product_page = False
        product_id_matches = False
        added_to_cart = False
        discovery_method = ""
        product_id = product['product_id']
        product_quant = product['quantity']
        json_dict = orders_dict_list[order_index]
        href_one = ""
        num_products = len(orders_dict_list[order_index]['products'])

        # Adds two strings to the product_id that would show up in the url for the given item.
        product_id_bh = "bh/" + product_id
        product_id_dp = "dp/" + product_id
        product_id_alts_list = [product_id_bh, product_id_dp]

        search_product_id(driver, product_id)

        # Ensures that the search results load.
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='s-result-list s-search-results sg-row']")))

        # Collects all the results from the search using a variety of different methods.

        # Method 1: Span
        search_results = driver.find_elements_by_xpath("//span[@class='a-size-medium a-color-base a-text-normal']")
        if len(search_results) > 0:
            discovery_method = "span"

        # Method 2: Div
        elif len(search_results) == 0:
            search_results = driver.find_elements_by_xpath(
                "//div[@class='a-section a-spacing-medium']//a[@class='a-link-normal a-text-normal']")
            if len(search_results) > 0:
                discovery_method = "div"

        time.sleep(.5)

        num_results = get_num_results(driver)

        # If there is only 1 result, make sure the product id is in the link url. Then, extract the href.
        if num_results == 1:

            # Extracts the url for the search result.
            prev_url = driver.current_url
            search_results[0].click()
            while prev_url == driver.current_url:
                pass

            href_one = driver.current_url

            # Check if the product_id is in the product page url.
            if any(product_id_alt in href_one for product_id_alt in product_id_alts_list):
                product_id_matches = True
            went_to_product_page = True

        # If there is more than one search result.
        elif num_results > 1:
            multiple_hrefs = []

            for search_result in search_results:
                if discovery_method == "span":
                    result_href = search_result.find_element_by_xpath('..').get_attribute("href")
                    multiple_hrefs.append(result_href)

                if product_id_bh in result_href or product_id_dp in result_href:
                    product_id_matches = True
                    href_one = result_href
                    driver.get(result_href)
                    went_to_product_page = True
                    break

        # Chooses One-time purchase if it is an option.
        if check_exists_by_xpath(driver, "//i[@class='a-icon a-accordion-radio a-icon-radio-inactive']"):
            alternate_selection_icon = driver.find_element_by_xpath("//i[@class='a-icon a-accordion-radio a-icon-radio-inactive']")
            alt_select_parent = alternate_selection_icon.find_element_by_xpath("..").text

            if "One-time purchase:" in alt_select_parent:
                driver.find_element_by_xpath("//i[@class='a-icon a-accordion-radio a-icon-radio-inactive']").click()
                time.sleep(2)

        # Check if select quantity and add to car exists
        select_quantity_exists = check_exists_by_xpath(driver, "//select[@id='quantity']")
        add_to_cart_exists = check_exists_by_xpath(driver, "//input[@id='add-to-cart-button']")

        select_quantity_num_avail = None
        # Select the quantity
        if went_to_product_page and product_id_matches and select_quantity_exists and add_to_cart_exists:
            select_quantity_num_avail = select_quantity(driver, product_quant)
            if select_quantity_num_avail:
                before_add_to_cart_quantity = get_num_cart_items(driver)
                driver.find_element_by_xpath("//input[@id='add-to-cart-button']").click()
                driver.get("https://www.amazon.com/")
                after_add_to_cart_quantity = get_num_cart_items(driver)

                if after_add_to_cart_quantity - before_add_to_cart_quantity == product_quant:
                    added_to_cart = True

        # Append the result of the order attempt to a dictionary/DataFrame
        result_row_dict = {'order_index': order_index,
                           'json_dict': json_dict,
                           'product_id': product_id,
                           'product_quant': product_quant,
                           'num_products': num_products,
                           'href_link': href_one,
                           'went_to_product_page': went_to_product_page,
                           'product_id_matches': product_id_matches,
                           'discovery_method': discovery_method,
                           'num_results': num_results,
                           'select_quantity_exists': select_quantity_exists,
                           'select_quantity_num_avail': select_quantity_num_avail,
                           'add_to_cart_exsts': add_to_cart_exists,
                           'added_to_cart': added_to_cart}
        order_results_dict_list.append(result_row_dict)

    return order_results_dict_list
