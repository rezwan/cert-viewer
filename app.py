import json
import os
import urllib
from flask import Flask, render_template, request
from pymongo import MongoClient

import config
import helpers
import secrets
from verify import verify_doc

app = Flask(__name__)
client = MongoClient(host=secrets.MONGO_URI)
# app.config["MONGO_URI"]=secrets.MONGO_URI
# app.config["MONGO_DBNAME"]=secrets.MONGO_DBNAME
# mongo = PyMongo(app)

@app.route('/')
def home_page():
	client.admin.coins.ensure_index([
			('user.name.familyName', 'text'),
			('user.name.givenName', 'text'),
	  	],
	  	name="search_index",
	  	weights={
	      	'user.name.familyName':100,
	      	'user.name.givenName':100
	  	}
		)
	print list(client.admin.coins.find({'$text': {'$search': 'juliana'}}, fields={'user.name.givenName':100}))
	recents = helpers.get_recently_issued()
	return render_template('index.html', recents=recents)

@app.route('/keys/<key_name>')
def key_page(key_name=None):
	if key_name in os.listdir(config.KEYS_PATH):
		content = helpers.read_file(config.KEYS_PATH+key_name)
		return content
	else:
		return 'Sorry, this page does not exist.'

@app.route('/<identifier>')
def award_by_hash(identifier=None):
	award = None
	if identifier+'.json' in os.listdir(config.JSONS_PATH):
		id = identifier
	else:
		hashmap_content = helpers.read_json(config.HASHMAP_PATH)
		id = hashmap_content.get(identifier, None)
	if id:
		award, verification_info = helpers.get_id_info(id)
	if award:
		return render_template('award.html', award=award, verification_info=urllib.urlencode(verification_info))
	return "Sorry, this page does not exist."

@app.route('/verify')
def verify():
	uid = request.args.get('uid')
	transactionID = request.args.get('transactionID')
	signed_cert_path = config.JSONS_PATH+uid+".json"
	verified = verify_doc(transactionID, signed_cert_path, config.CERT_MARKER)
	return str(verified)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
