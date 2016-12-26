# -*- coding: utf-8 -*-
import subprocess
import os
import re
import csv
import time
from dateutil.parser import parse
import shutil
from shutil import copyfile

title = ('Document number/name', 'Company name', 'ACN', 'ACN/ARSN (if applicable)',
         'Holder Name', 'Change Date', 'Previous Notice', 'Previous Date', 'Class',
         'Previouse Shares', 'Previous Percent', 'New Shares', 'New Percent', 'Error reason/Success')
monthDict = {}

# OUTPUT_NAME = '{}.csv'.format(time.strftime("%c"))
OUTPUT_NAME = 'OUTPUT.csv'
PDF_PATH = 'PDF_Example'

def main():
    print 'start'
    write_csv(title)
    fpath = get_all_file(PDF_PATH, '.pdf')
    for pdf in fpath:
        data_text = pdftotext(pdf)
        clean_text = str(cleaner_text(data_text))
        final_data = parser(clean_text,pdf)
        write_csv(final_data)



def parser(text,ftext):
    '''Find information from in text file'''
    print 'start parse file: ' + ftext

    document_number = ftext.split('/')[-1]
    document_number = document_number.split('.')[0]
    
    if text == 'None':
        return (document_number, '', '', '', '', '', '', '', 
            '', '', '', '', '', 'PDF may need OCR')

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
    error_reason = 'Success'
    
    search_change = re.compile(r'''There\swas\sa\schange''', re.X)
    
    search_date = re.compile(r'''(\s\d\d?[_\s]?[-/\s.:;][_\s]?\d\d?
                                [_\s]?[-/\s.:;][_\s]?\d\d\d?\d?)|
                                (\s\d\d?[_\s]?[-/\s.:;][_\s]?\w+
                                [_\s]?[-/\s.:;][_\s]?\d\d\d?\d?)''', re.X)
    
    search_comp_name = re.compile(r'((Name)|(Nome)|(To:?)|(TO:)).*\n')
    search_ACN = re.compile(r'''((ACN)|(AC\s?N/AR\s?S)|
                                 (ARSN:?)|
                                 (AR?BN)|
                                 (A\.R\.S\.N\.)|
                                 (A\.C\.N\.)).*\n''',re.X)
    search_ACN_2 = re.compile(r'''((if\s?applicable\))|
                                    (ACN)|
                                    (AC\s?N/AR\s?S)|
                                    (ARSN:?)|
                                    (ABN)|
                                    (A\.R\.S\.N\.)|
                                    (A\.C\.N\.)).*\n''',re.X)
    search_comp_name_2 = re.compile(r'((Name)|(Nome)).*\n',re.I)
    serch_ch = re.compile(r'\n.*(%)|(o/o)\s*\d.*(%)|(o/o).*\n')
    search_piece_1 = re.compile(r'''([1lL]\s*.\s*D,?eta[ilI]ls.*\n)|
                                    ([1l]\s*.\s*DETAILS.*\n)|
                                    (l.\s*Detoilsof)|
                                    (1.\sDeloilsof)|
                                    (1\. Details)|
                                    (1\. Dcttlil)''',re.X)
    search_piece_2 = re.compile(r'''(2. Previous and present voting power)|
                                    (2.\s*Pr[ce]v[il]ous)|
                                    (2.\s*Changes)|
                                    (2\.\s*PREV[lI]OUS)|
                                    (2\. Pr[eo]vious )|
                                    (2.\s*Details)''',re.X)
    
    piece_1 = search_piece_1.search(text)
    if piece_1:
        text_0 = text[0:piece_1.start()]
        text_1 = text[piece_1.start()::]
    else:
        piece_1 = re.search(r'^.*\n', text)
        text_0 = text
        text_1 = text
    piece_2 = search_piece_2.search(text_1)
    if piece_2:
        text_2 = text_1[piece_2.start()::]
        text_1 = text_1[0:piece_2.start()]
    else:
        piece_2 = piece_1
        text_2 = text_1[piece_2.start()::]

    if not (piece_1 or piece_2):
        return ((document_number, '', '', '', '', '', '', '', ''
                ,'', '', '', '', 'PDF not standard format'))

    comp_name = search_comp_name.search(text_0)
    ACN = search_ACN.search(text_0)
    comp_name_2 = search_comp_name_2.search(text_1)
    ACN_2 = search_ACN_2.search(text_1)
    change = search_change.search(text)
    
    if change:
        textDate = text[change.start()::]
        date_1 = search_date.search(textDate)
        if date_1:
            textDate = textDate[date_1.end()::]
            date_2 = search_date.search(textDate)
            if date_2:  
                date_3 = search_date.search(textDate[date_2.end()::])
    
    ch = serch_ch.search(text_2)
    if ch:
        ch = ch.group()
        ch = re.sub(r'\x03', '', ch)
        ch = re.split(r'\s\s+', ch.strip())
        if len(ch) == 5:
            ch_class = ch[0]
            previouse_shares = ch[1]
            previous_percen = ch[2]
            new_shares = ch[3]
            new_percent = ch[4]
        elif len(ch) == 4:
            previouse_shares = ch[0]
            previous_percen = ch[1]
            new_shares = ch[2]
            new_percent = ch[3]

    try:
        comp_name = comp_name.group().strip()
        comp_name = re.sub(r'\s\s+', ' ', comp_name)
        comp_name = re.sub(r'''(T?[Oo]?:?\s?Comp[ao]ny\s?N[ao]me[/l]Scheme:?)|
                             (To\s?:)''', 'COMPANY NAME:', comp_name, re.X)
        comp_name = comp_name.split(':')[-1].replace('_', '').strip()
    except AttributeError as e:
        pass
    
    try:
        comp_name_2 = comp_name_2.group().strip()
        comp_name_2 = comp_name_2[comp_name_2.find(' ')::].strip()
        if len(comp_name_2) > 1:
            comp_name_2 = comp_name_2.replace('_', '')
        else:
            comp_name_2 = ''
    except AttributeError as e:
        pass
    
    try:
        ACN = ''.join(i for i in ACN.group() if i.isdigit())
    except AttributeError as e:
        pass
    
    try:
        ACN_2 = ''.join(i for i in ACN_2.group() if i.isdigit())
    except AttributeError as e:
        pass
    
    try:
        date_1 = clear_date(date_1.group())
    except AttributeError as e:
        pass
    
    try:
        date_2 = clear_date(date_2.group())
    except AttributeError as e:
        pass
    
    try:
        # date_3 = date_3.group().replace(' ', '')
        date_3 = clear_date(date_3.group())
    except AttributeError as e:
        pass
    result = [document_number, comp_name, ACN, ACN_2, 
              comp_name_2, date_1, date_2, date_3, ch_class, previouse_shares,
              previous_percen, new_shares, new_percent, error_reason]
    
    for v in result:
        if not v:
            result[-1] = 'PDF not standard format'
    return tuple(result)


def clear_date(date):
    date = date.strip()
    date = re.sub(r'\n','',date)
    date = re.sub(r'[-/\s.:;]','/',date)
    date = re.sub(r'//+','/',date)
    try:
        dt = parse(date)
        date = dt.strftime('%d/%m/%Y')
    except ValueError as e:
        date = ''
    
    return date

def cleaner_text(org_text):
    '''Cleaning text for no alphabetic characters and other unnecessary symbols'''
    org_text = re.sub('\x0c', '', org_text)
    org_text = re.sub(ur'\xcd', '', org_text)
    org_text = re.sub(ur'\xa1', '', org_text)
    org_text = re.sub(ur'\u201d', '', org_text)
    org_text = re.sub(ur'\u2019', '', org_text)
    org_text = re.sub(ur'\u201c', '', org_text)
    if not org_text:
        return None
    clean_text = ''.join(i for i in org_text if ord(i) < 128)
    return org_text

def clear_dir(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): 
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def get_all_file(fpath, form):
    '''scanning all files in dir'''
    fpdf = []
    flist = []
    for file in os.listdir(fpath):
        if file.endswith(form):
            fpdf.append(file)
    for i in fpdf:
        flist.append(os.path.abspath(os.path.join(fpath, i)))
    return flist


def pdftotext(pdf, page=None):
    '''extract text from pdf file'''
    # print "to text = " + pdf
    if page is None:
        args = ['pdftotext', '-layout', '-q', pdf, '-']
    else:
        args = ['pdftotext', '-f', str(page), '-l', str(page), '-layout',
                '-q', pdf, '-']
    try:
        data = subprocess.check_output(args, universal_newlines=True)
    except subprocess.CalledProcessError, e:
        print e
    return data


def write_text(fname, data):
    form = '.txt'
    head, name = os.path.split(fname)
    path = os.path.abspath(os.path.join(TEXT_PATH, name.split('.')[0] + form))
    with open(path, 'w') as out_file:
        # writer = csv.writer(out_file)
        out_file.write(str(data))
        out_file.close()
    print 'write text file = ' + path


def write_csv(data):
    '''write csv file'''
    with open(OUTPUT_NAME, 'a') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(data)
        out_file.close()


if __name__ == '__main__':
    main()