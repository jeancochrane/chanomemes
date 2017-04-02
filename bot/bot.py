from __future__ import print_function
import sys
import time
import socket
import smtplib
from ssl import SSLError
from http.client import BadStatusLine
from io import BytesIO
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

from twitter import Twitter, TwitterStream, TwitterHTTPError, OAuth

import secrets
import flickr
import memer


def main():
    # Cache replies to avoid processing duplicates
    processed_ids = []

    # Initialize the stream
    bot_stream = TwitterStream(
        auth=AUTH)

    # Continuously iterate over the stream generator and make replies
    # (This runs an infinite loop - make sure to manage this code with
    # a process control system)
    while True:
        print("Listening for tweets...")
        try:

            for tweet in bot_stream.statuses.filter(track="@chano4mayor2k19"):
                if not tweet or tweet.get("timeout") or tweet["id_str"] in processed_ids:
                    continue
                if tweet.get("disconnect") or tweet.get("hangup"):
                    print("[WARN] Stream connection lost: %s" % str(tweet), file=sys.stderr)
                    break
                if tweet.get("text"):
                    print('Received tweet: "', tweet.get("text"), '"')
                    processed_ids.append(tweet["id_str"])
                    photo = flickr.get_photo()
                    url, user, user_profile = photo["url"], photo["user"], photo["user_profile"]
                    orig_img = memer.image(url)
                    text = get_text(tweet["text"])
                    print("Processed text: ", text)
                    img = memer.meme(orig_img, text, emoji=True)
                    email(tweet, img, {"user": user, "user_profile": user_profile})
                else:
                    print("[INFO] Received special message: %s" % str(tweet), file=sys.stderr)
        except(TwitterHTTPError, BadStatusLine, SSLError, socket.error) as e:
            print("[WARN] Stream connection lost - reconnecting... (%s, %s)"
                  % (type(e), e), file=sys.stderr)
            time.sleep(2)


def get_text(text):
    """
    Converts tweets to meme-ready text.
    """
    split_text = text.split("@chano4mayor2k19")
    # If the tweet is a direct @, strip our username
    if len(split_text[0]) <= 1:
        if split_text[1][0] == " ":
            return split_text[1][1:]
        else:
            return split_text[1]
    # Otherwise, just return the full text
    else:
        return text


def email(tweet, img, options={}):
    """
    Sends an email to a notification account with meme info.
    """
    global EMAIL_COUNTER

    fromaddr = secrets.email_username
    toaddr = secrets.email_handler
    username = secrets.email_username
    password = secrets.email_password

    # Prep the image for posting
    buff = BytesIO()
    img.save(buff, format="PNG")
    buff.seek(0)
    filename = "chano_meme_" + str(EMAIL_COUNTER) + ".png"

    msg = MIMEMultipart()
    msg['Subject'] = "New Chano Meme #" + str(EMAIL_COUNTER) + "!"
    msg['From'] = fromaddr
    msg['To'] = toaddr

    raw_text = "\r\n".join([
        "New mention from @" + tweet["user"]["screen_name"] + ": '" + tweet["text"] + "'",
        "",
        ""
    ])

    if options and options["user"] and options["user_profile"]:
        raw_text += "\r\n".join([
            "I suggest you reply with:",
            "",
            "#chano4mayor",
            "",
            "📸: " + options["user"] + " " + options["user_profile"],
            "",
            "(Remember, Twitter will shorten the link.)",
            ""
        ])

    raw_text += "\r\n" + "\r\n".join([
        "It's all you from here!",
        "",
        "<3,",
        "",
        "-Chano Bot"
    ])

    text = MIMEText(raw_text)
    msg.attach(text)
    image = MIMEImage(buff.getvalue(), name=filename)
    msg.attach(image)

    server = smtplib.SMTP(secrets.email_smtp_server)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()

    EMAIL_COUNTER += 1


def reply(tweet, img):
    """
    Replies automatically to a tweet given an image.

    (Disabled in the current version of Chano Bot.)
    """
    # Connect to REST API
    bot = Twitter(auth=AUTH, retry=5)

    # Prep the image for posting
    buff = BytesIO()
    img.save(buff, format="PNG")
    buff.seek(0)

    # Upload image to Twitter's server and collect its ID
    upload = Twitter(
        domain="upload.twitter.com",
        auth=AUTH,
        retry=5)
    img_id = upload.media.upload(media=buff.getvalue())["media_id_string"]

    # Send the reply
    bot.statuses.update(
        status="@" + tweet["user"]["screen_name"],
        in_reply_to_status_id=tweet["id_str"],
        media_ids=img_id)


if __name__ == '__main__':

    AUTH = OAuth(
        secrets.token,
        secrets.token_secret,
        secrets.consumer_key,
        secrets.consumer_secret
    )

    global EMAIL_COUNTER
    EMAIL_COUNTER = 1

    main()
