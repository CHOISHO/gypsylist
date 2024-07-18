#!/usr/bin/env python3

"""
gypsylist.py: A web scraper for nomadlist.com, to avoid site restrictions.
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import re
import argparse
import os

BROWSER_BOOT_TIME = 3
NOMADLIST_DOMAIN = "https://nomadlist.com"

# Flag parsing
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--path', '-p', dest="path", type=str, required=True, help="URL path to do the request.")
parser.add_argument('--headless', '-H', dest="headless", action='store_true', default=False, required=False, help="Set browser in headless mode.")
parser.add_argument('--delay', '-d', dest="delay", type=int, default=5, required=False, help="Scroll pause time (default 5).")
parser.add_argument('--emoji', '-e', dest="emoji", action='store_true', default=False, required=False, help="Scroll pause time (default 5).")
args = parser.parse_args()

# Setup
options = Options()
options.headless = args.headless
options.add_argument("window-size=1400x600")
driver = webdriver.Firefox(options=options)
driver.get(NOMADLIST_DOMAIN + args.path)

# Get scroll height
time.sleep(BROWSER_BOOT_TIME)
last_height = driver.execute_script("return document.body.scrollHeight")
last_element_rank = 0
while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(args.delay)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")

    last_element_rank = driver.execute_script("return document.querySelector('.grid.show.view').childNodes.length")
     
    if new_height == last_height or last_element_rank > 100:
        break
    last_height = new_height

# Retrieve page source code and close the browser
html = driver.page_source
driver.close()

# Selecting view-container div
main_page = BeautifulSoup(html, 'html.parser')
view = main_page.find("div", {"class": "view-container"})

# Selecting ul and list
view_container = BeautifulSoup(str(view), 'html.parser')
list_view = view_container.find("ul", {"class": "grid show view"})

with open("output3.csv", "w", encoding="utf-8") as f:
    f.write("name,country,overall,cost,internet,liked,safety\n")
    for li in list_view.find_all("li"):
        # Retrieve city name
        city_name = BeautifulSoup(str(li.find("h2", {"class": "itemName"})), 'html.parser')
        if city_name.get_text() == "{itemName}" or city_name.get_text() == "None":
            continue
        f.write(city_name.get_text().replace(',', '.').strip() + ",")

        # Retrieve country name
        city_country = BeautifulSoup(str(li.find("h3", {"class": "itemSub"})), 'html.parser')
        f.write(city_country.get_text().strip() + ",")

        # Find information parsing span
        city_span = BeautifulSoup(str(li), 'html.parser')
        regex = r"class=((?<![\\])['\"])(rating-(?:.(?!(?<![\\])\1))*.?)\1"

        for content in city_span.find_all("span", {"class": "action"}):
            matches = re.finditer(regex, str(content.contents), re.MULTILINE)
            matches_list = list(re.finditer(regex, str(content.contents), re.MULTILINE))
            length = len(matches_list)

            # Get matching groups
            for matchNum, match in enumerate(matches, start=1):
                item = match.group(2).split(" ")[0].split("-")[1]
                rank = match.group(2).split(" ")[2][1:]

                # Formatting output
                if item == "main":
                    item = "overall"
                elif item == "cost":
                    item = "cost"
                elif item == "internet":
                    item = "internet"
                elif item == "like":
                    item = "liked"
                elif item == "safety":
                    item = "safety"
                else:
                    continue
    
                if matchNum == length:
                    f.write(rank)
                else:
                    f.write(rank + ",")
        f.write("\n")
