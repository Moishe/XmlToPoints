import logging
import threading
import urllib
import urlparse

from google.appengine.api import urlfetch

from xml.dom.minidom import parseString
from xml import sax

class Parser():
  def parse(self, uri):
    points = None

    result = urlfetch.fetch(uri)

    if result.status_code == 200:
      contentHandler = self._getContentHandler()
      sax.parseString(result.content, contentHandler)
      points = contentHandler.points
    else:
      # TODO(moishel): raise parse exception
      pass

    return points


class GpxContentHandler(sax.handler.ContentHandler):
  def __init__(self):
    self.points = []

  def startElement(self, name, attrs):
    if name == 'trkpt':
      self.points.append([attrs.getValue('lat'),
                          attrs.getValue('lon')])


class GpxParser(Parser):
  def _getContentHandler(self):
    return GpxContentHandler()


class KmlContentHandler(sax.handler.ContentHandler):
  def __init__(self):
    self.in_linestring = False
    self.in_coordinates = False
    self.points = []

  def startElement(self, name, attrs):
    if name == 'LineString':
      self.in_linestring = True
    elif self.in_linestring and name == 'coordinates':
      self.in_coordinates = True

  def endElement(self, name):
    if name == 'LineString':
      self.in_linestring = False
    elif name == 'coordinates':
      self.in_coordinates = False

  def characters(self, content):
    if self.in_coordinates and self.in_linestring:
      coord_array = content.split(',')
      if len(coord_array) >= 2:
        self.points.append([coord_array[1].strip(),
                            coord_array[0].strip()])


class KmlParser(Parser):
  def _getContentHandler(self):
    return KmlContentHandler()