from json import loads, dumps
import requests
import hashlib
import os
import time

from colorama import Fore

from threading import Thread

def sha1(input):
    return hashlib.sha1(input.encode('utf-8')).digest().hex()[0:6]

class Image:
    def __init__(self, json):
        self.id = json["picture_id"]
        self.url = json["_links"]["self"]["href"]

class Notice:
    def __init__(self, json):
        self.date_of_birth = json["date_of_birth"]
        self.entity_id = json["entity_id"]
        self.first_name = json["forename"]
        self.last_name = json["name"]

        self.nationalities = json["nationalities"]

        self.links = json["_links"]

        self.full_data_url = self.links["self"]["href"]
        self.images_link = self.links["images"]["href"]
        
        self.full_data = None

        try:
            self.thumbnail = self.links["thumbnail"]["href"]
        except:
            pass

    def fetch_fulldata(self):
        try:
            self.full_data = requests.get(self.full_data_url).json()
        except:
            pass
        return self.full_data

    def fetch_images(self):
        res = requests.get(self.images_link)
        images = []

        try:
            images_urls = res.json()["_embedded"]["images"]
            

            for url in images_urls:
                image = Image(url)

                res = requests.get(image.url, stream=True)

                images.append(res.content)
        except:
            pass

        self.images = images
        return images

def processData(data):
    notice = Notice(data)
    hash = sha1(dumps(notice.entity_id))
    path = f"\\data\\{hash}\\"

    print(f"{Fore.BLACK}[{Fore.GREEN}START{Fore.BLACK}] {Fore.BLUE}Starting fetching images for {hash}")
    
    notice.fetch_images()
    notice.fetch_fulldata()

    if not os.path.exists(os.getcwd()+path) and len(notice.images) > 0:
        os.mkdir(os.getcwd()+path)
    else:
        print(f"{Fore.BLACK}[{Fore.RED}ERROR{Fore.BLACK}] {Fore.RED}Skipped fetching images for {hash}")
        return

    path = path.replace("\\","/")[1:]

    with open(f"{path}data.json","w") as json:
        json.write(dumps(notice.full_data))
        
    for image in notice.images:
        with open(f"{path}{sha1(str(image))}.jpeg","wb") as img:
            img.write(image)
    print(f"{Fore.BLACK}[{Fore.GREEN}SUCESS{Fore.BLACK}] {Fore.GREEN}Finished fetching images for {hash}")

def process(json):
    threads = []

    for data in json["_embedded"]["notices"]:
        processData(data)
        continue
        th = Thread(target=processData,args=[data])
        th.start()

        threads.append(th)

    for thread in threads:
        thread.join()

threads = []

"""
for i in range(0,24):
    json = loads(open(f"age\\{i}.json").read())

    th = Thread(target=process,args=[json])
    th.start()

    threads.append(th)
"""

for i in range(1,31):
    json_list = loads(open(f"data/age/{i}.json").read())

    for json in json_list:
        th = Thread(target=process,args=[json])
        th.start()

        threads.append(th)
        time.sleep(5)

for thread in threads: 
    thread.join()