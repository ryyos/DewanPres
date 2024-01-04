import os
import requests

from icecream import ic
from pyquery import PyQuery
from time import time
from datetime import datetime
from requests import Response

from src.utils.corrector import vname
from src.utils.fileIO import File
from src.utils.logs import logger
from src.utils.parser import Parser

class DewanPres:
    def __init__(self) -> None:
        
        self.__file = File()
        self.__parser = Parser()

        self.__MAIN_URL = 'https://dewanpers.or.id/data/organisasi'


    def main(self):

        response: Response = requests.get(self.__MAIN_URL)
        ic(response)
        self.__file.write_str(path='private/test.html', content=response.text)