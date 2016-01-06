# smbcCardSpider

This is a spider that crawls monthly statement of you SMBC credit card and output to a CSV file

## Dependecy and usage
Because csv module in Python 2.7.x has a hard time when writing a list that contains unicode characters, go for unicodecsv alternatively.
	
	pip install unicodecsv 

For the usage
	
	import Bill_parser
	vpass = Bill_parser.SMBC_bill('username','password') # your username and password for vpass website
	vpass.get_bill(year, month) # year and month for the statement
	
a csv file will be created with file name contains year and month e.g. '201210.csv'

## ToDo
1. Crawl statements for all credit cards
2. Handle errors