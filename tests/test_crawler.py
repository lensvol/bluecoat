# -*- coding: utf-8 -*-

from bluecoat.crawler import Crawler
import pytest


TEST_HOST = 'http://localhost/'


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
    assert crawler.looks_like_page(url) == expected


@pytest.mark.parametrize('url, expected', [
    ('http://localhost/about/', True),
    ('/about/', True),
    ('https://facebook.com', False),
    ('http://twitter.com', False),
    ('http://sexy.solutions/about.html', False),
    ('//scheme.less/index.html', False),
])
def test_is_local_url(crawler, url, expected):
    assert crawler.is_url_local(url) == expected


@pytest.mark.parametrize('url, expected', [
    ('http://localhost/about/', 'http://localhost/about/'),
    ('/about/', 'http://localhost/about/'),
    ('/about/../about.html', 'http://localhost/about.html'),
    ('/../../contacts.html', 'http://localhost/contacts.html'),
    ('.', 'http://localhost/'),
    ('/', 'http://localhost/'),
])
def test_canonicalize(crawler, url, expected):
    assert crawler.canonicalize(url) == expected

