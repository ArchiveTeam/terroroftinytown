terroroftinytown
================

[URLTeam](http://urlte.am)'s second generation of URL shortener archiving tools.

For details, please see the [wiki page](http://archiveteam.org/index.php?title=URLTeam).


Running
=======

Tracker
-------

You will need Python 3 and Redis.

How to run the tracker:

        pip3 install -r requirements-tracker.txt
        python3 -m terroroftinytown.tracker THE_CONFIG_FILE.conf

Use `--debug` when developing. Use `--xheaders` when running behind a web server reverse proxy.


Export
-------

        python3 -m terroroftinytown.tracker.export THE_CONFIG_FILE.conf output_dir

The output directory will be created if it does not exists. Specify `--format urlteam` to export in old URLTeam format (no BEACON headers). You will need GNU Sort installed.

A automatic script, to be run from cron, that drains the results, compress, and upload to Internet Archive:

        python3 -m terroroftinytown.release.supervisor config.conf \
        EXPORT_WORKING_DIRECTORY/ --verbose --batch-size 5000000


Test
----

[![Build Status](https://travis-ci.org/ArchiveTeam/terroroftinytown.svg?branch=master)](https://travis-ci.org/ArchiveTeam/terroroftinytown)

**Note: Web interface testing on Travis CI is currently broken due to outdated version of the Firefox binary. Please test locally.**

To run the tests including testing the web interface,

1. Install Firefox 48+
2. Install Selenium for Python from PyPI
3. Download geckodriver and put it located on `PATH` environment variable
4. Run test runner nose

For example, tests:

        apt-get install firefox
        pip3 install selenium
        wget https://github.com/mozilla/geckodriver/releases/download/v0.11.1/geckodriver-v0.11.1-OS_VERSION_HERE.tar.gz
        nosetests3


Client
------

The client should work in Python 2 and 3. Please be mindful when writing the client code.

See [terroroftinytown-client-grab](https://github.com/ArchiveTeam/terroroftinytown-client-grab) for details on how to run the scraper as part of the Warrior project.


Structure
=========

The project is split into two main components: client and tracker.

The client component contains the library needed for performing the request to the shortener. It uses generic shortener parameters such as the alphabet and sequence numbers. The client is responsible for converting the sequence numbers into shortcodes and then fetching them. 

The client also contains shortener specific code called services that customize the generic behavior. Custom behavior may be needed to extract the URLs from the HTML itself.

Once the client has finished scraping, it uploads the shortcode and URLs to the tracker.

The tracker component manages items and projects. Items represent the shortener tasks while projects represent the shortener parameters. Items contain a range of sequence numbers. Items that are checked out are called claims. The tracker supports automatically generating more items.

The tracker will attempt to distribute items across projects so the client does not work on more than one shortener per IP address to avoid bans.

There are two version numbers: Library version for `terroroftinytown.client.__init__` and Pipeline Version for `terroroftinytown-client-grab/pipeline.py`.


Notes
=====

When dealing with non-ASCII characters, one cannot simply treat them as UTF-8 since the originating URL may come from other character sets such as shift-jis. As such, it is ideal to handle the URLs in raw bytes as much as possible. Therefore, the files should be treated as bytes. If not possible, use a "lossless" encoding suitable for your environment. For Python, latin-1 should be used instead of UTF-8. Avoid percent-encoding as much as possible since some servers do not handle percent-encoding well.


