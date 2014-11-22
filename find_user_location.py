from __future__ import division
import sys
from instagram.client import InstagramAPI
from urllib2 import Request, urlopen, URLError
import json
from pprint import pprint


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

# def average_location_list(locations):
# 	""" averages a list of location tuples """
# 	return tuple(map(lambda elt: sum(elt) / float(len(elt)), zip(*locations)))

# def is_location_nearby(element, pivot, threshold):
# 	""" checks if a location is near another location based on threshold """
# 	lat_difference = abs(pivot[0] - element[0])
# 	lng_difference = abs(pivot[1] - element[1])
# 	within_threshold = lat_difference < threshold and lng_difference < threshold
# 	return True if within_threshold else False

# def sanitize_locations(locations):
# 	""" consolidates (lat, lng) tuples based on a threshold """
# 	master = []
# 	def filter_locations():
# 		nearby = []
# 		nearby.append(locations[0])
# 		for location in locations:
# 			if is_location_nearby(location, locations[0], THRESHOLD):
# 				nearby.append(location)
# 				locations.remove(location)
# 		master.append(average_location_list(nearby))
# 		if not locations == []:
# 			filter_locations()
# 	filter_locations()
# 	return master

def determine_city(clusters):
	cities = []
	for location in clusters:
		lat = str(location[0])
		lng = str(location[1])
		key = "AIzaSyCyjoz5Fhu26s6B6GK6k5ImZxMAkSdxL6E"
		request = Request("https://maps.googleapis.com/maps/api/geocode/json?latlng="
			+ lat
			+ ","
			+ lng
			+ "&key="
			+ key)
		try:
			response = urlopen(request)
			address_data = response.read()
			data = json.loads(address_data)
			city = data["results"][0]["formatted_address"].split(",")[-3]
			city = str(city).strip()
			""" TODO: super inefficient way of grouping cities because
				it hits google's endpoint far too many times """
			if not any(city in locations for locations in cities):
				cities.append((city, 1))
			else:
				tupleIndex = [index for index, location in enumerate(cities) if location[0] == city]
				city = list(cities[tupleIndex[0]])
				city[1] += 1
				updated_count = tuple(city)
				cities.remove(cities[tupleIndex[0]])
				cities.append(updated_count)
		except:
		    pass
	print cities

if __name__ == "__main__":
	locations = construct_location_data(23983519)
	# clusters = sanitize_locations(locations)
	determine_city(locations)