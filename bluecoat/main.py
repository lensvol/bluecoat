# -*- coding: utf-8 -*-

import sys

from bluecoat.crawler import Crawler
from bluecoat.exceptions import NothingToCrawlException


def print_sitemap(sitemap):
    pages = sorted(sitemap.keys())

    print u'Pages:\n{}\n'.format('\n'.join(pages))
    for page in pages:
        assets = sitemap[page]
        if assets:
            print u'Assets on {}:\n{}\n'.format(
                page,
                '\n'.join(sorted(assets)),
            )
        else:
            print u'No assets on {}\n'.format(page)


def processor():
    if len(sys.argv) > 1:
        for hostname in sys.argv[1:]:
            crawler = Crawler(hostname)

            print u'{}\nCrawling {}...'.format(
                '-' * 32,
                hostname,
            )
            try:
                sitemap = crawler.generate_sitemap()
            except NothingToCrawlException:
                print 'Nothing to see on {}, moving on.\n'.format(hostname)
                continue

            print 'Hostname: {}'.format(hostname)
            print_sitemap(sitemap)
    else:
        print u'Usage: bluecoat <host> [<host>...]'


if __name__ == '__main__':
    processor()
