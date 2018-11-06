
import os
import re
import xml.etree.ElementTree as ET

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty
from kivy.uix.popup import Popup


class KmlColor():
    def __init__(self):
        pass

    def convert(self, file):
        namespace = 'http://www.opengis.net/kml/2.2'
        ET.register_namespace('', namespace)
        available_colors = ['green', 'red', 'yellow', 'blue',
                            'purple', 'pink', 'orange', 'brown']

        found_colors = []
        try:
            xml_content = ET.parse(file)
        except:
            return (False, 'Invalid file')
        root = xml_content.getroot()

        # get found colors list from xml
        for doc in root.getchildren():
            for folder in doc.getchildren():
                if 'Folder' in folder.tag:
                    for place in folder.getchildren():
                        style = place.findall('{%s}styleUrl' % namespace)
                        for child in style:
                            color_text = child.text
                            color = \
                                ''.join(re.findall('#icon-[0-9]+-([A-Z0-9]+)',
                                                   color_text))
                            if color:
                                found_colors.append(color)
        found_colors = set(found_colors)

        if not found_colors:
            return (False, 'No colors to replace')

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
                            color = \
                                ''.join(re.findall('#icon-[0-9]+-([A-Z0-9]+)',
                                                   color_text))
                            if color:
                                child.text = \
                                    '#placemark-{}'.format(replace_dict[color])

        xml_content.write(file)
        return (True, None)


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    default_path = "/mnt/sdcard/" if os.path.isdir("/mnt/sdcard/") else "~"


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Root(FloatLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    show_convert_button = BooleanProperty(False)
    file_to_convert = StringProperty()
    file_converted = BooleanProperty(False)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.choose_file, cancel=self.dismiss_popup)
        self.file_converted = False
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def convert_file(self):
        kml_color = KmlColor()
        converted, error = kml_color.convert(self.file_to_convert)
        if error:
            self.file_converted = BooleanProperty(False)
        else:
            self.file_converted = BooleanProperty(True)

    def choose_file(self, path, filename):
        self.file_to_convert = os.path.join(path, filename[0])
        self.dismiss_popup()
        self.show_convert_button = BooleanProperty(True)


class Converter(App):
    pass


Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)


if __name__ == '__main__':
    Converter().run()
