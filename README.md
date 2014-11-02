terroroftinytown
================

URLTeam's second generation of URL shortener archiving tools.


Still a work-in-progress. The tracker and client code is maturing and should be ready for production. This readme will be updated once it completes.


Running
=======

Tracker
-------

You will need Python 3 and Redis.

How to run the tracker:

        pip3 install -r requirements-tracker.txt
        python3 -m terroroftinytown.tracker THE_CONFIG_FILE.conf

Use `--debug` when developing.

Export
-------

        python3 -m terroroftinytown.tracker.export THE_CONFIG_FILE.conf output_dir

The output directory will be created if it does not exists. Specify `--format urlteam` to export in old URLTeam format (no BEACON headers). You will need GNU Sort installed.

A automatic script, to be run from cron, that drains the results, compress, and upload to Internet Archive is still being written.


Test
----

[![Build Status](https://travis-ci.org/ArchiveTeam/terroroftinytown.svg?branch=master)](https://travis-ci.org/ArchiveTeam/terroroftinytown)

How to run the tests:

        apt-get install firefox
        pip3 install selenium
        nosetests3


Client
------

The client should work in Python 2 and 3. Please be mindful when writing the client code.

See [terroroftinytown-client-grab](https://github.com/ArchiveTeam/terroroftinytown-client-grab) for details on how to run the scraper as part of the Warrior project.


Structure
=========

The project is split into two main components: client and tracker.

The client component contains the library needed for performing the request to the shortener. It uses generic shortener parameters such as the alphabet and sequence numbers. The client is responsible for converting the sequence numbers into shortcodes and then fetching them. 

The client also contains shortener specific code called services that customize the generic behavior. Custom behavor may be needed to extract the URLs from the HTML itself.

Once the client has finished scraping, it uploads the shortcode and URLs to the tracker.

The tracker component manages items and projects. Items represent the shortener tasks while proejcts represent the shortener parameters. Items contain a range of sequence numbers. Items that are checked out are called claims. The tracker supports automatically generating more items.

The tracker will attempt to distribute items across projects so the client does not work on more than one shortener per IP address to avoid bans.

There are two version numbers: Library version for `terroroftinytown.client.__init__` and Pipeline Version for `terroroftinytown-client-grab/pipeline.py`.


Notes
=====

When dealing with non-ASCII characters, one cannot simply treat them as UTF-8 since the originating URL may come from other character sets such as shift-jis. As such, it is ideal to handle the URLs in raw bytes as much as possible. Therefore, the files should be treated as bytes. If not possible, use a "lossless" encoding suitable for your environment. For Python, latin-1 should be used instead of UTF-8. Avoid percent-encoding as much as possible since some servers do not handle percent-encoding well.


