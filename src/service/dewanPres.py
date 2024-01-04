import os
import requests
import html_to_json

from icecream import ic
from pyquery import PyQuery
from time import time, sleep
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

        self.__MAIN_DOMAIN = 'dewanpers.or.id'
        self.__MAIN_URL = 'https://dewanpers.or.id/data/organisasi'


    def extract_data(self, url: str):
        response = requests.get(url)
        html = PyQuery(response.text)

        TIMES = self.__parser.ex(html=html.find('div.hk-grid-widget.post-grid-widget'), selector="time")
        FOOTER = self.__parser.ex(html=html, selector='#frontpage-area_d_1 div.flush-columns')


        ic(len(self.__parser.ex(html=html, selector='div.content-block-row p:nth-child(2) a')))


        article = {
            "features": [],
            "banners": [
                {
                    "title": PyQuery(banner).text(),
                    "updated": PyQuery(TIMES[index]).attr('title') if index < len(TIMES) else None,
                    "url": self.__parser.ex(html=banner, selector="a").attr('href')
                } for index, banner in enumerate(html.find('div.hk-grid-widget.post-grid-widget h4'))
            ],
            "relevants":[
                {
                    "title": self.__parser.ex(html=meta, selector='h4').text(),
                    "url": self.__parser.ex(html=meta, selector='h4 a').attr('href'),
                    "posted": self.__parser.ex(html=meta, selector='time').attr('title'),
                    "image_url": self.__parser.ex(html=meta, selector='img').attr('data-src'),
                } for meta in self.__parser.ex(html=FOOTER, selector='div.content-block.no-highlight')
            ],
        }

        for index, feature in enumerate(html.find('div.content-block-content.content-block-content-hasicon')):
            url_meta = PyQuery(self.__parser.ex(html=html, selector='div.content-block-row p:nth-child(2) a')[index]).attr('href')
            response = requests.get(url_meta)
            METADATA = PyQuery(response.text)

            article["features"].append(
                    {
                        "domain": PyQuery(self.__parser.ex(html=html, selector='div.content-block-row p:nth-child(2) a')[index]).attr('href').split('/')[2],
                        "descriptions": self.__parser.ex(html=feature, selector='p').text(),
                        "url": PyQuery(self.__parser.ex(html=html, selector='div.content-block-row p:nth-child(2) a')[index]).attr('href'),
                        "metadata": {
                            "title": self.__parser.ex(html=METADATA, selector='#loop-meta  h1').text(),
                            "author": self.__parser.ex(html=METADATA, selector='span.entry-author > a').text(),
                            "created_time": self.__parser.ex(html=METADATA, selector='div.entry-byline-block.entry-byline-date > time').text(),
                            "image": self.__parser.ex(html=METADATA, selector='figure.wp-block-image.size-large > img').attr('data-src'),
                            "path_data_raw": "(Butuh disesuaikan)",
                            "sub_title": self.__parser.ex(html=METADATA, selector='div.entry-content p:nth-child(3) > strong').text(),
                            "content": self.__parser.ex(html=METADATA, selector='div.entry-content p').text(),
                            "tables": [
                                {
                                    METADATA.find('figure.wp-block-table > table tr:first-child > td:first-child').text(): self.__parser.ex(html=data, selector='td:first-child').text(),
                                    METADATA.find('figure.wp-block-table > table tr:first-child > td:nth-child(2)').text(): self.__parser.ex(html=data, selector='td:nth-child(2)').text(),
                                    METADATA.find('figure.wp-block-table > table tr:first-child > td:last-child').text(): self.__parser.ex(html=data, selector='td:last-child').text(),
                                } for data in METADATA.find('figure.wp-block-table > table tr')[1:]
                            ]
                        }
                    } 
                )

        return article
    
    
    def non_documentation(self, url: str) -> dict:
        response = requests.get('https://www.pwi.or.id/')
        
        html = PyQuery(response.text)
        
        article = {
            "domain": url.split('/')[2],
            "description": html.find('meta[name="description"]').attr('content'),
            "keyword": html.find('meta[name="keywords"]').attr('content'),
            "author": html.find('meta[name="author"]').attr('content'),
        }
        
        return article
        

    def main(self):

        response: Response = requests.get(self.__MAIN_URL)
        ic(response)
        html = PyQuery(response.text)

        for content in html.find(selector='#datatable1 tbody tr'):

            results = {
                "domain": self.__MAIN_DOMAIN,
                "crawling_time": str(datetime.now()),
                "crawling_time_epoch": int(time()),
                "attributes": {
                    "name": self.__parser.ex(html=content, selector='td:nth-child(3)').text(),
                    "url": self.__parser.ex(html=content, selector='td:last-child').text(),
                    "address": self.__parser.ex(html=content, selector='td:nth-child(4)').text()
                },
                
            }

            match results["attributes"]["name"]:

                case 'PEWARTA FOTO INDONESIA':
                    results.update({
                        "article": self.extract_data(url=self.__parser.ex(html=content, selector='td:last-child').text())
                    })
                    
                case _:
                    results.update({
                        "article": self.non_documentation(url=self.__parser.ex(html=content, selector='td:last-child').text())
                    })
                    

            self.__file.write_json(path=f'private/{vname(results["attributes"]["name"])}.json', content=results)
            ic("done")
            
