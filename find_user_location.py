from __future__ import division
import sys
from instagram.client import InstagramAPI
from urllib2 import Request, urlopen, URLError
import json
from pprint import pprint
from operator import itemgetter

THRESHOLD = .3
CLIENT_ID = 1570583193

access_token = open("token.txt").read()
api = InstagramAPI(access_token=access_token)

def find_users_we_follow():
	ids = []
	followed_users = api.user_follows(CLIENT_ID, as_generator=True)
	for index, page in enumerate(followed_users):
		for counter, user in enumerate(page[0]):
			username =  str(user).strip("User: ")
			ids.append((user.id.encode('utf8'), username))
	return ids

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
			except Exception as e:
				# print "Can't get lat or lng..." + str(e)
				pass
		if location_list == []:
			return "No location data available for user with id: " + user
		else:
			return location_list
	except Exception as e:
		# return "You don't have permissions to view media from user with id: " + user + "\n" + str(e)
		pass

def is_location_nearby(element1, element2, threshold):
	""" checks if a location is near another location based on threshold """
	lat_difference = abs(element2[0] - element1[0])
	lng_difference = abs(element2[1] - element1[1])
	within_threshold = lat_difference < threshold and lng_difference < threshold
	return True if within_threshold else False

def is_location_in_array(element, coordinates, threshold):
	unique = False
	for coordinate in coordinates:
		if is_location_nearby(element, coordinate, threshold):
			unique = True
	return unique

def cluster(list_of_coordinates):
	clustered_list = []
	clustered_list.insert(0,[list_of_coordinates[0]])
	list_of_coordinates.remove(list_of_coordinates[0])
	for pair in list_of_coordinates:
		if is_location_in_array(pair, clustered_list[0], THRESHOLD):
			clustered_list[0].append(pair)
			list_of_coordinates.remove(pair)
	return clustered_list

def create_clusters(list_of_coordinates):
	master = []
	while (not list_of_coordinates == []):
		master.append(cluster(list_of_coordinates)[0])
	return master

def average_location_list(locations):
	""" averages a list of location tuples """
	return tuple(map(lambda elt: sum(elt) / float(len(elt)), zip(*locations)))

def query_city(location):
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
		return city
	except Exception as e:
		# print "Can't get city from tuple..." + str(e)
		pass

def construct_city_mapping(list_of_clusters):
	city_map = {}
	for cluster in list_of_clusters:
		average_location = average_location_list(cluster)
		city_name = query_city(average_location)
		num_occurences = len(cluster)
		city_map[city_name] = num_occurences
	return city_map

def find_user_home(city_map):
	max_city = max(city_map.iteritems(), key=itemgetter(1))[0]
	max_occurences = max(city_map.iteritems(), key=itemgetter(1))[1]
	if max_city in ["Cambridge", "Mid-Cambridge"]:
		del city_map[max_city]
		return max(city_map.iteritems(), key=itemgetter(1))[0]
	else:
		return max_city

def construct_id_home_mapping(idlist):
	mapping = {}
	for user_tuple in idlist:
		print "Attemping to construct map for user ", user_tuple, "..."
		try:
			userid = user_tuple[0]
			locations = construct_location_data(userid)
			clusters = create_clusters(locations)
			city_map = construct_city_mapping(clusters)
			home = find_user_home(city_map)
			print user_tuple[1], home
			# coordinates = construct_location_data(user)
			# unique_locations = find_frequented_cities(coordinates)
			# home = find_user_home(unique_locations)
			# mapping[user] = home
		except Exception as e:
			# print "Master error..." + str(e)
			pass
	return mapping

if __name__ == "__main__":
	idlist = find_users_we_follow()
	construct_id_home_mapping(idlist)