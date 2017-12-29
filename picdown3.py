# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:48:23
# @modify date 2017-12-29 09:38:15
# @desc [原图链接获取]

import datetime
import hashlib
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
        thread = len(photo_urls) // 4
        if 0 < thread <= 9:
            thread = 4
        if thread >= 10:
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
        thread = len(photo_url) // 4
        if 0 < thread <= 9:
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


class pic46(object):
    def __init__(self):
        self.keya_host = "http://www.keyakizaka46.com"
        self.nogi_host = "http://blog.nogizaka46.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        }

    def urlAnalysis(self, url):
        if self.keya_host in url:
            img46 = self.keyaBlog(url)
        elif self.nogi_host in url:
            img46 = self.nogiBlog(url)
        else:
            img46 = None
        return img46

    def keyaBlog(self, url):
        response = requests.get(url, timeout=30, headers=self.headers)
        keya_blog_index = response.text
        keya_box_rule = r'<div class="box-article">(.*?)<div class="box-bottom">'
        keya_blog_box = re.findall(keya_box_rule, keya_blog_index, re.S | re.M)
        keya_img_rule = r'<.*?src="(.*?)".*?>'
        keya_imgs = re.findall(keya_img_rule, keya_blog_box[0])
        if keya_imgs:
            return keya_imgs
        else:
            return None

    def nogiBlog(self, url):
        response = requests.get(url, timeout=30, headers=self.headers)
        nogi_blog_index = response.text
        nogi_box_rule = r'<div class="entrybody">(.*?)<div class="entrybottom">'
        nogi_blog_box = re.findall(nogi_box_rule, nogi_blog_index, re.S | re.M)
        nogi_img_rule = r'<a.*?href="(.*?)".*?>'
        nogi_imgs_dcimg = re.findall(nogi_img_rule, nogi_blog_box[0])
        folder = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        media_path = os.path.join(os.getcwd(), folder)
        if not os.path.exists(media_path):
            os.mkdir(media_path)
        print("[3]Downloading...")
        for dcimg in nogi_imgs_dcimg:
            r = requests.Session()
            try:
                response = r.get(dcimg, timeout=30, headers=self.headers)
                dcimg_index = response.text
                dcimg_rule = r'<img.*?src="(.*?)".*?>'
                nogi_img_url = re.findall(dcimg_rule, dcimg_index)
                nogi_img_url = ''.join(nogi_img_url)
                nogi_img_data = r.get(
                    nogi_img_url, timeout=30, headers=self.headers)
                nogi_img_url = bytes(nogi_img_url, encoding="utf-8")
                save_name = hashlib.md5(nogi_img_url).hexdigest()[
                    8:-8] + ".jpg"
                save_path = os.path.join(media_path, save_name)
                with open(save_path, "wb") as code:
                    for chunk in nogi_img_data.iter_content(chunk_size=1024):
                        code.write(chunk)
            except BaseException:
                pass
        return "nogi"


class natalie(object):
    def __init__(self):
        self.natalie = "https://natalie.mu"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
        }

    def natalieImgList(self, url):
        response = requests.get(url, headers=self.headers, timeout=30)
        natalie_index = response.text
        natalie_imglist_rule = r'<ul class="NA_imageList clearfix">(.*?)</div>'
        natalie_imglist = re.findall(
            natalie_imglist_rule, natalie_index, re.S | re.M)
        natalie_img_index_rule = r'<a href="(.*?)" title=.*?>.*?</a>'
        imglist = re.findall(natalie_img_index_rule,
                             str(natalie_imglist), re.S | re.M)
        return imglist

    def __geturl(self, url):
        response = requests.get(url, headers=self.headers, timeout=30)
        natalie_body_rule = r'<figure>(.*?)<figcaption>'
        natalie_index = response.text
        natalie_body = re.findall(
            natalie_body_rule, natalie_index, re.S | re.M)
        natalie_img_rule = r'<img src="(.*?)" alt=".*?">'
        natalie_img = re.findall(
            natalie_img_rule, str(natalie_body), re.S | re.M)
        return natalie_img

    def natalieImgUrl(self, imglist):
        thread = len(imglist) // 4
        if 0 < thread <= 9:
            thread = 4
        if thread >= 10:
            thread = 8
        pool = Pool()
        imgurls = pool.map(self.__geturl, imglist)
        pool.close()
        pool.join()
        imgurls = [''.join(i) for i in imgurls]
        return imgurls


class mantanweb(object):
    def __init__(self):
        self.mantan_host = "https://mantan-web.jp"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
        }

    def mantanImgUrl(self, url):
        if "photo" not in url:
            mantan_code = url.split("/")[-1]
            mantan_photo_url = "{host}/photo/{code}".format(
                host=self.mantan_host, code=mantan_code)
        else:
            mantan_photo_url = url
        response = requests.get(
            mantan_photo_url, headers=self.headers, timeout=30)
        mantan_index = response.text
        mantan_imgbody_rule = r'<ul class="newsbody__thumblist">(.*?)</ul>'
        mantan_imgbody = re.findall(
            mantan_imgbody_rule, mantan_index, re.S | re.M)
        mantan_img_rule = r'<img src="(.*?)" srcset=".*?" />'
        mantan_imgs_thumb = re.findall(
            mantan_img_rule, str(mantan_imgbody), re.S | re.M)
        mantan_imgs = ["https:" + img.replace("thumb", "size6")
                       for img in mantan_imgs_thumb]
        return mantan_imgs


class picdown(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        }

    def urlCheck(self, url):
        url = url
        mdpr_host = "http[s]?://mdpr.jp/photo.*"
        mdpr_host_other = "http[s]?://mdpr.jp/.*"
        oricon_host = "http[s]?://www.oricon.co.jp/photo.*"
        oricon_host_news = "http[s]?://www.oricon.co.jp/news.*"
        ameblo_host = "http[s]?://ameblo.jp/.*/entry-.*"
        keya_host = "http[s]?://*.*46.com/s/k46o/diary/detail/.*"
        nogi_host = "http[s]?://*.*46.com/.*.php"
        natalie_host = "https://natalie.mu/.*"
        mantan_host = "https://mantan-web.jp/.*"
        if len(re.findall(mdpr_host, url)) or len(re.findall(mdpr_host_other, url)):
            result = {"site": "mdpr", "url": url}
        elif len(re.findall(oricon_host, url)) or len(re.findall(oricon_host_news, url)):
            result = {"site": "oricon", "url": url}
        elif len(re.findall(ameblo_host, url)):
            result = {"site": "ameblo", "url": url}
        elif len(re.findall(nogi_host, url)) or len(re.findall(keya_host, url)):
            result = {"site": "46", "url": url}
        elif len(re.findall(natalie_host, url)):
            result = {"site": "natalie", "url": url}
        elif len(re.findall(mantan_host, url)):
            result = {"site": "mantan", "url": url}
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
            elif target_site == "46":
                p = pic46()
                result = p.urlAnalysis(target_url)
            elif target_site == "natalie":
                n = natalie()
                imglist = n.natalieImgList(target_url)
                result = n.natalieImgUrl(imglist)
            elif target_site == "mantan":
                m = mantanweb()
                result = m.mantanImgUrl(target_url)
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
        thread = thread // 4
        if 0 < thread <= 9:
            thread = 4
        if thread >= 10:
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
    url = input("Enter a link or file:")
    folder = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    print("[1]Checking links...")
    urldict = p.urlCheck(url)
    print("[2]Getting image links...")
    urls = p.photoUrlGet(urldict)
    if urls != "nogi":
        print("[3]Downloading...")
        thread = len(urls)
        sec = p.photoDownload(urls, folder, thread)
        print("Lasted {} seconds".format(sec))


if __name__ == '__main__':
    main()
