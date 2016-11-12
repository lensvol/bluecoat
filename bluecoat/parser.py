# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup


def extract_assets(html):
    '''Extract paths to assets with links from specified HTML'''
    soup = BeautifulSoup(html, 'html.parser')

    tags_and_attributes = (
        ('a', 'href'),
        ('link', 'href'),
        ('img', 'src'),
        ('script', 'src'),
    )
    assets = []

    for tag, attribute in tags_and_attributes:
        asset_elements = soup.find_all(tag)
        assets.extend([
            element.attrs[attribute]
            for element in asset_elements
            if attribute in element.attrs
        ])

    return assets
