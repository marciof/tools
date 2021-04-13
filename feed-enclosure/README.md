# Introduction

This is a collection of scripts to help with feed enclosure downloading. They were made to work together with [Liferea](https://lzone.de/liferea/) and [uGet](https://ugetdm.com/) so as to try and get the best video quality possible of feed enclosures, and to minimize any required maintenance from the user.

# Dependencies

Check each script's documentation for required dependencies.

Only [Xubuntu](https://xubuntu.org/) 20.10 on x86-64 is supported/tested at the moment.

# Setup

## Configure download helper

In Liferea's [enclosure settings](https://lzone.de/liferea/help110/preferences_en.html#enclosures) change the download tool to the included script. For example:

    /home/user/feed-enclosure/liferea_download_enclosure.sh %s /home/user/Videos/Feeds/

## Enable automatic enclosure download 

After adding feeds to Liferea, exit it, and do the following to enable automatic downloading of feed enclosures:

    ./liferea_find_opml.sh | xargs cat | ./liferea_auto_enclosure_download.sh | tee feedlist.opml
    ./liferea_find_opml.sh | xargs mv --backup feedlist.opml

## Run Liferea minimized on startup

Use the included script:

    ./liferea_minimized.sh

## Notes

To force trigger downloading feed enclosures after Liferea has already updated all of them, then for each feed subscription delete all items and request a feed update.
