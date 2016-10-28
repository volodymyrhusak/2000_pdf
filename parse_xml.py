# -*- coding: utf-8 -*-
from  lxml import etree
import os
import codecs
from bs4 import BeautifulSoup

TEXT_PATH = 'TEXT_Example'
XML_PATH = 'XML_Example'
def get_all_file(fpath):
    '''scanning all files in dir'''
    fpdf = []
    for file in os.listdir(fpath):
        fpdf.append(file)
    flist = map(lambda x: '{}/{}'.format(fpath, x), fpdf)
    return flist

def write_text(fname,data):
    with open('{}/{}.txt'.format(TEXT_PATH,fname.split('/')[-1]), 'w') as out_file:
        # writer = csv.writer(out_file)
        out_file.write(str(data))
    print 'write text file = ' + fname


for v in get_all_file(XML_PATH):
    with open(v, 'rb') as file:
        data = file.read()
    soup = BeautifulSoup(data,'xml')
    allpage = soup.find_all('LTPage')
    for page in allpage:
        line = page.find_all('LTTextLineHorizontal')
        for l in line:
        	text = l.find_all('LTTextBoxHorizontal')
        	for t in text:
        		print t.text
	


	# for node in nodes:
	# 	print v
	# 	print node.text
	# 	with codecs.open('{}/{}.txt'.format(TEXT_PATH,v.split('/')[-1]), 'wb',errors = 'ignore') as out_file:
	# 		out_file.write(node.text)	