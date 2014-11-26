import datetime
from instagram.client import InstagramAPI
import csv
from find_user_location import find_users_we_follow, construct_location_data

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

def get_recent_media(idlist):
	for id_ in idlist:
		recent_media, next_ = IGapi.user_recent_media(user_id=id_, count=5)
		for media in recent_media:
			datetime = media.created_time
			year = int(datetime.strftime("%Y"))
			month = int(datetime.strftime("%m"))
			day = int(datetime.strftime("%d"))
			# these are the posts for which we can compare locations
			is_thanksgiving_post = year > 2013 and month > 10 and day > 23
			print is_thanksgiving_post
			


idlist = collect_csv_ids("hometowns.csv")
get_recent_media(idlist)
