import sys
from instagram.client import InstagramAPI

access_token = open("token.txt").read()
api = InstagramAPI(access_token=access_token)

def construct_location_data(user):
	""" constructs every possible (lat, long) tuple for a given user """
	location_list = []
	recent_media, next_ = api.user_recent_media(user_id=user, count=sys.maxint)
	for index, media in enumerate(recent_media):
	   # print "Caption " + str(index) + ": ", media.caption.text
		try:
	   		latitude = media.location.point.latitude
	   		longitude = media.location.point.longitude
	   		location_list.append((latitude, longitude))
		except:
			pass
	return location_list

if __name__ == "__main__":
	print construct_location_data(40849075)