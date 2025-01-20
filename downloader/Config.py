import json
import copy

class Config:
    def __init__(self, proxy=None, keyword=None, page_load_timeout=None, browser_driver_path=None, limit=10,
                 output_directory=None, keywords_from_file=None,search_engines = "bing"):
        self.proxy = proxy
        self.keyword = keyword
        self.page_load_timeout = page_load_timeout
        self.browser_driver_path = browser_driver_path
        self.limit = limit
        self.output_directory = output_directory
        self.keywords_from_file = keywords_from_file
        self.search_engines = search_engines

        self.sub_folder = "default"

    @property
    def keyword(self):
        return self._keyword.replace("&", "%26") if self._keyword else None

    @keyword.setter
    def keyword(self, value):
        self._keyword = value

    @property
    def output_directory(self):
        return self._output_directory if self._output_directory else "./download"

    @output_directory.setter
    def output_directory(self, value):
        self._output_directory = value

    # keywords json 解析
    def parse_config(self):
        if self.keywords_from_file is None:
            return [self]
        results = []
        with open('sample_config.json', 'r',encoding='utf-8') as file:
            data = json.load(file)
        for item in data:
            # 深拷贝
            copied_config = copy.deepcopy(self)
            copied_config.keyword = item['keywords']
            copied_config.limit = item['limit']
            copied_config.sub_folder = item['sub_folder']

            results.append(copied_config)
        return results

    def has_proxy(self):
        return self.proxy is not None