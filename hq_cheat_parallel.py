from os import listdir
from os.path import isfile, join
import os, io
import requests
import base64
import json
import time
from bs4 import BeautifulSoup
import multiprocessing

mypath = "/Users/nathaniel/Desktop/"


pool = multiprocessing.Pool(processes=10) # how much parallelism?

def process_url(url):
    # Do what you want
    return BeautifulSoup(requests.get(url).text, "html.parser").text.lower()


while True:
	time.sleep(1)

	# get files on desktop
	onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

	pngs = [f for f in onlyfiles if "png" in f]

	if len(pngs) == 0:
		continue

	print pngs
	file_name = pngs[0]

	request = {}

	ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'

	# Loads the image into memory
	with io.open(file_name, 'rb') as image_file:
	    request = {
	             	'image': {'content': base64.b64encode(image_file.read()).decode()},
	             	'features': [{
	             	    'type': 'TEXT_DETECTION'
	             	}]}

	api_key = 'AIzaSyB6hqzlFDRj7HzyS7fP4VxdD8P_BLzn_RQ'

	response = requests.post(ENDPOINT_URL,
	                             data=json.dumps({"requests" : [request]}),
	                             params={'key': api_key},
	                             headers={'Content-Type': 'application/json'})


	json_resp = json.loads(response.text)

	print json_resp

	text = json_resp['responses'][0]['textAnnotations'][0]['description'].lower()

	print text

	question = text.split('?')[0]

	answer_part = text.split('?')[1]

	question = ''.join([q + " " for q in question.split('\n') if not q == ''])
	answer_part = [a for a in answer_part.split('\n') if not a  == ''][:3]

	cx = "012733416576061855056:akoiulnpmxg"

	query = question# + " " + answer_part[0] + " " + answer_part[1] + " " + answer_part[2]

	print "query: " + query

	google_search_url = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}".format(api_key, cx, question)

	google_custom_search_json = requests.get(google_search_url,
	                             headers={'Content-Type': 'application/json'})

	parsed_json_search = json.loads(google_custom_search_json.text)

	items = parsed_json_search['items']

	list_of_urls = [i['link'] for i in items]

	downloaded_links = pool.map(lambda url: BeautifulSoup(requests.get(url).text, "html.parser").text.lower(), list_of_urls)

	results = [0, 0, 0]

	for item, soup in zip(items, downloaded_links):
		snip = item['snippet'].lower()

		if answer_part[0] in snip or answer_part[0] in soup:
			results[0] = results[0] + 1

		if answer_part[1] in snip or answer_part[1] in soup:
			results[1] = results[1] + 1

		if answer_part[2] in snip or answer_part[2] in soup:
			results[2] = results[2] + 1


	if results[0] > results[1] and results[0] > results[2]:
		print "A"
		os.system("say a")
	elif results[1] > results[0] and results[1] > results[2]:
		print "B"
		os.system("say b")
	elif results[2] > results[0] and results[2] > results[1]:
		print "C"
		os.system("say c")
	else:
		print "INCONCLUSIVE"
		os.system("say INCONCLUSIVE")



	print results

	# remove png images
	for png in pngs:
		os.remove(png)