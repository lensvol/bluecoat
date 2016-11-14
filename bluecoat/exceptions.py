# -*- coding: utf-8 -*-


class BluecoatException(Exception):
    '''Generic exception class for our application'''
    pass


class CrawlerException(BluecoatException):
    '''Basic exception for errors related to web crawler'''
    pass


class NothingToCrawlException(CrawlerException):
    '''Crawling failed for a web site'''
    pass