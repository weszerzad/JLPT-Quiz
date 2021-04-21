from PyPDF2 import PdfFileReader

def pretty_write(l, file_name):
    with open(file_name, "w") as text_file:
        for d in l:
            for key, value in d.items():
                text_file.write(str(key) + '=' + str(value))
                text_file.write("\n")
            text_file.write("\n")

def extract_information(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
        outlines = pdf.getOutlines()

    txt = f"""
    Information about {pdf_path}:     
    
    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {number_of_pages}
    Outlines:    
    """

    print(txt)
    pretty_write(outlines, "outlines.txt")

    return information

if __name__ == "__main__":
    path = "/Users/phuocpham/OneDrive - Shizuoka University/jlpt files/Đề N1 từ 7-2010 đến 12-2018 bq.pdf"
    extract_information(path)