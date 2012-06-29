import logging
import StringIO
import threading
import urllib
import urlparse
import zipfile

from google.appengine.api import urlfetch

from xml.dom.minidom import parseString
from xml import sax

class Parser():
  def parse(self, uri):
    points = None

    result = urlfetch.fetch(uri)

    if result.status_code == 200:
      content = self._preProcess(result.content)
      contentHandlers = self._getContentHandlers()
      while not points and len(contentHandlers) > 0:
        contentHandler = contentHandlers.pop()
        sax.parseString(content, contentHandler)
        points = contentHandler.points
    else:
      # TODO(moishel): raise parse exception
      pass

    return points

  def _preProcess(self, content):
    return content


class GpxContentHandler(sax.handler.ContentHandler):
  def __init__(self):
    self.points = []

  def startElement(self, name, attrs):
    if name == 'trkpt':
      self.points.append([attrs.getValue('lat'),
                          attrs.getValue('lon')])


class GpxParser(Parser):
  def _getContentHandlers(self):
    return [GpxContentHandler()]


class CoordinateBlockContentHandler(sax.handler.ContentHandler):
  def __init__(self):
    self.in_linestring = False
    self.in_coordinates = False
    self.points = []

  def startElement(self, name, attrs):
    if name == self.bounding_el:
      self.in_linestring = True
    elif self.in_linestring and name == 'coordinates':
      self.in_coordinates = True

  def endElement(self, name):
    if name == self.bounding_el:
      self.in_linestring = False
    elif name == 'coordinates':
      self.in_coordinates = False

  def characters(self, content):
    if self.in_coordinates and self.in_linestring:
      coord_list = content.split(' ')
      for coord in coord_list:
        coord_array = coord.split(',')
        if len(coord_array) >= 2:
          self.points.append([coord_array[1].strip(),
                              coord_array[0].strip()])


class KmlLineStringContentHandler(CoordinateBlockContentHandler):
  def __init__(self):
    CoordinateBlockContentHandler.__init__(self)
    self.bounding_el = 'LineString'

class KmlLinearRingContentHandler(CoordinateBlockContentHandler):
  def __init__(self):
    CoordinateBlockContentHandler.__init__(self)
    self.bounding_el = 'LinearRing'    
  

class KmlTrackContentHandler(sax.handler.ContentHandler):
  def __init__(self):
    self.in_track = False
    self.in_coord = False
    self.points = []
    
  def startElement(self, name, attrs):
    if name == 'gx:Track':
      self.in_track = True
    elif self.in_track and name == 'gx:coord':
      self.in_coord = True

  def endElement(self, name):
    if name == 'gx:Track':
      self.in_track = False
    elif name == 'gx:coord':
      self.in_coord = False

  def characters(self, content):
    if self.in_coord:
      coord_array = content.split(' ')
      if len(coord_array) >= 2:
        self.points.append([coord_array[1].strip(),
                            coord_array[0].strip()])


class KmlParser(Parser):
  def _getContentHandlers(self):
    return [KmlLineStringContentHandler(), KmlTrackContentHandler(), KmlLinearRingContentHandler()]

class KmzParser(KmlParser):
  def _preProcess(self, content):
    zf = zipfile.ZipFile(StringIO.StringIO(content))
    new_content = zf.read(zf.filelist[0].filename)
    return new_content
