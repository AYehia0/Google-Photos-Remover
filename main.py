"""

Delete idea, idk if it's gonna work or not

https://photos.google.com/_/PhotosUi/data/batchexecute?rpcids=XwAOJf&f.sid=-8354753373044497059&bl=boq_photosuiserver_20210722.08_p0&hl=en&soc-app=165&soc-platform=1&soc-device=1&_reqid=2110374&rt=c

https://photos.google.com/_/PhotosUi/data/batchexecute?rpcids=XwAOJf&f.sid=-{PHOTO_ID}&bl=boq_photosuiserver_{DATE}.08_p0&hl=en&soc-app=165&soc-platform=1&soc-device=1&_reqid={REQ_ID}&rt=c

"""

"""
The quota limit for requests to the Library API is 10,000 requests per project per day. 
This includes all API requests, such as uploading, listing media, and applying filters, 
but not accessing media bytes from a base URL.

"""
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Read Access Only

# 1- Go to the console : google cloud platform
# 2 - Go to the libarary : choose photos lib api

import os 
import json
import sys
import time
import requests
import math
import argparse
from datetime import datetime
from custom_google import Create_Service

# important : for deleting and doing some web automation
from scrape_main import *

# loading the configs
from config import *


def save_image(url, destination_folder, file_name):
    """Save image to a file"""

    # check if destination folder exists
    if not os.path.isdir(destination_folder):
        os.makedirs(destination_folder)

    # check if file exsits 
    # idk if "/" works on windows, who uses windows anyways 
    if os.path.isfile(f"{destination_folder}/{file_name}"):
        return

    # Checking if the response is OK
    response = requests.get(url)
    if response.status_code == 200:
        print('Downloading image {0}'.format(file_name))
        with open(os.path.join(destination_folder, file_name), 'wb') as f:
            f.write(response.content)
            f.close()

def get_media_items(service, filter_):
    """Download all photos based on the filter"""

    try : 
 
        media = service.mediaItems().search(body=filter_).execute()
        lst_media = media.get("mediaItems")
        next_page = media.get("nextPageToken")

        # while nextPage isn't empty
        while next_page:

            filter_['pageToken'] = next_page
            media = service.mediaItems().search(body=filter_).execute()

            if media.get('mediaItem') is not None:
                lst_media.append(media.get("mediaItems"))
                
                # updating
                next_page = media.get("nextPageToken")
                break
            else:
                next_page = ''

        return lst_media

    except Exception as e:
        print(e)
        return None

def conv_size(size_bytes):
    """Convert bytes to human readable size"""

    size_name = ("B", "KB", "MB", "GB")

    if size_bytes == 0:
        return "0B"

    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    return f"{s}{size_name[i]}"

def is_img(img_name):
    """Returns true if the filename isn't a video"""

    if img_name.split('.')[-1] in VID_EXT:
        return False

    return True

def get_img_size(img_url, img_name):
    """Get the size of the image by making a GET requests and check the head"""

    if img_url is None:
        return None, None

    # check if it's a video
    if not is_img(img_url):
        img_url += '=dv'
    else:
        img_url += '=d'

    try:
        img_size_bytes = int(requests.head(img_url, allow_redirects=True).headers['content-length'])
        human_read_size = conv_size(img_size_bytes)

        # return both human readable and bytes
        return human_read_size, img_size_bytes
    except :
        return None, None

def get_log(media_items, file_name, flag, using_log=False):
    """Saving a log file with all the info about the images from starting date to ending date""" 

    import csv

    # checking if the file exists, yes then headers must have been added
    header_added = os.path.isfile(file_name) 
    for media_item in media_items:
        img_name = media_item['filename']
        img_date = media_item['mediaMetadata']['creationTime']
        product_url = media_item['productUrl']

        if not using_log:
            img_url = media_item['baseUrl']
        else:
            img_url = None

        # getting img size
        img_size, _ = get_img_size(img_url, img_name)

        with open(file_name, mode='a', newline='') as log_file:

            fieldnames = ['Name', 'Url', 'Size', 'CreationDate', 'exists']
            writer = csv.DictWriter(log_file, fieldnames=fieldnames)

            if not header_added: 
                writer.writeheader()
                header_added = True
            writer.writerow({
                'Name': img_name,
                'Url': product_url,
                'Size': img_size,
                'CreationDate': img_date,
                'exists': flag
            })

def save_logs(media_items):
    """Save the logs for images based on some filters"""

    # name of the log_file based on today's date
    LOG_FILE_NAME = datetime.today().strftime('%Y-%m-%d_%H:%M:%S') + "_log.json"
    logs_ = []

    for img_res in media_items:

        # no login is required to view, gonna use it to get the actual size of the image
        img_url = img_res['baseUrl']

        # requires login
        product_url = img_res['productUrl']

        img_name = img_res['filename']

        # img size : 
        img_size_human, size_bytes  = get_img_size(img_url, img_name)

        data_template = {
            "filename" : img_name,
            "productUrl" : product_url,
            "size_human" : img_size_human,
            "size_bytes" : size_bytes,
            'mediaMetadata': {
                'creationTime': img_res['mediaMetadata']['creationTime']
            }
        }

        # appending 
        logs_.append(data_template)

    # Opening a file 
    file_ = open(LOG_FILE_NAME, 'w')

    # Saving the data
    json.dump(logs_, file_)

    # Closing the file
    file_.close()

    return LOG_FILE_NAME

def get_total_size(log):
    """
    Get the total size of all the images(to be downloaded/deleted) in human readable format 
    by summing all the bytes in the logfile then converting
    """

    file_size = 0

    for file_ in log:

        if file_['size_bytes'] is not None:
            file_size += file_['size_bytes']

    human_read_size = conv_size(file_size)

    return human_read_size

def delete_images(media_items, log_file=None):
    """Delete an images based on log file or some filters"""

    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as ec

    if log_file is None: 
        # getting the first ProductUrl : our start point 
        start_url = media_items[0]['productUrl']
        end_url = media_items[-1]['productUrl'] 

    else:
        try :
            # reading from a log file 
            file_handle = open(log_file, 'r')
            media_items = json.load(file_handle)

            start_url = media_items[0]['productUrl']
            end_url = media_items[-1]['productUrl'] 

            print(f"Total size to be removed : {get_total_size(media_items)}")

        except Exception as e:
            print("Invalid log file, make sure it's generated by that script!")
            print(e)
            sys.exit()
            
    # getting the webdriver ready
    options = Options()

    if not DEBUG:
        options.add_argument("--mute-audio")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

    profile = webdriver.FirefoxProfile(PROFILE_PATH)

    # Use the full path
    driver = webdriver.Firefox(firefox_profile=profile, options=options)

    driver.set_window_position(0, 0)
    driver.set_window_size(1024, 768)

    # WARNING msg
    print(f"You are deleting {len(media_items)} item")

    driver.get(end_url)
    end_url = driver.current_url

    # print("--------------------------------")
    # print(f"EndUrl : {end_url}")
    # print(f"TotalNumberOfPhotos : {len(media_items)}")
    # print("--------------------------------")

    time.sleep(1)
    driver.get(start_url)
    time.sleep(3)

    current_url = driver.current_url 

    # check for invalid urls 
    # so that u don't fall into an inf loop
    try:
        driver.find_element_by_xpath('/html/body/div[1]/div/c-wiz/div[4]/c-wiz/div[1]/c-wiz[3]/div[2]/c-wiz/div[2]/div/div')
    except :
        print("This Photo doesn't exist, are you sure you didn't delete before ?")
        sys.exit()

    while True:
        try:
            time.sleep(.5)

            driver.find_element_by_css_selector('body').send_keys("#")
            time.sleep(1)
            driver.find_element_by_css_selector('body').send_keys(Keys.RETURN)
            time.sleep(1)

            # getting the url
            url = driver.current_url

            #skips a photo, last or first idk
            if url == end_url:
                break
            print(f"Removing: {url}")
        except Exception as e:
            print(f"This Photo doesn't exist, are you sure you didn't delete before ? , Error: {e}")
            driver.close()
        
    driver.close()

def download_images(response):
    """Downloading an image by extracting the baseUrl from the response"""

    for img_res in response:
        
        img_name = img_res['filename']
        img_date = img_res['mediaMetadata']['creationTime']
        img_url = img_res['baseUrl']

        # check if the file is a video
        if not is_img(img_name):
            img_url += '=dv'
        else:
            img_url += '=d'

        # Saving the image
        save_image(img_url, "TEST", img_name)

def check_date(date):
    """Return True if the date is valid"""

    # Getting the date
    month, day, year = get_date(date)

    correctDate = None
    try:
        newDate = datetime(year, month, day)
        correctDate = True
    except ValueError:
        correctDate = False
    return correctDate

def get_date(full_date):
    """Return the date separated as : day, month, year"""

    month, day, year = map(int, full_date.split('/'))

    return day, month, year

def get_response_body(start_date, end_date):
    """Return the response containing the dates"""

    sdate_day, sdate_month, sdate_year = get_date(start_date)
    edate_day, edate_month, edate_year = get_date(end_date)

    request_body = {
        # Changing the page size determines how many to be fetched per request
        'pageSize': 20,
        'filters': {
            'dateFilter': {
                'ranges': [
                    {
                    'startDate': {
                        'year': sdate_year,
                        'month': sdate_month,
                        'day': sdate_day
                    },
                    'endDate': {
                        'year': edate_year,
                        'month': edate_month,
                        'day': edate_day
                    }
                    }
                ]
            }
        }
    }
    return request_body

def do_command(command_type, service, request_body, mod_flag, use_media_items=True, use_log_file=None):
    """
    Perform the command based on its type

    types :
        download : -d , creates the mediaItems, download then save logs
        remove :   -r , creates the mediaItems, Remove then save logs
        download_remove : -dr , creates the mediaItems, download , remove, then save logs
        get logs : -g , gets the logs from google photos api

    flags :
        mod_flag : modification flag, Photo exists in the server or not
        use_media_items : while deleting using a log file, None is used
        use_log_file: setting the name for some Print log file 
    """

    # Flags to know what to do
    download_flag, remove_flag = False, False

    print("Getting data from google.photos please wait...")
    # Getting the info about the range of dates

    if use_media_items:
        # checking if log file is provided 
        media_items = get_media_items(service, request_body)

        if media_items is None:
            print("No images, Exiting...")
            return

    # checking the type of the command 
    if command_type == '-dr':
        download_flag, remove_flag = True, True
    elif command_type == '-d':
        download_flag = True
    elif command_type == '-r':
        remove_flag = True

    if download_flag:
        # Downloading the images
        print("Downloading, please wait...")
        download_images(media_items)

    if remove_flag:

        if use_media_items == False:
            media_items = None
            print(f"Getting data from {use_log_file} please wait...")
            delete_images(media_items, use_log_file)

        # Removing the images
        print("Removing, please wait...")
        delete_images(media_items)

    if command_type == '-g':
        print("Saving to a log file...")

        get_log(media_items, 'report_logs.csv', True) 
        save_logs(media_items)

        return

    # Saving logs
    print("Saving to a log file...")
    get_log(media_items, 'downloaded_removed.csv', mod_flag) 


def main():
    # Create the parser
    my_parser = argparse.ArgumentParser(description='Download/Remove Google-Photos using your terminal')

    # Add Date arguments
    my_parser.add_argument('-s', '--start_date', metavar='', type=str, help='Starting date must be M/D/Y')
    my_parser.add_argument('-e', '--end_date', metavar='', type=str, help='Ending date must be M/D/Y')

    # only one command allowed
    group = my_parser.add_mutually_exclusive_group()
 
    group.add_argument('-d', '--download', action='store_true', help='command: Download Photos')
    group.add_argument('-r', '--remove', action='store_true', help='command: Remove Photos')
    group.add_argument('-dr', '--download-remove', action='store_true', help='command: Download then Remove')

    # logs related args
    my_parser.add_argument('-g', '--get', action='store_true', help='Get a info based on the date')
    my_parser.add_argument('--log', '-l', dest="log", help="Use an existing log file to remove photos")

    # Execute parse_args()
    args = my_parser.parse_args()

    # check for invalid options 
    if (args.download_remove or args.download) and args.log:
        my_parser.error("Can't download using an existing log file!")

    if (args.start_date or args.end_date) and args.log:
        my_parser.error("Use the date range with while only --download, --remove or --download_remove")

    if not (args.download or args.download_remove or args.remove or args.get):
        my_parser.error('No action requested, add --download or --remove or --get')
    else:
        if args.start_date and args.end_date:

            # Creating the service
            service = Create_Service(CRED_FILE, APP_NAME, API_VERSION, SCOPES)

            # getting the date
            sdate = args.start_date
            edate = args.end_date

            # checking the date
            if not check_date(sdate) or not check_date(edate):
                print("Invalid date...")
                sys.exit()
            
            # setting the response 
            request_body = get_response_body(sdate, edate)

            # if get only
            if args.get:
                do_command('-g', service, request_body, True)

            # if download and remove 
            if args.download_remove:
                do_command('-dr', service, request_body, False)

            # if download only
            if args.download:
                do_command('-d', service, request_body, True)

            # if remove only
            if args.remove:
                do_command('-r', service, request_body, False)

        elif args.log:

            if args.get:
                my_parser.error("Use the --log arg with only -r ")

            if args.remove:
                # since we're fetching from a log file
                service, request_body = None, None
                do_command('-r', service, request_body, False,  use_media_items=False, use_log_file=args.log)

        else:
            my_parser.error('Invalid Operation, use -h for more info')

if __name__=='__main__':
    main()
