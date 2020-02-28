import PyPDF2
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


#converts pdf, returns its text content as a string
def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text
def page_by_page_extract(pdf_url):
    pdfFileObj = open(pdf_url, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    num_pages = pdfReader.numPages
    extracted_text = {}
    for page in range(0, num_pages, 1):
        page_text = str(convert(pdf_url, [page]))
        page_text = page_text.replace(u"\n", u' ')
        page_text = page_text.replace(u'\xa0',u' ')
        page_text = page_text.replace(u'\x0c', u' ')
        extracted_text[page] = page_text
    return extracted_text
