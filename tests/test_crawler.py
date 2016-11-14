# -*- coding: utf-8 -*-

from urlparse import urlparse
import pytest
import responses
from urlparse import urljoin

from bluecoat.crawler import Crawler
from bluecoat.exceptions import NothingToCrawlException

TEST_HOST = 'http://our.site'


@pytest.fixture()
def crawler():
    return Crawler(TEST_HOST)


@pytest.mark.parametrize('url, expected', [
    ('/contacts/', True),
    ('/help', True),
    ('/about.html', True),
    ('/top.htm', True),
    ('/static/script.js', False),
    ('/image/logo.jpg', False),
])
def test_looks_like_page(crawler, url, expected):
    assert crawler._looks_like_page(urlparse(url)) == expected


@pytest.mark.parametrize('url, expected', [
    ('http://our.site/about/', True),
    ('/about/', True),
    ('https://facebook.com', False),
    ('http://twitter.com', False),
    ('http://sexy.solutions/about.html', False),
    ('//scheme.less/index.html', False),
])
def test_is_local_url(crawler, url, expected):
    assert crawler._is_url_local(urlparse(url)) == expected


@pytest.mark.parametrize('url, expected', [
    ('http://our.site/about/', 'http://our.site/about/'),
    ('/about/', 'http://our.site/about/'),
    ('/about/../about.html', 'http://our.site/about.html'),
    ('/../../contacts.html', 'http://our.site/contacts.html'),
    ('.', 'http://our.site/'),
    ('/', 'http://our.site'),
    ('https://facebook.com', 'https://facebook.com'),
])
def test_canonicalize(crawler, url, expected):
    assert crawler._canonicalize(urlparse(url)).geturl() == expected


@responses.activate
def test_crawling_reaches_all_html_pages_even_missing_ones():
    EXAMPLE_HTML = '''
<!DOCTYPE html>
<html>
<head>
  <title></title>
  <link rel="stylesheet" href="styles/app.css" />
  <script src="scripts/app.js"></script>
</head>
<body>
    <a href="http://google.com">Here be dragons.</a>
    <a href="{}">Another local page</a>
</body>
</html>
'''.format(urljoin(TEST_HOST, 'example2.html'))

    EXAMPLE2_HTML = '''
<!DOCTYPE html>
<html>
<head>
  <script src="scripts/other.js"></script>
</head>
<body>
    <a href="{}">Here be dragons.</a>
    <a href="nonexistent_page.html">This page does not exist.</a>
</body>
</html>
'''.format('about.html')

    ABOUT_HTML = '''
<html><head><title>Title</title></head><body>
<a href="http://facebook.com">G!</a></body></html>
'''

    EXPECTED_SITEMAP = {
        u'/': [
            u'{}/styles/app.css'.format(TEST_HOST),
            u'http://google.com',
            u'{}/example2.html'.format(TEST_HOST),
            u'{}/scripts/app.js'.format(TEST_HOST),
        ],
        u'/about.html': [
            u'http://facebook.com',
        ],
        u'/example2.html': [
            u'{}/scripts/other.js'.format(TEST_HOST),
            u'{}/about.html'.format(TEST_HOST),
            u'{}/nonexistent_page.html'.format(TEST_HOST),
        ]
    }

    responses.add(responses.GET, urljoin(TEST_HOST, 'nonexistent_page.html'),
                  status=404, body='<html><head></head><body></body></html>',
                  content_type='text/html')
    for root_path, response in [
        ('/', EXAMPLE_HTML),
        ('example2.html', EXAMPLE2_HTML),
        ('about.html', ABOUT_HTML),
    ]:
        responses.add(responses.GET, urljoin(TEST_HOST, root_path),
                      body=response, content_type='text/html')

    asset_extractor = Crawler(TEST_HOST)
    sitemap = asset_extractor.generate_sitemap()

    requested_urls = set([
        call.request.url
        for call in responses.calls
    ])

    assert len(responses.calls) == 4
    assert requested_urls == {
        'http://our.site/',
        'http://our.site/about.html',
        'http://our.site/example2.html',
        'http://our.site/nonexistent_page.html',
    }
    assert sitemap == EXPECTED_SITEMAP


@responses.activate
def test_crawling_non_existent_site():
    asset_extractor = Crawler('localhost')

    with pytest.raises(NothingToCrawlException):
        asset_extractor.generate_sitemap()
