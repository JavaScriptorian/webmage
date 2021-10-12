import os
import re
import requests
import time
from bs4 import BeautifulSoup as BS 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# Creates a new exception which can be thrown if the status code is not 200.
class RequestError(Exception):
    pass


class WebSpell:
    def __init__(self, url, driverPath=None, encoding='utf-8'):
        self.url = url
        self.filename = self.slug()
        self.encoding = encoding
        self.driverPath = driverPath


    def slug(self):
        if os.path.isfile(self.url):
            self.open()
            return self.url
        elif 'http' not in self.url:
            assert Exception("You have not inputted a valid URL or filename.")
        slug = re.sub(r'https?://', r'', self.url)
        slug = re.sub(r'www\.', r'', slug)
        slug = re.sub(r'/', r'.', slug)
        slug = re.sub(r'\?', r'__', slug)
        slug = re.sub(r'\.__', r'__', slug)
        return slug

    # For opening HTML files on local drive.
    def open(self):
        with open(self.url, 'r', encoding='utf-8') as fOut:
            self.soup = BS(fOut.read(), 'html.parser')
            return fOut.read().splitlines()

    # For requesting static HTML files by HTTP request.
    def get(self):
        self.request = requests.get(self.url)
        self.encoding = self.request.encoding
        self.response = self.request.status_code
        if self.response != 200:
            assert Exception(f"Your request was rejected. Status Code: {self.response}")
        self.soup = BS(self.request.content, 'html.parser')
        self.method = 'get'
        return {"request": self.request, "soup": self.soup}

    # For opening webpage with headless Chrome driver.
    def drive(self, nextURL=False, ghost=False):
        # Check to see if driverPath is None. If None, then install from ChromeDriverManager package.
        if self.driverPath == None: 
            self.driverPath = ChromeDriverManager().install()

        if not hasattr(self, 'driver'):
            options = webdriver.ChromeOptions()
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            if ghost == True:
                options.add_argument('--headless')
            self.driver = webdriver.Chrome(self.driverPath, chrome_options=options)
        if nextURL:
            self.url = nextURL
        self.driver.get(self.url)
        self.soup = BS(self.driver.page_source, 'html.parser')
        self.method = 'drive'
        return self.driver

    def close(self):
        self.driver.close()

    # For selecting first item based on CSS selector.
    def select(self, css_selector):
        if hasattr(self, 'soup'):
            return self.soup.select_one(css_selector)
        else:
            # For colors:
            # https://ozzmaker.com/add-colour-to-text-in-python/#:~:text=To%20make%20some%20of%20your,right%20into%20the%20print%20statement.
            selection = input('\033[1;37;45mWarning:\033[0;37;40m You did not use the get() or drive() function.\nWhich function do you want to use? (GET or DRIVE): ')
            while True:
                if selection.lower() == 'drive':
                    self.drive()
                    break
                elif selection.lower() == 'get':
                    self.get()
                    break
                else:
                    selection = input('\033[1;37;45mWarning:\033[0;37;40m You need to type DRIVE or GET. Try again! ')
            
            if self.method == 'drive':
                return self.driver.find_element_by_css_selector(css_selector)
            return self.soup.select_one(css_selector)

    # For selecting all items based on CSS selector.
    def selectAll(self, css_selector):
        if self.method == 'get':
            return self.soup.select(css_selector)
        elif self.method == 'drive':
            return self.driver.find_elements_by_css_selector(css_selector)
        else:
            # For colors:
            # https://ozzmaker.com/add-colour-to-text-in-python/#:~:text=To%20make%20some%20of%20your,right%20into%20the%20print%20statement.
            selection = input('\033[1;37;45mWarning:\033[0;37;40m You did not use the get() or drive() function.\nWhich function do you want to use? (GET or DRIVE): ')
            while True:
                if selection.lower() == 'drive':
                    self.drive()
                    break
                elif selection.lower() == 'get':
                    self.get()
                    break
                else:
                    selection = input('\033[1;37;45mWarning:\033[0;37;40m You need to type DRIVE or GET. Try again! ')
            if self.method == 'get':
                return self.soup.select(css_selector)
            elif self.method == 'drive':
                return self.driver.find_elements_by_css_selector(css_selector)

    
    def write(self, soupObject=False, filename=False):
        filename = filename if filename else self.filename
        with open(filename, 'w', encoding='utf-8') as fOut:
            if not soupObject:
                print(self.soup, file=fOut)
            else:
                print(soupObject, file=fOut)


    def append(self, soupObject=False, filename=False):
        filename = filename if filename else self.filename
        if not soupObject:
            with open(filename, 'a', encoding='utf-8') as fOut:
                print(self.soup, file=fOut)
        else:
            with open(filename, 'a', encoding='utf-8') as fOut:
                print(soupObject, file=fOut)


    def click(self, css_selector):
        if hasattr(self, 'driver'):
            self.drive()
        self.driver.select(css_selector).click()
        self.wait(5)
        self.soup = BS(self.driver.page_source, 'html.parser')


    def scroll(self, time_interval, scroll_count):
        self.wait(time_interval)
        counter = 0
        last_height = self.driver.execute_script("return document.scrollingElement.scrollHeight")


        while scroll_count == 'infinite' or counter <= scroll_count:
            scrollTo = self.driver.execute_script("return document.scrollingElement.scrollHeight")
            self.driver.execute_script(f"document.scrollingElement.scrollTop = document.scrollingElement.scrollHeight;")
            # Wait to load page
            counter += 1
            print(f'Scroll #{counter} completed!')
            time.sleep(time_interval)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.scrollingElement.scrollHeight")
            print(new_height, last_height)

            if new_height == last_height:
                break
            last_height = new_height

    def wait(self, time_interval):
        time.sleep(time_interval)
