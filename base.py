#! python3
# base.py - go to envt canada site, compare yest's temp to yest's avg historical temp

###
# https://www.twilio.com/blog/build-deploy-twitter-bots-python-tweepy-pythonanywhere
###

import requests, bs4, os, datetime, tweepy, csv, pandas

yest_date = datetime.datetime.now() - datetime.timedelta(1)

yest_day = yest_date.strftime('%d')
yest_month = yest_date.strftime('%m')
yest_year = yest_date.strftime('%Y')

def check_temps():
	# returns true if yest's forecast beats yest's average high, as per weather.gc.ca's website, in Yellowknife
	
	yest_url = "http://climate.weather.gc.ca/climate_data/daily_data_e.html?Year="+yest_year+"&Month="+yest_month+"&Day="+yest_day+"&StationID=51058&Prov=NT&urlExtension=_e.html"
	historic_url = "http://climate.weather.gc.ca/climate_normals/results_1981_2010_e.html?stnID=1706&autofwd=1"
	print(yest_url)

	yest_date_str = yest_date.strftime('%B %d, %Y')
	print(yest_date_str)

	yest_soup = bs4.BeautifulSoup(requests.get(yest_url).text, "html.parser")
	yest_temp = yest_soup.select('div#dynamicDataTable > table > tbody > tr')[ int(yest_day) ].select('td')[1].text
	print("Yesterday's High:\n"+yest_temp)

	historic_temp = calculateNormals(yest_month, yest_day)
	
	print("Is yesterday's temp above the daily historic average?")
	print(float(yest_temp) > float(historic_temp))

	if float(yest_temp) > float(historic_temp):
		return "Yesterday in Yellowknife, the temperature was "+str(abs(float(yest_temp)-float(historic_temp)))+" degrees warmer than the historic average.\n\n#ClimateChangeRightNow #ClimateAction"

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


def calculateNormals(month, day, stnID = '1706'):

	avg_temps = pandas.DataFrame()

	for intYr in range(1970,1971+1):
	        
        # Build the query
		strQry = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=' + stnID + "&Year=" + str(intYr) +'&Month=' + str(month) + "&timeframe=1&submit=Download+Data" 

		#ßprint('Querying station ' + stnID + ' for year ' + str(intYr) + ' and month ' + str(month) )
         
        # Parse the response       
		response = requests.get(strQry)
		month_data = list( csv.reader(response.content.decode('utf-8').splitlines(), delimiter=",") )[15:]

		df = pandas.DataFrame(month_data)
		df = df.rename(columns=df.iloc[0]).drop(df.index[0])
		df['Temp (°C)'] = pandas.to_numeric(df['Temp (°C)'])
		
		# Keep only input day data and add it to the previous years' data
		df = df[( df.Day == day )]
		avg_temps = pandas.concat([avg_temps, df])

	avg_temp = avg_temps['Temp (°C)'].mean() 
	print( month+'-'+day+"'s average temp back in the day was:\n"+str(avg_temp) )
	return(avg_temp)

check_temps()
#tweet()
#calculateNormals('01', '01')