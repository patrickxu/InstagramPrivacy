from __future__ import division
import sys
from instagram.client import InstagramAPI

THRESHOLD = 4

access_token = "39712567.f589aa9.6f2db3e548e141ebac0e795574922ef6"
api = InstagramAPI(access_token=access_token)

def construct_location_data(user):
	""" constructs every possible (lat, long) tuple for a given user """
	location_list = []
	try:
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
	except:
		return "You don't have permission to follow user with id: " + str(user)

def sanitize_locations(locations):
	""" consolidates (lat, lng) tuples based on a threshold """
	def average_location_list(locations):
		""" averages a list of location tuples """
		return tuple(map(lambda elt: sum(elt) / float(len(elt)), zip(*locations)))
	def is_location_nearby(element, pivot, threshold):
		""" checks if a location is near another location based on threshold """
		lat_difference = abs(pivot[0] - element[0])
		lng_difference = abs(pivot[1] - element[1])
		within_threshold = lat_difference < threshold and lng_difference < threshold
		return True if within_threshold else False
	master = []
	def filter_locations():
		nearby = []
		nearby.append(locations[0])
		for location in locations:
			if is_location_nearby(location, locations[0], THRESHOLD):
				nearby.append(location)
				locations.remove(location)
		master.append(average_location_list(nearby))
		if not locations == []:
			filter_locations()
	filter_locations()
	return master

if __name__ == "__main__":
	locations = construct_location_data(39712567)
	print sanitize_locations(locations)