from __future__ import division
import sys
from instagram.client import InstagramAPI
from urllib2 import Request, urlopen, URLError
import json
from pprint import pprint
from operator import itemgetter

THRESHOLD = .3
CLIENT_ID = 1570583193

# authenticate with IG
access_token = open("token.txt").read()
IGapi = InstagramAPI(access_token=access_token)

# returns a list of ids
def find_users_we_follow():
	""" uses the IG API to scrape all id's that our fake account follows """
	ids = []
	followed_users = IGapi.user_follows(CLIENT_ID, as_generator=True)
	# IG returns 50 users at a time which we have to paginate through
	for page in followed_users:
		for user in page[0]:
			# strip the username and id and convert to ASCII
			username =  str(user).strip("User: ")
			userid = str(user.id)
			ids.append((userid, username))
	return ids

# returns a list of (lat, lng) tuples associated with a given id 
def construct_location_data(user):
	""" constructs every available (lat, lng) tuple for a given user """
	location_list = []
	try:
		# scrape all media (picture or video) from a given user
		recent_media, next_ = IGapi.user_recent_media(user_id=user, count=sys.maxint)
		for media in recent_media:
			# try to get location data from a piece of media, if available
			try:
		   		latitude = media.location.point.latitude
		   		longitude = media.location.point.longitude
	   			location_list.append((latitude, longitude))
			except Exception as e:
				pass
		# sometimes media JSON has empty lat, lng fields, so we need to check
		if location_list == []:
			return "No location data available for user with id: " + user
		else:
			return location_list
	except Exception as e:
		pass

# returns True if two location tuples are nearby, else False
def is_location_nearby(element1, element2, threshold):
	""" checks if two (lat, lng) tuples are close based on 
		a global THRESHOLD value """
	lat_difference = abs(element2[0] - element1[0])
	lng_difference = abs(element2[1] - element1[1])
	within_threshold = lat_difference < threshold and lng_difference < threshold
	return True if within_threshold else False

# returns the averaged location list
def average_location_list(locations):
	""" averages a list of (lat, lng) coordinates 
		for use in clustering """
	return tuple(map(lambda elt: sum(elt) / float(len(elt)), zip(*locations)))

# returns a list of lists of (lat, lng) tuples that are relatively close to each other
def cluster(list_of_coordinates):
	""" takes in a list of coordinates--(lat, lng) tuples--and sorts
		tuples into sublists based on global THRESHOLD value """
	clustered_list = []
	# append a coordinate to pivot around, and remove it from the list
	clustered_list.append(list_of_coordinates[0])
	list_of_coordinates.remove(list_of_coordinates[0])
	count = 0
	# while we still have coordinates to sort
	while count < len(list_of_coordinates):
		pair = list_of_coordinates[count]
		# to compare coordinates, average coordinate sublist to create estimate
		average_location = average_location_list(clustered_list)
		# if we have a match, add it to the sublist
		if is_location_nearby(pair, average_location, THRESHOLD):
			clustered_list.append(pair)
			del list_of_coordinates[count]
		else:
			count += 1
	return clustered_list

# returns a list of lists of clusters that are closeby
def create_clusters(list_of_coordinates):
	""" uses the cluster() method to calculate the two-dimensional
		cluster sublist """
	cluster_lists = []
	while (not list_of_coordinates == []):
		cluster_lists.append(cluster(list_of_coordinates))
	return cluster_lists

"""
	Parameters: Takes in a lat-long coordinate
	Function: Uses API to return city, state for lat-long coordinate
	Returns: City, state string
"""
def query_city(location):
	lat = str(location[0])
	lng = str(location[1])
	#NoahKey
	#key = "AIzaSyCyjoz5Fhu26s6B6GK6k5ImZxMAkSdxL6E"
	key = "AIzaSyB7ZZTzG8-hhXKpCbuYbRinFb18mrMV55c"
	#key = "AIzaSyAaJpkAmGeVO1qrmTb-qGrDCRAJxs8NjTk"
	request = Request("https://maps.googleapis.com/maps/api/geocode/json?latlng="
		+ lat
		+ ","
		+ lng
		# added locality for easier parsing
		+ "&result_type=locality"
		+ "&key="
		+ key)
	try:
		response = urlopen(request)
		address_data = response.read()
		data = json.loads(address_data)
		results = data["results"][0]["formatted_address"]
		components = data["results"][0]["address_components"]
		# pprint(components)
		city = components[0]["long_name"]
		if components[-1]["short_name"] == u'US':
			# state = ' '.join(results.split(",")[-2].strip().split(" ")[:-1])
			# city = results.split(",")[-3]
			state = components[2]["short_name"]
		else:
			# split_res = results.split(',')
			state = components[-1]["short_name"]
			if state.isnumeric():
				state = components[-2]["short_name"]
			# city = split_res[-2]
		whole = str(city).strip() + ', ' + state.strip()
		# print whole
		# city = [0]["long_name"]
		# city = str(city).strip()
		return whole
	except Exception as e:
		print "Can't get city from tuple..." + str(e)
		# pass

"""
	Parameters: list of lists, with each list being a cluster
	Function: Takes each "cluster", calculates (city, state) associated with cluster 
				and the number of pictures associated with the location
	Returns: dictionary with (city, state) keys, and number of occurrences for value
"""
def construct_city_mapping(list_of_clusters):
	city_map = {}
	max_city = max(list_of_clusters, key = len)
	max_city_occurences = len(max_city)
	max_city_average = average_location_list(max_city)
	city_name = query_city(max_city_average)
	if city_name in ["Cambridge, MA", "Mid-Cambridge, MA"]:
		list_of_clusters.remove(max_city)
		second_max_city = max(list_of_clusters, key = len)
		second_max_city_occurences = len(second_max_city)
		second_max_city_average = average_location_list(second_max_city)
		second_city_name = query_city(second_max_city_average)
		city_map[second_city_name] = second_max_city_occurences
	else:
		city_map[city_name] = max_city_occurences
	return city_map
	# for cluster in list_of_clusters:
	# 	average_location = average_location_list(cluster)
	# 	city_name = query_city(average_location)
	# 	num_occurences = len(cluster)
	# 	city_map[city_name] = num_occurences
	# return city_map

"""
	Parameters: Takes a dictionary that has location keys and number of occurrences values
	Function: Calculates the city with most occurrences that is not Cambridge, MA
	Returns: string of city with most occurrences that is not Cambridge, MA
"""
def find_user_home(city_map):
	max_city = max(city_map.iteritems(), key=itemgetter(1))[0]
	max_occurences = max(city_map.iteritems(), key=itemgetter(1))[1]
	if max_city in ["Cambridge, MA", "Mid-Cambridge, MA"]:
		del city_map[max_city]
		return max(city_map.iteritems(), key=itemgetter(1))[0]
	else:
		return max_city

"""
	Parameters: list of ids and a filename
	Function: Calculates the assumed hometown for each of these users, and writes all username-hometown tuples to a txt file
	Returns: Dictionary that has username as key, and hometown as value.
"""
def construct_id_home_mapping(idlist, f):
	mapping = {}
	for user_tuple in idlist:
		# print "Attemping to construct map for user ", user_tuple, "..."
		try:
			userid = user_tuple[0]
			locations = construct_location_data(userid)
			clusters = create_clusters(locations)
			city_map = construct_city_mapping(clusters)
			# home = find_user_home(city_map)
			print user_tuple[1], city_map.keys()[0]
			to_write = user_tuple[1] + '\t' + city_map.keys()[0] + '\n'
			f.write(to_write)
			# coordinates = construct_location_data(user)
			# unique_locations = find_frequented_cities(coordinates)
			# home = find_user_home(unique_locations)
			# mapping[user] = home
		except Exception as e:
			print "Master error..." + str(e)
			# pass
	return mapping

if __name__ == "__main__":
	# check = [(42.375097093, -71.115406025), (42.375097093, -71.115406025), (42.37446105, -71.120158211), (42.374981758, -71.115754964), (42.375273924, -71.115778573), (42.375149103, -71.115834927), (37.619562741, -122.385499283), (42.375440123, -71.115521276), (42.375274299, -71.115690174)]
	# print len(create_clusters(check))
	f = open('user_hometowns.txt', 'w')
	f.write('username\thometown\n')
	# construct_id_home_mapping(['415272494'], f)
	idlist = find_users_we_follow()
	construct_id_home_mapping(idlist[:5], f)
	f.close()

