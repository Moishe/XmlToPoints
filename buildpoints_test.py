import buildpoints

import unittest
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed

class MockParser():
  def parse(uri, use_cache):
    pass

class TestBuildPoints(unittest.TestCase):
  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_memcache_stub()

  def test_build_points(self):
    points = buildpoints.BuildPoints('foo.gxp').points()

if __name__ == '__main__':
  unittest.main()
