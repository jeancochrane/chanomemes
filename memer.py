from io import BytesIO
from math import ceil

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
    font = ImageFont.truetype(font, 36)
    img_width, img_height = img.size

    # Handle line breaks in text
    lines = []
    if '/' in text:
        for line in text.split('/'):
            lines.append(line)
    elif '\n' in text:
        for line in text.split('\n'):
            lines.append(line)
    else:
        lines.append(text)

    # Create linebreaks when text is too long for the image
    cleaned_lines = lines
    for line in lines:
        if draw.textsize(line) > img_width:
            too_long = True
            line_copy = line
            while too_long:
                line_copy = line_copy[0:len(line_copy)-1]
                if draw.textsize(line_copy) <= img_width:
                    stopping_point = len(line_copy)
                    too_long = False
            frag1 = line[0:stopping_point]
            frag2 = line[stopping_point:]
            line = frag1 + '\n' + frag2
        cleaned_lines.append(line)

    # Figure out how many lines there are
    if len(lines) % 2 == 0:
        halfway_pt = (len(lines)/2) - 1
        split_text = [lines[0:halfway_pt], lines[halfway_pt:]]
    else:
        halfway_pt = ceil(len(lines)/2)
        split_text = [lines[0:halfway_pt], lines[halfway_pt:]]

    # Make the drawing
    draw.multiline_text((0, 0), split_text[0], (255, 255, 255),
                        font=font,
                        align='center')

    # TODO: Draw the second half on the bottom of the image
    return img
