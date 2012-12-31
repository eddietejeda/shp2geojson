# Create your views here.
import os, sys, tempfile, zipfile
import django.contrib.gis
import tempfile
import shutil
import pprint
import os.path

from django import forms
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings


# http://geoinformaticstutorial.blogspot.com/2012/10/reprojecting-shapefile-with-gdalogr-and.html

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

      unzip(zipfile_shp)

      fro = os.path.join(settings.DATA_ROOT, filename + '.shp')
      to = os.path.join(settings.APP_STATIC, filename + '.geojson')

      reproject_shp_file_covert_to_geojson( fro, to )
      
      print to
      with open(to, 'r') as content_file:
        geojson_content = content_file.read()
      return HttpResponse(geojson_content, content_type="application/json")
      # return redirect()      
    else:
      return HttpResponse('Please provide zip file')

  else:
    form = UploadFileForm()
    return render_to_response('index.html', {'form': form})


def handle_uploaded_file(f, filename):
  with open( os.path.join(settings.DATA_ROOT, filename) , 'wb+') as destination:
    for chunk in f.chunks():
      destination.write(chunk)


class UploadFileForm(forms.Form):
  file  = forms.FileField()


def reproject_shp_file_covert_to_geojson( fro, to):
  if(os.path.isfile(to)):
    print 'Using cached version of ' + to    
  else:
    
    ogr2ogr_path = ''
    if 'PRODUCTION' in os.environ:
      ogr2ogr_path = '/app/.geodjango/gdal/bin/'

    cmd=ogr2ogr_path + 'ogr2ogr -overwrite -F "GeoJSON" -t_srs EPSG:4326 '+to+' ' + fro
    print cmd
    response = os.popen(cmd,"r")


def unzip( fullpath ):
  dirname = os.path.dirname(fullpath)
  
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