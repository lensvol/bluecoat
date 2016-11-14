# bluecoat

Simple web crawler for listing assets (e.g. links to other pages, CSS) from a website.

## Installation

Install from source:

```
python setup.py install
```

Running tests:

```
py.test
```

## Usage

```
bluecoat <hostname> [<hostname>...]
```

## Example output

```
Crawling yoyowallet.com...

Pages:
/
/assets.html
/benefits.html
/contact.html
/cookies.html
/founders.html
/index.html
/jobs.html
/legal.html
/licenses/android.html
/licenses/ios.html
/licenses/jump-terms.html
/licenses/security.html
/licenses/terms-conditions.html
/licenses/transparency.html
/retailer.html
/security.html
/support.html
/team.html

Assets on /:
http://blog.yoyowallet.com
http://cdn.mxpnl.com/site_media/images/partner/badge_light.png
http://techcrunch.com/2015/12/21/yoyo-launches-mobile-wallet-in-the-u-s/
...
```

## TODO
* Proper logging
* Multiple workers
* Use existing `sitemap.xml` to speed up discovery

