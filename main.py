import os 
import requests
from custom_google import Create_Service

APP_NAME = "photoslibrary"
API_VERSION = "v1"
CRED_FILE = "secrets.json"
SCOPES = [
    "https://www.googleapis.com/auth/photoslibrary.readonly.appcreateddata",
    "https://www.googleapis.com/auth/photoslibrary.readonly"
]


"""
The quota limit for requests to the Library API is 10,000 requests per project per day. 
This includes all API requests, such as uploading, listing media, and applying filters, 
but not accessing media bytes from a base URL.

"""
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Read Access Only

# 1- Go to the console : google cloud platform
# 2 - Go to the libarary : choose photos lib api

def download_image(url, destination_folder, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        print('Downloading image {0}'.format(file_name))
        with open(os.path.join(destination_folder, file_name), 'wb') as f:
            f.write(response.content)
            f.close()

service = Create_Service(CRED_FILE, APP_NAME, API_VERSION, SCOPES)


# getting the albums 

def get_all_albums():
    test_album = service.albums().list(pageSize=50).execute()
    album_me = test_album.get("albums")
    next_page = test_album.get("nextPageToken")

    while next_page:
        test_album = service.albums().list(pageSize=50, pageToken=next_page).execute()
        album_me.append(test_album.get("albums"))
        next_page = test_album.get("nextPageToken")

    return album_me


media = service.mediaItems().list(pageSize=50).execute()
lst_media = media.get("mediaItems")
next_page = media.get("nextPageToken")
print(lst_media[5])
# # downloading the first batch
# for media_entry in lst_media:
#     file_name = media_entry["filename"]
#     base_url = media_entry["baseUrl"] + '=d'
#     download_file(base_url, "photos", file_name)


# # while next_page:
#     media = service.mediaItems().list(pageSize=50, pageToken=next_page).execute()
#     lst_media.append(media.get("mediaItems"))
#     next_page = media.get("nextPageToken")

#     # updating


"""
https://photos.google.com/_/PhotosUi/data/batchexecute?rpcids=XwAOJf&f.sid=-8354753373044497059&bl=boq_photosuiserver_20210722.08_p0&hl=en&soc-app=165&soc-platform=1&soc-device=1&_reqid=2110374&rt=c

https://photos.google.com/_/PhotosUi/data/batchexecute?rpcids=XwAOJf&f.sid=-8354753373044497059&bl=boq_photosuiserver_20210722.08_p0&hl=en&soc-app=165&soc-platform=1&soc-device=1&_reqid=2810374&rt=c

"""