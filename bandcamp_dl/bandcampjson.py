import re
import logging

import demjson


class BandcampJSON:
    def __init__(self, body, debugging: bool=False):
        self.body = body
        self.json_data = []

        if debugging:
            logging.basicConfig(level=logging.DEBUG)

    def generate(self):
        """Grabbing needed data from the page"""
        self.get_pagedata()
        self.get_js()
        return self.json_data

    def get_pagedata(self):
        logging.debug(" Grab pagedata JSON..")
        pagedata = self.body.find('div', {'id': 'pagedata'})['data-blob']
        self.json_data.append(pagedata)

    def get_js(self):
        """Get <script> element containing the data we need and return the raw JS"""
        logging.debug(" Grabbing embedded scripts..")
        embedded_scripts_raw = [self.body.find("script", {"type": "application/ld+json"}).string]
        for script in self.body.find_all('script'):
            try:
                album_info = script['data-tralbum']
                embedded_scripts_raw.append(album_info)
            except:
                continue
        for script in embedded_scripts_raw:
            js_data = self.js_to_json(script)
            self.json_data.append(js_data)

    def js_to_json(self, js_data):
        """Convert JavaScript dictionary to JSON"""
        logging.debug(" Converting JS to JSON..")
        # Decode with demjson first to reformat keys and lists
        decoded_js = demjson.decode(js_data)
        # Encode to make valid JSON, add to list of JSON strings
        return demjson.encode(decoded_js)
        
