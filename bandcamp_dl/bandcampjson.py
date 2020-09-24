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
        self.regex = re.compile(r"(?<=var\s" + target + "\s=\s).*?(?=};)", re.DOTALL)
        self.target = target
        self.js_to_json()
        return self.json_data

    def get_pagedata(self):
        logging.debug("Grab pagedata JSON..")
        pagedata = self.body.find('div', {'id': 'pagedata'})['data-blob']
        self.json_data['pagedata'] = pagedata

    def get_js(self):
        """Get <script> element containing the data we need and return the raw JS"""
        logging.debug("Grabbing embedded script..")
        self.js_data = self.body.find("script", {"src": False}, text=re.compile(self.target)).string
        self.extract_data(self.js_data)

    def extract_data(self, js: str):
        """Extract values from JS dictionary

        :param js: Raw JS
        """
        self.js_data = self.regex.search(js).group().replace('" + "', '') + "}"

    def js_to_json(self):
        """Convert JavaScript dictionary to JSON"""
        logging.debug(" Converting JS to JSON..")
        # Decode with demjson first to reformat keys and lists
        decoded_js = demjson.decode(self.js_data)
        # Encode to make valid JSON, add to list of JSON strings
        self.json_data['target'] = demjson.encode(decoded_js)
