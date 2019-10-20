#!/usr/bin/env python

"""fetch-installer.py: Fetches macOS products from Apple's SoftwareUpdate service."""

__author__ = "konsumer"
__copyright__ = "Copyright 2019, David Konsumer"
__license__ = "GPLv3"
__version__ = "1.0"

# no deps!
import argparse
import errno
import os
import platform
import plistlib
import re
import subprocess
import sys
import time
try:
  from urllib.request import urlopen # Python 3
except ImportError:
  from urllib2 import urlopen # Python 2

suCatalogUrl = 'https://swscan.apple.com/content/catalogs/others/index-10.15seed-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog'

def mkdir_p(path):
  """ Recursive mkdir """
  try:
    os.makedirs(path)
  except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise

def run(cmd, silent = True):
  """ Run a command-array """
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  if not silent:
    for line in process.stdout:
      print(line)

def progress(current, total, title='', size=50, on='#', off=' '):
  """ Show a progress-bar """
  change = (float(current) / float(total))
  delta = int(change * size) + 1
  percent = change * 100.0
  print "\r%s%02d%% [%s%s]" % (title, percent, on * delta, off * (size - delta)),
  sys.stdout.flush()


def download(url, file, size=None, title=''):
  """ Download a large binary file, with progress """
  response = urlopen(url)
  if size is None:
    meta = response.info()
    size = int(meta.getheaders("Content-Length")[0])
  CHUNK = 16 * 1024
  i = 0
  with open(file, 'wb') as f:
    while True:
      i = i + 1
      chunk = response.read(CHUNK)
      if not chunk:
        break
      progress(CHUNK*i, size, title)
      f.write(chunk)

def get(url):
  """ Get the text contents of a URL"""
  return urlopen(url).read()

def getProducts():
  """ get a list of releases from Apple """
  catalog = plistlib.readPlistFromString(get(url=suCatalogUrl))
  installer_products = {}
  if 'Products' in catalog:
    for product_key in list(catalog['Products'].keys()):
      product = catalog['Products'][product_key]
      try:
        if product['ExtendedMetaInfo']['InstallAssistantPackageIdentifiers']['OSInstall'] == 'com.apple.mpkg.OSInstall':
          product = catalog['Products'][product_key]
          dist = plistlib.readPlistFromString(get(url=product['Distributions'].get('English')))
          packages = [ p for p in product['Packages'] if p['URL'].endswith('BaseSystem.dmg') ]
          installer_products[product_key] = {
            'date': product['PostDate'],
            'version': dist['VERSION'],
            'build': dist['BUILD'],
            'url': packages[0]['URL'],
            'size': packages[0]['Size']
          }
      except KeyError:
        continue
  return installer_products

def getInstaller(osx='10.15.1', out = None):
  """ main entry-point gets an IMG file for a version of OSX """
  if out is None:
    out = './installer-%s.img' % (osx) 
  imgPath = os.path.realpath(out)
  imgDir = os.path.dirname(imgPath)
  dmgPath = "%s.dmg" % (os.path.splitext(imgPath)[0])
  if os.path.exists(imgPath):
    print '%s exists. Skipping.' % (imgPath)
  else:
    if os.path.exists(dmgPath):
      print '%s exists. Skipping.' % (dmgPath)
    else:
      print "Getting info from Apple's catalog."
      products = getProducts()
      product = None
      for p in products:
        product = products[p]
        if product['version'] == osx:
          download(product['url'], dmgPath, product['size'], title='Downloading %s (product: %s, build: %s) ' % (osx, p, product['build']))
          break
      if not product:
        parser.print_help()
        print "\n%s wasn't found in Apple's Catalog.\n\nAvailable versions:" % (args['osx'])
        for p in products:
          print '  %s (product: %s, build: %s)' % (products[p]['version'], p, products[p]['build'])
        sys.exit(1)
  if not os.path.exists(imgPath):
    print 'Extracting installer DMG to IMG.'
    run(['%s/dmg2img' % (os.path.dirname(os.path.realpath(__file__))), dmgPath, imgPath])


if __name__== "__main__":
  parser = argparse.ArgumentParser(description="Fetch macOS products from Apple's SoftwareUpdate service, and save installer img file.")
  parser.add_argument('--osx', help='The version of OSX to download. Defaults to 10.15.1.', default='10.15.1')
  parser.add_argument('--out', help='The output path to use.', metavar='PATH')
  a = parser.parse_args()
  getInstaller(a.osx, a.out)


