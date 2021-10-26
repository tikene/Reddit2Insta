@echo off
SET subredditname=dankmemes
SET upvotes=1000
SET subredditsearchlimit=500
SET timebetween=300
SET username=
SET password=
SET captionhastags=
SET rclientid=
SET rclientsecret=
SET rusername=
SET rpassword=
SET ruseragent=Reddit2Instagram Bot

powercfg -CHANGE -disk-timeout-ac 0

title @%username%
cls

echo [%username%] Searching in %subredditsearchlimit% posts from r/%subredditname% with more than %upvotes% upvotes on a %timebetween% second(s) delay

CMD /K python RedditToInstagram.py --subredditname %subredditname% --upvotes %upvotes% --subredditsearchlimit %subredditsearchlimit% --timebetween %timebetween% --username %username% --password %password% --captionhastags %captionhastags% --rclientid %rclientid% --rclientsecret %rclientsecret% --rusername %rusername% --rpassword %rpassword% --ruseragent %ruseragent%
