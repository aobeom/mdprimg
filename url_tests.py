import unittest
from picdown import picdown


class urltest(unittest.TestCase):
    def setUp(self):
        self.target = {
            "mdpr": "https://mdpr.jp/photo/detail/6356062",
            "oricon": "https://www.oricon.co.jp/news/2110695/",
            "ameblo": "https://ameblo.jp/sayaka-kanda/entry-12372153694.html",
            "keya": "http://www.keyakizaka46.com/s/k46o/diary/detail/12853?ima=0000&cd=member",
            "natalie": "https://natalie.mu/eiga/news/275350",
            "mantan": "https://mantan-web.jp/article/20180501dog00m200043000c.html",
            "mthetvdpr": "https://thetv.jp/news/detail/145669/",
            "tpl": "https://tokyopopline.com/archives/100688"
        }
        self.p = picdown()

    def tearDown(self):
        pass

    def common(self, url):
        urldict = self.p.urlCheck(url)
        urls = self.p.picRouter(urldict)
        self.assertNotEqual(None, urls)

    def test_mdpr(self):
        url = self.target["mdpr"]
        self.common(url)

    def test_oricon(self):
        url = self.target["oricon"]
        self.common(url)

    def test_ameblo(self):
        url = self.target["ameblo"]
        self.common(url)

    def test_keya(self):
        url = self.target["keya"]
        self.common(url)

    def test_natalie(self):
        url = self.target["natalie"]
        self.common(url)

    def test_mantan(self):
        url = self.target["mantan"]
        self.common(url)

    def test_mthetvdpr(self):
        url = self.target["mthetvdpr"]
        self.common(url)

    def test_tpl(self):
        url = self.target["tpl"]
        self.common(url)


if __name__ == '__main__':
    tests = unittest.TestLoader().loadTestsFromTestCase(urltest)
    unittest.TextTestRunner(verbosity=2).run(tests)
