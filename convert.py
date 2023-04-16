
"""
해당 파일은 유튜브 업로드를 위한 동영상 파일 이름을 변경해주는 스크립트입니다.
유튜브 업로드를 위해 이름을 변경하지 않는다면 해당 스크립트를 사용하실 필요는 없습니다.
"""


import json
import os

data = None
with open("origin.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for d in data:
    video_path = os.path.abspath("./clips/{}.mp4".format(d["url"].split("/")[-1]))
    thumbnail_path = os.path.abspath("./clips/{}".format(d["thumbnail_url"].split("/")[-1]))
    fmt = "{0} {1} {2}".format(d["created_at"], d["title"], d["creator_name"])
    new_video_path = os.path.abspath("./clips/{}.mp4".format(fmt))
    new_thumbnail_path = os.path.abspath("./clips/{}.jpg".format(fmt))
    os.rename(video_path, new_video_path)
    os.rename(thumbnail_path, new_thumbnail_path)
    d["url"] = fmt + ".mp4"
    d["thumbnail_url"] = fmt + ".jpg"

with open("origin.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)