# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2017-12-22 09:48:23
# @modify date 2018-06-22 22:42:58
# @desc [原图链接获取]
import hashlib
import json
import multiprocessing
import os
import re
import sys
import time
from multiprocessing.dummy import Pool

import requests
from lxml import etree

try:
    import queue
except ImportError:
    import Queue as queue

if sys.version > '3':
    py3 = True
else:
    py3 = False


# url处理的额外规则
class picExtra(object):
    def __init__(self):
        pass

    # mdpr统一跳转至photo页面
    def mdprImgCenter(self, url, host, headers):
        if "photo" in url:
            picurl = url
        else:
            # google amp标识清除
            if "/amp" in url:
                url = url.replace("/amp", "")
            urlpart = url.split("/")
            url = host + '/' + urlpart[3] + '/' + urlpart[-1]
            news_index = requests.get(
                url, timeout=30, headers=headers).text
            # 提取photo页面
            html = etree.HTML(news_index)
            img_center = html.xpath(
                r'//a[@data-click="head_img_link"]')[0].get("href")
            picurl = host + ''.join(img_center)
        return picurl

    # oricon统一跳转至photo页面
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

    # mantan统一跳转至photo页面
    def mantanImgCenter(self, url, host):
        if "photo" not in url:
            mantan_code = url.split("/")[-1]
            picurl = "{host}/photo/{code}".format(host=host, code=mantan_code)
        else:
            picurl = url
        return picurl


# Instagram从JS中获取
class instapic(object):
    def __init__(self):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
        }

    def instaPicUrl(self, url):
        response = requests.get(url, headers=self.headers, timeout=30)
        insta_body = response.text
        insta_pics = []
        # 提取JS请求的内容
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


# ameblo通过接口获取
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


# nogizaka46博客图片获取
class nogizaka(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        }

    def nogiBlog(self, url):
        nogi_imgs = []
        response = requests.get(url, timeout=30, headers=self.headers)
        nogi_blog_index = response.content
        nogi_html = etree.HTML(nogi_blog_index)
        # 获取dcimg地址
        img_center = nogi_html.xpath(r'//div[@class="entrybody"]//a')
        if img_center:
            nogi_imgs_dcimg = [i.get("href") for i in img_center]
            img_tag = True
        # 获取直链
        else:
            img_center = nogi_html.xpath(r'//div[@class="entrybody"]/img')
            nogi_imgs_dcimg = [i.get("src") for i in img_center]
            img_tag = False
        # 保存到本地
        media_path = os.path.join(os.getcwd(), "media")
        if not os.path.exists(media_path):
            os.mkdir(media_path)
        for dcimg in nogi_imgs_dcimg:
            r = requests.Session()
            # dcimg地址则提取原图地址
            if img_tag:
                response = r.get(dcimg, timeout=30, headers=self.headers)
                dcimg_index = response.text
                dcimg_html = etree.HTML(dcimg_index)
                nogi_img_url = dcimg_html.xpath(
                    r'//div[@id="contents"]//img')[0].get("src")
                if "expired.gif" in nogi_img_url:
                    nogi_img_url = "http://dcimg.awalker.jp/img/expired.gif"
            else:
                nogi_img_url = dcimg
            # 单独下载模块
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
        # 返回一个uri列表提供本地下载
        if nogi_imgs:
            return nogi_imgs
        else:
            return None


# 通用图片下载
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
            "thetv.jp": "https://thetv.jp",
            "tokyopopline.com": "https://tokyopopline.com"
        }
        self.picExtra = picExtra()

    # 返回url状态码
    def __urlInvalid(self, url):
        response = requests.get(url, headers=self.headers, timeout=30)
        return response.status_code

    # 提取图片地址
    def __get_core(self, para):
        img_main = para[0]
        img_i_rule = para[1]
        ibody = requests.get(img_main, headers=self.headers, timeout=46)
        ibody = etree.HTML(ibody.text)
        img_src = ibody.xpath(img_i_rule)
        for i in img_src:
            img_url = i.get("src").split("?")[0]
            if img_url:
                return img_url

    # 检查输入url有效性
    def urlCheck(self, url):
        http_code = self.__urlInvalid(url)
        site = url.split("/")[2]
        result = {}
        if http_code == 200:
            # 正则匹配域名和目录
            host_rule = re.compile(
                r'https?://(.*mdpr\.jp/.*|.*oricon\.co\.jp|.*ameblo\.jp/.*/entry-.*|.*46.com|.*natalie\.mu|.*mantan-web\.jp|.*thetv.jp|.*tokyopopline\.com|.*instagram.com/p/.*)')
            if host_rule.match(url):
                result["data"] = url
                result["type"] = site
                return result

    # 规则路由
    def picRouter(self, result):
        if result:
            site = result["type"]
            url = result["data"]
            if "mdpr" in site:
                url = self.picExtra.mdprImgCenter(
                    url, self.host[site], self.headers)
                img_i_rule = '//figure[@class="square"]//img'
                rule = {
                    "mode": "direct",
                    "i_rule": img_i_rule
                }
                pics = self.picRules(url, self.host[site], **rule)
            elif "oricon" in site:
                url = self.picExtra.oriconImgCenter(url, self.host[site])
                img_a_rule = '//div[@class="photo_thumbs"]//a'
                img_i_rule = '//div[@class="centering-image"]//img'
                img_other_rule = '//li[@class="item"]//a[@class="inner"]'
                rule = {
                    "mode": "indirect",
                    "a_rule": img_a_rule,
                    "i_rule": img_i_rule,
                    "other_rule": img_other_rule
                }
                pics = self.picRules(url, self.host[site], **rule)
            elif "ameblo" in site:
                a = ameblo()
                pics = a.amebloImgUrl(url)
            elif "nogizaka" in site:
                n = nogizaka()
                pics = n.nogiBlog(url)
            elif "keyakizaka" in site:
                img_i_rule = '//div[@class="box-article"]//img'
                rule = {
                    "mode": "direct",
                    "i_rule": img_i_rule
                }
                pics = self.picRules(url, **rule)
            elif "natalie" in site:
                img_a_rule = '//div[@class="GAE_newsListImage NA_imageUnit"]//li//a'
                img_i_rule = '//div[@class="NA_figureUnit"]//img'
                rule = {
                    "mode": "indirect",
                    "a_rule": img_a_rule,
                    "i_rule": img_i_rule,
                    "other_rule": ""
                }
                pics = self.picRules(url, **rule)
            elif "mantan" in site:
                img_a_rule = '//ul[@class="newsbody__thumblist"]//a'
                img_i_rule = '//figure//img'
                rule = {
                    "mode": "indirect",
                    "a_rule": img_a_rule,
                    "i_rule": img_i_rule,
                    "other_rule": ""
                }
                pics = self.picRules(url, self.host[site], **rule)
            elif "thetv" in site:
                img_a_rule = '//ul[@class="list_thumbnail"]/li/a[@alt]'
                img_i_rule = '//figure/a/img|//figure/img'
                rule = {
                    "mode": "indirect",
                    "a_rule": img_a_rule,
                    "i_rule": img_i_rule,
                    "other_rule": ""
                }
                pics = self.picRules(url, self.host[site], **rule)
            elif "instagram" in site:
                i = instapic()
                pics = i.instaPicUrl(url)
            elif "tokyopopline" in site:
                img_i_rule = '//dl[@class="gallery-item"]/dt/a'
                rule = {
                    "mode": "direct",
                    "i_rule": img_i_rule
                }
                pics = self.picRules(url, **rule)
            return pics
        else:
            return None

    # 规则处理
    def picRules(self, url, site=None, **rules):
        mode = rules["mode"]
        body = requests.get(url, headers=self.headers, timeout=46)
        html = etree.HTML(body.text)
        img_urls = []
        if site:
            site = site
        else:
            site = ""
        # 图片地址在多个页面时
        if mode == "indirect":
            img_a_rule = rules["a_rule"]
            img_i_rule = rules["i_rule"]
            img_other_rule = rules["other_rule"]
            img_body_main = html.xpath(img_a_rule)
            if img_body_main:
                img_entry_main = [site + i.get("href") for i in img_body_main]
            else:
                img_body_main = html.xpath(img_other_rule)
                img_entry_main = [site + i.get("href") for i in img_body_main]
            thread = len(img_entry_main) / 4
            img_i_rules = [img_i_rule] * len(img_entry_main)
            if 0 <= thread <= 9:
                thread = 4
            if thread > 9:
                thread = 8
            pool = Pool(thread)
            img_urls = pool.map(self.__get_core, zip(
                img_entry_main, img_i_rules))
            pool.close()
            pool.join()
        # 图片地址在同一个页面
        elif mode == "direct":
            img_i_rule = rules["i_rule"]
            img_src = html.xpath(img_i_rule)
            if img_src:
                for i in img_src:
                    if i.get("src"):
                        img_urls.append(i.get("src").split("?")[0])
                    else:
                        img_urls.append(i.get("href").split("?")[0])
        else:
            img_urls = None
        return img_urls

    # 全局下载处理函数
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

    # 下载调用函数
    def picDownload(self, urls, folder, thread):
        urls = urls
        nums = range(1, len(urls) + 1)
        t = [folder for i in range(0, len(urls))]
        thread = thread / 4
        if 0 <= thread <= 9:
            thread = 4
        if thread > 9:
            thread = 8
        t = threadProcBar(self.__download, list(zip(nums, urls, t)), thread)
        t.worker()
        t.process()


def process_num(total, current):
    num = current / float(total) * 100
    return num


class threadProcBar(object):
    def __init__(self, func, tasks, pool=multiprocessing.cpu_count()):
        self.func = func
        self.tasks = tasks

        self.bar_i = 0
        self.bar_len = 50
        self.bar_max = len(tasks)

        self.p = Pool(pool)
        self.q = queue.Queue()

    def __dosth(self, percent, task):
        if percent == self.bar_max:
            return self.done
        else:
            self.func(task)
            return percent

    def worker(self):
        process_bar = '[' + '>' * 0 + '-' * 0 + ']' + '%.2f' % 0 + '%' + '\r'
        sys.stdout.write(process_bar)
        sys.stdout.flush()
        pool = self.p
        for i, task in enumerate(self.tasks):
            try:
                percent = pool.apply_async(self.__dosth, args=(i, task))
                self.q.put(percent)
            except BaseException as e:
                break

    def process(self):
        pool = self.p
        while 1:
            result = self.q.get().get()
            if result == self.bar_max:
                self.bar_i = self.bar_max
            else:
                self.bar_i += 1
            num_arrow = int(self.bar_i * self.bar_len / self.bar_max)
            num_line = self.bar_len - num_arrow
            percent = self.bar_i * 100.0 / self.bar_max
            process_bar = '[' + '>' * num_arrow + '-' * \
                num_line + ']' + '%.2f' % percent + '%' + '\r'
            sys.stdout.write(process_bar)
            sys.stdout.flush()
            if result == self.bar_max-1:
                pool.terminate()
                break
        pool.join()
        self.__close()

    def __close(self):
        print('')


def timer(func):
    def warpper(*args, **kwargs):
        start = time.time()
        func()
        t_diff = time.time() - start
        if t_diff < 60:
            second = round(t_diff, 2)
            minute = 0
            hour = 0
        elif 60 <= t_diff < 3600:
            hour = 0
            minute = int(t_diff // 60)
            second = round(t_diff - minute * 60, 2)
        else:
            hour = int(t_diff//3600)
            minute = int((t_diff - (hour * 3600))//60)
            second = round(t_diff - hour * 3600 - minute * 60, 2)
        latest = "Cost time: {}:{}:{}".format(hour, minute, second)
        print(latest)
    return warpper


def pic_proc(proc, urls, folder, site):
    if "nogizaka" not in site:
        os.mkdir(folder)
        print("[3]Downloading...")
        thread = len(urls)
        proc.picDownload(urls, folder, thread)


@timer
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

    pic_proc(p, urls, folder, urldict["type"])
    sys.exit("Press Enter to exit.")


if __name__ == '__main__':
    main()
