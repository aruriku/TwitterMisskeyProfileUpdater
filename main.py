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

# ... is this bad practice? It's not like it's going to change.
client = Client('en-US')
client.load_cookies('cookies.json')


def UpdateRequest(payload):
    headers = {'Authorization': 'bearer ' + AUTH_TOKEN}
    response = requests.post("https://" + URL + '/api/i/update', json=payload, headers=headers)
    print("UpdateRequest: Processing response...")
    ProcessResponse(response)

def ProcessResponse(response):
    if response.status_code == 200 or response.status_code == 204:
        print("success!")
    else:
        print("failed!")
        response.raise_for_status()

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
    ProcessResponse(response)
    # return response code?

def SearchForImage(imageURL):
    response = requests.get(imageURL)
    ProcessResponse(response)

    hash_md5 = hashlib.md5()
    for chunk in response.iter_content(chunk_size=4096):
        hash_md5.update(chunk)
    
    payload = {
        'md5' : hash_md5.hexdigest(),
        'i' : AUTH_TOKEN
    }

    response = requests.post("https://" + URL + '/api/drive/files/find-by-hash', json=payload)
    print("SearchForImage: Processing response...")
    ProcessResponse(response)
    print(response.json())
    json_data = response.json()
    
    for item in json_data:
        if 'id' in item:
            imageId = item['id']
            break

    return imageId


def Runner(): # Better name for this?
    user = client.get_user_by_screen_name(USER)

    ## Avatar
    # Process the image url to grab a higher res one
    try:
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
    except requests.exceptions.HTTPError as http_err:
        print(f"A HTTP error has occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"A request error has occured: {req_err}")
    except Exception as err:
        print(f"An error has occurred. {err}")
    finally:
        #TODO: maybe make it so It'll run it sooner if it fails?
        print("Trying again in 24 hours...")


def main():
    print("Running!")

    # run on start
    Runner()

    # Then, run every 24hours
    schedule.every(24).hours.do(Runner)
    while True:
        schedule.run_pending()
        time.sleep(300) 

main()