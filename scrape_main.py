import time
import os
import requests
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

GOOGLE_PHOTOS = "https://photos.google.com/"
LOG_FILE_DOWN = "downloaded_logs.txt"
LOG_FILE_DEL = "deleted_logs.txt"
PROFILE_PATH = "/home/none/.config/chromium/"
PATH = os.getcwd() + '/test'
DEBUG = False

def download_image(url, destination_folder, file_name):

    response = requests.get(url)
    if response.status_code == 200:
        print('Downloading image {0}'.format(file_name))
        with open(os.path.join(destination_folder, file_name), 'wb') as f:
            f.write(response.content)
            f.close()

def click(driver, element_xpath):
    """Clicks the first photo to enter the gallery mode"""

    # max time to the first photo to appear 
    max_wait_time = 10 

    element_get = WebDriverWait(driver, max_wait_time).until(ec.presence_of_element_located((By.XPATH, element_xpath)))

    element_get.click()

def click_info(driver):

    info_button = '/html/body/div[1]/div/c-wiz/div[4]/c-wiz/div[1]/c-wiz[2]/div[2]/span/div/div[7]/span/button'

    # check if it's clicked or not
    try :
        element_get = WebDriverWait(driver, 3).until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/c-wiz/div[4]/c-wiz/div[1]/div[2]')))
    except :
        print("It's not there")

def save_log(log, file_):
    """Save the logs for deleted images and added images"""

    file_handler = open(file_, 'a')
    file_handler.write(log + '\n')

    file_handler.close()



def navigate(driver, move=1):
    """Use the arrow key to navigate the gallary"""
    
    # For testing
    # next_photo_xpath = '//*[@id="ow81"]/c-wiz[3]/div[2]/div[2]'

    moves = [Keys.LEFT, Keys.RIGHT]
    driver.find_element_by_css_selector('body').send_keys(moves[move])

def get_download_url(driver):
    """Gets the url of the photo"""
    max_wait_time = 2

    photo_url_xpath = '/html/body/div[1]/div/c-wiz/div[4]/c-wiz/div[1]/c-wiz[3]/div[2]/c-wiz/div[2]/div/div/img'
    photo_get = WebDriverWait(driver, max_wait_time).until(ec.visibility_of_element_located((By.XPATH, photo_url_xpath)))

    return photo_get.get_attribute("src")


def delete_photo(driver):

    del_icon_xpath = '/html/body/div[1]/div/c-wiz/div[4]/c-wiz/div[1]/c-wiz[2]/div[2]/span/div/div[9]/span/button'
    confirm_xpath = '/html/body/div[1]/div/div[2]/div/div[2]/div[3]/button[2]'

    # # click somewhere to activate the shit 
    # driver.find_element_by_css_selector('body').click()

    # clicking the icon
    driver.find_element_by_xpath(del_icon_xpath).click()

    time.sleep(2)
    # Confirm
    driver.find_element_by_xpath(confirm_xpath).click()

def check_exist(filename):
    
    name = filename.split('.')[0]

    # getting all files in the PATH
    file_list = os.listdir(PATH)

    for file_ in file_list:
        if name in file_:
            return True

    return False


def download_fast_shortcut(driver, filename):
    """Download directly using the Shift+D shortcut, no need to get the url"""

    #if not os.path.exists(filename):
    if not check_exist(filename):
        driver.find_element_by_css_selector('body').send_keys(Keys.SHIFT + "D")

def get_photo_info(driver):
    """Get Size, name and date of photo"""

    try: 
        metadata = driver.find_elements_by_class_name("rCexAf")
        metadata = [m.text for m in metadata if m.text != '']

        date = metadata[0].replace(" ", "_").replace("\n", "_")
        photo_name = metadata[1].split('\n')[0]
        size = metadata[1].split('\n')[-1].replace(' ','')

        print(f"date: {date}, name: {photo_name}, size: {size}")
        return date, photo_name, size
    except Exception as e :
        print(f"Error: {e}")


def main():

    date, filename, size = get_photo_info(driver) 

    # change the filename : name_date_size
    filename_mod = f"{filename}_{date}_{size}"

    # downloading 
    download_fast_shortcut(driver, filename_mod)
    save_log(filename, LOG_FILE_DOWN)

    delete = input(f"Do you want to delete {filename} ? (Y/N): ") 

    if delete.upper() == 'Y':
        delete_photo(driver)

        # append to the log file
        save_log(filename, LOG_FILE_DEL)
    else :
        navigate(driver)

    # important : to avoid getting false photo info
    time.sleep(2)

if __name__=='__main__':

    options = Options()
    options.add_argument(f"--user-data-dir={PROFILE_PATH}")

    if not DEBUG:
        options.add_argument("--mute-audio")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

    # Changing the download path 
    prefs = {'download.default_directory' : PATH}
    options.add_experimental_option('prefs', prefs)

    driver = webdriver.Chrome(options=options)

    driver.set_window_position(0, 0)
    driver.set_window_size(1024, 768)

    driver.get(GOOGLE_PHOTOS)

    # Clicking the first photo
    first_photo_xpath = '//*[@id="ow45"]/div[1]/div[2]/div[1]/div[2]'
    click(driver, first_photo_xpath)    

    time.sleep(1) 
    click_info(driver)

    time.sleep(2)

    while True:
        try:  
            main()
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
