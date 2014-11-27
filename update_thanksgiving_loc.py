import datetime
from instagram.client import InstagramAPI
import csv
from find_user_location import query_city, average_location_list

# authenticate with IG
access_token = open("token.txt").read()
IGapi = InstagramAPI(access_token=access_token)

# returns a list of the user ids that we have loc data for
def collect_csv_ids(file_):
	""" reads through the csv and collects the id column """
	ids = []
	csvfile = open(file_)
	# read each row into a dict
	reader = csv.DictReader(csvfile)
	for row in reader:
		ids.append(row["userid"])
	return ids

# returns a list of media posted during thanksgiving vacation
def get_recent_media(id_):
	""" loops through recent media and checks against a start date """
	location_list = []
	recent_media, next_ = IGapi.user_recent_media(user_id=id_, count=5)
	for media in recent_media:
		datetime = media.created_time
		# strip the relevant date information
		year = int(datetime.strftime("%Y"))
		month = int(datetime.strftime("%m"))
		day = int(datetime.strftime("%d"))
		# these are the posts for which we can compare locations
		is_thanksgiving_post = year > 2013 and month > 10 and day > 23
		if is_thanksgiving_post:
			try:
		   		latitude = media.location.point.latitude
		   		longitude = media.location.point.longitude
	   			location_list.append((latitude, longitude))
			except Exception as e:
				pass
	return (id_, average_location_list(location_list))

# returns a santized mapping from user to thanksgiving location
def sanitize_recent_media(file_):
	""" removes empty location data (e.g. [] or ()) """
	master = []
	for id_ in collect_csv_ids(file_):
		if get_recent_media(id_)[1]:
			master.append(get_recent_media(id_))
	return master

# returns a mapping from userid to thanksgiving location
def find_thanksgiving_address(mapping):
	""" changes (lat, lng) associated with user to readable address """
	city_mapping = {}
	for tuple_ in mapping:
		list_ = list(tuple_)
		list_[1] = query_city(list_[1])
		new_tuple = tuple(list_)
		id_ = new_tuple[0]
		address = str(new_tuple[1])
		city_mapping[id_] = address
	return city_mapping

def write_updated_location(city_mapping, file):
	""" writes the thanksgiving location to a new column in the csv """
	# code code code

if __name__ == "__main__":
	mapping = sanitize_recent_media("hometowns_to_test.csv")
	print find_thanksgiving_address(mapping)
