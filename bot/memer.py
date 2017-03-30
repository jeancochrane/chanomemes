from io import BytesIO
from math import ceil
import random
from os import listdir

import requests
from PIL import Image, ImageFont, ImageDraw


def image(url):
    """
    Opens an image from the given URL for processing.
    """
    r = requests.get(url)
    img = Image.open(BytesIO(r.content)).convert('RGBA')
    return img


def meme(img, text):
    """
    Superimposes text over a given image.

    Params –
        img: a PIL Image (obj)
        text: text to superimpose (str)
    """
    # Choose a random font from the fonts/ directory
    possible_fonts = [("fonts/" + font) for font in listdir('fonts')]
    font_choice = random.sample(possible_fonts, 1)[0]
    font = ImageFont.truetype(font_choice, 36)
    # Hashtag should always be comic sans
    hashtag_font = ImageFont.truetype('fonts/comic_sans.ttf', 24)

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
            line_copy = frag1 + '\n' + frag2
        cleaned_lines.append(line_copy)

    # Figure out how many lines there are
    if len(cleaned_lines) > 1:
        if len(cleaned_lines) % 2 == 0:
            halfway_pt = (len(cleaned_lines)//2)
            split_text = [cleaned_lines[0:halfway_pt], cleaned_lines[halfway_pt:]]
        else:
            halfway_pt = ceil(len(cleaned_lines)/2)
            split_text = [cleaned_lines[0:halfway_pt], cleaned_lines[halfway_pt:]]
    else:
        split_text = cleaned_lines.copy()

    # Draw the text on the canvas
    position = [5, 0]
    rotation_degree = random.uniform(-30, 30)
    if len(split_text) == 1:
        # Start with black text
        draw.text(position, '\n'.join(split_text), (0, 0, 0),
                            font=font)
        # Shift position over a lil and add white on top
        draw.text((position[0]-2, position[1]-2), '\n'.join(split_text),
                  (255, 255, 255), font=font)
    else:
        for line in split_text:
            draw.text(position, '\n'.join(line), (0, 0, 0),
                                font=font)
            draw.text((position[0]-2, position[1]-2), '\n'.join(line),
                      (255, 255, 255), font=font)
            position[1] += draw.textsize('\n'.join(line), font=font)[1] + 16

    # Rotate the text canvas for DRAMATIC EFFECT and resize other canvases
    rotated_text = text_img.rotate(
        rotation_degree,
        expand=1,
        resample=Image.BICUBIC)
    img.resize(rotated_text.size)
    hashtag_img.resize(img.size)

    # Write the hashtag in the bottom right-hand corner
    hashtag_position = [hashtag_img.size[0]-175, hashtag_img.size[1]-35]

    # hashtag_position = [303, 262]

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
