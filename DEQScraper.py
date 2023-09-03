import time

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from pandas import *
import csv


def by_vis_text(drp, text):
    drpDown = Select(get_element(By.ID, drp))
    attempts = 0
    while attempts < 10:
        try:
            drpDown.select_by_visible_text(text)
            break
        except:
            attempts = attempts + 1
            print("exception when calling " + text + " on " + drp)


def get_element(by_val, value):
    try:
        elem = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((by_val, value))  # This is a dummy element
        )
    finally:
        return driver.find_element(by_val, value)


def get_elements(by_val, value):
    try:
        elem = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((by_val, value))  # This is a dummy element
        )
    finally:
        return driver.find_elements(by_val, value)


# hp: "horsepower", lifetime: "vehicleRemainingLife:, fuel: "fuelVolumePerEngine",
# year: "modelYear", upgradeYear: "retrofitYear"
def edit_field(name, val, data):
    print("editing field: " + name)
    el = get_element(By.ID, name)
    if name == "modelYear" or name == "retrofitYear":
        by_vis_text(name, str(val))
    else:
        el.clear()
        el.send_keys(str(val))
    data.append(str(val))
    time.sleep(.2)


# Update to path of your driver
csvName = "test"
driver = webdriver.Chrome()
driver.get("https://cfpub.epa.gov/quantifier/index.cfm?action=user.account")
login = get_element(By.ID, "login")
pw = get_element(By.ID, "password")
login.send_keys("dmaslia@umich.edu")
pw.send_keys("goofball1")


pw.send_keys(Keys.RETURN)
buttons = get_elements(By.CLASS_NAME, "gridButton")
driver.execute_script("arguments[0].click();", buttons[0])
# Set All Ranges Below
yearRange = range(2012, 2024)
# Record ranges below, with other info about current scrape
metadata = "this is a current test"
# For big tests
upgrades = ["A: Neither SCR nor DPF", "B: SCR Only", "C: DPF Only", "D: Both SCR and DPF"]
titles = ["fuel", "hp", "tier", "upgrade", "life expectancy", "NOx", "PM2.5", "HC", "CO", "CO2"]
# Master data
full_data = []

with open(csvName, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(metadata)


for year in yearRange:
    data = []
    # Enter edit page
    edit_btn = get_element(By.ID, "editGroupBtn-1")
    edit_btn.click()
    # Insert fields to edit below:
    edit_field("modelYear", year, data)
    edit_field("retrofitYear", year, data)
    edit_field("vehicleRemainingLife", 5, data)
    # Save
    save = get_element(By.ID, "saveGroupBtn")
    save.click()
    # Quantify
    quantify = get_element(By.XPATH, "//input[@title='Quantify Project Emissions']")
    quantify.click()
    # Record data
    rows = get_elements(By.CLASS_NAME, "data")
    for cell in rows[0].find_elements(By.TAG_NAME, 'td'):
        data.append(cell.text)
    data.pop()
    # Add to master data
    full_data.append(data)
    # Go back
    back = get_element(By.XPATH, "//input[@title='Return to the Update Project page']")
    back.click()


with open(csvName, 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(full_data)


# SPARE CODE IF WE ARE CHANGE TIER
#                     if t == 3:
#                         by_vis_text("Tier", "Tier 3")
#                         data.append("Tier 3")
#                         data.append("n/a")
#                         if u != 0:
#                             collect = False
#                     else:
#                         by_vis_text("Tier", "Tier 4")
#                         data.append("Tier 4")
#                         if t == 4:
#                             by_vis_text("Interim_Flg", "Interim")
#                             by_vis_text("aftertreatmentCd", upgrades[u])
#                             data.append(upgrades[u])
#                         else:
#                             by_vis_text("Interim_Flg", "Final")
#                             if u == 0:
#                                 collect = False
#                                 by_vis_text("aftertreatmentCd", upgrades[1])
#                                 data.append(upgrades[1])
#                             else:
#                                 by_vis_text("aftertreatmentCd", upgrades[u])
#                                 data.append(upgrades[u])
