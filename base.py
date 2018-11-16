#! python3
# base.py - go to envt canada site, compare today's temp to today's avg historical temp

import requests, bs4, tweepy, os, time

def check_temps():
	# returns true if today's forecast beats today's average high, as per weather.gc.ca's website, in Toronto
	soup = bs4.BeautifulSoup(requests.get('https://weather.gc.ca/city/pages/on-143_metric_e.html').text, "html.parser")
	today = int(soup.select('span.high.wxo-metric-hide')[0].contents[0][:-2])
	average = int(soup.select('td > span.wxo-metric-hide')[0].contents[0][:-2])
	print("Today's forecast (C):")
	print(today)

	print("Today's average high (C):")
	print(average)
	
	print("Is today's temp above the daily historic average?")
	print(today > average)


def tweet():
	
	consumer_key = os.environ['consumer_key']
	consumer_secret = os.environ['consumer_secret']
	access_token = os.environ['access_token']
	access_token_secret = os.environ['access_token_secret']

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	user = api.me()
	api.update_status('Testing Testing ' + str(time.time()) )


check_temps()
tweet()