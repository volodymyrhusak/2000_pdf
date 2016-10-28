# -*- coding: utf-8 -*-
import subprocess
import os
import re
import csv
import pdfquery
import lxml
import time
title = ('Document number/name','Company name','ACN','ACN/ARSN (if applicable)',
    'Holder Name','Change Date','Previous Notice','Previous Date','Class',
    'Previouse Shares','Previous Percent','New Shares','New Percent','Error reason/Success')
OUTPUT_NAME = '{}.csv'.format(time.strftime("%c"))
PDF_PATH = '2000'
TEXT_PATH = 'TEXT_Example'
XML_PATH = 'XML_Example'
CSV_PATH = 'CSV_Example'

def main():
    print 'start'
    write_csv(title)
    fpath = get_all_file_new(PDF_PATH, '.pdf')
    for pdf in fpath:
        # data_text =pdf_to_xml(pdf)
        data_text =pdftotext(pdf)
        clean_text = cleaner_text(data_text)
        write_text(pdf,clean_text)
    fpath = get_all_file(TEXT_PATH, '.txt')
    for text in fpath:
        final_data = parser(text)
        write_csv(final_data)

def create_dir(dirc):
    if not os.path.exists(dirc):
        os.makedirs(dirc)

def get_all_file_new(fpath, form):
    '''scanning all files in dir'''
    fxml = set()
    for file in os.listdir(TEXT_PATH):
        fxml.add(file.split('.')[0])
    print len(fxml)
    fpdf = []

    for file in os.listdir(fpath):
        fname = file.split('.')[0]
        if file.endswith(form) and fname not in fxml :
            fpdf.append(fname)
    print len(fpdf)
    fpdf.sort()
    flist = []
    for i,x in enumerate(fpdf):
        flist.append('{}/{}'.format(fpath, x+form))
        if i == 2000:
            break

    # flist = map(lambda x: '{}/{}'.format(fpath, x+form), fpdf)
    # print len(flist)
    return flist


    
def parser(ftext):
    '''Find information from in text file'''
    error_reason = 'Success'
    document_number = ftext.split('/')[-1] 
    document_number = document_number.split('.')[0]
    with open(ftext, 'r') as file:
        text = file.read()
        file.close()
    # text = unicode(text, "utf-8")
    if text == 'None':
        return (document_number,'','','','','','','','','','','','','PDF may need OCR')
    # print ftext
    comp_name = ''
    ACN = ''
    comp_name_2 = ''
    ACN_2 = ''
    date_1 = ''    
    date_2 = ''    
    date_3 = ''
    ch_class = ''
    previouse_shares = ''
    previous_percen = ''
    new_shares = ''
    new_percent = ''
    text_0 = text
    text_1 = text
    text_2 = text
    text_3 = text
                                      
    piece_1 = re.search(r'([1lL]\s*.\s*D,?eta[ilI]ls.*\n)|([1l]\s*.\s*DETAILS.*\n)|(l.\s*Detoilsof)|(1.\sDeloilsof)|(1\. Details)|(1\. Dcttlil)', text)
    if piece_1:
        text_0 = text[0:piece_1.start()]
        text_1 = text[piece_1.start()::]
    else:  
        piece_1 = re.search(r'^.*\n',text)  
        text_0 = text
        text_1 = text
    piece_2 = re.search(r'(2. Previous and present voting power)|(2.\s*Pr[ce]v[il]ous)|(2.\s*Changes)|(2\.\s*PREV[lI]OUS)|(2\. Pr[eo]vious )|(2.\s*Details)', text_1)
    if piece_2:
        text_2 = text_1[piece_2.start()::]
        text_1 = text_1[0:piece_2.start()] 
    else:
        piece_2 = piece_1 
        text_2 = text_1[piece_2.start()::]  
    piece_3 = re.search(r'([32].\s*[CG]h[ao]ng[eo]s?)|(CHANGES)|(Ctnnges)|(Details)', text_2) 
    if piece_3:
        text_3 = text_2[piece_3.start()::]
        text_2 = text_2[0:piece_3.start()]
    else:
        piece_3 = piece_2
        text_3 = text_2[piece_3.start()::]
    piece_4 = re.search(r'([4(il)].\s*Present)|(4.\s*Plesem)|(4.\s*Details)|(4.\s*PRESEN)',text_3)
    if piece_4:
        text_4 = text_3[piece_4.start()::]
        text_3 = text_3[0:piece_4.start()]
    else:
        piece_4 = piece_3
        text_4 = text_3[piece_4.start()::]
    piece_5 = re.search(r'([56L].\s*[GC]hann?ges?)|([5L].\s*Chonn?ges?)|(5.\s*CHANGES)|(5. Changes in associati)',text_4)
    if piece_5:
        text_5 = text_4[piece_5.start()::]
        text_4 = text_4[0:piece_5.start()]
    else:
        piece_5 = piece_4
        text_5 = text_4[piece_5.start()::]
    piece_6 = re.search(r'(Addrr?esses\s*\n)|(ADDRESSES\s*\n)',text_5)
    if piece_6:
        text_6 = text_5[piece_6.start()::]
        text_5 = text_5[0:piece_6.start()]
    else:
        piece_6 = piece_5
        text_6 = text_5[piece_6.start()::]

    if not(piece_1 or piece_2):
        return ((document_number,'','','','','','','','','','','','','PDF not standard format'))


    
    comp_name = re.search(r'(Name)|(Nome)|(To:?).*\n', text_0)
    ACN = re.search(r'((ACN)|(AC\s?N/AR\s?S)|(ARSN:?)|(ABN)|(A\.R\.S\.N\.)|(A\.C\.N\.)).*\n', text_0)

    ACN_2 = re.search(r'((if\s?applicable\))|(ACN)|(AC\s?N/AR\s?S)|(ARSN:?)|(ABN)|(A\.R\.S\.N\.)|(A\.C\.N\.)).*\n', text_1)
    comp_name_2 = re.search(r'((Name)|(Nome)).*\n', text_1)
        
    date_1 = re.search(r'(\s\d\d?\s?[-/\s.:;]\s?\w+\s?[-/\s.:;]\s?\d\d\d?\d?\s)|(\s\d\d?\s*\w+\s*\d\d\d\d\s)|(\s\d\d?\s*/\s*\d\d?\s*/\s*\d\d\d?\d?\s)|(\s\d\d?[/-]\w+[/-]\d\d\d?\d?\s)', text_1)
    if date_1:
        date_2 = re.search(r'(\s\d\d?\s?[-/\s.:;]\s?\w+\s?[-/\s.:;]\s?\d\d\d?\d?\s)|(\s\d\d?\s*\w+\s*\d\d\d\d\s)|(\s\d\d?\s*/\s*\d\d?\s*/\s*\d\d\d?\d?\s)|(\s\d\d?[/-]\w+[/-]\d\d\d?\d?\s)', text_1[date_1.end()::])
        if date_2:
            date_3 = re.search(r'(\s\d\d?\s?[-/\s.:;]\s?\w+\s?[-/\s.:;]\s?\d\d\d?\d?\s)|(\s\d\d?\s*\w+\s*\d\d\d\d\s)|(\s\d\d?\s*/\s*\d\d?\s*/\s*\d\d\d?\d?\s)|(\s\d\d?[/-]\w+[/-]\d\d\d?\d?\s)', text_1[date_2.end()::])
        
        
    ch = re.search(r'\n.*%\s*\d.*%.*\n',text_2)
    if ch: 
        ch = ch.group()
        ch = re.sub(r'\x03','',ch)
        ch = re.split(r'\s\s+',ch.strip())
        if len(ch)==5:
            ch_class = ch[0]
            previouse_shares = ch[1]
            previous_percen = ch[2]
            new_shares = ch[3]
            new_percent = ch[4]
        elif len(ch)==4:
            previouse_shares = ch[0]
            previous_percen = ch[1]
            new_shares = ch[2]
            new_percent = ch[3]


    try:
        comp_name = comp_name.group().strip()
        comp_name = re.sub(r'\s\s+',' ',comp_name)
        comp_name = re.sub(r'(T?[Oo]?:?\s?Comp[ao]ny\s?N[ao]me[/l]Scheme:?)|(To\s?:)','COMPANY NAME:', comp_name,  re.U)
        comp_name = comp_name.split(':')[-1].replace('_','').strip()
        print comp_name
    except AttributeError as e:
        pass
    try:
        comp_name_2 = comp_name_2.group().strip()
        comp_name_2 = comp_name_2[comp_name_2.find(' ')::].strip()
        if len(comp_name_2)>1:
            comp_name_2 = comp_name_2.replace('_','')
        else:
            comp_name_2 = ''   
    except AttributeError as e:
        pass
    try:
        ACN = ''.join(i for i in ACN.group() if i.isdigit() )
    except AttributeError as e:
        pass
    try:
         ACN_2 = ''.join(i for i in ACN_2.group() if i.isdigit() )
    except AttributeError as e:
        pass
    try:
        date_1 = date_1.group().replace(' ', '')
    except AttributeError as e:
        pass   
    try:
        date_2 = date_2.group().replace(' ', '')
    except AttributeError as e:
        pass
    try:
        date_3 = date_3.group().replace(' ', '')
    except AttributeError as e:
        pass
    # return ['',comp_name,'','','','','','','','','','','','',]
    result = [document_number,comp_name,ACN,ACN_2,comp_name_2,date_1,date_2,date_3,ch_class,previouse_shares,previous_percen,new_shares,new_percent,error_reason]
    for v in result:
        # str(v.replace('\u2019',''))
        if not v:
            result[-1] = 'PDF not standard format'
        # if 
    return tuple(result)
    # return [document_number,comp_name,ACN,ACN_2,comp_name_2,date_1,date_2,date_3,'','','','','',error_reason]

def cleaner_text(org_text):  
    '''Cleaning text for no alphabetic characters and other unnecessary symbols'''
    org_text = re.sub('\x0c','', org_text)
    org_text = re.sub(ur'\xcd','', org_text)
    org_text = re.sub(ur'\xa1','', org_text)
    org_text = re.sub(ur'\u201d','', org_text)
    org_text = re.sub(ur'\u2019','', org_text)
    org_text = re.sub(ur'\u201c','', org_text)
    if not org_text:
        return None        
    clean_text = ''.join(i for i in org_text if ord(i) < 128)
    return org_text


def get_all_file(fpath, form):
    '''scanning all files in dir'''
    fpdf = []
    flist = []
    for file in os.listdir(fpath):
        if file.endswith(form):
            fpdf.append(file)
    fpdf.sort()
    for i in xrange(2000):
        flist.append('{}/{}'.format(fpath, fpdf[i]))
    print len(flist)

    # flist = map(lambda x: '{}/{}'.format(fpath, x), fpdf)
    return flist

def pdftotext(pdf,page=None):
    '''extract text from pdf file'''
    print "to text = " + pdf
    if page is None:
        args = ['pdftotext', '-layout', '-q', pdf, '-']
    else:
        args = ['pdftotext', '-f', str(page), '-l', str(page), '-layout',
                '-q', pdf, '-']
    try:
        data = subprocess.check_output(args, universal_newlines=True)
    except subprocess.CalledProcessError, e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    # print type(data)
    return data
def pdf_to_xml(fname):
    print fname
    pdf = pdfquery.PDFQuery(fname)
    pdf.load()
    with open('{}/{}.xml'.format(XML_PATH,fname.split('/')[-1]), 'wb') as f:
        f.write(lxml.etree.tostring(pdf.tree, pretty_print=True, encoding="utf-8"))

def write_text(fname,data):
    with open('{}/{}.txt'.format(TEXT_PATH,fname.split('/')[-1]), 'w') as out_file:
        # writer = csv.writer(out_file)
        out_file.write(str(data))
    print 'write text file = ' + fname

def write_csv(data):
    '''write csv file'''
    with open(OUTPUT_NAME, 'a') as out_file:
        writer = csv.writer(out_file)
        print data
        writer.writerow(data)


def rest():
    s=u'''To:Company Name/Scheme\n
         To:Company Name/Scheme\n
         To:Company Name/Scheme\n
         To:Company Name/Scheme\n'''
    s = re.search(ur':C',s)
    print s.group()

    
if __name__ == '__main__':
    create_dir('TEXT_Example')
    create_dir('CSV_Example')
    create_dir(XML_PATH)
    main()
    # print list('')
    # parser('PDF_Example/01588989-1.pdf.txt')
	# get_all_pdf_file(PDF_PATH)
    # rest()