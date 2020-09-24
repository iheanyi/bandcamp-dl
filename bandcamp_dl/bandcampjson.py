import re
import logging

import demjson


class BandcampJSON:
    def __init__(self, body, debugging: bool=False):
        self.body = body
        self.json_data = dict()

        if debugging:
            logging.basicConfig(level=logging.DEBUG)

    def generate(self):
        """Grabbing needed data from the page"""
        self.get_pagedata()
        self.get_js()
        self.js_to_json()
        return self.json_data

    def get_pagedata(self):
        logging.debug("Grab pagedata JSON..")
        pagedata = self.body.find('div', {'id': 'pagedata'})['data-blob']
        self.json_data['pagedata'] = pagedata

    def get_js(self):
        """Get <script> element containing the data we need and return the raw JS"""
        logging.debug("Grabbing embedded script..")
        self.js_data = self.body.find("script", {"type": "application/json+ld"}).string

    def js_to_json(self):
        """Convert JavaScript dictionary to JSON"""
        logging.debug(" Converting JS to JSON..")
        # Decode with demjson first to reformat keys and lists
        decoded_js = demjson.decode(self.js_data)
        # Encode to make valid JSON, add to list of JSON strings
        self.json_data['target'] = demjson.encode(decoded_js)
