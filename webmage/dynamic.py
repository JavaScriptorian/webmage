from bs4 import BeautifulSoup as BS
import re
from selenium import webdriver
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager

class DynamicSpell:
    def __init__(self, url, driver_path=None, ghost=False):
        self.url = url
        self.driver_path = driver_path
        self.ghost = ghost

        self.initialize_driver()

    def initialize_driver(self):
        # Get chrome driver if no path is given.
        if self.driver_path == None:
            self.driver_path = ChromeDriverManager().install()

        # Set options to ignore useless errors.
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        if self.ghost:
            options.add_argument('--headless')
        # Open the chrome browser. It will show up unless ghost == True.
        self.driver = webdriver.Chrome(self.driver_path, chrome_options=options)
        # Go to the initialized webpage.
        self.driver.get(self.url)


    def close(self):
        self.driver.close()


    # For selecting first item based on CSS selector.
    def select(self, css_selector):
        return self.driver.find_element_by_css_selector(css_selector)


    # For selecting first item based on CSS selector.
    def selectAll(self, css_selector):
        return self.driver.find_elements_by_css_selector(css_selector)

    # Changes the URL of the original soup.
    def change_url(self, url):
        self.url = url
        self.driver.get(url)

    # Click on a element by its css selector
    def click(self, css_selector):
        self.driver.find_element_by_css_selector(css_selector).click()

    # Click on all elements by its css selector. Waits 0.25 between each click by default
    def clickAll(self, css_selector, wait_interval=0.25):
        clickable_elements = self.driver.find_elements_by_css_selector(css_selector).click()
        for el in clickable_elements:
            el.click()
            self.wait(wait_interval)

    def scroll(self, wait_interval, scroll_count, callback=None, verbose=True):
        counter = 1
        last_height = self.driver.execute_script("return document.scrollingElement.scrollHeight")

        while counter <= scroll_count:
            self.driver.execute_script(f"document.scrollingElement.scrollTop = document.scrollingElement.scrollHeight;")
            # Wait to load page
            self.wait(wait_interval)
            if verbose:
                print(f'\rScroll #{counter} completed!', end='')
            counter += 1
            
            # Execute callback function
            if callback:
                callback(self)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.scrollingElement.scrollHeight")
            print(new_height, last_height)

            if new_height == last_height:
                break
            last_height = new_height
        # Go to next line after scroll completion.
        print('')


    def infinite_scroll(self, wait_interval, callback=None, verbose=True):
        counter = 1
        last_height = self.driver.execute_script("return document.scrollingElement.scrollHeight")

        while True:
            self.driver.execute_script(f"document.scrollingElement.scrollTop = document.scrollingElement.scrollHeight;")
            # Wait to load page
            self.wait(wait_interval)
            if verbose:
                print(f'\rScroll #{counter} completed!', end='')
            counter += 1
            
            # Execute callback function
            if callback:
                callback(self.driver)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.scrollingElement.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height
        # Go to next line after scroll completion.
        print('')


    # Wait a certain amount of seconds to continue code.
    def wait(self, time_interval):
        sleep(time_interval)

    # Gets the end name of the URL
    def get_slug(self):
        # Get portion of URL after last forward slash.
        slug =  re.sub(r'^.+?/([^/]+?)$', r'\1', self.url)
        # Remove any hashes
        slug = re.sub(r'#[^#]+?$', r'', slug)
        # Remove any queries
        slug = re.sub(r'\?.+?$', r'', slug)
        return slug