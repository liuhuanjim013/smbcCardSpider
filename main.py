# -*-coding:utf-8-*-

import Bill_parser
username = 'username'
password = 'password'
if __name__ == '__main__':
    vpass = Bill_parser.SMBC_bill(username,password)
    vpass.get_bills()