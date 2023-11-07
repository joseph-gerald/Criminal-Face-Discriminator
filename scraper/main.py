import requests
from json import dumps
from time import sleep

def fetchJsonByAge(min: int, max: int):
    URL = f"https://ws-public.interpol.int/notices/v1/red?=&ageMin={min}&ageMax={max}" # &resultPerPage=160
    
    print("#"*50)
    print(f"> scraping ages {min}-{max} | {URL}")
    print("#"*50)

    res = requests.get(URL)
    json = [res.json()];
    print(int(json[0]["total"]))
    if(int(json[0]["total"]) > 160):
        for char in "abcdefghijklmnopqrstuvwxyz":
            attempts = 0
            while True:
                attempts += 1
                try:
                    TEMP_URL = f"{URL}&name={char}"
                    print(f"scraping {char} | {TEMP_URL}")
                    res = requests.get(TEMP_URL, timeout=3)
                    json.append(res.json())
                    break
                except:
                    print(f"failed on {char}")
                    sleep(1)
                    if attempts >= 3:
                        print(f"gave up on {char}")
                        break;
                    else:
                        print(f"retrying on {char}")
                        continue
    return json

for i in range(33,120):
    sleep(1)
    json = fetchJsonByAge(i,i+1)

    with open(f"age\{i}.json", "w") as txt:
        txt.write(dumps(json))