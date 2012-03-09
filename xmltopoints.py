#!/usr/bin/python

import buildpoints

import logging
import os
import urllib
import urlparse
import webapp2

from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.api import urlfetch

from django.utils import simplejson as json
from xml.dom.minidom import parseString


class DemoPage(webapp2.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'demo.html')
    self.response.out.write(template.render(path, {}))


class RenderPage(webapp2.RequestHandler):
  def get(self):
    uris = self.request.get('uris', '').split(',')
    path = os.path.join(os.path.dirname(__file__), 'map.html')
    cache = self.request.get('cache', 'y')
    logging.info(uris);
    self.response.out.write(template.render(path, {'uris': uris,
                                                   'cache': cache}))


class XmlToPointsServlet(webapp2.RequestHandler):
  def get(self):
    # get the xml specified as a param
    uri = self.request.get('uri')
    jsonp = self.request.get('jsonp')
    use_cache = self.request.get('cache', 'y') == 'y'

    points = None
    if use_cache:
      points = memcache.get(uri)

    if not points:
      points = buildpoints.BuildPoints(uri).points()
      memcache.add(uri, points)

    if jsonp:
      self.response.out.write('%s(%s);' % (jsonp, json.dumps(points)))
    else:
      self.response.out.write(json.dumps(points))


app = webapp2.WSGIApplication([
    ('/', DemoPage),
    ('/map', RenderPage),
    ('/getpoints', XmlToPointsServlet)], debug=True)
