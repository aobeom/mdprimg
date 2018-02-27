# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:48:23
# @modify date 2018-02-24 20:42:35
# @desc [原图链接获取]

import datetime
import hashlib
import json
import os
import re
import sys
import time
from multiprocessing.dummy import Pool

import requests

if sys.version > '3':
    py3 = True
else:
    py3 = False


class picExtra(object):
    def __init__(self):
        pass

    def mdprImgCenter(self, url, host, headers):
        if "photo" in url:
            picurl = url
        else:
            if "/amp" in url:
                url = url.replace("/amp", "")
            urlpart = url.split("/")
            url = host + '/' + urlpart[3] + '/' + urlpart[-1]
            news_index = requests.get(
                url, timeout=30, headers=headers).text
            img_center_rule = r'<a data-click="head_img_link" data-pos="1" href="(.*?)" .*?>'
            img_center = re.findall(img_center_rule, news_index, re.S | re.M)
            picurl = host + ''.join(img_center)
        return picurl

    def oriconImgCenter(self, url, host):
        if "news" in url:
            if "full" not in url:
                picurl = url + "photo/1/"
            else:
                picurl = url.replace("full/", "photo/1/")
        elif len(re.findall(r'[0-9]+', url)) == 2:
            urlpart = url.split("/")
            picurl = host + '/' + urlpart[3] + '/' + urlpart[4] + '/'
        else:
            picurl = url
        return picurl

    def mantanImgCenter(self, url, host):
        if "photo" not in url:
            mantan_code = url.split("/")[-1]
            picurl = "{host}/photo/{code}".format(host=host, code=mantan_code)
        else:
            picurl = url
        return picurl


class instapic(object):
    def __init__(self):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
        }

    def instaPicUrl(self, url):
        response = requests.get(url, headers=self.headers, timeout=30)
        insta_body = response.text
        insta_pics = []
        insta_rule = r'<script type="text/javascript">window._sharedData = (.*?);</script>'
        insta_str = re.findall(insta_rule, insta_body, re.S | re.M)
        insta_json = json.loads(''.join(insta_str))
        insta_core = insta_json["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]
        if "edge_sidecar_to_children" in insta_core:
            insta_content = insta_core["edge_sidecar_to_children"]["edges"]
            for i in insta_content:
                insta_node = i["node"]
                if insta_node["__typename"] == "GraphImage":
                    insta_pics.append(insta_node["display_url"])
                elif insta_node["__typename"] == "GraphVideo":
                    insta_pics.append(insta_node["video_url"])
        else:
            insta_type = insta_core["is_video"]
            if insta_type:
                insta_node = insta_core["video_url"]
                insta_pics.append(insta_node)
            else:
                insta_node = insta_core["display_url"]
                insta_pics.append(insta_node)
        return insta_pics


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


class nogizaka(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        }

    def nogiBlog(self, url):
        nogi_imgs = []
        response = requests.get(url, timeout=30, headers=self.headers)
        nogi_blog_index = response.text
        nogi_box_rule = r'<div class="entrybody">(.*?)<div class="entrybottom">'
        nogi_blog_box = re.findall(nogi_box_rule, nogi_blog_index, re.S | re.M)
        nogi_img_rule = r'<a.*?href="(.*?)".*?>'
        nogi_imgs_dcimg = re.findall(nogi_img_rule, nogi_blog_box[0])
        media_path = os.path.join(os.getcwd(), "media")
        if not os.path.exists(media_path):
            os.mkdir(media_path)
        for dcimg in nogi_imgs_dcimg:
            r = requests.Session()
            response = r.get(dcimg, timeout=30, headers=self.headers)
            dcimg_index = response.text
            dcimg_rule = r'<img.*?src="(.*?)".*?>'
            nogi_img_url = re.findall(dcimg_rule, dcimg_index)
            nogi_img_url = ''.join(nogi_img_url)
            if "expired.gif" in nogi_img_url:
                nogi_img_url = "http://dcimg.awalker.jp/img/expired.gif"
            nogi_img_data = r.get(
                nogi_img_url, timeout=30, headers=self.headers)
            if py3:
                nogi_img_url = bytes(nogi_img_url, encoding="utf-8")
            hash_name = hashlib.md5(nogi_img_url).hexdigest()[8:-8]
            save_name = hash_name + ".jpg"
            save_path = os.path.join(media_path, save_name)
            save_uri = "/media/" + save_name
            nogi_imgs.append(save_uri)
            with open(save_path, "wb") as code:
                for chunk in nogi_img_data.iter_content(chunk_size=1024):
                    code.write(chunk)
        if nogi_imgs:
            return nogi_imgs
        else:
            return None


class picdown(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        }
        self.host = {
            "mdpr.jp": "https://mdpr.jp",
            "www.oricon.co.jp": "https://www.oricon.co.jp",
            "www.keyakizaka46.com": "http://www.keyakizaka46.com",
            "natalie.mu": "https://natalie.mu",
            "mantan-web.jp": "https://mantan-web.jp",
            "thetv.jp": "https://thetv.jp"
        }
        self.picExtra = picExtra()

    def __urlInvalid(self, url):
        response = requests.get(url, headers=self.headers, timeout=30)
        return response.status_code

    def __get_core(self, para):
        url = para[0]
        rule = para[1]
        response = requests.get(url, headers=self.headers, timeout=46)
        pic_index = response.text
        pic_urls = re.findall(rule, pic_index, re.S | re.M)
        return pic_urls

    def urlCheck(self, url):
        http_code = self.__urlInvalid(url)
        site = url.split("/")[2]
        result = {}
        if http_code == 200:
            host_rule = [
                "http[s]?://mdpr.jp/photo.*",
                "http[s]?://mdpr.jp/.*",
                "http[s]?://www.oricon.co.jp/photo.*",
                "http[s]?://www.oricon.co.jp/news.*",
                "http[s]?://ameblo.jp/.*/entry-.*",
                "http[s]?://*.*46.com/s/k46o/diary/detail/.*",
                "http[s]?://*.*46.com/.*.php",
                "http[s]?://natalie.mu/.*",
                "http[s]?://mantan-web.jp/.*",
                "http[s]?://thetv.jp/news/.*",
                "http[s]?://(www.)?instagram.com/p/.*"
            ]
            for rule in host_rule:
                if len(re.findall(rule, url)):
                    result["datas"] = url
                    result["type"] = site
                    return result

    def picRouter(self, result):
        site = result["type"]
        url = result["datas"]
        if "mdpr" in site:
            url = self.picExtra.mdprImgCenter(
                url, self.host[site], self.headers)
            fil_rule = r'<figure class="square">.*?<a href="(.*?)".*?>.*?</a>.*?</figure>'
            pic_rule = r'<figure class="main-photo f9em">.*?<img src="(.*?)".*?>.*?</figure>'
            piclist = self.picRules(url, site, fil_rule)
            pics = self.picUrlsGet(piclist, pic_rule)
        elif "oricon" in site:
            url = self.picExtra.oriconImgCenter(url, self.host[site])
            fil_rule = r'<li class="item">.*?<a href="(.*?)" class="inner">.*?<p class="item-image">'
            fil_rule2 = r'"(/news/[0-9]+/photo/[0-9]+/)"class='
            pic_rule = r'<div class="centering-image">.*?<img.*?src="(.*?)".*?>.*?</div>'
            piclist = self.picRules(url, site, fil_rule, fil_rule2)
            pics = self.picUrlsGet(piclist, pic_rule)
        elif "ameblo" in site:
            a = ameblo()
            pics = a.amebloImgUrl(url)
        elif "nogizaka" in site:
            n = nogizaka()
            pics = n.nogiBlog(url)
        elif "keyakizaka" in site:
            fil_rule = r'<div class="box-article">(.*?)<div class="box-bottom">'
            fil_rule_add = r'<.*?src="(.*?)".*?>'
            piclist = self.picRules(url, site, fil_rule, addrule=fil_rule_add)
            pics = piclist
        elif "natalie" in site:
            fil_rule = r'<ul class="NA_imageList clearfix">(.*?)<div class="NA_articleFooter clearfix">'
            fil_rule_add = r'<a href="(.*?)" title=.*?>.*?</a>'
            pic_rule = r'<figure>.*?<img src="(.*?)".*?>.*?<figcaption>'
            piclist = self.picRules(url, site, fil_rule, addrule=fil_rule_add)
            pics = self.picUrlsGet(piclist, pic_rule)
        elif "mantan" in site:
            url = self.picExtra.mantanImgCenter(url, self.host[site])
            fil_rule = r'<li class="newsbody__thumb.*?>.*?<a href="(.*?page=[0-9]+)">.*?</li>'
            pic_rule = r'<img src="(.*?_size6.jpg)" srcset=".*?" alt=".*?" />'
            piclist = self.picRules(url, site, fil_rule)
            pics = self.picUrlsGet(piclist, pic_rule)
        elif "thetv" in site:
            fil_rule = r'<li class="list_thumbnail__item"><a href="(.*?)" data-echo-background=".*?" alt=".*?" onContextmenu="return false"></a></li>'
            pic_rule = r'<figure>.*?<img src="(.*?)".*?>.*?</figure>'
            piclist = self.picRules(url, site, fil_rule)
            pics = self.picUrlsGet(piclist, pic_rule)
        elif "instagram" in site:
            i = instapic()
            pics = i.instaPicUrl(url)
        return pics

    def picRules(self, url, site, rule1, rule2=None, addrule=None):
        response = requests.get(url, headers=self.headers, timeout=46)
        pic_index = response.text
        pic_list = re.findall(rule1, pic_index, re.S | re.M)
        if not pic_list:
            pic_list = re.findall(rule2, pic_index, re.S | re.M)
            if not pic_list:
                return [url]
        if addrule:
            pic_list = re.findall(addrule, str(pic_list), re.S | re.M)
        pic_nlist = []
        for p in pic_list:
            if p.startswith("http"):
                pic_nlist.append(p)
            else:
                pic_nlist.append(self.host[site] + p)
        return pic_nlist

    def picUrlsGet(self, piclist, rule1, rule2=None):
        thread = len(piclist) / 4
        pic_rule = [rule1] * len(piclist)
        if 0 <= thread <= 9:
            thread = 4
        if thread > 9:
            thread = 8
        pool = Pool(thread)
        picurls = pool.map(self.__get_core, zip(piclist, pic_rule))
        pool.close()
        pool.join()
        pics = [''.join(p) for p in picurls if p]
        return pics

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

    def picDownload(self, urls, folder, thread):
        urls = urls
        nums = range(1, len(urls) + 1)
        t = [folder for i in range(0, len(urls))]
        thread = thread / 4
        if 0 <= thread <= 9:
            thread = 4
        if thread > 9:
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
    if py3:
        url = input("Url: ")
    else:
        url = raw_input("Url: ")
    folder = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    print("[1]Checking links...")
    urldict = p.urlCheck(url)
    print("[2]Getting image links...")
    urls = p.picRouter(urldict)
    if urls != "nogi":
        print("[3]Downloading...")
        thread = len(urls)
        sec = p.picDownload(urls, folder, thread)
        print("Lasted {} seconds".format(sec))


if __name__ == '__main__':
    main()
