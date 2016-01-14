# -*-coding:utf-8-*-

import Bill_parser
import argparse
from datetime import datetime

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='smbc bill parser')
    parser.add_argument('--username', action='store', type=str, dest='username')
    parser.add_argument('--password', action='store', type=str, dest='password')
    parser.add_argument('--year', action='store', type=int, dest='year', default=datetime.now().year)
    parser.add_argument('--month', action='store', type=int, dest='month', default=datetime.now().month)
    options = parser.parse_args()
    vpass = Bill_parser.SMBC_bill(options.username, options.password)
    vpass.get_bills(options.year, options.month)
