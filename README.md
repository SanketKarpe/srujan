# Srujan- Safer Networks for Smart Homes
https://sanketkarpe.github.io/srujan/

Srujan is a new type of network segregation system, based on Raspberry Pi, that can be easily deployed on home networks. 
It allows home users to segregate the devices connecting to their home networks based on the threat profile. 
User can keep their smart home devices separate from their computers and mobile devices to mitigate risk of cross 
infection from low-trust devices like smart cameras, speakers and thermostats. Srujan was created to address the 
challenges around the plethora of IOT devices being deployed in smart homes that are vulnerable and do not receive 
patches. Srujan can intelligently segregate the home network into different zones based on the device type. 
It automatically identifies and alerts users when the IOT devices attempt to contact any IP or domain which has been 
blacklisted by [Google Safe Browsing](https://safebrowsing.google.com/) , [hpHosts](https://www.hosts-file.net/) or [Spamhaus](https://www.spamhaus.org/zen/).

#### Srujan provides the following features:

* Intelligent segregation of devices based on their type
* Ability to create network usage stats for each device
* Ability to quarantine untrusted devices
* Easy to integrate with SIEM
* Ability to lookup IP/Domain against Google Safe Browsing.
* Integration with [ANWI (All New Wireless IDS)](https://github.com/anwi-wips/anwi)
* Prevent call-home pings to manufacturer for enhanced privacy.

#### Reporting Dashboard
![Reporting Dashboard](https://github.com/SanketKarpe/srujan/blob/master/docs/images/dashboard.PNG)

