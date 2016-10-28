# -*- coding: utf-8 -*-
import pdfquery
import lxml
import os

PDF_PATH = 'fpdf2'
TEXT_PATH = 'TEXT_Example'
XML_PATH = 'XML_Example'

def pdf_to_xml(fname):
    print 'Start parse ' + fname
    pdf = pdfquery.PDFQuery(fname)
    pdf.load()
    print 'load PDF'
    data = lxml.etree.tostring(pdf.tree, pretty_print=True, encoding="utf-8")
    print 'End parse ' + fname
    with open('{}/{}.xml'.format(XML_PATH,fname.split('/')[-1]), 'wb') as f:
        f.write(data)
        f.close()
    del pdf     
    del data     
    return None    

def get_all_file(fpath, form):
    '''scanning all files in dir'''
    fxml = set()
    for file in os.listdir(XML_PATH):
        fxml.add(file.split('.')[0])
    print len(fxml)
    fpdf = set()

    for file in os.listdir(fpath):
    	fname = file.split('.')[0]
        if file.endswith(form) and fname not in fxml :
            fpdf.add(fname)
    print len(fpdf)
    flist = map(lambda x: '{}/{}'.format(fpath, x+form), fpdf)
    # print len(flist)
    return flist

for v in get_all_file(PDF_PATH, '.pdf'):
	pdf_to_xml(v)

# get_all_file(PDF_PATH, '.pdf')
print ('Done')