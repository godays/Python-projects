#!/usr/bin/env python3

"""Web spy for gitlab"""
import sys

from bs4 import BeautifulSoup
import requests

URL_GITLAB = "https://about.gitlab.com/features/"
PATH_GITLAB_FEATURES = "gitlab_features.html"


class SpyWeb:
    """Spy web class"""

    def __init__(self):
        """initialization"""
        self.av_cnt = 0
        self.n_av_cnt = 0

    @staticmethod
    def get_html_url(url: str):
        """get html file from url"""
        response = requests.get(url)
        return response.text

    @staticmethod
    def get_html_from_file(file_name: str):
        """get html from file"""
        with open(file_name, "r", encoding='utf-8') as fin:
            content = fin.read()
            return content

    def calculate_free_and_non_free_products(self, logging_html, to_save=True):
        """calculate products"""
        logging_soup = BeautifulSoup(logging_html, features="html.parser")
        free_prod_attr = logging_soup.find_all("a",
                                               attrs={"title": "Available in GitLab SaaS Free"}
                                               )
        non_free_prod_attr = logging_soup.find_all("a",
                                                   attrs={"title": "Not available in SaaS Free"}
                                                   )
        free_product_number = len(free_prod_attr)
        non_free_product_number = len(non_free_prod_attr)

        if to_save:
            self.av_cnt = free_product_number
            self.n_av_cnt = non_free_product_number
        return free_product_number, non_free_product_number

    def print_product_info(self):
        """printing results"""
        print("free products:", self.av_cnt)
        print("enterprise products:", self.n_av_cnt)


def process_cli_arguments(arguments):
    """process cmd args"""
    spy_web = SpyWeb()
    if arguments[1] == "gitlab":
        url_site = spy_web.get_html_url(URL_GITLAB)
    else:
        url_site = spy_web.get_html_from_file(PATH_GITLAB_FEATURES)
    spy_web.calculate_free_and_non_free_products(url_site)
    spy_web.print_product_info()


def main():
    """main func"""
    process_cli_arguments(sys.argv)


if __name__ == "__main__":
    main()
