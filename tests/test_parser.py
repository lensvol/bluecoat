# -*- coding: utf-8 -*-

from bluecoat import parser


def test_document_without_assets_parses_ok():
    html_document = '''
    <html>
        <head></head>
        <body></body>
    </html>
    '''

    assets = parser.extract_assets(html_document)
    assert assets == []


def test_assets_without_required_tags_parses_ok():
    html_document = '''
    <html>
        <head><link /></head>
        <body><a>Empty link</a></body>
    </html>
    '''

    assets = parser.extract_assets(html_document)
    assert assets == []


def test_malformed_document_parsing_fails():
    html_document = '<html>Here goes nothing'

    assets = parser.extract_assets(html_document)
    assert assets == []


def test_document_with_assets_parses_ok():
    html_document = '''
<!DOCTYPE html>
<html>
    <head>
      <title></title>
      <link rel="stylesheet" href="styles/app.css" />
      <script src="scripts/app.js"></script>
    </head>
    <body>
        <a href="http://google.com">Here be dragons.</a>
    </body>
</html>
    '''
    assets = parser.extract_assets(html_document)
    assert assets == [
        u'http://google.com',
        u'styles/app.css',
        u'scripts/app.js',
    ]
