TODO
=====

Once stuff in here is done and finalized, properly document it in the readme file.


Tracker
=======


The tracker will be similar to `universtal-tracker` and the previous URLTeam tracker. In the old tracker, the parameters (delays, alphabets, HTTP status codes) for fetching the URLs were placed in the client code. This made it difficult to add changes/tweaks or adding some relativity small and unknown shorteners. This new shortener will have all the parameters in the tracker which hopefully will cover 80% of the existing shorteners out there. Otherwise, custom code inside the client code is inevitable.

The tracker will use sequence numbers to generate the shortcodes. Shortcodes are derived from the alphabet parameters. Shortners may either be incremental or random. The algorithm to generate random shortcodes is not yet determined.


Format
======


The URLTeam format content of the files will be the same: the shortcode text, a pipe, and the URL. However, the URLs may contain control characters and characters outside the ASCII range. The new validation code should properly percent encode the unprintable control characters.

When dealing with non-ASCII characters, one cannot simply treat them as UTF-8 since the originating URL may come from other character sets such as shift-jis. As such, it is ideal to handle the URLs in raw bytes as much as possible. Therefore, the files should be treated as bytes. If not possible, use a "lossless" encoding suitable for your environment. For Python, latin-1 should be used instead of UTF-8. Avoid percent-encoding as much as possible since some servers do not handle percent-encoding well.


The BEACON format is more explicit; it includes the full origin URL.



Set-it-and-forget-it store idea
================================

A simple way to store the URL datasets is to upload the existing URLTeam torrent to archive.org. Then, new URLs are uploaded as new items similar to how existing WARCs files are uploaded using the MegaWARC factory. This reduces the burden of having the entire dataset required to roll out an new release. It's messier and won't be easy to navigate.

Each new item could be 10 GB in size with each shortener service as a separate XZ or GZ file. An accompanying text or json file should describe the full URL needed to rebuild the shortlinks from the URL. An additional text file containing only shortcodes could be a companion to the compressed file.



Ambitious public store idea
===========================

An ambitious to store all the URLs datasets into GitHub. Using source control on the URLs allows proper tracking of changes, resolution of duplicates, and manual contributions.

Uncompressed, there is about 500GB of data. GitHub has a maximum repository size of 1GB. Ideally, each repository will represent one shortener service. Large shorteners can be overcome by using many repositories. GitHub has unlimited repositories (see https://github.com/gitpan which has at least 220000 repositories). Using many repositories will require careful structuring of the datasets.

The ideal directory structure will consist of a prefix tree of the shortcode. However, shortcodes are case sensitive while some filesystems are case-insensitive. As such, it is recommend that directory and filenames use percent-encoding of the shortcodes for ambiguous characters. (Percent-encoded text is very obvious that it is percent-encoding.)

To handle large shorteners, the directories will need to be split up among repositories. The structure will need to allow the repositories to fill up to no more than 750GB. For shortners that are dead and not expected to change, the structure should use minimal repositories.

A possible directory structure may look like this:

    shortener-name/
        00/
            00/
                00/
                    000000.txt
        0%61/
            %61%61/
                %61%61/
                    0%61%61%61%61%61.txt

The filename of the text file indicates the prefix of the shortcodes in the text file. Each text file should not be larger than 50MB (which is the GitHub limit).


Client
--------

The client code likely will look the same as the old client code. However, the goal is to write the client code as modular library so it can be used standalone or integrated with a Seesaw-kit pipeline.


Release
---------

Unlike the previous release, the dataset will be in GitHub. As a result, the person doing the release will not need to have all the files present. Ideally, a cron job on the tracker will be able to use git to add new data and commit it back to the repositories.


