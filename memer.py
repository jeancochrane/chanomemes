from io import BytesIO
from math import ceil
import random

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
    img_width, img_height = img.size
    text_img = Image.new(img.mode, img.size)
    draw = ImageDraw.Draw(text_img)
    font = ImageFont.truetype(font, 36)
    

    # Handle line breaks in text
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
            print('Line too long!')
            too_long = True
            line_copy = line
            while too_long:
                print('Img width %s, line length %s'
                      % (img_width, draw.textsize(line_copy, font=font)[0]))
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
    print('cleaned_lines: ', cleaned_lines)
    if len(cleaned_lines) > 1:
        if len(cleaned_lines) % 2 == 0:
            halfway_pt = (len(cleaned_lines)//2)
            split_text = [cleaned_lines[0:halfway_pt], cleaned_lines[halfway_pt:]]
        else:
            halfway_pt = ceil(len(cleaned_lines)/2)
            split_text = [cleaned_lines[0:halfway_pt], cleaned_lines[halfway_pt:]]
    else:
        split_text = cleaned_lines.copy()

    print('split_text: ', split_text)

    # Make the drawing
    position = [5, 0]
    rotation_degree = random.uniform(0, 45)
    if len(split_text) == 1:
        draw.text(position, '\n'.join(split_text), (255, 255, 255),
                            font=font)
    else:
        for line in split_text:
            draw.text(position, '\n'.join(line), (255, 255, 255),
                                font=font)
            position[1] += draw.textsize('\n'.join(line), font=font)[1] + 16
    rotated_text = text_img.rotate(rotation_degree, expand=1)
    img.resize(rotated_text.size)
    img.paste(rotated_text)
    return img
