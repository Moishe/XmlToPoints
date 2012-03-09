function endsWith(str, suffix) {
  return str.indexOf(suffix, str.length - suffix.length) !== -1;
}

$('a').each(function(idx, el) {

  if (el.href  && endsWith(el.href.toLowerCase(), '.gpx')) {
    $(el).after('<a href="http://xmltopoints.appspot.com/map?uris=' +
      el.href + '">[view]</a>');
  }
});
