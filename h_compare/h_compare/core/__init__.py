import re
import json

__author__ = 'Yang ZHANG'
import difflib
import requests
from bs4 import BeautifulSoup


def extract_tag_attr(wrapped_tag_list, id_filter=None, class_filter=None):
    """
    Extract tag name, id and class name from a HTML string in HTML diff table.

    For <img> tags, alt, title and image file name are also extracted

    :param wrapped_tag_list: HTML string from HTML diff table
    :param id_filter: specify certain id(s) to be filtered out
    :param class_filter: specify certain class names to be filtered out
    :return: list of dict [{'tag': [], 'id': [], 'class': []}]
    """
    if not class_filter:
        class_filter = []

    if not id_filter:
        id_filter = []

    text = ''

    for t in wrapped_tag_list:
        if t.string is not None:
            text += t.string

    tmp_list = re.findall(re.compile('<[^/].+?>'), text)
    out_list = []

    for t in tmp_list:

        add_flag = True

        if id_filter is not None:
            for i in id_filter:
                if len(re.findall(re.compile('id=["\']([^"\']*%s[^"\']*)["\']' % i), t)) > 0:
                    add_flag = False

        if class_filter is not None:
            for i in class_filter:
                if len(re.findall(re.compile('class=["\']([^"\']*%s[^"\']*)["\']' % i), t)) > 0:
                    add_flag = False

        tag_ = re.findall(re.compile('<([a-z1-6]+).'), t)
        id_ = re.findall(re.compile('id=["\']([^"\']+)["\']'), t)
        class_ = re.findall(re.compile('class=["\']([^"\']+)["\']'), t)

        if len(id_) == 0 and len(class_) == 0:
            add_flag = False

        out = {"tag": tag_, "id": id_, "class": class_}

        if tag_[0] == "img":
            add_flag = True
            out["alt"] = re.findall(re.compile('alt=["\']([^"\']+)["\']'), t)
            out["title"] = re.findall(re.compile('title=["\']([^"\']+)["\']'), t)
            src = re.findall(re.compile('src=["\']([^"\']+)["\']'), t)[0]
            out["file"] = src[src.rindex("/") + 1:]

        if add_flag:
            out_list.append(out)

    return out_list


def diff(a, b):
    b = set(b)
    return [aa for aa in a if aa not in b]


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
                                               self.__url[0], self.__url[1], True, 0)

    def spec_compare(self):
        self.__r = []
        self.__bs = []
        self.__nav = []
        self.__topic = []
        diff_tocnav = (False, [])
        diff_topic = (False, [])
        diff_headings = (False, [])

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
            diff_tocnav = (True, '[ERROR] One of the pages has multiple "#tocnav"s. ')

        else:
            diff_bs = BeautifulSoup(self.__html_diff.make_table(self.__nav[0].prettify().split("\n"),
                                                                self.__nav[1].prettify().split("\n"),
                                                                self.__url[0], self.__url[1], True, 0))

            if not (len(diff_bs.find_all("td")) == 6 and len(
                    diff_bs.find_all(text=re.compile("No Differences Found")))):
                tag_list1 = diff_bs.select("tr > td:nth-of-type(3)")
                tag_list2 = diff_bs.select("tr > td:nth-of-type(6)")
                diff_tocnav = (True, [extract_tag_attr(tag_list1), extract_tag_attr(tag_list2)])

        # div.topic
        if len(self.__topic) % 2 != 0:
            diff_topic = (True, '[ERROR] The number of ".topic" from the two pages doesn\'t match. ')

        else:
            # headings
            headings = [[], []]

            for n in range(2):
                tmp = self.__topic[n]
                for i in range(1, 7):
                    for j in tmp.find_all("h%d" % i):
                        headings[n].append(("h%d" % i, j.text.strip()))

            diff_headings = (
                not (len(diff(headings[0], headings[1])) == 0 and len(diff(headings[1], headings[0])) == 0),
                [diff(headings[0], headings[1]), diff(headings[1], headings[0])]
            )

            # topic
            diff_bs = BeautifulSoup(self.__html_diff.make_table(self.__topic[0].prettify().split("\n"),
                                                                self.__topic[1].prettify().split("\n"),
                                                                self.__url[0], self.__url[1], True, 0))

            if not (len(diff_bs.find_all("td")) == 6 and len(
                    diff_bs.find_all(text=re.compile("No Differences Found")))):
                tag_list1 = diff_bs.select("tr > td:nth-of-type(3)")
                tag_list2 = diff_bs.select("tr > td:nth-of-type(6)")
                diff_topic = (
                    True, [extract_tag_attr(tag_list1, class_filter=["LW_CollapsibleArea", "sectionblock", "sub"]),
                           extract_tag_attr(tag_list2, class_filter=["LW_CollapsibleArea", "sectionblock", "sub"])])

        if diff_tocnav[0]:
            diff_tocnav = diff_tocnav[1]
        else:
            diff_tocnav = False

        if diff_headings[0]:
            diff_headings = diff_headings[1]
        else:
            diff_headings = False

        if diff_topic[0]:
            diff_topic = diff_topic[1]
        else:
            diff_topic = False

        return {"diff_tocnav": diff_tocnav, "diff_headings": diff_headings, "diff_topic": diff_topic}


def main():
    # h_compare = HCompare("http://tnstage.redmond.corp.microsoft.com/en-US/library/dn497701(VS.111).aspx",
    # "http://technet.microsoft.com/en-us/library/dn497701")
    h_compare = HCompare("http://sandboxmsdnstage.redmond.corp.microsoft.com/en-us/library/dn518133.aspx",
                         "http://msdn.microsoft.com/en-us/library/f1535029-05e5-4bc5-bc6d-84920b1be2a7")
    h_compare.compare()
    result = h_compare.spec_compare()
    print result


if __name__ == '__main__':
    main()
