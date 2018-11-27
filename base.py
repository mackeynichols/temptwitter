#! python3
# base.py - go to envt canada site, compare yest's temp to yest's avg historical temp

###
# https://www.twilio.com/blog/build-deploy-twitter-bots-python-tweepy-pythonanywhere
###

import requests, bs4, os, datetime, tweepy

def check_temps():
	# returns true if yest's forecast beats yest's average high, as per weather.gc.ca's website, in Toronto
	yest_date = datetime.datetime.now() - datetime.timedelta(1)

	yest_day = yest_date.day
	yest_month = yest_date.month
	yest_year = yest_date.year
	yest_url = "http://climate.weather.gc.ca/climate_data/daily_data_e.html?Year="+str(yest_year)+"&Month="+str(yest_month)+"&Day="+str(yest_day)+"&StationID=51058&Prov=NT&urlExtension=_e.html"
	historic_url = "http://climate.weather.gc.ca/climate_normals/results_1981_2010_e.html?stnID=1706&autofwd=1"
	print(yest_url)

	yest_date_str = yest_date.strftime('%B %d, %Y')
	print(yest_date_str)

	yest_soup = bs4.BeautifulSoup(requests.get(yest_url).text, "html.parser")
	yest_temp = yest_soup.select('div#dynamicDataTable > table > tbody > tr')[yest_day].select('td')[1].text
	print("Yesterday's High:\n"+yest_temp)

	historic_soup = bs4.BeautifulSoup(requests.get(historic_url).text, "html.parser")
	historic_temp = historic_soup.select('div.table-responsive > table > tbody > tr')[2].select('td')[yest_month-1].text
	print("Yesterday's Historic Monthly high:\n" + historic_temp)

	
	print("Is yesterday's temp above the daily historic average?")
	print(float(yest_temp) > float(historic_temp))

	if float(yest_temp) > float(historic_temp):
		return "Yesterday in Yellowknife, the temperature was "+str(abs(float(yest_temp)-float(historic_temp)))+" degrees warmer than the daily maximum climate normal."

	else: 
		return ''


def tweet():
	if check_temps() != '':

		consumer_key = os.environ['consumer_key']
		consumer_secret = os.environ['consumer_secret']
		access_token = os.environ['access_token']
		access_token_secret = os.environ['access_token_secret']

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		api = tweepy.API(auth)

		user = api.me()
		api.update_status(check_temps()) 

	else: 
		print('Today not warmer than historic avg')


tweet()