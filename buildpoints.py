import parsers
import urllib
import urlparse

class BuildPoints():
  PARSERS = {'kml': parsers.KmlParser(),
             'gpx': parsers.GpxParser()}

  def __init__(self, uri):
    parsed_uri = urlparse.urlparse(uri)

    self.uri = urlparse.urlunparse((parsed_uri.scheme,
                                    parsed_uri.netloc,
                                    urllib.quote(parsed_uri.path),
                                    urllib.quote(parsed_uri.params),
                                    urllib.quote(parsed_uri.query),
                                    urllib.quote(parsed_uri.fragment)))
    self.path = parsed_uri.path
    self.extension = self.path.split('.')[-1]

  def points(self):
    if self.extension in BuildPoints.PARSERS:
      return BuildPoints.PARSERS[self.extension].parse(self.uri)
