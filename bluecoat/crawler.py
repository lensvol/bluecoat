# -*- coding: utf-8 -*-

import requests

from urlparse import urlparse
import posixpath

from bluecoat.parser import extract_assets
from bluecoat.exceptions import CrawlerException


class Crawler(object):
    starting_address = None
    our_address = None
    session = None

    def _extract_hostname(self, url):
        parts = urlparse(url)
        return parts.netloc

    def __init__(self, url):
        if not url.startswith('http'):
            url = 'http://' + url

        self.starting_address = url
        self.our_address = urlparse(self.starting_address)
        self.session = requests.Session()

    def _is_url_local(self, url):
        hostname = self._extract_hostname(url)
        return not hostname or hostname == self.our_address.netloc

    def _canonicalize(self, url):
        parsed = urlparse(url)
        parsed_path = parsed.path

        # Must be external host, leave as it is
        if parsed.netloc and parsed.netloc != self.our_address.netloc:
            return url

        # We need this to correctly compensate for '../' at root,
        # e.g. '../about.html'
        if not parsed_path.startswith('/'):
            parsed_path = '/' + parsed_path

        # No need to waste CPU if we resolve root path
        if parsed_path in ['.', '/']:
            return self.our_address.geturl()

        # Compensate for '../' in URL
        resolved_path = posixpath.normpath(parsed_path)

        # There is something weird going on with trailing slashes
        # (see https://bugs.python.org/issue1707768)
        if parsed.path.endswith('/'):
            resolved_path += '/'

        canon_url = parsed._replace(
            scheme=self.our_address.scheme,
            path=resolved_path,
            netloc=self.our_address.netloc,
            fragment=None,
        )
        return canon_url.geturl()

    def _looks_like_page(self, url):
        parts = urlparse(url)
        last_part = parts.path.rsplit('/')[-1]

        return any([
            parts.path.endswith('/'),
            parts.path.endswith('.html'),
            parts.path.endswith('.htm'),
            last_part and '.' not in last_part,
        ])

    def crawl_page(self, url):
        full_url = self._canonicalize(url)
        try:
            response = self.session.get(full_url)
            assets = extract_assets(response.content)
        except Exception, e:
            raise CrawlerException(e.message)

        if response.status_code != 200:
            message = 'Unexpected status code: {}'.format(response.status_code)
            raise CrawlerException(message)

        return full_url, assets

    def traverse(self):
        links_to_traverse = {self._canonicalize(self.starting_address)}
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

            full_url = full_url.replace(self.starting_address, '') or '/'
            sitemap[full_url] = list(set(map(self._canonicalize, assets)))

            local_links = filter(
                lambda url: self._is_url_local(url) and self._looks_like_page(url),
                set(assets),
            )
            new_links = [
                link for link in local_links
                if link not in already_seen
            ]
            links_to_traverse.update(new_links)
        return sitemap

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            repr(self.starting_address),
        )