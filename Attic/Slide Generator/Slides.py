#!/usr/bin/python
# -*- coding: utf8 -*-

# Dependencies:
# - PyYAML, <http://pyyaml.org/>
# - flickrpy, <http://code.google.com/p/flickrpy/>
# - Python Imaging Library, <http://www.pythonware.com/products/pil/>


from __future__ import division, with_statement
import Image, ImageChops, ImageDraw, ImageFont
import flickr, yaml
import os, re, sys, urllib


def drawTitle(settings, slide, title, padding = 15):
    (draw, size) = (ImageDraw.Draw(slide), 40)
    color = settings[u'Text color']
    
    while True:
        font = ImageFont.truetype(settings[u'Font'], size)
        (width, height) = draw.textsize(title, font = font)
        
        if abs(width - settings[u'Width']) < padding:
            draw.text((3, 3), title, fill = color[u'Background'], font = font)
            draw.text((0, 0), title, fill = color[u'Foreground'], font = font)
            return slide
        
        size += 1 if width < settings[u'Width'] else -1


def extractSlides(slides):
    searchTextPattern = ur'[*]([^*]+)[*]'
    (titles, searchTerms) = ([], [])
    
    for slide in slides:
        (searchText,) = re.findall(searchTextPattern, slide)
        title = re.sub(searchTextPattern, ur'\1', slide)
        
        titles.append(title)
        searchTerms.append(searchText)
    
    return (titles, searchTerms)


def getUrl(photo):
    try:
        return photo.getURL(urlType = u'source')
    except flickr.FlickrError:
        return u'http://static.flickr.com/%s/%s_%s.jpg' \
            % (photo.server, photo.id, photo.secret)


def getUrls(text, limit = 20):
    print(u'Searching Flickr for "%s"...' % text)
    return map(getUrl, flickr.photos_search(text = text, per_page = limit))


def makeSlide(settings, image):
    (WIDTH, HEIGHT) = (settings[u'Width'], settings[u'Height'])
    (width, height) = image.size
    
    newHeight = height * WIDTH // width
    newWidth = width * HEIGHT // height
    
    if newHeight <= HEIGHT:
        newWidth = WIDTH
    elif newWidth <= WIDTH:
        newHeight = HEIGHT
    
    x = (WIDTH - newWidth) // 2
    y = (HEIGHT - newHeight) // 2
    
    slide = image.resize((newWidth, newHeight), Image.ANTIALIAS)
    slide = slide.crop((0, 0, WIDTH, HEIGHT))
    slide = ImageChops.offset(slide, x, y)
    
    draw = ImageDraw.Draw(slide)
    color = settings[u'Text color'][u'Background']
    
    if newHeight < HEIGHT:
        draw.rectangle([(0, 0), (WIDTH, y)], fill = color)
        draw.rectangle([(0, y + newHeight), (WIDTH, HEIGHT)], fill = color)
    elif newWidth < WIDTH:
        draw.rectangle([(0, 0), (x, HEIGHT)], fill = color)
        draw.rectangle([(x + newWidth, 0), (WIDTH, HEIGHT)], fill = color)
    
    return slide


def makeSlides(config):
    flickr.API_KEY = config[u'Flickr'][u'API key']
    flickr.API_SECRET = config[u'Flickr'][u'API secret']
    
    (titles, searchTerms) = extractSlides(config[u'Slides'])
    (searchedText, slideNumber) = ({}, 1)
    
    mainTitle = config[u'Title']
    settings = config[u'Settings']
    color = settings[u'Text color']
    
    for name in color:
        color[name] = tuple(color[name])
    
    if not os.path.exists(mainTitle):
        os.mkdir(mainTitle)
    
    for title, searchText in zip(titles, searchTerms):
        print(u'Creating slide %i...' % slideNumber)
        
        if searchText not in searchedText:
            urls = getUrls(searchText)
            
            if len(urls) == 0:
                print(u'No images found for "%s"' % searchText)
                continue
            
            searchedText[searchText] = urls
        
        if len(searchedText[searchText]) == 0:
            print(u'No more images for "%s"' % searchText)
            continue
        
        url = searchedText[searchText].pop()
        print(u'Downloading image from <%s>...' % url)
        
        (imageFileName, headers) = urllib.urlretrieve(url)
        simpleSlide = makeSlide(settings, Image.open(imageFileName))
        slide = drawTitle(settings, simpleSlide, title)
        
        slideFileName = u'%s/%i.%s' % (mainTitle, slideNumber, settings[u'Format'])
        slide.save(slideFileName)
        print(u'Saved as "%s".\n' % slideFileName)
        
        slideNumber += 1


def main(args):
    if len(args) != 2:
        print(u'Usage: <configuration file>')
    else:
        makeSlides(yaml.load(file(args.pop())))
    
    return 0


if __name__ == u'__main__':
    sys.exit(main(sys.argv))
