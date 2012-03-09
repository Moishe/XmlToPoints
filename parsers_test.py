import parsers

import unittest
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed

class MockResult():
  mock_result = None

class MockResultFromFile():
  def __init__(self, filename):
    f = open(filename)
    self.content = f.read()
    self.status_code = 200

class StaticMockResult():
  def __init__(self, content, status_code):
    self.content = content
    self.status_code = status_code

def mock_urlfetch(url):
  return MockResult.mock_result

class TestParser(unittest.TestCase):
  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_memcache_stub()
    parsers.urlfetch.fetch = mock_urlfetch

  def checkValidPoints(self, points):
    for point in points:
      self.assertEqual(2, len(point))

  def test_gpx_parser(self):
    MockResult.mock_result = MockResultFromFile('mock.gpx')
    points = parsers.GpxParser().parse('http://example.com/foo')
    self.assertEquals(318, len(points))
    self.checkValidPoints(points)

  def test_kml_parser(self):
    MockResult.mock_result = MockResultFromFile('mock.kml')
    points = parsers.KmlParser().parse('http://example.com/foo')
    self.checkValidPoints(points)

  def test_gpx_parser_with_memcache(self):
    uri = 'http://example.com/foo'
    MockResult.mock_result = MockResultFromFile('mock.gpx')
    points = parsers.GpxParser().parse(uri)

    MockResult.mock_result = StaticMockResult(404, '')
    cached_points = parsers.GpxParser().parse(uri)

    self.assertEqual(points, cached_points)


if __name__ == '__main__':
  print "really?"
  unittest.main()
