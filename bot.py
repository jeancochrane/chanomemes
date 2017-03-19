from twitter import Twitter, OAuth
from twitter import TwitterStream, Timeout, HeartbeatTimeout, Hangup
from wordfilter import Wordfilter

import secrets
from . import flickr, memer

AUTH = OAuth(
    secrets.token,
    secrets.token_secret,
    secrets.consumer_key,
    secrets.consumer_secret)


def main():
    # Cache replies to avoid processing duplicates
    processed_ids = []

    # Initialize the stream
    bot_stream = TwitterStream(
        auth=AUTH,
        track="@chano4mayor2k19",
        retry=5)

    # Continuously iterate over the stream generator and make replies
    for tweet in bot_stream.user():
        if tweet is not None:
            if tweet is Timeout:
                main()
                break
            elif tweet is HeartbeatTimeout:
                main()
                break
            elif tweet is Hangup:
                break
            elif tweet.get("text") and tweet["id_str"] not in processed_ids:
                processed_ids.append(tweet["id_str"])
                url = flickr.get_photo()
                orig_img = memer.image(url)
                text = get_text(tweet["text"])
                img = memer.meme(orig_img, text)
                reply(tweet, img)


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
        return("Sorry Friend!\nWe don't support abusive language.")


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
