from os import listdir
from os.path import isfile, join
import os, io
import requests
import base64
import json
import time
from bs4 import BeautifulSoup
import Queue
import threading
import constants

# path to desktop
mypath = "/Users/nathaniel/Desktop/"


# Code to Download web pages in parallel

# utility - spawn a thread to execute target for each args
def run_parallel_in_threads(target, args_list):
    result = Queue.Queue()
    # wrapper to collect return value in a Queue
    def task_wrapper(*args):
        result.put(target(*args))
    threads = [threading.Thread(target=task_wrapper, args=args) for args in args_list]
    for t in threads:
        t.start()
    for t in threads:
        t.join(1) # timemout of 1 second so it doesn't waste time downloading huge files like PDFs
    return result

def fetch(url):
	#print "fetching " + url
	return BeautifulSoup(requests.get(url).text, "html.parser")

def get_soups(urls):
	q = run_parallel_in_threads(fetch, urls)

	res = []

	while q.qsize() > 0:
		res.append(q.get())

	return res

while True:
	time.sleep(0.5)

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

	api_key = constants.api_key

	response = requests.post(ENDPOINT_URL,
	                             data=json.dumps({"requests" : [request]}),
	                             params={'key': api_key},
	                             headers={'Content-Type': 'application/json'})


	json_resp = json.loads(response.text)

	#print json_resp

	text = json_resp['responses'][0]['textAnnotations'][0]['description'].lower()

	#print text


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


	results = [0, 0, 0]

	for item in items:
		snip = item['snippet'].lower()

		if answer_part[0] in snip:
			results[0] = results[0] + 1

		if answer_part[1] in snip:
			results[1] = results[1] + 1

		if answer_part[2] in snip:
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
		print results
		
		os.system("say INCONCLUSIVE")
		
		soups = get_soups([(item['link'],) for item in items])

		for i in range(len(soups)):
			print "soup " + str(i)

			soup = soups[i]

			text = soup.text.lower()

			if answer_part[0] in text:
				results[0] = results[0] + 1

			if answer_part[1] in text:
				results[1] = results[1] + 1

			if answer_part[2] in text:
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