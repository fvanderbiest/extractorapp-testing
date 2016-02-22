#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import base64
import ssl
import time
import zipfile
from httplib2 import Http
import urllib2
try:
    from simplejson import loads, dumps
except ImportError:
    from json import loads, dumps
from lxml import objectify, etree


instance_base_url = os.getenv('EXTRACTORAPP_INSTANCE_BASEURL', 'https://sdi.georchestra.org')
username = os.getenv('EXTRACTORAPP_INSTANCE_USERNAME', 'testadmin')
password = os.getenv('EXTRACTORAPP_INSTANCE_PASSWORD', 'testadmin')
email = os.getenv('EXTRACTORAPP_REQUESTOR_EMAIL', 'test@me.com')

spec = {
    "emails": [email],
    "globalProperties": {
        "projection": "EPSG:4326",
        "resolution": 10,
        "rasterFormat": "geotiff",
        "vectorFormat": "shp",
        "bbox": {
            "srs": "EPSG:4326",
            "value": [-180, -90, 180, 90]
        }
    },
    "layers": [
    # external public layer, not a georchestra instance
    {
        "bbox": {
            "srs": "EPSG:4326",
            "value": [1.1883944217289, 46.850175233645, 1.3510331483644, 46.946553738317]
        },
        "owsUrl": "http://services.sandre.eaufrance.fr/geo/eth_FXX",
        "owsType": "WFS",
        "layerName": "CoursEau"
    },
    # external public layer, a georchestra instance
    {
        "bbox": {
            "srs": "EPSG:4326",
            "value": [-180, -90, 180, 90]
        },
        "owsUrl": "http://geobretagne.fr/geoserver/draaf/ows",
        "owsType": "WFS",
        "layerName": "draaf:L_BAIEHYDRO_ULVES_R53"
    },
    # local public layer
    {
        "bbox": {
            "srs": "EPSG:4326",
            "value": [1.1883944217289, 46.850175233645, 1.3510331483644, 46.946553738317]
        },
        "owsUrl": instance_base_url+"/geoserver/ci/wfs",
        "owsType": "WFS",
        "layerName": "ci:unprotectedVectorLayer"
    },
    # local private layer
    {
        "bbox": {
            "srs": "EPSG:4326",
            "value": [1.1883944217289, 46.850175233645, 1.3510331483644, 46.946553738317]
        },
        "owsUrl": instance_base_url+"/geoserver/ci/wfs",
        "owsType": "WFS",
        "layerName": "ci:protectedVectorLayer"
    }]
}


def post_dict(url, dictionary):
    '''
    Pass the whole dictionary as a json body to the url.
    Make sure to use a new Http object each time for thread safety.
    '''
    http_obj = Http(None, disable_ssl_certificate_validation=True)
    resp, content = http_obj.request(
        uri=url,
        method='POST',
        headers={
            'Content-Type': 'application/json; charset=UTF-8',
            "Authorization": "Basic {0}".format(base64.b64encode("{0}:{1}".format(username, password))),
        },
        body=dumps(dictionary),
    )
    return content


def download(url):
    file_name = url.split('=')[-1]+'.zip'

    request = urllib2.Request(url)
    base64string = base64.b64encode('%s:%s' % (username, password))
    request.add_header("Authorization", "Basic %s" % base64string)
    context = ssl._create_unverified_context()
    print "Polling file..",
    while True:
        # file might not be available right now
        try:
            u = urllib2.urlopen(request, context=context)
        except urllib2.HTTPError:
            time.sleep(1)
            print ".",
            continue
        break
    print ".\n"

    f = open(file_name, 'wb')
    while True:
        buffer = u.read(8192)
        if not buffer:
            break
        f.write(buffer)
    f.close()
    return file_name

def main():
    print 'Extracting {} layers:'.format(len(spec['layers']))
    for layer in spec['layers']:
        print "  * {} from {}".format(layer['layerName'], layer['owsUrl'])
    print '\n'
    resp = post_dict(
        url = instance_base_url+'/extractorapp/extractor/initiate',
        dictionary = spec
    )
    try:
        root = objectify.fromstring(resp)
    except etree.XMLSyntaxError:
        print "Service did not respond as expected. Problem with credentials ?"
        return
    print 'Archive is downloaded from {}'.format(root.link.text)
    filename = download(root.link.text)
    archive = zipfile.ZipFile(filename, 'r')
    failures = archive.read('extraction-{}/failures.txt'.format(filename.split('.zip')[0]))
    print failures


if __name__ == "__main__":
    main()
