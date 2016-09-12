import pymysql.cursors
import requests
from requests.exceptions import HTTPError

def initdb(CID):
	DC=getdb(CID)
	if (DC>4):
		host=(DC*2)+2
	else:
		host=(DC*2)-1
	#Fix to make sure we always get two digits hosts
	# IE dbp3 is actually dbp03
	if (host < 10) :
		hoststr='0'+str(host)
	else :
		hoststr=str(host)

	connection = pymysql.connect(host='dbp'+hoststr,
	                             user='TEST',
	                             passwd='TEST',
	                             db='TEST',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)

	return connection

def initdb_staging(CID):
	DC=getdb(CID)
	if (DC>4):
		host=(DC*2)+2
	else:
		host=DC*2
	print host
	#Fix to make sure we always get two digits hosts
	# IE dbp3 is actually dbp03
	if (host < 10) :
		hoststr='0'+str(host)
	else :
		hoststr=str(host)
	print hoststr
	connection = pymysql.connect(host='dbp'+hoststr,
	                             user='TEST',
	                             passwd='TEST',
	                             db='TEST',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection
	#print connection.messages
