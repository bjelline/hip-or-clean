## Hip or Clean

Compare and constrast resulst from 

### DOHMH New York City Restaurant Inspection Results 

Downloaded csv on April 7 2015 contains 500.664 entries
for 162.711 inspections of 25.317 businisses in 86 categories.

Businesses are identified by their CAMIS id (first column of the csv).
Inspections are identified by CAMIS id and date.

Could also use SODA API?

Background:

  * Their site http://www.nyc.gov/html/doh/html/services/restaurant-inspection.shtml
  * Table for download https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/xx67-kt59
  * SODA API https://data.cityofnewyork.us/resource/xx67-kt59.json
  * https://github.com/eaternet/adapters/wiki/Agency:-New-York-City

### Foursquare API

Looked at venues/explore and venues/search, only search seems to work
for user-less API.  need to iterate over results of search to get ratings.

* always add v=20140806 https://developer.foursquare.com/overview/versioning


### how to run locally

    cp sample.env .env
    foreman start

this should give you a version that runs with a local postgres
database and no api access.  add your foursquare tokens to .env 
and enable the api to populate your database

### how to deploy to heroku

    heroku create
    heroku plugins:install git://github.com/ddollar/heroku-config.git
