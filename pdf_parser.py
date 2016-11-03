import os
import scraperwiki
import pdfquery
import lxml.etree
import xml.etree.ElementTree as et
import pandas as pd
from shutil import copyfile
import re


XML_DIR = 'xml'
PDF_DIR = 'pdf'

def get_all_file(fpath, form):
    '''scanning all files in dir'''
    fpdf = []
    for file in os.listdir(fpath):
        if file.endswith(form):
            fpdf.append(file)
    flist = map(lambda x: '{}/{}'.format(fpath, x), fpdf)
    return flist


def copy_file():
    allPDF = get_all_file(PDF_ALLFILES,'.pdf')
    for file in allPDF:
        fnew = '{}/{}'.format(PDF_PATH, file.split('/')[-1])
        copyfile(file, fnew)
        print('file - ' + file + ' copy to - ' + fnew)


def pdf_to_xml_pdfquery(filename):
    pdf = pdfquery.PDFQuery('{}/{}.pdf'.format(PDF_DIR, filename))
    pdf.load()
    with open('{}/{}.xml'.format(XML_DIR, filename), 'wb') as f:
        f.write(lxml.etree.tostring(pdf.tree, pretty_print=True, encoding="utf-8"))


def pdf_to_xml(filename):
    with open("{}/{}.pdf".format(PDF_DIR, filename), "rb") as f:
        pdf = f.read()

    xml = scraperwiki.pdftoxml(pdf).replace('<b>', '').replace('</b>', '')

    try:
        tree = lxml.etree.fromstring(xml.encode('utf8'))        
    except lxml.etree.XMLSyntaxError:
        with open('{}/{}.xml'.format(XML_DIR, filename), 'w') as f:
            f.write(xml)
    else:
        for page in tree:
            for element in page:
                if element.text == ' ':
                    page.remove(element)

        with open('{}/{}.xml'.format(XML_DIR, filename), 'wb') as f:
            f.write(lxml.etree.tostring(tree, pretty_print=True))    

    print('Convert {} file to xml file'.format(filename))


def xml_parser(filename):

    try:
        xml = lxml.etree.parse('{}/{}.xml'.format(XML_DIR, filename))       
    except lxml.etree.XMLSyntaxError:
        return [filename, '', '', '', '', '', '', '', '', '', '', '', '', 'PDF may need OCR']

    data_list = [filename,]

    # --- company name ---
    try:
        company_name = str(xml.xpath('//page/text[contains(text(), "Company Name/Scheme")]')[0].getnext().text).strip()
        if 'ACN' in company_name:
            top = int(xml.xpath('//page/text[contains(text(), "Company Name/Scheme")]')[0].get('top'))
            path = '//page/text[@top=$top]'
            data_list.append(str(xml.xpath(path, top=top)[1].getnext().text).strip())
        else:
            data_list.append(company_name)
    except IndexError:
        data_list.append('')

    # --- acn ---
    try:
        acn = str(xml.xpath('//page/text[contains(text(), "ACN")]')[0].getnext().text).strip()
        if not ''.join(acn.split()).isdigit():
            top = int(xml.xpath('//page/text[contains(text(), "ACN")]')[0].get('top'))
            path = '//page/text[@top=$top]'
            data_list.append(str(xml.xpath(path, top=top)[1].text).strip())
        else:
            data_list.append(acn)
    except IndexError:
        data_list.append('')

    # --- acn/arsn ---
    try:
        acn_arsn = str(xml.xpath('//page/text[contains(text(), "ACN/ARSN (if applicable)")]')[0].getnext().text).strip()
        if not ''.join(acn_arsn.split()).isdigit():
            acn_arsn = str(xml.xpath('//page/text[contains(text(),"Name ")]')[0].getnext().getnext().text).strip()
            acn_arsn = acn_arsn[acn_arsn.find('ACN')+4:acn_arsn.find(')')]
            data_list.append(acn_arsn)
        else:
            data_list.append(acn_arsn)
    except IndexError:
        data_list.append('')

    # --- holder name ---
    try:
        holder_name = str(xml.xpath('//page/text[contains(text(),"Name ")]')[0].getnext().text).strip()
        data_list.append(holder_name)
    except IndexError:
        data_list.append('')

    # --- change date ---
    try:
        change_date = xml.xpath('//page/text[contains(text(), "substantial holder on")]')
        if len(change_date[0].getnext().text) <= 3:
            data_list.append(str(change_date[0].getnext().text + '/' + \
                change_date[0].getnext().getnext().getnext().text + '/' + \
                change_date[0].getnext().getnext().getnext().getnext().getnext().text).strip())
        else:
            data_list.append(str(change_date[0].getnext().text).strip())
    except IndexError:
        data_list.append('')

    # --- previous notice ---
    try:
        previous_notice = xml.xpath('//page/text[contains(text(), "company on")]')  
        if len(previous_notice[0].getnext().text) <= 3:
            data_list.append(str(previous_notice[0].getnext().text + '/' + \
                previous_notice[0].getnext().getnext().getnext().text + '/' + \
                previous_notice[0].getnext().getnext().getnext().getnext().getnext().getnext().text).strip())
        else:
            data_list.append(str(previous_notice[0].getnext().text).strip())
    except IndexError:
        data_list.append('')

    # --- previous date ---
    try:
        previous_date = xml.xpath('//page/text[contains(text(), "notice was dated")]')
        if len(previous_date[0].getnext().text) <= 3:
            data_list.append(str(previous_date[0].getnext().text + '/' + \
                previous_date[0].getnext().getnext().getnext().text + '/' + \
                previous_date[0].getnext().getnext().getnext().getnext().getnext().text).strip())
        else:
            data_list.append(str(previous_date[0].getnext().text).strip())
    except IndexError:
        data_list.append('')

    # --- class ---
    try:
        left = xml.xpath('//page/text[contains(text(), "Class of")]')[0].get('left')
        path = '//page/text[contains(text(), "Voting")]/following::text[@left=$left]'
        data_list.append(str(xml.xpath(path, left=left)[0].text).strip())
    except IndexError:
        data_list.append('')

    # --- previous shares ---
    try:
        left = xml.xpath('//page/text[contains(text(), "Class of")]')[0].get('left')
        path = '//page/text[contains(text(), "Voting")]/following::text[@left=$left]'
        data_list.append(str(xml.xpath(path, left=left)[0].getnext().text).strip())
    except (IndexError, AttributeError):
        data_list.append('')

    # --- previous percent ---
    try:
        left = xml.xpath('//page/text[contains(text(), "Class of")]')[0].get('left')
        path = '//page/text[contains(text(), "Voting")]/following::text[@left=$left]'
        data_list.append(str(xml.xpath(path, left=left)[0].getnext().getnext().text).strip())
    except (IndexError, AttributeError):
        data_list.append('')

    # --- new shares ---
    try:
        left = xml.xpath('//page/text[contains(text(), "Class of")]')[0].get('left')
        path = '//page/text[contains(text(), "Voting")]/following::text[@left=$left]'
        data_list.append(str(xml.xpath(path, left=left)[0].getnext().getnext().getnext().text).strip())
    except (IndexError, AttributeError):
        data_list.append('')

    # --- new percent ---
    try:
        left = xml.xpath('//page/text[contains(text(), "Class of")]')[0].get('left')
        path = '//page/text[contains(text(), "Voting")]/following::text[@left=$left]'
        data_list.append(str(xml.xpath(path, left=left)[0].getnext().getnext().getnext().getnext().text).strip())
    except (IndexError, AttributeError):
        data_list.append('')

    if all(data_list[1:]):
        data_list.append('Success')
    elif any(data_list[1:]):
        data_list.append('PDF not standard format')
    else:
        data_list.append('PDF may need OCR')
    
    return data_list


def main():
    filenames = [os.path.splitext(i)[0] for i in os.listdir(XML_DIR)]

    # for filename in filenames:
    #     pdf_to_xml(filename)

    data = {
        'Document number/name': [],
        'Company name': [],
        'ACN': [],
        'ACN/ARSN (if applicable)': [],
        'Holder Name': [],
        'Change Date': [],
        'Previous Notice': [],
        'Previous Date': [],
        'Class': [],
        'Previouse Shares': [],
        'Previous Percent': [],
        'New Shares': [],
        'New Percent': [],
        'Error reason/Success': [],
        }

    for index, filename in enumerate(filenames[:50]):
        data['Document number/name'].append(xml_parser(filename)[0])
        data['Company name'].append(xml_parser(filename)[1])
        data['ACN'].append(xml_parser(filename)[2])
        data['ACN/ARSN (if applicable)'].append(xml_parser(filename)[3])
        data['Holder Name'].append(xml_parser(filename)[4])
        data['Change Date'].append(xml_parser(filename)[5])
        data['Previous Notice'].append(xml_parser(filename)[6])
        data['Previous Date'].append(xml_parser(filename)[7])
        data['Class'].append(xml_parser(filename)[8])
        data['Previouse Shares'].append(xml_parser(filename)[9])
        data['Previous Percent'].append(xml_parser(filename)[10])
        data['New Shares'].append(xml_parser(filename)[11])
        data['New Percent'].append(xml_parser(filename)[12])
        data['Error reason/Success'].append(xml_parser(filename)[13])

        if xml_parser(filename)[13] != 'PDF may need OCR':
            print('{}- '.format(index + 1) + 'SUCCESS: successfully parse ' + filename + ' file')   
        else:
            print('{}- '.format(index + 1) + 'ERROR: could not parse ' + filename + ' file')          

    df = pd.DataFrame(data, columns = [
            'Document number/name', 
            'Company name',
            'ACN', 
            'ACN/ARSN (if applicable)', 
            'Holder Name',
            'Change Date', 
            'Previous Notice', 
            'Previous Date', 
            'Class', 
            'Previouse Shares',
            'Previous Percent',
            'New Shares',
            'New Percent',
            'Error reason/Success',
            ])

    df.to_csv('output.csv', index=False)


if __name__ == "__main__":
    print('-' * 50)
    print('***** BEGIN *****')
    print('-' * 50)
    main()
    print('-' * 50)
    print('***** END *****')
    print('-' * 50)