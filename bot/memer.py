from __future__ import division
from io import BytesIO
from math import ceil
import random

import requests
from PIL import Image, ImageFont, ImageDraw

BACKGROUND_COLORS = [
    (0, 128, 128),
    (0, 153, 0),
    (0, 102, 204),
    (179, 0, 255),
    (255, 51, 0),
    (204, 163, 0),
    (0, 0, 0)
]

FOREGROUND_COLORS = [
    (0, 255, 255),
    (102, 255, 51),
    (153, 204, 255),
    (240, 204, 255),
    (255, 173, 153),
    (255, 214, 51)
]


def image(url):
    """
    Opens an image from the given URL for processing.
    """
    r = requests.get(url)
    img = Image.open(BytesIO(r.content)).convert('RGBA')
    return img


def debug_meme(img_path):
    img = Image.open('/Users/jeancochrane/Desktop/corey_new.jpeg').convert('RGBA')
    m = meme(img, 'Im in LOVE with my city bitch i sleep in my hat')
    m.show()


def meme(img, text):
    """
    Superimposes text over a given image.

    Params –
        img: a PIL Image (obj)
        text: text to superimpose (str)
    """
    # Fonts and type color
    font = ImageFont.truetype('fonts/roboto.ttf', 36)
    hashtag_font = ImageFont.truetype('fonts/roboto.ttf', 24)
    background_color = random.sample(BACKGROUND_COLORS, 1)[0]
    foreground_color = random.sample(FOREGROUND_COLORS, 1)[0]

    # Get some useful info about the image and instantiate the canvases
    img_width, img_height = img.size
    text_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
    hashtag_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_img)
    hashtag_draw = ImageDraw.Draw(hashtag_img)

    # Clean up line breaks in text
    lines = []
    if '/' in text:
        for line in text.split('/'):
            # Split on the slash, getting rid of spaces
            stripped_line = line
            if line[0] == ' ':
                stripped_line = stripped_line[1:]
            if line[-1] == ' ':
                stripped_line = stripped_line[0:-1]
            lines.append(stripped_line)
    elif '\n' in text:
        for line in text.split('\n'):
            stripped_line = line
            if line[0] == ' ':
                stripped_line = stripped_line[1:]
            if line[-1] == ' ':
                stripped_line = stripped_line[0:-1]
            lines.append(stripped_line)
    else:
        lines.append(text)

    # Create linebreaks when text is too long for the image
    cleaned_lines = []
    for line in lines:
        line_copy = line
        if draw.textsize(line, font=font)[0] > img_width:
            too_long = True
            line_copy = line
            while too_long:
                line_copy = line_copy[0:len(line_copy)-1]
                if draw.textsize(line_copy, font=font)[0] <= img_width:
                    # Find the closest preceding space
                    if (line_copy[-1] == ' ') or (' ' not in line_copy):
                        stopping_point = len(line_copy)
                        too_long = False
            frag1 = line[0:stopping_point-1]
            frag2 = line[stopping_point:]
            cleaned_lines.append(frag1)
            cleaned_lines.append(frag2)
        else:
            cleaned_lines.append(line_copy)

    # Draw the text on the canvas
    if len(cleaned_lines) < 4:
        rotation_degree = random.uniform(-30, 30)
    else:
        rotation_degree = random.uniform(-20, 20)
    y = 0

    for line in cleaned_lines:
        width, height = font.getsize(line)
        width = (img_width - width)/2
        draw.text((width, y), line, background_color, font=font)
        draw.text((width+2, y-2), line,
                   foreground_color, font=font)
        y += 40

    # Rotate the text canvas for DRAMATIC EFFECT and resize other canvases
    if rotation_degree > 0:
        center = None
        translate = None
    else:
        center = (0, 0)
        translate = ((3/10)*rotation_degree, 3*rotation_degree)

    rotated_text = text_img.rotate(
        rotation_degree,
        expand=1,
        center=center,
        resample=Image.BICUBIC,
        translate=translate)
    img.resize(rotated_text.size)
    hashtag_img.resize(img.size)

    # Write the hashtag in the bottom right-hand corner
    hashtag_position = [hashtag_img.size[0]-175, hashtag_img.size[1]-35]

    # Start with black text...
    hashtag_draw.text(hashtag_position, '#Chano4Mayor', (0, 0, 0),
                      font=hashtag_font)
    # Then white text, shifted over
    hashtag_draw.text((hashtag_position[0]-2, hashtag_position[1]-2),
                      '#Chano4Mayor', (255, 255, 255), font=hashtag_font)

    # Paste text layers over the image
    img.paste(rotated_text, (0, 0), mask=rotated_text)
    img.paste(hashtag_img, (0, 0), mask=hashtag_img)
    return img
