# -*- coding: utf-8 -*-

import sys

from parser import extract_assets


def processor():
    if len(sys.argv) > 1:
        for fn in sys.argv[1:]:
            try:
                with open(fn, 'r') as fp:
                    html_document = fp.read()
                assets = extract_assets(html_document)
            except IOError:
                print 'I/O error while parsing file {}'.format(fn)
                continue

            print 'Assets in {}:\n'.format(fn)
            for asset in assets:
                print '*', asset
            print '---\n'
    else:
        print 'Usage: bluecoat <filename> [<filename2>...]'


if __name__ == '__main__':
    processor()
