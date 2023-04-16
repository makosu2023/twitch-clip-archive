import os
import re
import json
from time import sleep
import requests

"""
1. twitch helix API get Auth token.
2. users login broadcast id get.
3. get clips list.
4. export json file.
"""


def step1(client_id, client_secret, user_login):
    # twitch helix API get Auth token.
    # https://dev.twitch.tv/docs/authentication/getting-tokens-oauth#oauth-client-credentials-flow
    url = "https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials".format(
        client_id, client_secret)
    headers = {"Content-Type": "application/json"}
    res = requests.post(url, headers=headers)
    res.raise_for_status()
    access_token = res.json()["access_token"]

    # users login broadcast id get. and download thumbnail image.
    # https://dev.twitch.tv/docs/api/reference#get-users
    url = "https://api.twitch.tv/helix/users?login={}".format(user_login)
    headers = {"Content-Type": "application/json", "Client-ID": client_id,
               "Authorization": "Bearer {}".format(access_token)}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    # get user_id, profile_iamge_url, and display_name.
    json_data = res.json()
    user_id = json_data["data"][0]["id"]
    user_profile_image_url = json_data["data"][0]["profile_image_url"].replace("{width}", "300").replace("{height}",
                                                                                                         "300")
    display_name = json_data["data"][0]["display_name"]
    res = requests.get(user_profile_image_url)
    res.raise_for_status()
    with open("profile.png", "wb") as f:
        f.write(res.content)

    # replace index.html link.
    index_html = open("index.html", "r", encoding="utf-8").read()
    index_html = index_html.replace("{{ TWITCH_USER_LOGIN }}", user_login).replace("{{ TWITCH_USER_ID }}",
                                                                                   user_id).replace(
        "{{ TWITCH_DISPLAY_NAME }}", display_name)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    # get clips list.
    # https://dev.twitch.tv/docs/api/reference#get-clips
    url = "https://api.twitch.tv/helix/clips?broadcaster_id={}&first=100".format(user_id)
    headers = {"Content-Type": "application/json", "Client-ID": client_id,
               "Authorization": "Bearer {}".format(access_token)}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    data = res.json()["data"]
    while "cursor" in res.json()["pagination"]:
        cursor = res.json()["pagination"]["cursor"]
        url = "https://api.twitch.tv/helix/clips?broadcaster_id={}&first=100&after={}".format(user_id, cursor)
        headers = {"Content-Type": "application/json", "Client-ID": client_id,
                   "Authorization": "Bearer {}".format(access_token)}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data.extend(res.json()["data"])

    # get game name. step by step 100.
    # https://dev.twitch.tv/docs/api/reference#get-games
    game_ids = []
    for d in data:
        game_ids.append(d["game_id"])
    game_ids = list(set(game_ids))
    game_ids = [game_ids[i:i + 100] for i in range(0, len(game_ids), 100)]
    game_names = {}
    for game_id in game_ids:
        url = "https://api.twitch.tv/helix/games?id={}".format("&id=".join(game_id))
        headers = {"Content-Type": "application/json", "Client-ID": client_id,
                   "Authorization": "Bearer {}".format(access_token)}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        for d in res.json()["data"]:
            game_names[d["id"]] = d["name"]
    # set game name.
    for d in data:
        if d["game_id"] == '':
            d["game_name"] = "None"
        else:
            d["game_name"] = game_names[d["game_id"]]
    # export json file.
    with open("origin.json".format(user_login), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


"""
download clips and thumbnail image.
"""


def step2():
    def parse_slug(url):
        if url.startswith(r"https://clips.twitch.tv/embed?clip="):
            return re.match(r"https://clips.twitch.tv/embed?clip=([a-zA-Z_\-]+)", url).group(1)
        url = url.split("?")[0]  # remove query string
        if re.match(r"https://www.twitch.tv/[a-zA-Z0-9_]+/clip/[a-zA-Z0-9_\-]+", url) \
                or re.match(r"https://clips.twitch.tv/[a-zA-Z0-9_\-]+", url):
            return url.split("/")[-1]

    def request_clips_detail_info(slug):
        resp = requests.post("https://gql.twitch.tv/gql", headers={
            "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"
        }, json=[
            {
                "operationName": "VideoAccessToken_Clip",
                "variables": {
                    "slug": slug
                },
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "36b89d2507fce29e5ca551df756d27c1cfe079e2609642b4390aa4c35796eb11"
                    }
                }
            }
        ])
        data = resp.json()
        # print(data)
        source_url = data[0]['data']['clip']['videoQualities'][0]['sourceURL']
        signature = data[0]['data']['clip']['playbackAccessToken']['signature']
        token = data[0]['data']['clip']['playbackAccessToken']['value']
        # print(source_url, signature, token)
        return signature, source_url, token

    def urlencode(text: str) -> str:
        return re.sub(r'[^a-zA-Z0-9_\-]', lambda m: '%%%02X' % ord(m.group(0)), text)

    def get_clip_download_url(url) -> str:
        slug = parse_slug(url)
        if slug is None:
            return None
        signature, source_url, token = request_clips_detail_info(slug)
        if signature is None or source_url is None or token is None:
            return None
        return source_url + "?sig=" + signature + "&token=" + urlencode(token)


    def download_file(url, local_filename):
        # NOTE the stream=True parameter below
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)
        return local_filename

    with open("origin.json", mode="r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        for data in json_data:
            video_path = os.path.abspath("./clips/{}.mp4".format(data["url"].split("/")[-1]))
            thumbnail_path = os.path.abspath("./clips/{}".format(data["thumbnail_url"].split("/")[-1]))
            if not os.path.isfile(video_path):
                # download twitch clips.
                print("downloaded: {} {}".format(data["title"], data["url"]))
                download_file(get_clip_download_url(data["url"]), video_path)
                download_file(data["thumbnail_url"], thumbnail_path)


if __name__ == "__main__":
    with open("secret.json", mode="r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
        client_id = json_data["TWITCH_CLIENT_ID"]
        client_secret = json_data["TWITCH_CLIENT_SECRET"]
        user_login = json_data["TWITCH_USER_LOGIN"]
        if not os.path.isfile("origin.json"):
            step1(client_id, client_secret, user_login)
        try:
            step2()
        except Exception as e:
            print(e)
            print("download error. please retry. X(...")
            sleep(10)
            exit(-1)
        print("success process...")
        print("now remove \"secret.json\" file.")
        print("good bye~! :D")
        sleep(30)
        exit(0)
