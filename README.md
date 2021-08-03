<p align="center">
  <a>
    <img src="https://img.shields.io/github/last-commit/AYehia0/Google-Photos-Remover?style=for-the-badge&logo=github" alt="commit"><br>
    <img src="https://forthebadge.com/images/badges/built-with-love.svg">
    <img src="https://forthebadge.com/images/badges/open-source.svg">
    <img src="https://forthebadge.com/images/badges/made-with-python.svg">
  </a>
</p>


# Google-Photos-Remover
Remove and Download photos from your Google-Photos using google's api and selenium.


# Getting started 

- [Requirements](#requirements)
- [Installation](#installaion)
- [Usage](#usage)
- [Todo](#todo)

# Requirements

  1. API keys from google: check [google-console](https://console.cloud.google.com/apis/api/photoslibrary.googleapis.com/) then download the keys as json file.
  2. FIREFOX profile with your google account logged in : [mozila guide](https://support.mozilla.org/en-US/kb/profile-manager-create-remove-switch-firefox-profiles)
  3. Python 3.5+
  4. Install the google-api ```pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib``` 
  5. Selenium, ```pip install selenium```
  6. Geckodriver : install based on your OS, or use the one in the repo by specifiy the ```executable_path```
  
  
# Installation 

  1. clone the repo
  2. set the ```config.py```.
  3. run

# Usage 

run ```python main.py -h``` for guide.

```
usage: main.py [-h] [-s] [-e] [-d | -r | -dr] [-g] [--log LOG]

Download/Remove Google-Photos using your terminal

optional arguments:
  -h, --help            show this help message and exit
  -s , --start_date     Starting date must be M/D/Y
  -e , --end_date       Ending date must be M/D/Y
  -d, --download        command: Download Photos
  -r, --remove          command: Remove Photos
  -dr, --download-remove
                        command: Download then Remove
  -g, --get             Get a info based on the date
  --log LOG, -l LOG     Use an existing log file to remove photos
```

## Examples 

1. download images then remove from the server.
```
$ python main.py -dr -s 3/12/2019 -e 6/12/2019
Getting data from google.photos please wait...
Downloading, please wait...
Downloading image 260417015_64482.jpg
Downloading image 853436938_384185.jpg
Downloading image 455208641_180536.jpg
Downloading image 257914262_382413.jpg
...
```
2. get csv file with the images without downloading.
```
$ python main.py -g -s 3/12/2019 -e 6/12/2019     
Getting data from google.photos please wait...
Saving to a log file...
```
3. remove photos based on a log file.
```
$ python main.py -r --log 2021-08-01_17:14:28_log.json 
Getting data from google.photos please wait...
Getting data from 2021-08-01_17:14:28_log.json please wait...
...
```

# Todo

- [ ] use a database to save logs to avoid duplicate entries.
- [ ] remove using the csv





