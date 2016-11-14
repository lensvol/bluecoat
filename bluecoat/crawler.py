# -*- coding: utf-8 -*-

from urlparse import urlparse
import posixpath

import requests

from bluecoat.parser import extract_assets
from bluecoat.exceptions import (
    CrawlerException,
    NothingToCrawlException,
)


class Crawler(object):
    """
    Web crawler which lists pages on a site and prepares a map of
    resources referenced from them.
    """
    _starting_address = None
    _our_address = None
    _session = None

    def __init__(self, url):
        # We need to explicitly add scheme here,
        # because requests requires it
        if not url.startswith('http'):
            url = 'http://' + url

        self._starting_address = url
        self._our_address = urlparse(self._starting_address)
        self._session = requests.Session()

    def _is_url_local(self, url):
        """
        Check if supplied URL is local relative to our starting point
        """
        return not url.netloc or url.netloc == self._our_address.netloc

    def _canonicalize(self, url):
        """
        Clean supplied URL, discarding query fragments (hashbangs) and parameters.
        Also we will try to resolve path traversal symbols ('.', '..').

        This function won't try to improve URLs external to our starting point.
        """
        parsed_path = url.path

        if not self._our_address:
            raise ValueError('Can\'t canonicalize URL without local address')

        # Must be external host, leave as it is
        if not self._is_url_local(url):
            return url

        # We need this to correctly compensate for '../' at root,
        # e.g. '../about.html'
        if not parsed_path.startswith('/'):
            parsed_path = '/' + parsed_path

        # No need to waste CPU if we resolve root path
        if parsed_path in ['.', '/']:
            return self._our_address

        # Compensate for '../' in URL
        resolved_path = posixpath.normpath(parsed_path)

        # There is something weird going on with trailing slashes
        # (see https://bugs.python.org/issue1707768)
        if url.path.endswith('/'):
            resolved_path += '/'

        canon_url = url._replace(
            scheme=self._our_address.scheme or 'http',
            path=resolved_path,
            netloc=self._our_address.netloc,
            fragment=None,
        )
        return canon_url

    def _looks_like_page(self, parts):
        """
        Heuristic detection of possible candidates for asset extraction.
        """
        last_part = parts.path.rsplit('/')[-1]

        return any([
            parts.path.endswith('/'),
            parts.path.endswith('.html'),
            parts.path.endswith('.htm'),
            last_part and '.' not in last_part,
        ])

    def crawl_page(self, full_url):
        """
        Retrieve requested URL and try to extract all available
        assets from received content.

        We will panic if anything other than 200.
        """
        try:
            response = self._session.get(full_url)
        except Exception, e:
            raise CrawlerException(e.message)

        content_type = response.headers.get('Content-Type', 'text/html').split(';')
        if response.status_code != 200:
            raise CrawlerException('Unexpected status: {}'.format(response.status_code))
        elif content_type[0] != 'text/html':
            raise CrawlerException('Unexpected Content-Type: {}'.format(content_type))

        return full_url, extract_assets(response.content)

    def generate_sitemap(self):
        """
        Generate sitemap-like collection of resources from specified starting
        address. Our crawler will try to discover and extract links to local
        assets from any visible page (HTML).
        """
        links_to_traverse = {self._our_address.geturl()}
        already_seen = set()
        sitemap = {}

        while links_to_traverse:
            page = links_to_traverse.pop()
            already_seen.add(page)
            try:
                full_url, assets = self.crawl_page(page)
            except CrawlerException, ce:
                print 'Crawling failed for {}: {}'.format(
                    page,
                    ce.message,
                )
                continue

            full_url = full_url.replace(self._starting_address, '') or '/'
            assets = map(urlparse, assets)
            assets = set(map(self._canonicalize, assets))
            sitemap[full_url] = [
                link.geturl()
                for link in assets
            ]

            # We only want to follow only links local to this site
            # and skip resources e.g .js, .css and so on.
            local_links = filter(
                lambda url: self._is_url_local(url) and self._looks_like_page(url),
                set(assets),
            )
            new_links = [
                link.geturl() for link in local_links
                if link.geturl() not in already_seen
            ]
            links_to_traverse.update(new_links)

        # If we have no resources and visited only one link, then it means
        # we failed completely at crawling that site.
        # TODO: Better design next time, so this hack would not be needed
        if not sitemap and len(already_seen) == 1:
            raise NothingToCrawlException(self._starting_address)

        return sitemap

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            repr(self._starting_address),
        )
