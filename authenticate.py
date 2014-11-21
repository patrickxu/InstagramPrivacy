from instagram.client import InstagramAPI

access_token = ""
api = InstagramAPI(access_token=access_token)
recent_media, next_ = api.user_recent_media(user_id=1, count=10)
for media in recent_media:
   print media.caption.text