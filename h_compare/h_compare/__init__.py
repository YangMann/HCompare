__author__ = 't-yaz'
import difflib
import requests
from bs4 import BeautifulSoup


class HCompare(object):
    def __init__(self, *url):
        self.__html_diff = difflib.HtmlDiff()
        self.__n = len(url)
        self.__url = url
        self.__r = []

    def set_n(self, n):
        self.__n = n

    def set_url(self, *url):
        self.set_n(len(url))
        self.__url = url

    def compare(self):
        self.__r = []
        if self.__n > 2:
            print "Comparison of more than 2 HTML pages is not supported. "
            return
        for i_url in self.__url:
            self.__r.append(requests.get(i_url))
        if self.__n == 2:
            return self.__html_diff.make_table(BeautifulSoup(self.__r[0].text).prettify().split("\n"),
                                               BeautifulSoup(self.__r[1].text).prettify().split("\n"),
                                               self.__url[0], self.__url[1], True)


def main():
    h_compare = HCompare("http://tnstage.redmond.corp.microsoft.com/en-US/library/dn497701(VS.111).aspx",
                         "http://technet.microsoft.com/en-us/library/dn497701")
    h_compare.compare()


if __name__ == '__main__':
    main()