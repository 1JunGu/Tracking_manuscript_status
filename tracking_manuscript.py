import sys
import time
from datetime import datetime

import my_logging as MyLog
import remind_wechat as wechat
import remind_mail as mail

from selenium import webdriver
from selenium.webdriver import EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

class TrackingManuscript:
    def __init__(self, username, password, logger, site_type):
        self.logger = logger  # logger object
        self.username = username  # manuscript username
        self.password = password  # manuscript password
        self.site_type = site_type #plex or scholarOne

    def handle_popup(self, driver, timeout=5):
        button_text = ["Continue","Accept"] #only for the two buttons
        # Wait for the button_text pop-up window to appear, up to timeout seconds
        try:
            # First, try to find the "Continue" button
            try:
                button = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@class='actions']/input[@class='ejp-btn' and @value='Continue']"))
                )
                button.click()
                self.logger.debug("Clicked the 'Continue' button")
                return  # Exit the function if the "Continue" button is found and clicked
            except TimeoutException:
                self.logger.debug("No 'Continue' button found")

            # If the "Continue" button is not found, try to find the "Accept" button
            try:
                button = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Accept')]"))
                )
                button.click()
                self.logger.debug("Clicked the 'Accept' button")
                return  # Exit the function if the "Accept" button is found and clicked
            except TimeoutException:
                self.logger.debug("No 'Accept' button found")

            self.logger.debug("No 'Continue' or 'Accept' button found, Proceeding with the script")
        except NameError as e:
            self.logger.error(str(e) + ", terminating the script.")

    def find_link_by_strategy(self,driver, link_text, strategy="link_text", timeout=10):
        try:
            if strategy == "partial_link_text":
                locator = (By.PARTIAL_LINK_TEXT, link_text)
            elif strategy == "link_text":
                locator = (By.LINK_TEXT, link_text)
            elif strategy == "xpath":
                locator = (By.XPATH, f"//a[contains(text(), '{link_text}')]")
            elif strategy == "css_selector":
                locator = (By.CSS_SELECTOR, f"a[href*='{link_text.lower().replace(' ', '_')}']")
            else:
                raise ValueError(f"Unknown locator strategy: {strategy}")

            link = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return link
        except TimeoutException:
            self.logger.debug(f"TimeoutException: No link found containing the text '{link_text}' using the {strategy} strategy.")
            return None
        except ValueError as ve:
            self.logger.error(str(ve))
            return None

    def find_and_click_link(self,driver, link_text, timeout):
        strategies = ["partial_link_text","link_text", "xpath", "css_selector"]
        for strategy in strategies:
            self.logger.debug(f"Trying to find the '{link_text}' link using the {strategy} strategy.")
            link = self.find_link_by_strategy(driver, link_text, strategy, timeout)
            if link:
                self.logger.debug(f"using {strategy} strategy found the '{link_text}' link.")
                link.click()
                self.logger.debug(f"Clicked the '{link_text}' link")
                return
            else:
                self.logger.debug(f"Failed to find the '{link_text}' link using the {strategy} strategy.")
        else:
            self.logger.critical(f"fatal error: using all strategies failed to find the '{link_text}' link.")
            return None

    def extract_current_stage(self,driver): #use this function for plex
        # Use BeautifulSoup to parse the page HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # Find the <th> element containing the text_stage
        if self.site_type == "plex":
            text_stage = "Current Stage"
            # Find the <th> element containing the text_stage
            current_stage_header = soup.find("th", string=lambda text: text_stage in text if text else False)
            if current_stage_header:
                # Extract the actual stage information in the next <td> element
                current_stage = current_stage_header.find_next_sibling("td").text.strip()
                return current_stage
            else:
                self.logger.error(f"No header and {text_stage} information found.")
                return None
        elif self.site_type == "scholarOne":
            # Find the <td> element with the specified style and class
            status_cell = soup.find("td", style="border-bottom:none",text=True) #By adding text=True, we ensure that the <td> element contains text content 
            if status_cell:
                current_stage = status_cell.find("span", class_="pagecontents").get_text(strip=True)
                return current_stage
            else:
                self.logger.error(f"no status cell found.")
                return None


    def extract_stage_table(self,driver):
        # Use BeautifulSoup to parse the page HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")

        if self.site_type == "plex":
            # Find the table with the desired structure
            table = soup.find("table", attrs={"border": "5"}) #border = 5

            if table:
                # Check if the table has the desired header cells
                header_cells = table.find_all("th")
                if len(header_cells) >= 2 and header_cells[0].get_text(strip=True) == "Stage" and header_cells[1].get_text(strip=True) == "Start Date":
                    # Extract the table HTML
                    table_html = str(table)
                    self.logger.debug("Extracted the stage table.")
                    return table_html
                else:
                    self.logger.error("Table does not have the desired header cells.")
                    raise ValueError("Table does not have the desired header cells.")
            else:
                self.logger.error("Table not found.")
                raise ValueError("Table not found.")

        elif self.site_type == "scholarOne":
            # Find the table element by its id
            table = soup.find("table", attrs={"id": "authorDashboardQueue"})
            if table:
                # Extract the table HTML
                table_html = str(table)
                self.logger.debug("Extracted the stage table.")
                return table_html       
            else:
                self.logger.error("Table not found.")
                raise ValueError("Table not found.")
            

    def activate_browser(self,headless=True):
        options = EdgeOptions()
        options.use_chromium = True # use the chromium version of Edge
        if headless:
            options.add_argument('--headless')
        options.add_experimental_option('detach',True) # detach the browser
        # activate the browser
        driver = webdriver.Edge(options=options)
        return driver

    def login_and_navigate(self,driver,login_url):
        # navigate to the website
        driver.get(login_url)
        self.logger.debug("Navigated to the website")
        # wait for 10 seconds
        driver.implicitly_wait(5)
        self.handle_popup(driver, timeout=5)

        if self.site_type == "plex":
            # Note: the below code requires the Selenium version 4.0 or higher
            driver.find_element(by=By.ID, value="login").send_keys(self.username)
            driver.find_element(by=By.ID, value="password").send_keys(self.password)
            driver.find_element(By.XPATH, "//input[@value='Login']").click()
            self.logger.debug("Filled the login form and clicked the 'Login' button")
            self.handle_popup(driver,timeout=2)

            # Check if the "Live Manuscripts" link exists and navigate to it
            self.find_and_click_link(driver, "Live Manuscripts", timeout=5)
            self.handle_popup(driver, timeout=2)
            # Check if the "Check Status" link exists and navigate to it
            self.find_and_click_link(driver, "Check Status", timeout=5)
            self.handle_popup(driver, timeout=2)
            return driver
        elif self.site_type == "scholarOne":
            # Note: the below code requires the Selenium version 4.0 or higher
            driver.find_element(by=By.ID, value="USERID").send_keys(self.username)
            driver.find_element(by=By.ID, value="PASSWORD").send_keys(self.password)
            driver.find_element(by=By.ID, value="logInButton").click()
            self.logger.debug("Filled the login form and clicked the 'Login' button")

            driver.find_element(By.XPATH, "//a[contains(@href, 'AUTHOR_VIEW_MANUSCRIPTS')]").click()
            self.logger.debug("Navigate to the author page")

            return driver

    def monitor_status_changes(self, driver,notification_method, previous_stage_info):
        driver.refresh()
        self.logger.debug("Refreshed the page") #the time interval should be less than 30 minutes
        current_table = self.extract_stage_table(driver)
        current_status = self.extract_current_stage(driver)

        if current_status != previous_stage_info:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"Current Stage: {current_status}, Now : {current_time}"
            self.logger.status(message)
            previous_stage_info = current_status
            if notification_method == "wechat":
                return message
            elif notification_method == "email":
                return message, current_table, current_status