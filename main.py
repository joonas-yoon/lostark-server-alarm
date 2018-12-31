import requests
import json

from bs4 import BeautifulSoup as bs
from time import sleep
from random import randrange
from pushbullet import Pushbullet
from time import gmtime, strftime

with open('secret.json') as f:
    data = json.load(f)

ACCESS_TOKEN = data["access_token"]
PUSH = Pushbullet(ACCESS_TOKEN)

preState = {}

def get_html(url):
    _html = ""
    resp = requests.get(url)
    if resp.status_code == 200:
        _html = resp.text
    return _html


def send_push(serverName, changes):
    title = "[{}]".format(serverName) + " " + "/".join(changes)
    text = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    PUSH.push_note(title, text)
    print(serverName, changes)


while True:
    URL = "https://loaq.kr/wait"
    html = get_html(URL)
    soup = bs(html, 'html.parser')

    status = soup.find("div", {"class": "status"})
    servers = status.find_all("a")

    for server in servers:
        name = server.find("dt")
        waitCount = server.find("dd", {"class": "cnt"})
        makeAvailable = server.find("dd", {"class": "time"})

        if name is None or waitCount is None or makeAvailable is None:
            #print("Something wrong in processing:", server)
            continue

        name = name.getText().strip(' \n\t')
        waitCount = waitCount.getText().strip(' \n\t')
        makeAvailable = makeAvailable.getText().strip(' \n\t')

        if not name in preState:
            preState[name] = {}

        changes = []
        if preState[name].get('waitCount') != waitCount:
            changes.append(waitCount)
        if preState[name].get('makeAvailable') != makeAvailable:
            changes.append(makeAvailable)

        preState[name].update({'waitCount': waitCount})
        preState[name].update({'makeAvailable': makeAvailable})

        if len(changes) > 0:
            send_push(name, changes)

    delay = 10.0 + randrange(1, 10)
    sleep(delay)

