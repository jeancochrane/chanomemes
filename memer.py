from io import BytesIO

import requests
from PIL import Image, ImageFont, ImageDraw


FONT = 'fonts/impact.ttf'


def image(url):
    """
    Opens an image from the given URL for processing.
    """
    r = requests.get(url)
    img = Image.open(BytesIO(r.content))
    return img


def meme(img, text, font=FONT):
    """
    Superimposes text over a given image.

    Params –
        img: a PIL Image (obj)
        text: text to superimpose (str)
        font: filepath to the font to use (str)
    """
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font, 16)
    draw.text((0, 0), text, (255, 255, 255), font=font)
    return img


img = image(get_photo())
meme(img, 'Testing!', 'impact.ttf')
