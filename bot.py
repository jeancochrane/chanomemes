from __future__ import print_function
import sys
import time
import socket
from ssl import SSLError
from http.client import BadStatusLine
from os import listdir

from twitter import Twitter, TwitterStream, TwitterHTTPError, OAuth
from wordfilter import Wordfilter

import secrets
import flickr
import memer

AUTH = OAuth(
    secrets.token,
    secrets.token_secret,
    secrets.consumer_key,
    secrets.consumer_secret)

FONTS = [("fonts/" + font) for font in listdir('fonts')]


def main():
    # Cache replies to avoid processing duplicates
    processed_ids = []

    # Initialize the stream
    bot_stream = TwitterStream(
        auth=AUTH,
        track="@chano4mayor2k19",
        retry=5)

    # Continuously iterate over the stream generator and make replies
    # (This runs an infinite loop – make sure to manage this code with
    # a process control system)
    while True:
        try:
            for tweet in bot_stream.user():
                if not tweet or tweet.get("timeout") or tweet["id_str"] in processed_ids:
                    continue
                if tweet.get("disconnect") or tweet.get("hangup"):
                    print("[WARN] Stream connection lost: %s" % str(tweet), file=sys.stderr)
                    break
                if tweet.get("text"):
                    processed_ids.append(tweet["id_str"])
                    url = flickr.get_photo()
                    orig_img = memer.image(url)
                    text = get_text(tweet["text"])
                    img = memer.meme(orig_img, text)
                    reply(tweet, img)
                else:
                    print("[INFO] Received special message: %s" % str(tweet), file=sys.stderr)
        except(TwitterHTTPError, BadStatusLine, SSLError, socket.error) as e:
            print("[WARN] Stream connection lost - reconnecting... (%s, %s)"
                  % (type(e), e), file=sys.stderr)
            time.sleep(2)


def get_text(text):
    filt = Wordfilter()
    filt.removeWord('bitch')
    if not filt.blacklisted(text):
        if '\"' in text:
            quotes = '\"'
        else:
            return("Hey Bud!\nPut your text in \"quotes\"" +
                   "and I\'d be happy to make you a meme!")
        return(text.split(quotes)[1])
    else:
        return("Sorry Friend!\nWe don't support that kind of language.")


def reply(tweet, img):
    # Connect to REST API
    bot = Twitter(auth=AUTH, retry=5)

    # Upload image to Twitter's server and collect its ID
    upload = Twitter(
        domain="upload.twitter.com",
        auth=AUTH,
        retry=5)
    img_id = upload.media.upload(media=img)["media_id_string"]

    # Send the reply
    bot.statuses.update(
        status="@" + tweet["user"]["screen_name"],
        in_reply_to_status_id=tweet["id_str"],
        media_ids=[img_id])


if __name__ == '__main__':
    main()
