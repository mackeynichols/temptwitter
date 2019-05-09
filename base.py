#! python3
# base.py - Tweets temperature deviation from the average for a list of Canadian weather stations



import requests, bs4, os, datetime, tweepy, csv, pandas, json

class Twitterbot:

	def __init__(self, array_of_station_ids, keyfile):
		# Initialize stations, twitter keys, and dates

		# WORKING: detect station ID based on input name
		self.stations = array_of_station_ids
		self.keys = json.load(open(keyfile))

		self.yest_date = datetime.datetime.now() - datetime.timedelta(1)
		self.yest_day = self.yest_date.strftime('%d')
		self.yest_month = self.yest_date.strftime('%m')
		self.yest_year = self.yest_date.strftime('%Y')


	def tweet(self):
		# Sends a tweet with notable temperature deviations from the average from listed station, if any

		message = build_tweet( check_temps( self.stations ))
		if message != '':

			auth = tweepy.OAuthHandler(self.keys['consumer_key'], self.keys['consumer_secret'])
			auth.set_access_token(self.keys['access_token'], self.keys['access_token_secret'])
			api = tweepy.API(auth)

			user = api.me()
			api.update_status(status=message) 

		else: 
			print('Today not different than historic avg')


	def build_tweet(self, deviations):
		pass



	def check_temps(self):
		# returns true if yest's forecast beats yest's average high, as per weather.gc.ca's website, in Yellowknife
		# WORKING: replace "Yellowknife" above with all stations in input

		deviations = {}

		for station in self.stations:

			print(station)
			station_hist = station #WORKING

			# BUILD URLS
			yest_url = "http://climate.weather.gc.ca/climate_data/daily_data_e.html?Year="+self.yest_year+"&Month="+self.yest_month+"&Day="+self.yest_day+"&StationID="+station+"&Prov=NT&urlExtension=_e.html"
			historic_url = "http://climate.weather.gc.ca/climate_normals/results_1981_2010_e.html?stnID="+station_hist+"&autofwd=1"

			# GET YESTERDAY'S TEMP
			yest_soup = bs4.BeautifulSoup(requests.get(yest_url).text, "html.parser")
			yest_temp = yest_soup.select('div#dynamicDataTable > table > tbody > tr')[ int(self.yest_day) ].select('td')[3].text

			# GET HISTORIC AVG TEMP
			historic_temp = self.calculateNormals(self.yest_month, self.yest_day, station)
			

			# IF NO DEVIATION, SKIP TO NEXT INPUT STATION
			try:
				if not (float(yest_temp) - float(historic_temp) > 1 or float(yest_temp) - float(historic_temp) < -1):
					continue

				# IF DEVIATION, LOG ITS DETAILS
				else:

					deviations[station] = {}
					deviations[station]['above'] = float(yest_temp) - float(historic_temp) > 1
					deviations[station]['difference'] = str(round(abs(float(yest_temp)-float(historic_temp))))

			except:
				pass
				

		print(deviations)
		return deviations


		


	def calculateNormals(self, month, day, stnID):

		avg_temps = pandas.DataFrame()

		for intYr in range(1971,2000+1):
		        
	        # BUILD QUERY
			strQry = 'http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=' + stnID + "&Year=" + str(intYr) +'&Month=' + str(month) + "&timeframe=1&submit=Download+Data" 
	         
	        # PARSE RESPONSE      
			response = requests.get(strQry)
			month_data = list( csv.reader(response.content.decode('utf-8').splitlines(), delimiter=",") )[15:]

			df = pandas.DataFrame(month_data)
			df = df.rename(columns=df.iloc[0]).drop(df.index[0])
			df['Temp (°C)'] = pandas.to_numeric(df['Temp (°C)'])
			
			# ADD INPUT DAY'S DATA TO PREVIOUS YEAR'S
			df = df[( df.Day == day )]
			avg_temps = pandas.concat([avg_temps, df])

		#print(avg_temps['Temp (°C)'])
		avg_temp = avg_temps['Temp (°C)'].mean() 
		return(avg_temp)




	def do_history(above_or_below):
		with open('history.json', 'r+') as json_file:
			history = json.load(json_file)

			history[above_or_below] += 1

			days_above = history['above']
			days_below = history['below']		
			
			json_file.seek(0)
			json.dump(history, json_file)
			json_file.truncate()

			return('warmer/colder/total days : '+str(days_above)+'/'+str(days_below)+'/'+str((datetime.date.today() - datetime.date(2019, 1, 1)).days + 1) )

	
bot1 = Twitterbot(array_of_station_ids=['1706', '10227', '6747', '6629', '160'], keyfile='keys.json')
bot1.check_temps()