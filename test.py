# -*- coding: utf-8 -*-
import subprocess
import os
import re
import shutil
import csv
from shutil import copyfile
PDF_PATH = '2000'
TEXT_PATH = 'TEXT_Example'



def get_all_file(fpath, form):
    '''scanning all files in dir'''
    fpdf = []
    flist = []
    for file in os.listdir(fpath):
        if file.endswith(form):
            fpdf.append(file)
    fpdf.sort()
    # for i in xrange(2000):
    #     flist.append('{}/{}'.format(fpath, fpdf[i]))
    # print len(flist)

    flist = map(lambda x: '{}/{}'.format(fpath, x), fpdf)
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
        return ('','','','','','','','','','','','','','PDF may need OCR')
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


    
    comp_name = re.search(r'(Name)|(Nome)|(To:?).*\n', text_0)
    ACN = re.search(r'((ACN)|(AC\s?N/AR\s?S)|(ARSN:?)|(ABN)|(A\.R\.S\.N\.)|(A\.C\.N\.)).*\n', text_0)

    ACN_2 = re.search(r'((if\s?applicable\))|(ACN)|(AC\s?N/AR\s?S)|(ARSN:?)|(ABN)|(A\.R\.S\.N\.)|(A\.C\.N\.)).*\n', text_1)
    comp_name_2 = re.search(r'((Name)|(Nome)).*\n', text_1)
        
    date_1 = re.search(r'(\d\d?\s?[-/\s.:;]\s?\w+\s?[-/\s.:;]\s?\d\d\d?\d?)|(\d\d?\s*\w+\s*\d\d\d\d)|(\d\d?\s*/\s*\d\d?\s*/\s*\d\d\d?\d?)|(\d\d?[/-]\w+[/-]\d\d\d?\d?)', text_1)
    if date_1:
        date_2 = re.search(r'(\d\d?\s?[-/\s.:;]\s?\w+\s?[-/\s.:;]\s?\d\d\d?\d?)|(\d\d?\s*\w+\s*\d\d\d\d)|(\d\d?\s*/\s*\d\d?\s*/\s*\d\d\d?\d?)|(\d\d?[/-]\w+[/-]\d\d\d?\d?)', text_1[date_1.end()::])
        if date_2:
            date_3 = re.search(r'(\d\d?\s?[-/\s.:;]\s?\w+\s?[-/\s.:;]\s?\d\d\d?\d?)|(\d\d?\s*\w+\s*\d\d\d\d)|(\d\d?\s*/\s*\d\d?\s*/\s*\d\d\d?\d?)|(\d\d?[/-]\w+[/-]\d\d\d?\d?)', text_1[date_2.end()::])
        
        
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


    print ftext

    # # else:
    #     fnew = '{}/{}'.format('Erorrs_file', ftext.split('/')[-1])
    #     copyfile(ftext,fnew)
    # print ftext
    # print '----------------------------------------------------------'
    # print '----------------------------------------------------------'
    # print '----------------------------------------------------------'
    # print text_0
    # print '----------------------------------------------------------'
    # print text_1
    # print '----------------------------------------------------------'
    # print text_2
    # print '----------------------------------------------------------'
    print text_3
    # print '----------------------------------------------------------'
    # print text_4
    # print '----------------------------------------------------------'
    # print text_5
    # print '----------------------------------------------------------'
    # print text_6
    # print '----------------------------------------------------------'

















    # try:
    #     # print comp_name.group()
    #     ACN = ''.join(i for i in ACN.group() if i.isdigit() )
    #     ACN_2 = ''.join(i for i in ACN_2.group() if i.isdigit() )
    #     comp_name_2 = comp_name_2.group().strip()
    #     comp_name_2 = comp_name_2[comp_name_2.find(' ')::].strip()
    #     if len(comp_name_2)>1:
    #         comp_name_2 = comp_name_2
    #     else:
    #         comp_name_2 = ''
    #     date_1 = date_1.group().replace(' ', '')
    #     date_2 = date_2.group().replace(' ', '')
    #     date_3 = date_3.group().replace(' ', '')
    # except AttributeError as e:
    #     pass
    # # return ['',comp_name,'','','','','','','','','','','','',]
    # result = (document_number,comp_name,ACN,ACN_2,comp_name_2,date_1,date_2,date_3,'','','','','',error_reason)
    # for v in result:
    #     if not v:
    #         error_reason = 'PDF not standard format'

    # return (document_number,comp_name,ACN,ACN_2,comp_name_2,date_1,date_2,date_3,'','','','','',error_reason)

    # if not piece_1:
    #     return None
    # else:
    # text = re.sub(ur'\xcd','', text)
    # text = re.sub(ur'\xa1','', text)
    # text = re.sub(ur'\u201d','', text)
    # text = re.sub(ur'\u2019','', text)
    # text = re.sub(ur'\u201c','', text)
    # text = re.sub(ur'\sTo: Company Name/Scheme','COMPANY NAME:', text, re.U) 
    # text = re.sub(ur'\sTo:Company Name/Scheme','COMPANY NAME:', text,  re.U) 
    # text = re.sub(ur'Iq:?\s*Comp[ao]ny\s*N[ao]me[/l]Scheme:?','COMPANY NAME:', text,  re.U) 
    # text = re.sub(ur'þ\s*Comp[ao]ny\s*N[ao]me[/l]Scheme:?','COMPANY NAME:', text,  re.U)
    # text = re.sub(ur'fq\s*Comp[ao]ny\s*N[ao]me[/l]Scheme:?','COMPANY NAME:', text,  re.U)
    # text = re.sub(ur'(T?[Oo]?:?\s*Comp[ao]ny\s*N[ao]me[/l]Scheme:?)|(To:)','COMPANY NAME:', text,  re.U)
    # comp_name = re.findall(r'(?<=COMPANY NAME:).*\n' , text)
    # comp_name = re.findall(r'\nCOMPANY NAME:.*\n' , text)
    # comp_name = comp_name[0].replace('_','')
    # comp_name = re.sub(ur'\s\s+','', comp_name, re.U)
    # comp_name = comp_name.split(':')[-1].strip()DETAILS
    
    

def create_dir(dirc):
    if not os.path.exists(dirc):
        os.makedirs(dirc)

def copy_file():
    allPDF = get_all_file(PDF_PATH,'.pdf')
    for i, file in enumerate(allPDF):
        fnew = '{}/{}'.format('2000', file.split('/')[-1])
        copyfile(file,fnew)
        print 'file - ' + file + ' copy to - ' + fnew
def write_log(data):
     with open('log.log', 'a') as file:
        file.write(data)
        file.close()

def break_to_pieces(ftext):
    with open(ftext, 'r') as file:
        text = file.read()
        file.close()
    print 'File: {} in proces'.format(ftext)
    if text == 'None':
        return None
    isformat = re.findall(r'F[Oo][Rr][Mm]\s*60[435{]', text)
    if isformat:
        test(text, ftext)
    else:
        isformat = re.findall(r'Form 604', text)
        if not isformat:
            pass
            # write_log(ftext + '\n')
            fnew = '{}/{}'.format('Erorrs_file', ftext.split('/')[-1])
            # copyfile(ftext,fnew)
        else:
            test(text, ftext)

    # piece_1 = re.search(r'\n\s*1.?\s*Details\s*of\s*substantial\s*holder\s*(1).*\n',text)
    # piece_1 = re.findall(r'\n\s*1.\s*Details\s*of\s*substantial\s*(holder)?\s*.*\n',text)
    # if piece_1:
    #     mark = '' 
    # else:
    #     mark = 'don`t'
    #     log = 'in file: {} {} find piece_1: {}\n'.format(ftext, mark, piece_1)
    #     write_log(log)
def test(text, ftext):
    piece_1 = re.search(ur'([1l]\s*.\s*D,?eta[il]ls.*\n)|([1l]\s*.\s*DETAILS.*\n)', text,  re.U)
    print piece_1.group()
    text_1 = text[0:piece_1.start()-1]
    comp_name = re.search(ur'N[ao]me', text_1,  re.U)


def rm():
    txt = get_all_file('Erorrs_file', '.txt')
    map(lambda x: os.remove('{}/{}'.format(TEXT_PATH,x.split('/')[-1])),txt)

def open_csv(fpath):
    
    with open(fpath, 'r') as file:
        file_csv = csv.DictReader(file)
        response = list(file_csv)


        # map(lambda x: response.add(x),file_csv)
        for row in response:
            print row



if __name__ == '__main__':
    create_dir('Erorrs_file')
    # shutil.rmtree('Erorrs_file')
    # create_dir('Erorrs_file')
    # rm()
    for i in get_all_file(TEXT_PATH,'.txt'):
        # parser('TEXT_Example/01298372-1.pdf.txt')
        parser(i)
        # break
    # copy_file()
    # open_csv('CSV_PDFs.csv')