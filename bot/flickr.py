import random
import json

import requests

import secrets

def get_photo():
    """
    Returns the URL of a random CC-licensed image of Chance.
    """
    endpoint = "https://api.flickr.com/services/rest/"
    api_key = secrets.flickr_api_key
    method = "flickr.photos.search"
    format = "json"
    license = "1,2,4,5,7"  # All CC
    text = "chance the rapper"
    content_type = 1  # Photos only (no screenshots)

    params = {
        "api_key": api_key,
        "method": method,
        "format": format,
        "license": license,
        "text": text,
        "content_type": content_type
    }

    photo_url_template = "https://farm{farm_id}.staticflickr.com/{server_id}/{id}_{secret}.jpg"

    r = requests.get(endpoint, params=params)
    if r.status_code == 200:
        try:
            response_text = r.text[14:-1]
            data = json.loads(response_text)
            photos = data["photos"]["photo"]
            random_photo = random.sample(photos, 1)

            photo_id = random_photo[0]["id"]
            server_id = random_photo[0]["server"]
            farm_id = random_photo[0]["farm"]
            secret = random_photo[0]["secret"]

            photo_url = photo_url_template.format(
                id=photo_id,
                server_id=server_id,
                farm_id=farm_id,
                secret=secret
            )

            return photo_url
        except ValueError:
            print('Catching ValueError')
            print('Request URL: ', r.url)
            print('Encoding: ', r.encoding)
            print('Content type: ', r.headers['content-type'])
            with open('bad_output.txt', 'w') as out:
                json.dump(r.text, out)
    else:
        print('Bad status code: ', r.status_code)
        print('Request URL: ', r.url)
