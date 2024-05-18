#selenium test
from selenium import webdriver
from selenium.webdriver.common.by import By

# activate the browser
driver = webdriver.Edge()
# navigate to the website
driver.get("https://www.selenium.dev/selenium/web/web-form.html")
# acquire the title of the website
title = driver.title
# print the title
print(title)

# wait for 0.5 seconds
driver.implicitly_wait(0.5)

# find the text box and submit button
text_box = driver.find_element(by=By.NAME, value="my-text")
submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

# enter the text in the text box
text_box.send_keys("Selenium")
submit_button.click()

text = message.text
print(text)

# close the browser
driver.quit()
