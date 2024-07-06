from twikit import Client
import requests
import schedule
import time
import hashlib
import os
from dotenv import load_dotenv, find_dotenv


# For some reason it doesn't call find_dotenv by itself on my machine...
load_dotenv(find_dotenv(usecwd=True))

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
URL = os.getenv("URL")
USER = os.getenv("USER")

def UpdateRequest(payload):
    headers = {'Authorization': 'bearer ' + AUTH_TOKEN}
    response = requests.post("https://" + URL + '/api/i/update', json=payload, headers=headers)
    print("UpdateRequest: Processing response...")
    ProcessResponse(response.status_code, response.json)

# Maybe add a return for this.
def ProcessResponse(status_code, json):
    if status_code == 200 or status_code == 204:
        print("success!")
    else:
        print("failed!")
        print(f"Status Code: {status_code}")
        print(json) #TODO: Output the JSON cleanly

def UpdateBanner(imageId):
    payload = {
        'bannerId' : imageId,
        'i' : AUTH_TOKEN
    }
    UpdateRequest(payload)

def UpdateAvatar(imageId):
    payload = {
        'avatarId' : imageId,
        'i' : AUTH_TOKEN
    }
    UpdateRequest(payload)

def UploadImage(url):
    headers = {'Authorization': 'bearer ' + AUTH_TOKEN}
    payload = {
        'url' : url,
        'i' : AUTH_TOKEN
    }
    response = requests.post("https://" + URL + '/api/drive/files/upload-from-url', json=payload, headers=headers)
    print("UploadImage: Processing response...")
    ProcessResponse(response.status_code, response.json)
    # return response code?

def SearchForImage(imageURL):
    response = requests.get(imageURL)
    hash_md5 = hashlib.md5()
    
    for chunk in response.iter_content(chunk_size=4096):
        hash_md5.update(chunk)
    
    payload = {
        'md5' : hash_md5.hexdigest(),
        'i' : AUTH_TOKEN
    }

    response = requests.post("https://" + URL + '/api/drive/files/find-by-hash', json=payload)
    print("SearchForImage: Processing response...")
    ProcessResponse(response.status_code, response.json())
    print(response.json())
    json_data = response.json()
    
    for item in json_data:
        if 'id' in item:
            imageId = item['id']
            break

    return imageId


def Runner(client): # Better name for this?
    user = client.get_user_by_screen_name(USER)

    ## Avatar
    # Process the image url to grab a higher res one
    hires_image_url = user.profile_image_url.replace("_normal", "_400x400")
    print(f"AVATAR URL: {hires_image_url}")
    UploadImage(hires_image_url)
    imageId = SearchForImage(hires_image_url)
    UpdateAvatar(imageId)
    
    time.sleep(30) # maybe schedule each individually?


    ## Banner
    print(f"BANNER URL: {user.profile_banner_url}")
    UploadImage(user.profile_banner_url)
    imageId = SearchForImage(user.profile_banner_url)
    UpdateBanner(imageId)


def main():
    print("Running!")
    client = Client('en-US')
    client.load_cookies('cookies.json')


    # run every 24hours
    schedule.every(24).hours.do(Runner(client))
    while True:
        schedule.run_pending()
        time.sleep(300) 

main()