## Script to get current Flick Electric Co spot price
### Author: Tomas Maggio (tomasmaggio@gmail.com)

import os, time
from datetime import datetime
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
from influxdb import InfluxDBClient
import html2text
import re

# Loop around login page
while True:
	# Browser
	br = mechanize.Browser()

	# Cookie Jar
	cj = cookielib.LWPCookieJar()
	br.set_cookiejar(cj)

	# Browser options
	br.set_handle_equiv(True)
	br.set_handle_gzip(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)
	br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

	br.addheaders = [('User-agent', 'Chrome')]

	# The site we will navigate into, handling it's session
	connected = False
	tried = 0
	while not connected:
		try:
			br.open('https://id.flickelectric.co.nz/identity/users/sign_in')
			connected = True
		except mechanize.HTTPError as e:
			print e.code
                        tried += 1
                        if tried > 4:
                        	exit()
                        sleep(3)
                except mechanize.URLError as e:
                        print e.reason.args
                        tried += 1
                        if tried > 4:
                        	exit()
                        sleep(3)

	# View available forms
	for f in br.forms():
		print f

	# Select the second (index one) form (the first form is a search query box)
	br.select_form(nr=0)

	# User credentials
	br.form['user[email]'] = 'YOUR_ID'
	br.form['user[password]'] = 'YOU_PASSWORD'

	# Login
	br.submit()

	# Define inflluxdb connection
	client = InfluxDBClient('X.X.X.X', 8086, 'writer', 'writer', 'collections')

	# Loop and execute every 90 minutes
	count = 0
	tried = 0
	connected = False
	while (count < 90):
		    print 'The count is:', count
		    count = count + 1
		    print "Requesting price using logged in session..."

	# Save html code so we can parse it
		    while not connected:
		    	try:
		    		content = br.open('https://myflick.flickelectric.co.nz/dashboard/snapshot').read()
				connected = True
			except mechanize.HTTPError as e:
				print e.code
				tried += 1
				if tried > 4:
					exit()
				sleep(3)
			except mechanize.URLError as e:
				print e.reason.args
				tried += 1
				if tried > 4:
					exit()
				sleep(3)
		    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
		    print "Current time: %s" % current_time
		    soup = BeautifulSoup(content)
		    rawprice = soup.find("div", {"class": "dial"})
		    strprice = str(rawprice).split('\n')[0]

	# Regex to find the line we want
		    price = re.findall(r'data-value-cents="(.*)">', strprice)
		    decimals = float(", ".join(price))
		    valor = str(round(decimals,2))
		    print(valor)
		    json_body = [
		    {
		        "measurement": "current_price",
		        "tags": {
		            "provider": "flick",
		            "region": "canterbury"  # Your region here
		        },
		        "time": current_time,
		        "fields": {
		            "value": (valor)
		        }
		    }
		]
		    #print(json_body)
		    client.write_points(json_body)
		    time.sleep(60)

	print "Good bye! See you in 90 minutes around here"
