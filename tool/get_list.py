import requests
from bs4 import BeautifulSoup
import json
import re
import os

# URL of the webpage to fetch
host = "https://www.ly.gov.tw"
url = "/Pages/List.aspx?nodeid=109"

# Create directory 'img' if it does not exist
img_dir = "./img"
if not os.path.exists(img_dir):
    os.makedirs(img_dir)

def get_county_value(location):
    if "臺北市" in location:
        return "taipei"
    if "新北市" in location:
        return "new-taipei"
    if "桃園市" in location:
        return "taoyuan"
    if "臺中市" in location:
        return "taichung"
    if "臺南市" in location:
        return "tainan"
    if "高雄市" in location:
        return "kaohsiung"
    if "新竹縣" in location:
        return "hsinchu-county"
    if "苗栗縣" in location:
        return "miaoli"
    if "彰化縣" in location:
        return "changhua"
    if "南投縣" in location:
        return "nantou"
    if "雲林縣" in location:
        return "yunlin"
    if "嘉義縣" in location:
        return "chiayi-county"
    if "屏東縣" in location:
        return "pingtung"
    if "宜蘭縣" in location:
        return "yilan"
    if "花蓮縣" in location:
        return "hualien"
    if "臺東縣" in location:
        return "taitung"
    if "澎湖縣" in location:
        return "penghu"
    if "基隆市" in location:
        return "keelung"
    if "新竹市" in location:
        return "hsinchu-city"
    if "嘉義市" in location:
        return "chiayi-city"
    if "金門縣" in location:
        return "kinmen"
    if "連江縣" in location:
        return "lienchiang"
    return None

def get_legislator_location(link):
    r = requests.get(
        f"{host}{link}",
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
        },
    )
    body = r.content.decode("utf-8")

    match = re.search(r"<li>選區：(.*)<\/li>", body)
    location = match.group(1).strip() if match else None
    return location

def get_legislator_img(img, name):
    img_data = requests.get(f"{host}{img}").content
    img_filename = os.path.join(img_dir, f"{name}.jpg")
    with open(img_filename, "wb") as img_file:
        img_file.write(img_data)


def get_legislator(legislator):
    name = legislator.find("div", {"class": "legislatorname"}).text
    party = (
        legislator.find("img", {"class": "six-party-icon"})
        .attrs["alt"]
        .replace("徽章", "")
    )
    img = legislator.find("img", {"class": "img-thumbnail"}).attrs["src"]
    link = legislator.find("a").attrs["href"]

    print(f"Scraping {name}...")
    location = get_legislator_location(link)

    img_filename = os.path.join(img_dir, f"{name}.jpg")
    if not os.path.exists(img_filename):
        get_legislator_img(img, name)

    return {
        "name": name,
        "party": party,
        "img": img,
        "link": link,
        "location": location,
        "county": get_county_value(location),
    }

# Send a GET request to the webpage
response = requests.get(
    f"{host}{url}",
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    },
)

legislators = []
# Check if the request was successful
if response.status_code == 200:
    # Parse the content of the webpage
    soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")

    legislator_doms = soup.find_all("div", {"class": "six-legislatorAvatar"})
    for legislator_dom in legislator_doms:
        legislator = get_legislator(legislator_dom)
        legislators.append(legislator)
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    # Save legislators into a JSON file

with open("./legislators.json", "w", encoding="utf-8") as f:
    json.dump(legislators, f, ensure_ascii=False, indent=4)
