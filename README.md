# chanomemes
![Do Androids dream of electric memes?](https://cloud.githubusercontent.com/assets/473542/24084419/69dc069e-0cc0-11e7-9c31-dbe037ea39b2.jpg)

*thx [@kalilsn](https://github.com/kalilsn) for the pic*

A Twitter bot that automatically generates memes about Chance the rapper based on interactions with other Twitter users.

## Installation

Requires Python 3.3+. If you've got that, go ahead with the standard operating procedure for Python:

```console
pip install --upgrade -r requirements.txt
```

To do the API stuff, you'll need to add your creds to `bot/secrets.py.example` and rename it to `bot/secrets.py`.

## Scraping the images

To make its memes, the bot randomly selects from a small collection of images of Chance that we scraped from CC-licensed images on Flickr. If you want to re-run our scraper, open a Python interpreter and run the following code from the `bot` directory:

```python
import flickr
flickr.scrape_photos()
```

This will save a big blob of JSON to the file `bot/chance_pics.json`. I keep it in that format (instead of as images) to more easily access image metadata later on.

Since the scraper runs a free-text query against the Flickr API, a lot of the returned images aren't actually of Chance. You can quickly sift through the scraped images and decide which to keep using the following method:

```python
flickr.edit_scraped_photos()
```

This will launch a command-line session, opening each link in your browser 1-by-1 and asking you whether to keep the image or not. All of your approved images will be written to `bot/edited_chance_pics.json`, which is the final file that the bot reads from to source its images.

## Running the bot

The following command will make the bot run in an endless loop:

```console
cd bot
python bot.py
```

The bot makes use of the Twitter streaming API, which creates a generator that you can iterate over endlessly without using much memory. Still, make sure to wrap this in a process manager like [Supervisor](http://supervisord.org/) if you want to gracefully catch errors while running the code on a server.

You can test the meme-generating functionality like so:

```python
import memer

filepath = "path/to/sample/image.png"
text = "Your testing text goes here"

memer.debug_meme(filepath, text)
```

*Be warned: the debugger automatically opens the image your default image viewer.*

## Expected behavior

On Twitter, the bot has been written to:

1. listen for mentions @ our account
2. remove our handle from the text and prep it for memeing
3. paste the text onto a random image of Chance in [Word Art](https://twitter.com/wordartt?lang=en) fashion
4. add some emojis on top, for flavor
5. deliver a notification email to us with the image + suggested reply text, so that we can manually review

There also exists a `reply()` method in `bot/bot.py` that is set up to automatically reply to tweets in step 5 instead of sending a notification. Our team ultimately decided against using it for the sake of curbing abuse, but it shouldn't be too hard to implement. 

If you'd like to edit any of this functionality, you should tweak `bot/bot.py`. These docs mostly exist to help me remember what I did if I ever come back to this code, so I won't go into modification in any detail, but if you [open an issue](https://github.com/jeancochrane/chanomemes/issues) I'd be glad to assist you in adapting this code to for your own project.

## Acknowledgements

I used the following non-standard open source Python libraries to build this bot, and they were lovely to work with:

- [Python Twitter Tools](https://github.com/sixohsix/twitter) - Python wrapper on the Twitter API
- [Requests](http://docs.python-requests.org/en/master/) - HTTP for humans
- [Pillow (PIL fork)](https://github.com/python-pillow/Pillow) - Programmatic imaging magic
- [Wordfilter](https://github.com/dariusk/wordfilter) - Remove slurs from text without even thinking about it

Thanks to the developers on these projects for helping me make my mischief.

## License

Technically released under the MIT License. Do whatever the hell you want with this code and I'll be delighted.
