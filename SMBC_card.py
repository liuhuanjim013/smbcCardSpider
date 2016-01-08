# -*- coding:utf-8 -*-

import requests
import json
from datetime import datetime
from time import time
import sys


class SMBC_card(object):
    """
    Attributes:
    login_url: str API for login authorization
    bill_url: str API for statement access
    card_url: str API for retrieving credit card list
    switch_url: str API for switching current credit card
    user_id: str Username for SMBC card website
    password: str Password for SMBC card website
    now: datetime object for current date
    """
    def __init__(self, user_id, password):

        if not user_id or not password:
            raise UserOrPwdNone("the username or password can't empty string")
            sys.exit(2)
        self.login_url = "https://www.smbc-card.com/memapi/jaxrs/xt_login/agree/v1"
        self.bill_url = "https://www.smbc-card.com/memapi/jaxrs/web_meisai/web_meisai_top/v1"
        self.card_url = "https://www.smbc-card.com/memapi/jaxrs/multicard/dropdownlist_init/v1"
        self.switch_url = "https://www.smbc-card.com/memapi/jaxrs/multicard/operation_card_update/v1"
        self.user_id = user_id
        self.password = password
        self.now = datetime.now()
        self.session = requests.Session()
        self.card_list = {}
        self.cookies = []

    def login(self):
        login_payload = self.__create_login_payload()
        login_header = self.__create_header(header_type='login')
        r = self.session.post(
            self.login_url, data=login_payload, headers=login_header, allow_redirects=True)
        self.cookies = r.cookies

    def parse(self, card, year=None, month=None):

        if not year or not month or not (1 <= month <= 12) or year > self.now.year:
            year = self.now.year
            month = self.now.month

        payload = self.__create_bill_payload(year, month)
        header = self.__create_header()
        self.switch_to_card(card)
        r = self.session.post(self.bill_url, data=payload, headers=header)
        return r.text

    def switch_to_card(self, card_id):
        header = self.__create_header()
        payload = self.__create_card_switch_payload(card_id)
        self.session.post(self.switch_url, data=payload, headers=header)

    def retrieve_card_list(self):
        header = self.__create_header()
        payload = self.__create_card_list_payload()
        data = self.session.post(self.card_url, data=payload, headers=header)
        data = json.loads(data.text)
        for card in data['body']['content']['DropdownListInitDisplayServiceBean']['multiCardInfoList']:
            self.card_list[card['value']] = card['name']

    def __create_header(self, header_type=None):
        if header_type == 'login':
            referer = "https://www.smbc-card.com/memx/login/index.html"
        else:
            referer = "https://www.smbc-card.com/memx/web_meisai/top/index.html"
        header = {
            "Referer": referer,
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Content-Type": "application/json"
        }

        return header

    def __custom_timestamp(self):
        return str(int(time() * 1e3))

    def __create_login_payload(self):
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
        timestamp = self.__custom_timestamp()
        return ('{"header":{"requestHash":3154381724,"requestTimestamp":' + timestamp +
                ',"corpCode":""},"body":{"content":{"userid":"' + self.user_id +
                '","password":"' + self.password + '","ADP0001":"=1&userid=' +
                self.user_id + '&password=' + self.password + '&ADP0001="}}}')

    def __create_bill_payload(self, year, month):
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
        timestamp = self.__custom_timestamp()
        year_month = str(year) + '%02d' % month
        return ('{"header":{"requestHash":1494552592,"requestTimestamp":' +
                timestamp + ',"corpCode":""},"body":{"content":{"p01":' +
                year_month + ',"p03":1}}}')

    def __create_card_switch_payload(self, card_id):
        """
        {
          "header": {
            "requestHash": 3364688549,
            "requestTimestamp": 1452232308185,
            "corpCode": ""
          },
          "body": {
            "content": {
              "cardIdentifyKey": "XXXXXXXXXXXXXXX"
            }
          }
        }
        """
        timestamp = self.__custom_timestamp()
        return ('{"header":{"requestHash":3364688549,"requestTimestamp":' +
                timestamp + ',"corpCode":""},"body":{"content":{"cardIdentifyKey":"' +
                card_id + '"}}}')

    def __create_card_list_payload(self):
        """
        {
        "header": {
            "requestHash": 2160136501,
            "requestTimestamp": 1452232313497,
            "corpCode": ""
        },
          "body": {
            "content": {
              "displayDropdownList": "enable"
            }
          }
        }
        """
        timestamp = self.__custom_timestamp()
        return ('{"header":{"requestHash":2160136501,"requestTimestamp":' +
                timestamp + ',"corpCode":""},"body":{"content":{"displayDropdownList":"enable"}}}')

class UserOrPwdNone(BaseException):

    """
    Raised if the user id or password is None
    """

