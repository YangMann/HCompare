import re

__author__ = 'Yang ZHANG'
import difflib
import requests
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit


class HCompare(object):
    def __init__(self, *url):
        self.__html_diff = difflib.HtmlDiff()
        self.__n = len(url)
        self.__url = url
        self.__r = []
        self.__bs = []
        self.__nav = []
        self.__topic = []

    def set_n(self, n):
        self.__n = n

    def set_url(self, *url):
        self.set_n(len(url))
        self.__url = url

    def compare(self):
        self.__r = []
        self.__bs = []
        if self.__n > 2:
            print "Comparison of more than 2 HTML pages is not supported. "
            return
        for i_url in self.__url:
            self.__r.append(requests.get(i_url))
        if self.__n == 2:
            for i in range(len(self.__r)):
                self.__bs.append(BeautifulSoup(self.__r[i].text).prettify())
            return self.__html_diff.make_table(self.__bs[0].split("\n"),
                                               self.__bs[1].split("\n"),
                                               self.__url[0], self.__url[1], True, 2)

    def spec_compare(self):
        self.__r = []
        self.__bs = []
        self.__nav = []
        self.__topic = []
        diff_tocnav = (False, {})
        diff_topic = (False, {})
        if self.__n > 2:
            print "Comparison of more than 2 HTML pages is not supported. "
            return
        for i_url in self.__url:
            self.__r.append(requests.get(i_url))
        if self.__n == 2:
            for i in range(len(self.__r)):
                self.__bs.append(BeautifulSoup(self.__r[i].text))

        for i in range(len(self.__bs)):
            self.__nav.append(self.__bs[i].find("div", id="tocnav"))
            for x in self.__bs[i].find_all("div", class_="topic"):
                self.__topic.append(x)

        # div#tocnav
        if len(self.__nav) != 2:
            print "Nah __nav"
            diff_tocnav = (True, '[ERROR] One of the pages has multiple "#tocnav"s. ')
        else:
            diff_bs = BeautifulSoup(self.__html_diff.make_table(self.__nav[0].prettify().split("\n"),
                                                                self.__nav[1].prettify().split("\n"),
                                                                self.__url[0], self.__url[1], True, 0))
            if not (len(diff_bs.find_all("td")) == 6 and len(
                    diff_bs.find_all(text=re.compile("No Differences Found")))):
                tag_list1 = diff_bs.select("tr > td:nth-of-type(3)")
                tag_list2 = diff_bs.select("tr > td:nth-of-type(6)")
                # print re.search(r'id="(.*)"', str(text_list), re.M | re.I).group(1)
                text1 = ''
                for t in tag_list1:
                    if t.string is not None:
                        text1 += t.string
                print text1
                print re.findall(re.compile('<([a-z]+).id="([^"]+)"|<([a-z]+).class="([^"]+)"|<([a-z]+).class="([^"]+)".id="([^"]+)"'), text1)
                text2 = ''
                for t in tag_list2:
                    if t.string is not None:
                        text2 += t.string
                print re.findall(r'id="([^"]+)"', text2)

        # div.topic
        if len(self.__topic) != 2:
            print "Nah __topic"
        else:
            diff_bs = BeautifulSoup(self.__html_diff.make_table(self.__topic[0].prettify().split("\n"),
                                                                self.__topic[1].prettify().split("\n"),
                                                                self.__url[0], self.__url[1], True, 2))
            # print self.__html_diff.make_table(self.__topic[0].prettify().split("\n"),
            #                                   self.__topic[1].prettify().split("\n"),
            #                                   self.__url[0], self.__url[1], True, 2)
            return self.__html_diff.make_table(self.__topic[0].prettify().split("\n"),
                                               self.__topic[1].prettify().split("\n"),
                                               self.__url[0], self.__url[1], True, 2)


def main():
    # h_compare = HCompare("http://tnstage.redmond.corp.microsoft.com/en-US/library/dn497701(VS.111).aspx",
    # "http://technet.microsoft.com/en-us/library/dn497701")
    h_compare = HCompare("http://sandboxmsdnstage.redmond.corp.microsoft.com/en-us/library/dn518133.aspx",
                         "http://msdn.microsoft.com/en-us/library/f1535029-05e5-4bc5-bc6d-84920b1be2a7")
    h_compare.compare()
    h_compare.spec_compare()


if __name__ == '__main__':
    main()
