shp2geojson
========================

Most online map services use longitude/latitude coordinates with WGS84 projection. Local governments most often provide ESRI Shapefiles using all kinds of funky projections. I want to be able to take any Shapefile with any projection and covert it to GeoJSON using Lat/Long and work with that. You can easily install GDAL/OGR to change the filetypes, but I wanted to create a service that was ready and available for anyone to use at anytime. Setting up GDAL/OGR on Heroku can be a pain and now you don't have to.

So I created a simple webservice that takes a Shapefile (zipped) and returns a GeoJSON file. I want this service to have a long life and future applications to be dependent on it so I wanted it to be on Heroku.


Install on Heroku
-----

    $ heroku create --stack cedar --buildpack http://github.com/cirlabs/heroku-buildpack-geodjango/

    $ git push heroku master
    ...
    -----> Heroku receiving push
    -----> Fetching custom buildpack... done
    -----> Python app detected
    -----> Fetching and installing GEOS 3.3.2
    -----> Installing ...
       GEOS installed
    -----> Fetching and installing Proj.4 4.7.0
    -----> Installing ...
       Proj.4 installed
    -----> Fetching and installing GDAL 1.8.1
    -----> Installing ...
       GDAL installed
    -----> Preparing virtualenv version 1.7
    ... etc.

    $ heroku config:set GDAL_LIBRARY_PATH='/app/.geodjango/gdal/lib/libgdal.so'
    $ heroku config:set GEOS_LIBRARY_PATH='/app/.geodjango/geos/lib/libgeos_c.so'
    $ heroku config:set GDAL_LIBRARY_PATH='TRUE'


Install locally
-----

If you use virtualenv or virtualenvwrapper, be sure to create your enviroment.

    $ brew install gdal geos
    $ git clone https://github.com/eddietejeda/shp2geojson.git
    $ cd shp2geojson
    $ pip install -r requirements.txt
    $ foreman start

Open browser on 0.0.0.0:5000




