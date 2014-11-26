import datetime
from instagram.client import InstagramAPI
import csv
from find_user_location import find_users_we_follow, construct_location_data

# print(
#     datetime.datetime.fromtimestamp(
#         int("1284101485")
#     ).strftime('%Y-%m-%d %H:%M:%S')
# )

# authenticate with IG
access_token = open("token.txt").read()
IGapi = InstagramAPI(access_token=access_token)

def collect_csv_ids(file_):
	ids = []
	csvfile = open(file_)
	reader = csv.DictReader(csvfile)
	for row in reader:
		ids.append(row["userid"])
	return ids
