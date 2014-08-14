terroroftinytown
================

URLTeam's second generation of URL shortener archiving tools.


Still a work-in-progress. This readme will be updated once it completes.


Running
=======

Tracker
-------

How to run the tracker:

        pip3 install -r requirements-tracker.txt
        python3 -m terroroftinytown.tracker THE_CONFIG_FILE.conf

Use `--debug` when developing.


Test
----

How to run the tests:

        apt-get install firefox
        pip3 install selenium
        nosetests3


Client
------

See [terroroftinytown-client-grab](https://github.com/ArchiveTeam/terroroftinytown-client-grab).
