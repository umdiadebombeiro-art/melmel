import os, time, random, requests
from datetime import datetime, timezone, timedelta

IG_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
IG_ID = os.getenv("INSTAGRAM_USER_ID")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT = os.getenv("TELEGRAM_CHAT_ID")

def req(method, url, **kw):
    for i in range(5):
        try:
            r = method(url, timeout=30, **kw)
        except:
            r = None
        if r and r.status_code not in (429, 500, 502, 503, 504):
            return r
        time.sleep(1.5 * (2 ** i) + random.uniform(0, 1))
    return r

def get_media():
    url = f"https://graph.facebook.com/v19.0/{IG_ID}/media"
    params = {"fields":"id,caption,media_type,media_url,permalink,timestamp","access_token":IG_TOKEN,"limit":5}
    r = req(requests.get, url, params=params)
    return r.json().get("data", []) if r and r.ok else []

def send_photo(photo, cap):
    req(requests.post, f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
        data={"chat_id": TG_CHAT, "photo": photo, "caption": cap[:1024]})

def send_msg(txt):
    req(requests.post, f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        data={"chat_id": TG_CHAT, "text": txt})

limite = datetime.now(timezone.utc) - timedelta(minutes=10)
for m in get_media():
    ts = datetime.fromisoformat(m["timestamp"].replace("Z","+00:00"))
    if ts < limite: continue
    legenda = f"{m.get('caption','')}\n\n{m['permalink']}"
    if m["media_type"] in ("IMAGE","CAROUSEL_ALBUM"):
        send_photo(m["media_url"], legenda)
    else:
        send_msg(legenda)
