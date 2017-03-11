from io import BytesIO

import requests
from PIL import Image, ImageFont, ImageDraw

from .flickr import get_photo


def open_image(url):
    """
    Opens an image from the given URL for processing.
    """
    r = requests.get(url)
    img = Image.open(BytesIO(r.content))
    return img


def add_text(img, text, font):
    """
    Superimposes text over a given image.

    Params –
        img: a PIL Image (obj)
        text: text to superimpose (str)
        font: filepath to the font to use (str)
    """
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font, 16)
    draw.text((0, 0), "Sample Text", (255, 255, 255), font=font)
    img.show()


img = open_image(get_photo())
add_text(img, 'Testing!', 'impact.ttf')
