#! python3
# -*- coding: utf-8 -*-
"""Naukri Daily update - Using Chrome"""

import io
import logging
import os
import sys
import time
import tempfile
import shutil
import uuid
import atexit
from datetime import datetime
from random import choice, randint
from string import ascii_uppercase, digits

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
# from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.chrome.options import Options    #use when running locally
# import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Get the current working directory
cwd = os.getcwd()

# Add folder Path of your resume
originalResumePath = os.path.join(cwd, 'ArpitCV_Perf.pdf')
# Add Path where modified resume should be saved
modifiedResumePath = os.path.join(cwd, 'ArpitCV_Perf.pdf')

# Update your naukri username and password here before running
username = "arpit160195@gmail.com"
password = "Varanasi@12345"
mob = "8766283235"  # Type your mobile number here

# False if you dont want to add Random HIDDEN chars to your resume
updatePDF = False

# If Headless = True, script runs Chrome in headless mode without visible GUI
headless = False

# ----- No other changes required -----

# Set login URL
NaukriURL = "https://www.naukri.com/nlogin/login"
# NaukriURL = "https://www.naukri.com/mnjuser/homepage"

logging.basicConfig(
    level=logging.INFO, filename="naukri.log", format="%(asctime)s    : %(message)s"
)
# logging.disable(logging.CRITICAL)
os.environ["WDM_LOCAL"] = "1"
os.environ["WDM_LOG_LEVEL"] = "0"


def log_msg(message):
    """Print to console and store to Log"""
    print(message)
    logging.info(message)


def catch(error):
    """Method to catch errors and log error details"""
    _, _, exc_tb = sys.exc_info()
    lineNo = str(exc_tb.tb_lineno)
    msg = "%s : %s at Line %s." % (type(error), error, lineNo)
    print(msg)
    logging.error(msg)


def getObj(locatorType):
    """This map defines how elements are identified"""
    map = {
        "ID": By.ID,
        "NAME": By.NAME,
        "XPATH": By.XPATH,
        "TAG": By.TAG_NAME,
        "CLASS": By.CLASS_NAME,
        "CSS": By.CSS_SELECTOR,
        "LINKTEXT": By.LINK_TEXT,
    }
    return map[locatorType.upper()]


def GetElement(driver, elementTag, locator="ID"):
    """Wait max 15 secs for element and then select when it is available"""
    try:

        def _get_element(_tag, _locator):
            _by = getObj(_locator)
            if is_element_present(driver, _by, _tag):
                return WebDriverWait(driver, 15).until(
                    lambda d: driver.find_element(_by, _tag)
                )

        element = _get_element(elementTag, locator.upper())
        if element:
            return element
        else:
            log_msg("Element not found with %s : %s" % (locator, elementTag))
            return None
    except Exception as e:
        catch(e)
    return None


def is_element_present(driver, how, what):
    """Returns True if element is present"""
    try:
        driver.find_element(by=how, value=what)
    except NoSuchElementException:
        return False
    return True


def WaitTillElementPresent(driver, elementTag, locator="ID", timeout=30):
    """Wait till element present. Default 30 seconds"""
    result = False
    driver.implicitly_wait(0)
    locator = locator.upper()

    for _ in range(timeout):
        time.sleep(0.99)
        try:
            if is_element_present(driver, getObj(locator), elementTag):
                result = True
                break
        except Exception as e:
            log_msg("Exception when WaitTillElementPresent : %s" % e)
            pass

    if not result:
        log_msg("Element not found with %s : %s" % (locator, elementTag))
    driver.implicitly_wait(3)
    return result


def tearDown(driver):
    try:
        driver.close()
        log_msg("Driver Closed Successfully")
    except Exception as e:
        catch(e)
        pass

    try:
        driver.quit()
        log_msg("Driver Quit Successfully")
    except Exception as e:
        catch(e)
        pass


def randomText():
    return "".join(choice(ascii_uppercase + digits) for _ in range(randint(1, 5)))


def LoadNaukri(headless):
    """Open Chrome to load Naukri.com"""
    options = Options()
    # options = uc.ChromeOptions()

    # Explicitly specify the Chrome binary location
    # options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"    #use when running locally
    options.binary_location = "/usr/bin/google-chrome"

    # Create a temporary directory for user data
    user_data_dir = tempfile.mkdtemp(prefix="chrome-user-data-" + str(uuid.uuid4()))
    log_msg("the user dir used is: " + user_data_dir)
    options.add_argument(f"--user-data-dir={user_data_dir}")

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'


    # Add additional Chrome options
    # options.add_argument("--disable-notifications")
    # options.add_argument("--start-maximized")
    # options.add_argument("--disable-popups")
    options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # options.add_argument("--disable-software-rasterizer")
    # options.add_argument("--incognito")

    # Initialize ChromeDriver
    driver = None
    try:
        # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)    #use when running locally
        driver = webdriver.Chrome(service=Service(executable_path=os.environ.get('CHROMEDRIVER_PATH')), options=options)
        log_msg("Created a new instance of Chrome Driver")
    except Exception as e:
        log_msg("Failed to create a new instance of Chrome Driver")
        log_msg(f"Error during Chrome initialization: {e}")
        raise e

    # Ensure the temporary directory is cleaned up when the driver quits
    def cleanup():
        try:
            if os.path.exists(user_data_dir):
                shutil.rmtree(user_data_dir, ignore_errors=True)
                log_msg(f"Deleted user data directory: {user_data_dir}")
        except Exception as e:
            log_msg("Failed to delete user data directory")

    atexit.register(cleanup)

    driver.get(NaukriURL)
    driver.implicitly_wait(1)
    return driver



def naukriLogin(headless=False):
    """Open Chrome browser and Login to Naukri.com"""
    status = False
    driver = None
    username_locator = "//*[@id='usernameField']"
    password_locator = "//*[@id='passwordField']"
    login_btn_locator = "//*[@type='submit' and normalize-space()='Login']"
    skip_locator = "//*[text() = 'SKIP AND CONTINUE']"
    heading_locator = "//div[@class='info__heading']"

    try:
        driver = LoadNaukri(headless)

        print(driver.title)

        if "naukri" in driver.title.lower():
            log_msg("Website Loaded Successfully.")
        else:
            log_msg("Website not loaded.")

        emailFieldElement = None
        if is_element_present(driver, By.XPATH, username_locator):
            log_msg("inside checking the username and pwd locator presence")
            if WaitTillElementPresent(driver, username_locator, "XPATH", 10):
                emailFieldElement = GetElement(driver, username_locator, locator="XPATH")
            if WaitTillElementPresent(driver, password_locator, "XPATH", 10):
                passFieldElement = GetElement(driver, password_locator, locator="XPATH")
            if WaitTillElementPresent(driver, login_btn_locator, "XPATH", 10):
                loginButton = GetElement(driver, login_btn_locator, locator="XPATH")
        else:
            log_msg("None of the elements found to login.")

        if emailFieldElement is not None:
            log_msg("inside pushing data in username and pwd locators")
            emailFieldElement.send_keys(username)
            driver.implicitly_wait(1)
            if emailFieldElement.get_attribute("value") == username:
                log_msg("Username entered successfully")
            else:
                log_msg("Username not entered successfully")
            passFieldElement.send_keys(password)
            driver.implicitly_wait(1)
            if passFieldElement.get_attribute("value") == password:
                log_msg("Password entered successfully")
            else:
                log_msg("Password not entered successfully")
            if loginButton is not None:
                log_msg("Login button found")
                loginButton.send_keys(Keys.ENTER)
                time.sleep(5)

                # After login, check for homepage heading or user profile indicator
                if WaitTillElementPresent(driver, heading_locator, "XPATH", timeout=20):
                    CheckPoint = GetElement(driver, heading_locator, "XPATH")
                    if CheckPoint:
                        log_msg("Naukri Login Successful")
                        status = True
                    else:
                        log_msg("Login checkpoint element not found")
                else:
                    log_msg("Login likely failed – homepage not loaded.")

            else:
                log_msg("Login button not found")
            # loginButton.click()
        else:
            log_msg("credentials not entered")

            # Added click to Skip button
            print("Checking Skip button")

            if WaitTillElementPresent(driver, skip_locator, "XPATH", 10):
                GetElement(driver, skip_locator, "XPATH").click()

            print(driver.title)

            if "home" in driver.title.lower():
                log_msg("Homepage Loaded Successfully.")
            else:
                log_msg("Homepage not loaded.")

            # CheckPoint to verify login
            if WaitTillElementPresent(driver, heading_locator, "XPATH", timeout=50):
                CheckPoint = GetElement(driver, heading_locator, "XPATH")
                if CheckPoint:
                    log_msg("Naukri Login Successful")
                    status = True
                    return (status, driver)
                else:
                    log_msg("Unknown Login Error")
                    return (status, driver)
            else:
                log_msg("Unknown Login Error")
                return (status, driver)

    except Exception as e:
        catch(e)
    return (status, driver)


def UpdateProfile(driver):
    try:
        mobXpath = "//*[@name='mobile'] | //*[@id='mob_number']"
        saveXpath = "//button[@ type='submit'][@value='Save Changes'] | //*[@id='saveBasicDetailsBtn']"
        view_profile_locator = "//*[contains(@class, 'view-profile')]//a"
        edit_locator = "(//*[contains(@class, 'icon edit')])[1]"
        save_confirm = "//*[text()='today' or text()='Today']"
        close_locator = "//*[contains(@class, 'crossIcon')]"

        WaitTillElementPresent(driver, view_profile_locator, "XPATH", 20)
        profElement = GetElement(driver, view_profile_locator, locator="XPATH")
        profElement.click()
        driver.implicitly_wait(2)

        if WaitTillElementPresent(driver, close_locator, "XPATH", 10):
            GetElement(driver, close_locator, locator="XPATH").click()
            time.sleep(2)

        WaitTillElementPresent(driver, edit_locator + " | " + saveXpath, "XPATH", 20)
        if is_element_present(driver, By.XPATH, edit_locator):
            editElement = GetElement(driver, edit_locator, locator="XPATH")
            editElement.click()

            WaitTillElementPresent(driver, mobXpath, "XPATH", 20)
            mobFieldElement = GetElement(driver, mobXpath, locator="XPATH")
            if mobFieldElement:
                mobFieldElement.clear()
                mobFieldElement.send_keys(mob)
                driver.implicitly_wait(2)
                
                saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
                saveFieldElement.send_keys(Keys.ENTER)
                driver.implicitly_wait(3)
            else:
                log_msg("Mobile number element not found in UI")

            WaitTillElementPresent(driver, save_confirm, "XPATH", 10)
            if is_element_present(driver, By.XPATH, save_confirm):
                log_msg("Profile Update Successful")
            else:
                log_msg("Profile Update Failed")

        elif is_element_present(driver, By.XPATH, saveXpath):
            mobFieldElement = GetElement(driver, mobXpath, locator="XPATH")
            if mobFieldElement:
                mobFieldElement.clear()
                mobFieldElement.send_keys(mob)
                driver.implicitly_wait(2)
    
                saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
                saveFieldElement.send_keys(Keys.ENTER)
                driver.implicitly_wait(3)
            else:
                log_msg("Mobile number element not found in UI")

            WaitTillElementPresent(driver, "confirmMessage", locator="ID", timeout=10)
            if is_element_present(driver, By.ID, "confirmMessage"):
                log_msg("Profile Update Successful")
            else:
                log_msg("Profile Update Failed")

        time.sleep(5)

    except Exception as e:
        catch(e)


def UpdateResume():
    try:
        # random text with with random location and size
        txt = randomText()
        xloc = randint(700, 1000)  # this ensures that text is 'out of page'
        fsize = randint(1, 10)

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", fsize)
        can.drawString(xloc, 100, "lon")
        can.save()

        packet.seek(0)
        new_pdf = PdfReader(packet)
        existing_pdf = PdfReader(open(originalResumePath, "rb"))
        pagecount = len(existing_pdf.pages)
        print("Found %s pages in PDF" % pagecount)

        output = PdfWriter()
        # Merging new pdf with last page of my existing pdf
        # Updated to get last page for pdf files with varying page count
        for pageNum in range(pagecount - 1):
            output.add_page(existing_pdf.pages[pageNum])

        page = existing_pdf.pages[pagecount - 1]
        page.merge_page(new_pdf.pages[0])
        output.addPage(page)
        # save the new resume file
        with open(modifiedResumePath, "wb") as outputStream:
            output.write(outputStream)
        print("Saved modified PDF : %s" % modifiedResumePath)
        return os.path.abspath(modifiedResumePath)
    except Exception as e:
        catch(e)
    return os.path.abspath(originalResumePath)


def UploadResume(driver, resumePath):
    try:
        attachCVID = "attachCV"
        CheckPointXpath = "//*[contains(@class, 'updateOn')]"
        saveXpath = "//button[@type='button']"
        close_locator = "//*[contains(@class, 'crossIcon')]"

        driver.get("https://www.naukri.com/mnjuser/profile")

        time.sleep(2)
        if WaitTillElementPresent(driver, close_locator, "XPATH", 10):
            GetElement(driver, close_locator, locator="XPATH").click()
            time.sleep(2)

        WaitTillElementPresent(driver, attachCVID, locator="ID", timeout=10)
        AttachElement = GetElement(driver, attachCVID, locator="ID")
        AttachElement.send_keys(resumePath)

        if WaitTillElementPresent(driver, saveXpath, locator="ID", timeout=5):
            saveElement = GetElement(driver, saveXpath, locator="XPATH")
            saveElement.click()

        WaitTillElementPresent(driver, CheckPointXpath, locator="XPATH", timeout=30)
        CheckPoint = GetElement(driver, CheckPointXpath, locator="XPATH")
        if CheckPoint:
            LastUpdatedDate = CheckPoint.text
            todaysDate1 = datetime.today().strftime("%b %d, %Y")
            todaysDate2 = datetime.today().strftime("%b %#d, %Y")
            if todaysDate1 in LastUpdatedDate or todaysDate2 in LastUpdatedDate:
                log_msg(
                    "Resume Document Upload Successful. Last Updated date = %s"
                    % LastUpdatedDate
                )
            else:
                log_msg(
                    "Resume Document Upload failed. Last Updated date = %s"
                    % LastUpdatedDate
                )
        else:
            log_msg("Resume Document Upload failed. Last Updated date not found.")

    except Exception as e:
        catch(e)
    time.sleep(2)


def main():
    log_msg("-----Naukri.py Script Run Begin-----")
    driver = None
    try:
        status, driver = naukriLogin(headless)
        if status:
            UpdateProfile(driver)
            if os.path.exists(originalResumePath):
                if updatePDF:
                    resumePath = UpdateResume()
                    UploadResume(driver, resumePath)
                else:
                    UploadResume(driver, originalResumePath)
            else:
                log_msg("Resume not found at %s " % originalResumePath)

    except Exception as e:
        catch(e)

    finally:
        tearDown(driver)

    log_msg("-----Naukri.py Script Run Ended-----\n")


if __name__ == "__main__":
    main()
