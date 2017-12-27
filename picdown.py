# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:48:23
# @modify date 2017-12-25 05:31:00
# @desc [原图链接获取]

import datetime
import json
import os
import re
import time
from multiprocessing.dummy import Pool

import requests


class mdpr(object):
    def __init__(self):
        self.mdpr = "https://mdpr.jp"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        }

    def __imgCenter(self, url):
        if "photo" in url:
            photourl = url
        elif "fashion" in url:
            photourl = url
        else:
            if "/amp" in url:
                url = url.replace("/amp", "")
            urlpart = url.split("/")
            url = self.mdpr + '/' + urlpart[3] + '/' + urlpart[-1]
            news_index = requests.get(
                url, timeout=30, headers=self.headers).text
            img_center_rule = r'<a data-click="head_img_link" data-pos="1" href="(.*?)" .*?>'
            img_center = re.findall(img_center_rule, news_index, re.S | re.M)
            photourl = self.mdpr + ''.join(img_center)
        return photourl

    def mdprPhotoUrls(self, photourl):
        photo_url = self.__imgCenter(photourl)
        host = self.mdpr
        photo_index = requests.get(
            photo_url, timeout=30, headers=self.headers).text
        photo_urls_rule = r'<div class="list-photo clearfix" data-track="photo_img_list">(.*?)</div>'
        photo_list = re.findall(photo_urls_rule, photo_index, re.S | re.M)
        if len(photo_list) == 0:
            photo_urls_rule = r'<ul class="group-ph__list" data-click="right_photo_ranking">(.*?)</ul>'
            photo_list = re.findall(photo_urls_rule, photo_index, re.S | re.M)
        photo_url_rule = r'href="(.*?)"'
        photo_uri = re.findall(
            photo_url_rule, str(photo_list), re.S | re.M)
        photo_urls = [host + p for p in photo_uri]
        return photo_urls

    def __getpic(self, photourls):
        photo_urls = photourls
        photo_rule = r'<figure class="main-photo f9em">(.*?)</figure>'
        origin_photo_rule = r'src="(.*?)"'
        photo_index = requests.get(
            photo_urls, timeout=30, headers=self.headers).text
        photo_part = re.findall(photo_rule, photo_index, re.S | re.M)
        origin_photo_url = re.findall(
            origin_photo_rule, str(photo_part), re.S | re.M)
        return origin_photo_url

    def mdprOriginUrl(self, photourls):
        photo_urls = photourls
        thread = len(photo_urls) / 4
        if thread < 4:
            thread = 4
        if thread > 10:
            thread = 8
        pool = Pool(thread)
        origin_urls = pool.map(self.__getpic, photo_urls)
        pool.close()
        pool.join()
        origin_urls = [''.join(o) for o in origin_urls if o]
        return origin_urls


class oricon(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        }
        self.host = "https://www.oricon.co.jp"

    def __geturl(self, url):
        url = self.host + url
        photo_main_rule = r'<div class="main_photo_image">.*?<img.*?src="(.*?)".*?>.*?</div>'
        photo_index = requests.get(url, timeout=30, headers=self.headers).text
        photo_body = re.findall(photo_main_rule, photo_index, re.S | re.M)
        return ''.join(photo_body)

    def oriconPhotoList(self, url):
        if "full" not in url:
            url = url + "photo/1/"
        else:
            url = url.replace("full/", "photo/1/")
        photo_thumb_body_rule = r'<div class="photo_thumbs" .*?>(.*?)</div>'
        photo_index = requests.get(url, timeout=30, headers=self.headers).text
        photo_body = re.findall(photo_thumb_body_rule,
                                photo_index, re.S | re.M)
        if len(photo_body) == 0:
            photo_singel_rule = r'<div class="centering-image">.*?<img.*?src="(.*?)".*?>.*?</div>'
            photo_urls = re.findall(
                photo_singel_rule, photo_index, re.S | re.M)
            return photo_urls
        photo_body_rule = r'<a.*?href="(.*?)".*?>.*?</a>'
        photo_url = re.findall(photo_body_rule, str(photo_body), re.S | re.M)
        thread = len(photo_url) / 4
        if thread <= 4:
            thread = 4
        if thread >= 10:
            thread = 8
        pool = Pool(thread)
        photo_urls = pool.map(self.__geturl, photo_url)
        pool.close()
        pool.join()
        return photo_urls

    def __oriconCenterEnter(self, url):
        photo_index = requests.get(url, timeout=30, headers=self.headers).text
        photo_pre_rule = r'<li class="item">.*?<a href="(.*?)" class="inner">.*?<p class="item-image">'
        photo_list = re.findall(photo_pre_rule, photo_index, re.S | re.M)
        photo_first = self.host + photo_list[0]
        return photo_first

    def oriconPhotoCenter(self, url):
        nums = r'[0-9]+'
        if len(re.findall(nums, url)) < 2:
            photo_url = self.__oriconCenterEnter(url)
        else:
            photo_url = url
        photo_index = requests.get(
            photo_url, timeout=30, headers=self.headers).text
        photo_urls_rule = r'<div class="photo_slider" id="photo_slider_box">(.*?)</div>'
        photo_list = re.findall(photo_urls_rule, photo_index, re.S | re.M)
        photo_url_rule = r'data-original="(.*?)"'
        photo_uri = re.findall(
            photo_url_rule, str(photo_list), re.S | re.M)
        photo_urls = [p.replace("img100", "img660") for p in photo_uri]
        return photo_urls

    def oriconPhotoMode(self, url):
        if "news" in url:
            photourls = self.oriconPhotoList(url)
        else:
            photourls = self.oriconPhotoCenter(url)
        return photourls


class ameblo(object):
    def __init__(self):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }

    def amebloImgUrl(self, url):
        owner = url.split("/")[3]
        entry = url.split("-")[-1].split(".")[0]
        ameblo_api = "https://blogimgapi.ameba.jp/read_ahead/get.jsonp?"
        img_host = "http://stat.ameba.jp"
        params = {"ameba_id": owner, "entry_id": entry,
                  "old": "true", "sp": "false"}
        r = requests.get(ameblo_api, headers=self.headers, params=params)
        ameblo_image_callback = r.text
        ameblo_json_str = ameblo_image_callback.replace(
            "Amb.Ameblo.image.Callback(", "").replace(");", "")
        ameblo_dict = json.loads(ameblo_json_str)
        ameblo_img_list = ameblo_dict["imgList"]
        ameblog_img_urls = [img_host + img_list["imgUrl"]
                            for img_list in ameblo_img_list if entry in img_list["pageUrl"]]
        return ameblog_img_urls


class picdown(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}

    def urlCheck(self, url):
        url = url
        mdpr_host = "http[s]?://mdpr.jp/photo.*"
        mdpr_host_other = "http[s]?://mdpr.jp/.*"
        oricon_host = "http[s]?://www.oricon.co.jp/photo.*"
        oricon_host_news = "http[s]?://www.oricon.co.jp/news.*"
        ameblo_host = "http[s]?://ameblo.jp/.*/entry-.*"
        if len(re.findall(mdpr_host, url)) or len(re.findall(mdpr_host_other, url)):
            result = {"site": "mdpr", "url": url}
        elif len(re.findall(oricon_host, url)) or len(re.findall(oricon_host_news, url)):
            result = {"site": "oricon", "url": url}
        elif len(re.findall(ameblo_host, url)):
            result = {"site": "ameblo", "url": url}
        else:
            result = None
        return result

    def photoUrlGet(self, urldict):
        urldict = urldict
        if urldict:
            target_site = urldict["site"]
            target_url = urldict["url"]
            if target_site == "mdpr":
                m = mdpr()
                photo_urls = m.mdprPhotoUrls(target_url)
                result = m.mdprOriginUrl(photo_urls)
            elif target_site == "oricon":
                o = oricon()
                result = o.oriconPhotoMode(target_url)
            elif target_site == "ameblo":
                a = ameblo()
                result = a.amebloImgUrl(target_url)
        else:
            result = None
        return result

    def __download(self, para):
        nums = para[0]
        urls = para[1]
        times = para[2]
        data = requests.get(
            urls, timeout=30, headers=self.headers, stream=True)
        ext = urls.split(".")[-1]
        filename = str(times) + str(nums) + "." + ext
        savepath = os.path.join(times, filename)
        with open(savepath, "wb") as code:
            for chunk in data.iter_content(chunk_size=1024):
                code.write(chunk)

    def photoDownload(self, urls, folder, thread):
        urls = urls
        nums = range(1, len(urls) + 1)
        t = [folder for i in range(0, len(urls))]
        thread = thread / 4
        if thread < 4:
            thread = 4
        if thread > 10:
            thread = 8
        start = time.time()
        os.mkdir(folder)
        pool = Pool(thread)
        pool.map(self.__download, zip(nums, urls, t))
        pool.close()
        pool.join()
        end = time.time()
        s = int(end - start)
        formats = str(datetime.timedelta(seconds=s))
        return formats


def main():
    p = picdown()
    url = raw_input("Enter a link or file:")
    folder = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    print "[1]Checking links..."
    urldict = p.urlCheck(url)
    print "[2]Getting image links..."
    urls = p.photoUrlGet(urldict)
    print "[3]Downloading..."
    thread = len(urls)
    sec = p.photoDownload(urls, folder, thread)
    print "Lasted {} seconds".format(sec)


if __name__ == '__main__':
    main()
