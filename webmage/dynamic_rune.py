class DynamicRune:
    def __init__(self, selenium_rune, driver):
        self.selenium_rune = selenium_rune
        self.driver = driver
        self.text = selenium_rune.text
        self.innerHTML = selenium_rune.get_attribute('innerHTML')
        self.outerHTML = selenium_rune.get_attribute('outerHTML')
        self.attributes = {}

        for attribute in selenium_rune.get_property('attributes'):
            self.attributes[attribute['nodeName']] = attribute['nodeValue']
        ibrk = 0


    def __repr__(self):
        return f'Dynamic Rune: {self.outerHTML}'

    def __str__(self):
        return f'Dynamic Rune: {self.outerHTML}'

    def select(self, css_selector):
        return DynamicRune(self.selenium_rune.find_element_by_css_selector(css_selector), self.driver)

    def selectAll(self, css_selector):
        return [DynamicRune(i, self.driver)for i in self.selenium_rune.find_elements_by_css_selector(css_selector)]