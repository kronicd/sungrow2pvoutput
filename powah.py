import time
import pycurl
import urllib2
import urllib
import json
from StringIO import StringIO    
import sys
import httplib

pvo_host= "pvoutput.org"

pvo_key = "" 
pvo_systemid = ""                                  # Your PVoutput system ID here

sgDeviceId = ""
sgUserId = ""

# This class shamelessly sourced from:
# https://github.com/blebo/pv/blob/master/pv/pvoutput.py
class Connection():
	def __init__(self, api_key, system_id, host):
		self.host = host
		self.api_key = api_key
		self.system_id = system_id

	def add_output(self, date, generated, exported=None, peak_power=None, peak_time=None, condition=None,
			min_temp=None, max_temp=None, comments=None, import_peak=None, import_offpeak=None, import_shoulder=None):
		"""
		Uploads end of day output information
		"""
		path = '/service/r1/addoutput.jsp'
		params = {
				'd': date,
				'g': generated
				}
		if exported:
			params['e'] = exported
		if peak_power:
			params['pp'] = peak_power
		if peak_time:
			params['pt'] = peak_time
		if condition:
			params['cd'] = condition
		if min_temp:
			params['tm'] = min_temp
		if max_temp:
			params['tx'] = max_temp
		if comments:
			params['cm'] = comments
		if import_peak:
			params['ip'] = import_peak
		if import_offpeak:
			params['op'] = import_offpeak
		if import_shoulder:
			params['is'] = import_shoulder

		response = self.make_request('POST', path, params)

		if response.status == 400:
			raise ValueError(response.read())
		if response.status != 200:
			raise StandardError(response.read())

	def add_status(self, date, time, energy_exp=None, power_exp=None, energy_imp=None, power_imp=None, temp=None, vdc=None, cumulative=False):
		"""
		Uploads live output data
		"""
		path = '/service/r2/addstatus.jsp'
		params = {
				'd': date,
				't': time
				}
		if energy_exp:
			params['v1'] = energy_exp
		if power_exp:
			params['v2'] = power_exp
		if energy_imp:
			params['v3'] = energy_imp
		if power_imp:
			params['v4'] = power_imp
		if temp:
			params['v5'] = temp
		if vdc:
			params['v6'] = vdc
		if cumulative:
			params['c1'] = 1
		params = urllib.urlencode(params)

		response = self.make_request('POST', path, params)

		if response.status == 400:
			raise ValueError(response.read())
		if response.status != 200:
			raise StandardError(response.read())

	def get_status(self, date=None, time=None):
		"""
		Retrieves status information
		"""
		path = '/service/r1/getstatus.jsp'
		params = {}
		if date:
			params['d'] = date
		if time:
			params['t'] = time
		params = urllib.urlencode(params)

		response = self.make_request("GET", path, params)

		if response.status == 400:
			raise ValueError(response.read())
		if response.status != 200:
			raise StandardError(response.read())

		return response.read()

	def delete_status(self, date, time):
		"""
		Removes an existing status
		"""
		path = '/service/r1/deletestatus.jsp'
		params = {
				'd': date,
				't': time
				}
		params = urllib.urlencode(params)

		response = self.make_request("POST", path, params)

		if response.status == 400:
			raise ValueError(response.read())
		if response.status != 200:
			raise StandardError(response.read())

		return response.read()

	def make_request(self, method, path, params=None):
		conn = httplib.HTTPConnection(self.host)
		headers = {
				'Content-type': 'application/x-www-form-urlencoded',
				'Accept': 'text/plain',
				'X-Pvoutput-Apikey': self.api_key,
				'X-Pvoutput-SystemId': self.system_id
				}
		conn.request(method, path, params, headers)

		return conn.getresponse()

def getSolarEnergyOutput():
	start = time.strftime("%Y%m%d") + "00"
	end = time.strftime("%Y%m%d") + "23"

	response = urllib2.urlopen('http://www.solarinfobank.com/aapp/PlantDayChart?pid=1284&startYYYYMMDDHH='+start+'&endYYYYMMDDHH='+end+'&chartType=line&lan=en-us')
	webz = response.read()

	stuff  = json.loads(webz)

	if(stuff['isHasData']):
		return stuff['categories'], stuff['series'][0]['data']
	else:
		return False

def getSolarLastUpdateTime():
	response = urllib2.urlopen('http://www.solarinfobank.com/aapp/UnitDevices?uid='+sgUserId+'&lan=en-us')
	webz = response.read()

	stuff  = json.loads(webz)

	return str(stuff['units'][0]['devices'][0]['lastUpdatedTime'])
	
def getSolarTemps():
	start = time.strftime("%Y%m%d") + "00"
	end = time.strftime("%Y%m%d") + "23"

	response = urllib2.urlopen('http://www.solarinfobank.com//aapp/MonitorDayChart?dId='+sgDeviceId+'&startYYYYMMDDHH='+start+'&endYYYYMMDDHH='+end+'&chartType=line&monitorCode=106&lan=en-us')
	webz = response.read()

	stuff  = json.loads(webz)

	if(stuff['isHasData']):
		return stuff['categories'], stuff['series'][0]['data']
	else:
		return False

def getSolarETotal():
	start = time.strftime("%Y%m%d") + "00"
	end = time.strftime("%Y%m%d") + "23"

	response = urllib2.urlopen('http://www.solarinfobank.com/aapp/MonitorDayChart?dId='+sgDeviceId+'&startYYYYMMDDHH='+start+'&endYYYYMMDDHH='+end+'&chartType=line&monitorCode=103&lan=en-us')
	webz = response.read()

	stuff  = json.loads(webz)

	if(stuff['isHasData']):
		return stuff['categories'], stuff['series'][0]['data']
	else:
		return False

def getSolarVDC1():
	start = time.strftime("%Y%m%d") + "00"
	end = time.strftime("%Y%m%d") + "23"

	response = urllib2.urlopen('http://www.solarinfobank.com/aapp/MonitorDayChart?dId='+sgDeviceId+'&startYYYYMMDDHH='+start+'&endYYYYMMDDHH='+end+'&chartType=line&monitorCode=109&lan=en-us')
	webz = response.read()

	stuff  = json.loads(webz)

	if(stuff['isHasData']):
		return stuff['categories'], stuff['series'][0]['data']
	else:
		return False

def getSolarVDC2():
	start = time.strftime("%Y%m%d") + "00"
	end = time.strftime("%Y%m%d") + "23"

	response = urllib2.urlopen('http://www.solarinfobank.com/aapp/MonitorDayChart?dId='+sgDeviceId+'&startYYYYMMDDHH='+start+'&endYYYYMMDDHH='+end+'&chartType=line&monitorCode=111&lan=en-us')
	webz = response.read()

	stuff  = json.loads(webz)

	if(stuff['isHasData']):
		return stuff['categories'], stuff['series'][0]['data']
	else:
		return False

pvoutz = Connection(pvo_key, pvo_systemid, pvo_host)
lastUpdate = 0

while True:
	# get stuff from sungrow
	eOut = getSolarEnergyOutput()
	garbage, temps = getSolarTemps()
	garbage, eDay = getSolarETotal()
	garbage, vdc1 = getSolarVDC1()
	garbage, vdc2 = getSolarVDC2()

	if(eOut != False):
		
		# split times and powah
		times, eOut = eOut

		# find current record number
		lastIndex = 0
		for (i, item) in enumerate(eOut):
			if(item != None):
				lastIndex = i

		# find first update for the set
		firstIndex = 0
		for (i, item) in enumerate(eOut):
			if(item != None):
				firstIndex = i + 1
				break

		# push index to the last valid thingy for today, only on first run
		if(lastUpdate == 0):
			PVOStatus = pvoutz.get_status()
			print "Getting current status...."
			time.sleep(61) # api limit non-fuck
			date = PVOStatus.split(",")[0]
			timez = PVOStatus.split(",")[1]
			if(date == time.strftime("%Y%m%d")):
				lastUpdate = times.index(timez)

	    # sanity, on first run through we set last update to the first value
		if((lastUpdate == 0) or (lastUpdate > lastIndex)):
			lastUpdate = firstIndex
			print "resetting for new day or first run"

		for x in range(lastUpdate, lastIndex+1):
			#grab current values of interest
			powerTime = times[x]
			powerOut = eOut[x]
			cumulative = eDay[x]
			temp = temps[x]
			vdc = (vdc1[x] + vdc2[x])/2

			# show console output
			print "Time: " + str(powerTime) + " KW: " + str(powerOut) + " e-day: " + str(cumulative) + " temp: " + str(temp) + " vdc: " + str(vdc)
			
			# update pvoutput
			if(powerOut and cumulative): # make sure that we have actual values...
				pvoutz.add_status(time.strftime("%Y%m%d"), powerTime, power_exp=powerOut * 1000, energy_exp=cumulative * 1000, temp=str(temp), vdc=str(vdc))
				# dont fuck up API limits
				time.sleep(61)

			
		
		# update lastUpdate value
		lastUpdate = lastIndex
	else:
		print "aint no data.. make the sun come up"

	time.sleep(120)
	print "waiting for new data..."
