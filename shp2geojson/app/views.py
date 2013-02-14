# Create your views here.
import os, sys, tempfile, zipfile
import django.contrib.gis
import tempfile
import shutil
import pprint
import os.path
import urlparse
import json
import time

from django import forms
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings

# 
# 
# 

@csrf_exempt
def index(request):
  return upload_file(request)

def upload_file(request):
  if request.method == 'POST':
    form = UploadFileForm(request.POST, request.FILES)

    uploaded_filename = request.FILES['file'].name

    (filename, extension) = os.path.splitext(uploaded_filename)

    if extension == ".zip":

      handle_uploaded_file(request.FILES['file'], uploaded_filename)
      zipfile_shp = os.path.join(settings.DATA_ROOT, uploaded_filename)


      try:
        unzip(zipfile_shp)
      except:
        e = sys.exc_info()[0]
        return HttpResponse( json.dumps({'error': e}) , content_type="application/json")

      fro = os.path.join(settings.DATA_ROOT, filename, filename + '.shp')
      to = os.path.join(settings.APP_STATIC, filename + '.geojson')
      
      print 'to: ' + to
      try:
        reproject_shp_file_covert_to_geojson( fro, to )
        with open(to, 'r') as content_file:
          geojson_content = content_file.read()
      except:
        e = sys.exc_info()[0]
        geojson_content = json.dumps({'error': e})

      return HttpResponse(geojson_content, content_type="application/json")
    else:
      return HttpResponse( json.dumps({'error': 'Please provide zip file'}) , content_type="application/json")

  else:
    form = UploadFileForm()
    return render_to_response('index.html', {'form': form})


def handle_uploaded_file(f, filename):
  with open( os.path.join(settings.DATA_ROOT, filename) , 'wb+') as destination:
    for chunk in f.chunks():
      destination.write(chunk)


class UploadFileForm(forms.Form):
  file  = forms.FileField()


def reproject_shp_file_covert_to_geojson( fro, to, projection = 'EPSG:900913'):

  if(os.path.isfile(to)):
    print 'Using cached version of ' + to    
    print "created: %s" % time.ctime(os.path.getctime(to))

  else:
    
    # print 'OS Enviroment ' + os.environ
    ogr2ogr_path = ''
    if 'PRODUCTION' in os.environ:
      ogr2ogr_path = '/app/.geodjango/gdal/bin/'

    cmd=ogr2ogr_path + 'ogr2ogr -overwrite -F "GeoJSON" -t_srs '+ projection +' '+to+' ' + fro
    print cmd
    response = os.popen(cmd,"r")




def process_url(url, keep_params):
  parsed= urlparse.urlsplit(url)
  filtered_query= '&'.join(
    qry_item
    for qry_item in parsed.query.split('&')
    if qry_item.startswith(keep_params))
  return urlparse.urlunsplit(parsed[:3] + (filtered_query,) + parsed[4:])


def unzip( fullpath ):
  basename = os.path.basename(fullpath)
  (filename, extension) = os.path.splitext(basename)   
  dirname = os.path.join( os.path.dirname(fullpath),  filename)

  try: # Don't try to create a directory if exists
    os.mkdir(dirname)

    # Get a real Python file handle on the uploaded file
    fullpathhandle = open(fullpath, 'r') 

    # Unzip the file, creating subdirectories as needed
    zfobj = zipfile.ZipFile(fullpathhandle)
    for name in zfobj.namelist():
      if name.endswith('/'):
        try: # Don't try to create a directory if exists
          os.mkdir(os.path.join(dirname, name))
        except:
          pass
      else:
        outfile = open(os.path.join(dirname, name), 'wb')
        outfile.write(zfobj.read(name))
        outfile.close()

  except:
    pass

