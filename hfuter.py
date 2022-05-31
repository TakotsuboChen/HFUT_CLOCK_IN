import base64
import datetime
import json
import os
import time
import pytz
import requests
import random
from Crypto.Cipher import AES
from requests_toolbelt import MultipartEncoder
from fuckpic import makepic

output_data = ""
fail_reason = ""

class hfuter:
    def __init__(self, username, password) -> None:
        global output_data
        global fail_reason
        super().__init__()

        self.session = requests.session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 (4396363776)cpdaily/9.0.19  wisedu/9.0.19"
                          "Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37",
            "Accept": "application/json, text/plain, */*",
        })

        self.username = username
        self.password = password

        ret = self.__login()
        if ret:
            output_data += "{username}登录成功%0D%0A%0D%0A".format(username=self.username)
            self.logged_in = True
        else:
            output_data += "{username}登录失败！%0D%0A%0D%0A".format(username=self.username)
            self.logged_in = False

    def __login(self) -> bool:
        global output_data

        def encrypt_password(text: str, key: str):
            def pad(data_to_pad, block_size, style='pkcs7'):
                def bchr(s):
                    return bytes([s])

                padding_len = block_size - len(data_to_pad) % block_size
                if style == 'pkcs7':
                    padding = bchr(padding_len) * padding_len
                elif style == 'x923':
                    padding = bchr(0) * (padding_len - 1) + bchr(padding_len)
                elif style == 'iso7816':
                    padding = bchr(128) + bchr(0) * (padding_len - 1)
                else:
                    raise ValueError("Unknown padding style")
                return data_to_pad + padding

            key = key.encode('utf-8')
            text = text.encode('utf-8')

            text = pad(text, len(key), style='pkcs7')

            aes = AES.new(key, AES.MODE_ECB)
            password = aes.encrypt(text)
            password = base64.b64encode(password)
            return password

        ret = self.session.get("https://cas.hfut.edu.cn/cas/login")
        ret = self.session.get('https://cas.hfut.edu.cn/cas/vercode')
        millis = int(round(time.time() * 1000))
        ret = self.session.get(
            'https://cas.hfut.edu.cn/cas/checkInitVercode', params={'_': millis})
        key = ret.cookies['LOGIN_FLAVORING']

        if ret.json():
            output_data += '需验证码，目前该功能此脚本未支持%0D%0A%0D%0A'
            fail_reason = '需验证码，目前该功能此脚本未支持%0D%0A%0D%0A'
            return False
        else:
            output_data += '无需验证码%0D%0A%0D%0A'
        password = encrypt_password(self.password, key)
        ret = self.session.get(
            'https://cas.hfut.edu.cn/cas/policy/checkUserIdenty',
            params={'_': millis + 1, 'username': self.username, 'password': password})

        ret = ret.json()

        if ret['msg'] != 'success' and not ret['data']['authFlag']:
            return False

        if ret['data']['mailRequired'] or ret['data']['phoneRequired']:
            output_data += "你需要先进行手机或者邮箱的认证，请在PC上打开cas.hfut.edu.cn页面进行登录之后才可使用此脚本%0D%0A%0D%0A"
            fail_reason = "请在PC上打开cas.hfut.edu.cn页面进行登录之后才可使用此脚本%0D%0A%0D%0A"
            return False

        self.session.headers.update(
            {"Content-Type": "application/x-www-form-urlencoded"})
        ret = self.session.post(
            'https://cas.hfut.edu.cn/cas/login',
            data={
                'username': self.username,
                'capcha': "",
                'execution': "e1s1",
                '_eventId': "submit",
                'password': password,
                'geolocation': "",
                'submit': "登录"
            })
        self.session.headers.pop("Content-Type")

        if ret.text.find("cas协议登录成功跳转页面") != -1:
            return True
        else:
            return False

    def basic_infomation(self):
        global output_data
        if not self.logged_in:
            return {}

        self.session.get(
            "http://stu.hfut.edu.cn/xsfw/sys/swmjbxxapp/*default/index.do")

        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest"
        })
        self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/emapfunauth/welcomeAutoIndex.do"
        )
        self.session.headers.pop("Content-Type")
        self.session.headers.pop("X-Requested-With")

        ret = self.session.get(
            "http://stu.hfut.edu.cn/xsfw/sys/emapfunauth/casValidate.do",
            params={
                'service': '/xsfw/sys/swmjbxxapp/*default/index.do'
            }
        )

        self.session.headers.update({"X-Requested-With": "XMLHttpRequest"})
        self.session.headers.update(
            {"Referer": "http://stu.hfut.edu.cn/xsfw/sys/swmjbxxapp/*default/index.do"})
        ret = self.session.get(
            "http://stu.hfut.edu.cn/xsfw/sys/emappagelog/config/swmjbxxapp.do")
        self.session.headers.pop("X-Requested-With")

        config_data = {"APPID": "4930169432823497", "APPNAME": "swmjbxxapp"}
        self.session.headers.update(
            {"Content-Type": "application/x-www-form-urlencoded"})
        ret = self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/swpubapp/MobileCommon/getSelRoleConfig.do",
            data={"data": json.dumps(config_data)}
        ).json()
        if ret["code"] != "0":
            output_data += ret["msg"] + '%0D%0A%0D%0A'
            return {}
        ret = self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/swpubapp/MobileCommon/getMenuInfo.do",
            data={"data": json.dumps(config_data)}
        ).json()
        if ret["code"] != "0":
            output_data += ret["msg"] + '%0D%0A%0D%0A'
            return {}
        self.session.headers.pop("Content-Type")

        info = self.session.get(
            "http://stu.hfut.edu.cn/xsfw/sys/swmjbxxapp/StudentBasicInfo/initPageConfig.do",
            params={"data": "{}"}).json()
        self.session.headers.pop("Referer")

        return info['data']

    def daily_checkin(self, address: str, city: str, force: bool) -> int:
        global output_data
        global fail_reason
        if not self.logged_in:
            return 0

        today = datetime.datetime.now(
            tz=pytz.timezone('Asia/Shanghai')).timetuple()[:3]
        self.session.get(
            "http://stu.hfut.edu.cn/xsfw/sys/swmxsyqxxsjapp/*default/index.do")

        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest"
        })
        self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/emapfunauth/welcomeAutoIndex.do"
        )
        self.session.headers.pop("Content-Type")
        self.session.headers.pop("X-Requested-With")

        ret = self.session.get(
            "http://stu.hfut.edu.cn/xsfw/sys/emapfunauth/casValidate.do",
            params={
                'service': '/xsfw/sys/swmjbxxapp/*default/index.do'
            }
        )

        self.session.headers.update({"X-Requested-With": "XMLHttpRequest"})
        self.session.headers.update(
            {"Referer": "http://stu.hfut.edu.cn/xsfw/sys/swmjbxxapp/*default/index.do"})
        ret = self.session.get(
            "http://stu.hfut.edu.cn/xsfw/sys/emappagelog/config/swmxsyqxxsjapp.do")
        self.session.headers.pop("X-Requested-With")

        config_data = {"APPID": "5811260348942403",
                       "APPNAME": "swmxsyqxxsjapp"}
        self.session.headers.update(
            {"Content-Type": "application/x-www-form-urlencoded"})
        ret = self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/swpubapp/MobileCommon/getSelRoleConfig.do",
            data={"data": json.dumps(config_data)}
        ).json()
        if ret["code"] != "0":
            output_data += ret["msg"] + '%0D%0A%0D%0A'
            return 0
        ret = self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/swpubapp/MobileCommon/getMenuInfo.do",
            data={"data": json.dumps(config_data)}
        ).json()
        if ret["code"] != "0":
            output_data += ret["msg"] + '%0D%0A%0D%0A'
            return 0

        check = self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/swmxsyqxxsjapp/modules/mrbpa/judgeTodayHasData.do",
            data={"data": json.dumps({"TBSJ": "%.2d-%.2d-%.2d" % today})}
        ).json()

        if len(check['data']) == 1 and not force:
            return 2

        now_time = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
        self.session.headers.update({"Accept-Encoding": "gzip", "Content-Type": "multipart/form-data; boundary=+++++"})

        akmtoken = str(int((time.time() - random.randint(0, 20)) * 1000)) + \
                    str(random.randint(0, 99)) + "1"

        akmfile = {
            "token": (None, ""),
            "scope": (None, akmtoken[0:-1]),
            "fileToken": (None, akmtoken),
            "storeId": (None, "image"),
            "file": (
                "image.jpg",
                open("akm.jpg", "rb"),
                "image/jpeg"
            )
        }

        akm = self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/emapcomponent/file/uploadTempFileAsAttachment.do",
            data=MultipartEncoder(akmfile, boundary="+++++")).json()


        xcktoken = str(int((time.time()) * 1000)) + \
                    str(random.randint(0, 99)) + "1"

        xckfile = {
            "token": (None, ""),
            "scope": (None, xcktoken[0:-1]),
            "fileToken": (None, xcktoken),
            "storeId": (None, "image"),
            "file": (
                "image.jpg",
                open("xck.jpg", "rb"),
                "image/jpeg"
            )
        }

        xck = self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/emapcomponent/file/uploadTempFileAsAttachment.do",
            data=MultipartEncoder(xckfile, boundary="+++++")).json()

        self.session.headers.pop("Content-Type")
        self.session.headers.pop("Accept-Encoding")

        info = self.session.get(
            "http://stu.hfut.edu.cn/xsfw/sys/swmxsyqxxsjapp/modules/mrbpa/getSetting.do",
            data={"data": "{}"}
        ).json()

        start_time = "%04d-%02d-%02d " % today + \
                     info['data']['DZ_TBKSSJ'] + " +0800"
        start_time = datetime.datetime.strptime(
            start_time, "%Y-%m-%d %H:%M:%S %z")
        end_time = "%04d-%02d-%02d " % today + \
                   info['data']['DZ_TBJSSJ'] + " +0800"
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S %z")


        output_data += "打卡起始时间:" + str(start_time) + '%0D%0A%0D%0A'
        output_data += "打卡结束时间:" + str(end_time) + '%0D%0A%0D%0A'
        output_data += "　　现在时间:" + str(now_time) + '%0D%0A%0D%0A'
        if start_time < now_time and now_time < end_time:
            output_data += "在打卡时间内" + '%0D%0A%0D%0A'
        else:
            output_data += "不在打卡时间内" + '%0D%0A%0D%0A'
            fail_reason = "不在打卡时间内" + '%0D%0A%0D%0A'
            return 0

        self.session.headers.update(
            {"Content-Type": "application/x-www-form-urlencoded"})
        last_form = self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/swmxsyqxxsjapp/modules/mrbpa/getStuXx.do",
            data={"data": json.dumps({"TBSJ": "%.2d-%.2d-%.2d" % today})}
        ).json()

        if last_form['code'] != "0":
            return 0

        studentKey = self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/swmxsyqxxsjapp/modules/mrbpa/studentKey.do",
            data={}
        ).json()

        new_form = last_form['data']
        new_form.update({
            "DZ_SFSB": "1",
            "GCKSRQ": "",
            "GCJSRQ": "",
            "DFHTJHBSJ": "",
            "DZ_TBDZ": address,
            "DZ_TBSJDZ": city,
            "BY1": "1",
            "TBSJ": "%.2d-%.2d-%.2d" % today,
            "DZ_AKMSFYC": "0",
            "DZ_SCAKMJT": akmtoken,
            "DZ_XCKSFYC": "0",
            "DZ_SCXCKJT": xcktoken,
            "studentKey": studentKey['data']['studentKey']
        })

        paramkey = self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/swmxsyqxxsjapp/modules/mrbpa/setCode.do",
            data={"data": json.dumps(new_form)}
        ).json()

        ret = self.session.post(
            "http://stu.hfut.edu.cn/xsfw/sys/swmxsyqxxsjapp/modules/mrbpa/saveStuXx.do",
            data={"data": json.dumps(paramkey['data'])}
        ).json()

        self.session.headers.pop("Content-Type")
        self.session.headers.pop("Referer")
        if ret['code'] == "0":
            return 1
        else:
            return 0


def main():
    global output_data
    global fail_reason
    env_dist = os.environ
    makepic(env_dist['name'], env_dist['phone'])
    stu = hfuter(username=env_dist['username'], password=env_dist['password'])
    Force = False
    if 'force' in env_dist:
        if env_dist['force'] == 'T':
            Force = True
    ret = stu.daily_checkin(env_dist['address'], env_dist['city'], Force)
    if ret == 0:
        print('打卡失败')
        output_data = 'title=打卡失败&text=' + output_data
        push_title = '打卡失败'
    if ret == 1:
        print('打卡成功')
        output_data = 'title=打卡成功&text=' + output_data
        push_title = '打卡成功'
    if ret == 2:
        print('今日已打卡')
        push_title = '今日已打卡'

    if 'sckey' in env_dist:
        # 旧版ScKey
        requests.post('https://sc.ftqq.com/' + env_dist['sckey'] + '.send?' + output_data)
        # 新版ScKey
        requests.post('https://sctapi.ftqq.com/' + env_dist['sckey'] + '.send?' + output_data)
    if 'barkkey' in env_dist:
        if 'barkaddress' in env_dist:
            requests.get(env_dist['barkaddress'] + env_dist['barkkey'] + '/' + push_title + '/' + fail_reason)
        else:
            requests.get('https://api.day.app/' + env_dist['barkkey'] + '/' + push_title + '/' + fail_reason)
            

if __name__ == "__main__":
    main()
