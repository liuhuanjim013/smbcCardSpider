# -*- coding:utf-8 -*-

import requests
import json
from datetime import datetime
from time import time


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
    session: requests.Session for keeping login
    card_list: dict that contains all credit card. key: card id, value: card name
    """

    def __init__(self, user_id, password):

        if not user_id or not password:
            raise UserOrPwdNone("the username or password can't empty string")

        self.login_url = "https://www.smbc-card.com/memapi/jaxrs/xt_login/agree/v1"
        self.bill_url = "https://www.smbc-card.com/memapi/jaxrs/web_meisai/web_meisai_top/v1"
        self.card_url = "https://www.smbc-card.com/memapi/jaxrs/multicard/dropdownlist_init/v1"
        self.switch_url = "https://www.smbc-card.com/memapi/jaxrs/multicard/operation_card_update/v1"
        self.user_id = user_id
        self.password = password
        self.now = datetime.now()
        self.session = requests.Session()
        self.card_list = {}

    def login(self):
        """
        Initialize Login Session for following operations
        Returns: None
        """
        login_payload = self.__create_login_payload()
        login_header = self.__create_header(header_type='login')
        self.session.post(
                self.login_url, data=login_payload, headers=login_header, allow_redirects=True)

    def parse(self, card, year=None, month=None):
        """
        Retrieve statement of a credit card on certain time.
        Default value for year and month is current time.
        Args:
            card: str card id in SMBC website
            year: int e.g. 2016
            month: int e.g. 12

        Returns: str return value of the post request

        """

        if not year or not month or not (1 <= month <= 12) or year > self.now.year:
            year = self.now.year
            month = self.now.month

        payload = self.__create_bill_payload(year, month)
        header = self.__create_header()
        self.switch_to_card(card)
        r = self.session.post(self.bill_url, data=payload, headers=header)
        return r.text

    def switch_to_card(self, card_id):
        """
        In a login session, website keeps a default card id rather than specifying one when send queries.
        This method changes the current card id
        Args:
            card_id: str card id

        Returns: None

        """
        header = self.__create_header()
        payload = self.__create_card_switch_payload(card_id)
        self.session.post(self.switch_url, data=payload, headers=header)

    def retrieve_card_list(self):
        """
        Now it is able to check statements of all cards with login once
        This method fetches a list of credit card id and names
        Returns: None

        """
        header = self.__create_header()
        payload = self.__create_card_list_payload()
        data = self.session.post(self.card_url, data=payload, headers=header)
        data = json.loads(data.text)
        for card in data['body']['content']['DropdownListInitDisplayServiceBean']['multiCardInfoList']:
            self.card_list[card['value']] = card['name']

    def __create_header(self, header_type=None):
        """
        Actually wrong referer would not stop you from logging in or getting the statement.
        Just wanted to make it look like a real request.
        Args:
            header_type: dict header in request

        Returns:

        """
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
        """
        Get current unix time
        Returns: str unix time

        """
        return str(int(time() * 1e3))

    def __create_login_payload(self):
        """
        Payload for login
        Returns: str login_payload

        """

        timestamp = self.__custom_timestamp()
        login_payload = {
            "header": {
                "requestHash": 3154381724,
                "requestTimestamp": timestamp,
                "corpCode": ""
            },
            "body": {
                "content": {
                    "userid": self.user_id,
                    "password": self.password,
                    "ADP0001": '"=1&userid=' + self.user_id + '&password=' + self.password + '&ADP0001='
                }
            }
        }
        return json.dumps(login_payload)

    def __create_bill_payload(self, year, month):
        """
        :param int year:
        :param int month:
        :return:
        """
        timestamp = self.__custom_timestamp()
        year_month = str(year) + '%02d' % month
        payload = {
            "header": {
                "requestHash": 1494552592,
                "requestTimestamp": timestamp,
                "corpCode": ""
            },
            "body": {
                "content": {
                    "p01": year_month,
                    "p03": 1
                }
            }
        }

        return json.dumps(payload)

    def __create_card_switch_payload(self, card_id):
        """
        Change the default card in thee page for query
        """
        timestamp = self.__custom_timestamp()
        payload = {
            "header": {
                "requestHash": 3364688549,
                "requestTimestamp": timestamp,
                "corpCode": ""
            },
            "body": {
                "content": {
                    "cardIdentifyKey": card_id
                }
            }
        }
        return json.dumps(payload)

    def __create_card_list_payload(self):
        """

        """
        timestamp = self.__custom_timestamp()
        payload = {
            "header": {
                "requestHash": 2160136501,
                "requestTimestamp": timestamp,
                "corpCode": ""
            },
            "body": {
                "content": {
                    "displayDropdownList": "enable"
                }
            }
        }
        return json.dumps(payload)


class UserOrPwdNone(BaseException):
    """
    Raised if the user id or password is None
    """
