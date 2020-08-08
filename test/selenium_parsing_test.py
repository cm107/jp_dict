from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())

driver.get('https://jisho.org/search/%E6%97%A5')
print(f'driver.title: {driver.title}')
primary_elem = driver.find_element_by_id('primary')
print(dir(primary_elem))
print(f'primary_elem.text: {primary_elem.text}')
print(f'primary_elem.tag_name: {primary_elem.tag_name}')
driver.close()