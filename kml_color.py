#!/usr/bin/env python3

import sys
import re
import xml.etree.ElementTree as ET


namespace = 'http://www.opengis.net/kml/2.2'
ET.register_namespace('', namespace)
available_colors = ['green', 'red', 'yellow', 'blue',
                    'purple', 'pink', 'orange', 'brown']

found_colors = []
try:
    e = ET.parse(sys.argv[1])
except:
    print('Invalid input file: %s' % sys.argv[1])
    sys.exit(1)
root = e.getroot()

# get found colors list from xml
for doc in root.getchildren():
    for folder in doc.getchildren():
        if 'Folder' in folder.tag:
            for place in folder.getchildren():
                style = place.findall('{%s}styleUrl' % namespace)
                for child in style:
                    color_text = child.text
                    color = ''.join(re.findall('#icon-[0-9]+-([A-Z0-9]+)',
                                               color_text))
                    if color:
                        found_colors.append(color)
found_colors = set(found_colors)

if not found_colors:
    print('Colors to replace not found in %s' % sys.argv[1])
    sys.exit(0)

# create dictionary for replace found color to the one of available colors
replace_dict = {}
idx = 0
for found_color in found_colors:
    if idx >= len(available_colors):
        idx = 0
    replace_dict[found_color] = available_colors[idx]
    idx += 1

# replace found color to available one in xml
for doc in root.getchildren():
    for folder in doc.getchildren():
        if 'Folder' in folder.tag:
            for place in folder.getchildren():
                style = place.findall('{%s}styleUrl' % namespace)
                for child in style:
                    color_text = child.text
                    color = ''.join(re.findall('#icon-[0-9]+-([A-Z0-9]+)',
                                               color_text))
                    if color:
                        child.text = '#placemark-{color}'.format(color=replace_dict[color])

e.write(sys.argv[1])
print('File converted: %s' % sys.argv[1])
