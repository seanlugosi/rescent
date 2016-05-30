import petl as etl
import string,random

ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))


def translate(cell):
	# Get rid of the useless stuff and output (partially) RTM ready values
	# Goal ID 5 becomes goal5
    if cell=='E-Commerce':
        return 'transaction'
    else :
        return str.lower(cell[:4]+cell[8:])


def prep_file(csvfile):
	#Generate list of column we keep (View ID + All the Goals-Ecommerce)
	#Output :
	"""
	+---------+-------------+--------------------------+
	| View ID | variable    | value                    |
	+=========+=============+==========================+
	| 2405654 | transaction | Conversion + Revenue     |
	+---------+-------------+--------------------------+
	| 2405654 | goal1       | Not Used / Do not Import |
	+---------+-------------+--------------------------+
	| 2405654 | goal2       | Conversion               |
	+---------+-------------+--------------------------+
	| 2405654 | goal3       | Not Used / Do not Import |
	+---------+-------------+--------------------------+
	| 2405654 | goal4       | Not Used / Do not Import |
	+---------+-------------+--------------------------+
	"""

	cuts=[2,]+[i for i in range(4,25)]

	# Load file, keep the right columns,melt (aka switch columns to rows), 
	# convert them as string, rename the Goals into a CSMapping ready and convert the View to an int
	return etl.fromcsv(csvfile).cut(cuts).melt('View ID').convertall(str).convert('variable', lambda x : translate(x[18:-1])).convert('View ID',int)

def filter_agg(etlt):
	# Expects a prepped file
	# Filter out the goals not used then aggregate them by type (aka conv or conv+rev)
	# Output :
	""""
	+------------+----------------------+-----------------+
	| profileID  | type                 | goals           |
	+============+======================+=================+
	|    2405654 | Conversion           | ['goal2']       |
	+------------+----------------------+-----------------+
	|    2405654 | Conversion + Revenue | ['transaction'] |
	+------------+----------------------+-----------------+
	|   84468465 | Conversion           | ['goal2']       |
	+------------+----------------------+-----------------+
	|   84468465 | Conversion + Revenue | ['transaction'] |
	+------------+----------------------+-----------------+
	| 7885855456 | Conversion + Revenue | ['transaction'] |
	+------------+----------------------+-----------------+

	"""
	return etlt.select('value',lambda x : x=='Conversion' or x=='Conversion + Revenue').aggregate(('View ID','value'),list,'variable').setheader(['profileID','type','goals'])


def meta_table(etlt):
	# Expects an aggregated file
	# Returns a table of profileIDs grouped by their conversion mapping
	# Output :
	"""
	+---------------------+
	| value               |
	+=====================+
	| [2405654, 84468465] | > Those 2 profileIDs share the same structure 
	+---------------------+
	| [7885855456]        | > This one has a different one
	+---------------------+
	"""
	return etlt.aggregate('profileID',list,('type','goals')).aggregate('value',list,'profileID').cut(1)

def get_goals(profileIDs,etlt):
	mylist=list(etlt.selectin('profileID',profileIDs).cut(1,2).dicts())
	return {x['type']:x['goals'] for x in mylist}