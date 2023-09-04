import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import csv


def write_csv(_name, _data, plural):
    with open(_name, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        if plural:
            csvwriter.writerows(_data)
        else:
            csvwriter.writerow(_data)


# Separate helper to select option from a drop-down
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


# Helper to ensure we try to find element multiple times
def get_element(by_val, value):
    try:
        elem = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((by_val, value))  # This is a dummy element
        )
    finally:
        return driver.find_element(by_val, value)


# Helper to ensure we try to find elements multiple times
def get_elements(by_val, value):
    try:
        elem = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((by_val, value))  # This is a dummy element
        )
    finally:
        return driver.find_elements(by_val, value)


# Clicks "Get Default Value" for middle options
def click_defaults():
    ids = ["defaultFuelVolumeLink", "defaultUsageHrsLink", "defaultHorsepowerLink"]
    for _id in ids:
        el = get_element(By.ID, _id).find_elements(By.XPATH, '*')[0]
        el.click()


# Helper function to record an element, set drp to True if element is a drop down
def record_el(name, drp):
    el = get_element(By.ID, name)
    if drp:
        return Select(el).first_selected_option.text
    return el.get_attribute("value")


# All elements on page and whether they are drop-downs
elements = [
    ["modelYear", True], ["Tier", True], ["Interim_Flg", True],
    ["fuelType", True], ["fuelVolumePerEngine", False], ["calculatedFuelVolumePerEngine", False],
    ["usageRate", False], ["horsepower", False], ["aftertreatmentCd", True],
    ["retrofitYear", True], ["vehicleRemainingLife", False]
]


# Keeps track of all current variables
def record_state():
    state = []
    for el in elements:
        if el[0] == "aftertreatmentCd" and float(state[-1].replace(",", '')) < 25:
            state.append("N/A")
        else:
            state.append(record_el(el[0], el[1]))
    return state


# hp: "horsepower", lifetime: "vehicleRemainingLife:, fuel: "fuelVolumePerEngine",
# year: "modelYear", upgradeYear: "retrofitYear", After-Treatment Config: "aftertreatmentCd"
def edit_field(name, val):
    el = get_element(By.ID, name)
    if el.tag_name == "select":
        by_vis_text(name, str(val))
    else:
        el.clear()
        el.send_keys(str(val))
    time.sleep(.2)


# Update to path of your driver
csvName = "scr_fuel_vol_4000_9000.csv"
options = Options()
options.page_load_strategy = 'eager'
driver = webdriver.Chrome(options=options)
driver.get("https://cfpub.epa.gov/quantifier/index.cfm?action=user.account")
login = get_element(By.ID, "login")
pw = get_element(By.ID, "password")
login.send_keys("dmaslia@umich.edu")
pw.send_keys("goofball1")
pw.send_keys(Keys.RETURN)
buttons = get_elements(By.CLASS_NAME, "gridButton")
driver.execute_script("arguments[0].click();", buttons[0])


# Batch size to record on csv, higher number: more efficient, lower number: less loss on program crash
batch_size = 4
# Set all Ranges Below
fuel_vol = range(4000, 9000, 10)
# Record ranges below, with other info about current scrape
metadata = "this is a current test"
# For big tests
upgrades = ["A: Neither SCR nor DPF", "B: SCR Only", "C: DPF Only", "D: Both SCR and DPF"]
titles = [el[0] for el in elements]
titles.extend(["NOx", "PM2.5", "HC", "CO", "CO2"])
write_csv(csvName, titles, False)

master_data = []
for idx, fuel in enumerate(fuel_vol):
    if not idx % batch_size:
        write_csv(csvName, master_data, True)
        master_data = []
    # Enter edit page
    edit_btn = get_element(By.ID, "editGroupBtn-1")
    edit_btn.click()
    # Clicks defaults for elements that have that option
    click_defaults()
    # Insert fields to edit below:
    edit_field("modelYear", 2012)
    edit_field("retrofitYear", 2017)
    edit_field("fuelVolumePerEngine", fuel)
    edit_field("vehicleRemainingLife", 5)
    edit_field("aftertreatmentCd", upgrades[1])
    # Grab all current variable values
    data = record_state()
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
    master_data.append(data)
    # Go back
    back = get_element(By.XPATH, "//input[@title='Return to the Update Project page']")
    back.click()
