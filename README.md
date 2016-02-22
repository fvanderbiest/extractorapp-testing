# Extractorapp testing

## install

Requires python >= 2.7.9

```
$ sudo apt-get install python2.7 python2.7-dev python-virtualenv libxslt1-dev lib32z1-dev
$ virtualenv env
$ source env/bin/activate
$ pip install httplib2 simplejson lxml
```

Or build a docker image with, eg:
```
docker build -t fvanderbiest/extractorapp_testing .
```

## run

Pull image from docker hub & run with:
```
docker run --rm -v $(pwd):/tmp -u `id -u $USER` \
-e EXTRACTORAPP_INSTANCE_BASEURL='https://sdi.georchestra.org' \
-e EXTRACTORAPP_INSTANCE_USERNAME='testadmin' \
-e EXTRACTORAPP_INSTANCE_PASSWORD='testadmin' \
-e EXTRACTORAPP_REQUESTOR_EMAIL='test@me.com' \
fvanderbiest/extractorapp_testing
```

Or without docker:
```
export EXTRACTORAPP_INSTANCE_BASEURL='https://sdi.georchestra.org'
export EXTRACTORAPP_INSTANCE_USERNAME='testadmin'
export EXTRACTORAPP_INSTANCE_PASSWORD='testadmin'
export EXTRACTORAPP_REQUESTOR_EMAIL='test@me.com'
python test_extractorapp.py
```