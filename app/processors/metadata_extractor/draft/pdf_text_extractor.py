# bhttps://stackoverflow.com/questions/34837707/how-to-extract-text-from-a-pdf-file

from PyPDF2 import PdfReader

reader = PdfReader("example.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

import fitz  # install using: pip install PyMuPDF

with fitz.open("my.pdf") as doc:
    text = ""
    for page in doc:
        text += page.get_text()

print(text)

import PyPDF2

# creating a pdf file object
pdfFileObj = open('example.pdf', 'rb')

# creating a pdf reader object
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

# printing number of pages in pdf file
print(pdfReader.numPages)

# creating a page object
pageObj = pdfReader.getPage(0)

# extracting text from page
print(pageObj.extractText())

# closing the pdf file object
pdfFileObj.close()
