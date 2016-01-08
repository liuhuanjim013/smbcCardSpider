# -*-coding:utf-8-*-

import unicodecsv as csv
import SMBC_card as smbc
from datetime import datetime
import json


class SMBC_bill(object):
    def __init__(self, user, password):
        self.__cards = smbc.SMBC_card(user, password)
        self.__now = datetime.now()

    def get_bills(self, year=None, month=None):

        if not year or not month or not (1 <= month <= 12) or year > self.__now.year:
            year = self.__now.year
            month = self.__now.month

        self.__cards.login()
        self.__cards.retrieve_card_list()

        for card in self.__cards.card_list:
            statement = self.__cards.parse(card, year, month)
            data = json.loads(statement)

            ret = []
            try:
                rows = data['body']['content']['WebMeisaiTopDisplayServiceBean']['meisaiList']
                for row in rows:
                    if row['shiharaiPatternFlag']:
                        date = row['data'][3]
                        shop = row['data'][4]
                        pay = row['data'][5]
                        ret.append([date, shop, pay])

                file_name = (str(self.__now.year) +
                             '%02d' % self.__now.month +
                             self.__cards.card_list[card] + '.csv')

                self.__write_bill_to_csv(ret, file_name)
            except:
                continue

    def __write_bill_to_csv(self, ret, file_name):
        with open(file_name, mode='wb') as output_file:
            csv_writer = csv.writer(output_file)
            header = ['date', 'shop', 'pay']
            csv_writer.writerow(header)
            csv_writer.writerows(ret)
