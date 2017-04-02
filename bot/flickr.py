from __future__ import print_function
import random
import json
import sys
import subprocess
from os.path import isfile
from builtins import input

import requests

import secrets


def scrape_photos():
    """
    Creates a JSON file with all CC-licensed images of Chance.

    Generates the file `chance_pics.json` in this directory. Unfortunately,
    you'll have to edit the picture collection manually if you want to remove
    non-Chance images (until we can train a neural net to recognize Chance,
    that is).
    """
    endpoint = "https://api.flickr.com/services/rest/"
    api_key = secrets.flickr_api_key
    method = "flickr.photos.search"
    format = "json"
    license = "1,2,4,5,7"  # All CC
    text = "chance the rapper"
    content_type = 1  # Photos only (no screenshots)
    per_page = 500

    params = {
        "api_key": api_key,
        "method": method,
        "format": format,
        "license": license,
        "text": text,
        "content_type": content_type,
        "per_page": per_page
    }

    photo_url_template = "https://farm{farm_id}.staticflickr.com/{server_id}/{id}_{secret}.jpg"

    r = requests.get(endpoint, params=params)
    if r.status_code == 200:
        try:
            response_text = r.text[14:-1]
            data = json.loads(response_text)
            photos = data["photos"]["photo"]

            for photo in photos:
                photo_url = photo_url_template.format(
                    id=photo["id"],
                    server_id=photo["server"],
                    farm_id=photo["farm"],
                    secret=photo["secret"]
                )
                photo["url"] = photo_url

            with open('chance_pics.json', 'w') as out:
                json.dump(photos, out)
        except ValueError:
            print('Catching ValueError...', file=sys.stderr)
            print('Request URL: ', r.url, file=sys.stderr)
            print('Encoding: ', r.encoding, file=sys.stderr)
            print('Content type: ', r.headers['content-type'], file=sys.stderr)
            with open('bad_output.txt', 'w') as out:
                json.dump(r.text, out)
    else:
        print('Bad status code: ', r.status_code, file=sys.stderr)
        print('Request URL: ', r.url, file=sys.stderr)


def edit_scraped_photos():
    """
    Launches a command-line interface that allows you to view scraped images
    and remove any that you don't like.
    """
    if not isfile('chance_pics.json'):
        scrape_photos()
        edit_scraped_photos()
    else:
        with open('chance_pics.json') as f:
            pics = json.load(f)

        print('Launching image review...')
        current = 0
        total = len(pics)
        output = []
        for pic in pics:
            current += 1
            print('Image %s / %s:' % (current, total))
            print('===============')
            subprocess.Popen(['open', pic['url']])
            decision = False
            while not decision:
                ruling = input('Keep this image? (y / n) ')
                if ruling in ['Y', 'y', 'yes', '']:
                    output.append(pic)
                    decision = True
                elif ruling in ['N', 'n', 'no']:
                    decision = True
                else:
                    print("I didn't understand the input. Try one of: y / n")
                    print('Launching the image again...')
                    print('Image %s / %s:' % (current, total))
                    print('===============')
                    subprocess.Popen(['open', pic['url']])
        with open('edited_chance_pics.json', 'w') as f:
            json.dump(output, f)


def get_photo():
    """
    Returns the URL of a random CC-licensed image of Chance.
    """
    with open('edited_chance_pics.json') as f:
        pics = json.load(f)

    random_photo = random.sample(pics, 1)[0]

    # Retrieve author information for this photo
    endpoint = "https://api.flickr.com/services/rest/"
    api_key = secrets.flickr_api_key
    method = "flickr.people.getInfo"
    format = "json"

    params = {
        "api_key": api_key,
        "method": method,
        "format": format,
        "user_id": random_photo["owner"]
    }

    r = requests.get(endpoint, params=params)
    if r.status_code == 200:
        try:
            response_text = r.text[14:-1]
            data = json.loads(response_text)

            user = data['person']['realname']['_content']
        except ValueError:
            print('Catching ValueError...', file=sys.stderr)
            print('Request URL: ', r.url, file=sys.stderr)
            print('Encoding: ', r.encoding, file=sys.stderr)
            print('Content type: ', r.headers['content-type'], file=sys.stderr)
    else:
        print('Bad status code: ', r.status_code, file=sys.stderr)
        print('Request URL: ', r.url, file=sys.stderr)
        user = "User not found - check the link to find their name"

    photo = {
        "url": random_photo["url"],
        "user": user,
        "user_profile": "https://www.flickr.com/people/" + random_photo["owner"]
    }

    return photo
