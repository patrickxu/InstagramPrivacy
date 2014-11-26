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

# use Instagram API to get all the users tom_hammons follows
# RETURNS: list of ids we follow
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
		return "You don't have permissions to view media from user with id: " + user + "\n" + str(e)
		# pass

def is_location_nearby(element1, element2, threshold):
	""" checks if a location is near another location based on threshold """
	lat_difference = abs(element2[0] - element1[0])
	lng_difference = abs(element2[1] - element1[1])
	within_threshold = lat_difference < threshold and lng_difference < threshold
	if within_threshold:
		return True
	else:
		return False

"""I'm not sure that this function is necessary? I changed cluster()
so that it doesn't use this function """
def is_location_in_array(element, coordinates, threshold):
	unique = False
	for coordinate in coordinates:
		if is_location_nearby(element, coordinate, threshold):
			unique = True
	return unique

"""
	Parameters: Takes in a list of coordinates
	Function: calculates all points in list of coordinates that are within_threshold
				a certain threshold of the first coordinate
	Returns: A list of these coordinates that can be "clustered" with the first coordinate
"""
def cluster(list_of_coordinates):
	clustered_list = []
	clustered_list.append(list_of_coordinates[0])
	list_of_coordinates.remove(list_of_coordinates[0])
	count = 0
	while count < len(list_of_coordinates):
		pair = list_of_coordinates[count]
		average_location = average_location_list(clustered_list)
		# if is_location_in_array(pair, clustered_list[0], THRESHOLD):
		if is_location_nearby(pair, average_location, THRESHOLD):
			clustered_list.append(pair)
			del list_of_coordinates[count]
		else:
			count = count + 1
	return clustered_list

"""
	Parameters: Takes in a list of coordinates
	Function: calculates a list of lists, each being a cluster
	Returns: a list of lists, with each list being a cluster
"""
def create_clusters(list_of_coordinates):
	master = []
	while (not list_of_coordinates == []):
		master.append(cluster(list_of_coordinates))
	return master

"""
	Parameters: Takes in a list of coordinates
	Function: Calculates the average of these coordinates
	Returns: Average of the coordinates
"""
def average_location_list(locations):
	""" averages a list of location tuples """
	return tuple(map(lambda elt: sum(elt) / float(len(elt)), zip(*locations)))

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
	# key = "AIzaSyB7ZZTzG8-hhXKpCbuYbRinFb18mrMV55c"
	key = "AIzaSyAaJpkAmGeVO1qrmTb-qGrDCRAJxs8NjTk"
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
		print whole
		# city = [0]["long_name"]
		# city = str(city).strip()
		return whole
	except Exception as e:
		print "Can't get city from tuple..." + str(e)
		# pass

"""
	Parameters: list of lists, with each list being a cluster
	Function: Takes each "cluster", calculates city, state associate with cluster 
				and the number of pictures associated with the location
	Returns: dictionary with city, state keys, and number of occurrences for value
"""
def construct_city_mapping(list_of_clusters):
	city_map = {}
	for cluster in list_of_clusters:
		average_location = average_location_list(cluster)
		city_name = query_city(average_location)
		num_occurences = len(cluster)
		city_map[city_name] = num_occurences
	return city_map

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
			home = find_user_home(city_map)
			print user_tuple[1], home
			to_write = user_tuple[1] + '\t' + home + '\n'
			f.write(to_write)
			# coordinates = construct_location_data(user)
			# unique_locations = find_frequented_cities(coordinates)
			# home = find_user_home(unique_locations)
			# mapping[user] = home
		except Exception as e:
			print "Master error..." + str(e)
			# pass
	return mapping

"""
	Parameters: Takes in .txt file that has id, username, hometown tuples
	Function: Checks to see if user posted over Thanksgiving week, and if so, locations posted
	Returns: file of id, username, hometown, thanksgiving_location tuples
"""
def compare_TG(filename):
	f = open(filename, 'r')
	for line in f:
		split_line = line.split('\r')
		for l in split_line:
			lsplit = l.split('\t')
			if lsplit[0] != "username":
				username = lsplit[0]
				hometown = lsplit[1].strip('"')
				print username, hometown
		# print ''

if __name__ == "__main__":
	# check = [(42.375097093, -71.115406025), (42.375097093, -71.115406025), (42.37446105, -71.120158211), (42.374981758, -71.115754964), (42.375273924, -71.115778573), (42.375149103, -71.115834927), (37.619562741, -122.385499283), (42.375440123, -71.115521276), (42.375274299, -71.115690174)]
	# print len(create_clusters(check))
	# f = open('user_hometowns.txt', 'w')
	# f.write('username\thometown\n')
	# construct_id_home_mapping(['415272494'], f)
	# idlist = find_users_we_follow()
	# construct_id_home_mapping(idlist[:2], f)
	# f.close()
	compare_TG('user_hometowns.txt')





