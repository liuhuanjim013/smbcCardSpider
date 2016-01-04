# -*- coding:utf-8 -*-

import requests
from datetime import datetime
from time import time
import sys


class SMBC_card(object):

    def __init__(self, user_id, password):

        if not user_id or not password:
            raise UserOrPwdNone("the username or password can't empty string")
            sys.exit(2)
        self.login_url = "https://www.smbc-card.com/memapi/jaxrs/xt_login/agree/v1"
        self.bill_url = "https://www.smbc-card.com/memapi/jaxrs/web_meisai/web_meisai_top/v1"
        self.user_id = user_id
        self.password = password
        self.now = datetime.now()

    def parse(self, year=None, month=None):
        if not year or not month or not (1 <= month <= 12) or year > self.now.year:
            year = self.now.year
            month = self.now.month
        session = requests.Session()

        login_payload = self.create_login_payload()
        login_header = self.create_login_header()
        r1 = session.post(
            self.login_url, data=login_payload, headers=login_header, allow_redirects=True)

        payload = self.create_bill_payload(year, month)
        header = self.create_bill_header()
        r2 = session.post(
            self.bill_url, data=payload, headers=header, cookies=r1.cookies)

        return r2.text

    def custom_timestamp(self):
        return str(int(time() * 1e3))

    def create_login_payload(self):
        """
        login_payload = {
            "header": {
            "requestHash": 3154381724,
            "requestTimestamp": Unix timestamp * 1000,
            "corpCode": ""
          },
          "body": {
            "content": {
              "userid": userid,
              "password": password,
              "ADP0001": "=1&userid=userid&password=password&ADP0001="
            }
          }
        }
        """
        timestamp = self.custom_timestamp()
        return ('{"header":{"requestHash":3154381724,"requestTimestamp":' + timestamp +
                ',"corpCode":""},"body":{"content":{"userid":"' + self.user_id +
                '","password":"' + self.password + '","ADP0001":"=1&userid=' +
                self.user_id + '&password=' + self.password + '&ADP0001="}}}')

    def create_login_header(self):
        login_header = {
            "Referer": "https://www.smbc-card.com/memx/login/index.html",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Content-Type": "application/json"
        }

        return login_header

    def create_bill_payload(self, year, month):
        """
        payload = {
            "header": {
            "requestHash": 1494552592,
            "requestTimestamp": Unix timestamp,
            "corpCode": ""
          },
          "body": {
            "content": {
              "p01": "201601",
              "p03": 1
            }
          }
        }
        :param year:
        :param month:
        :return:
        """
        timestamp = self.custom_timestamp()
        year_month = str(year) + '%02d' % month
        return ('{"header":{"requestHash":1494552592,"requestTimestamp":' +
                timestamp + ',"corpCode":""},"body":{"content":{"p01":' +
                year_month + ',"p03":1}}}')

    def create_bill_header(self):
        header = {
            "Referer": "https://www.smbc-card.com/memx/web_meisai/top/index.html",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Content-Type": "application/json",
            "DNT": "1"
        }

        return header


class UserOrPwdNone(BaseException):

    """
    Raised if the user id or password is None
    """

if __name__ == '__main__':
    card = SMBC_card('username', 'password')
    print card.parse()
