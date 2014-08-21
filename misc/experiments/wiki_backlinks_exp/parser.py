import random
import time
import pickle
import os
import shutil


class Parser:

    """ Virtual class for parsers.

    If you want to create your parser, you should override
    get_response and get_raw_data functions

    Interface:
    parse -- get data
    parse_fresh -- get fresh data
    """

    init_dir = "parser"

    def __init__(self):
        if not os.path.exists(self.init_dir):
            raise RuntimeError("init dir not exists: "+ self.init_dir )

    def parse(self, query):
        """ Parse data for query.

        Works in 3 steps:
        getting data from server. Calls get_response. Saves data to 'response' file
        processing data. Calls get_raw_data. Saves data to 'raw_data' file. (Date, Value) format
        normalizing data. Calls get_data. Saves data to 'data' file.
        :param query: key word to search
        :return: None
        """
        dir_name = os.path.join(self.init_dir, query)
        if os.path.exists(dir_name):
            response = None
            raw_data = None
            data = None

            if not os.path.exists(os.path.join(dir_name, "response")):
                response = self.get_response(query)
                response_file = open(os.path.join(dir_name, "response"), 'wb')
                pickle.dump(response, response_file)
                response_file.close()
            else:
                response_file = open(os.path.join(dir_name, "response"), 'rb')
                response = pickle.load(response_file)

            if not os.path.exists(os.path.join(dir_name, "raw_data")):
                raw_data = self.get_raw_data(response)
                raw_data_file = open(os.path.join(dir_name, "raw_data"), 'wb')
                pickle.dump(raw_data, raw_data_file)
                raw_data_file.close()
            else:
                raw_data_file = open(os.path.join(dir_name, "raw_data"), 'rb')
                raw_data = pickle.load(raw_data_file)

            if not os.path.exists(os.path.join(dir_name, "data")):
                data = self.get_data(raw_data)
                data_file = open(os.path.join(dir_name, "data"), 'wb')
                pickle.dump(data, data_file)
                data_file.close()
            else:
                data_file = open(os.path.join(dir_name, "data"), 'rb')
                data = pickle.load(data_file)
        else:
            self.parse_fresh(query)

    def parse_fresh(self, query):
        dir_name = os.path.join(self.init_dir, query)
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.mkdir(dir_name)

        response = self.get_response(query)
        response_file = open(os.path.join(dir_name, "response"), 'wb')
        pickle.dump(response, response_file)
        response_file.close()

        raw_data = self.get_raw_data(response)
        raw_data_file = open(os.path.join(dir_name, "raw_data"), 'wb')
        pickle.dump(raw_data, raw_data_file)
        raw_data_file.close()

        data = self.get_data(raw_data)
        data_file = open(os.path.join(dir_name, "data"), 'wb')
        pickle.dump(data, data_file)
        data_file.close()

    def get_response(self, query):
        """ Get data from web
        :param query: name or tag to search
        :return: raw responses from web server
        """
        raise NotImplementedError()

    def get_raw_data(self, response):
        """ Get data from response
        :param response: web data (json, html page, etc)
        :return: raw data, list of pairs (date, value)
        """
        raise NotImplementedError()

    def get_data(self, raw_data):
        """ Normalize raw data
        :param raw_data: raw data, list of (date, value) tuples
        :return: normalized data, list of (date, normalized value) tuples
        """
        data = [(x, y) for x, y in sorted(raw_data, key=(lambda v: v[0]))]
        min_val = min(data, key=(lambda v: v[1]))[1]
        max_val = max(data, key=(lambda v: v[1]))[1]
        if max_val == min_val:
            return [(x, 0.5) for x, _ in data]
        return [(x, float(y - min_val)/(max_val - min_val)) for x, y in data]

    def sleep(self, min_time, max_time):
        time.sleep(random.randint(5, 10))