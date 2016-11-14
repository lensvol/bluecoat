# -*- coding: utf-8 -*-

import sys

from crawler import Crawler


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
            print u'Crawling {}'.format(hostname)
            sitemap = crawler.generate_sitemap()

            print_sitemap(sitemap)
    else:
        print u'Usage: bluecoat <host>'


if __name__ == '__main__':
    processor()
