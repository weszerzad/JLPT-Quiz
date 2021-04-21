from PyPDF2 import PdfFileReader, PdfFileWriter

if __name__ == "__main__":
    path = "/Users/phuocpham/OneDrive - Shizuoka University/jlpt files/Đề N1 từ 7-2010 đến 12-2018 bq.pdf"

    f = open(path, "rb")
    pdf = PdfFileReader(f)
    outlines = pdf.getOutlines()
    num_pages = pdf.getNumPages()

    outlines_dict = {}

    l1 = []
    l2 = []

    for ele in outlines:
        _start = str(ele.page).find("(")
        _end = str(ele.page).find(",")
        page_number = int(str(ele.page)[_start+1:_end]) - 6

        setattr(ele, "pageNumber", page_number)

        l1.append(ele.pageNumber)
        l2.append(ele.title)

    l1.append(num_pages + 1)

    for i in range(len(l1)-1):
        if i % 2 == 0:
            outlines_dict[(l1[i]-1, l1[i+1]-1)] = l2[i]
        else:
            outlines_dict[(l1[i] - 1, l1[i + 1] - 1)] = l2[i-1] + " " + l2[i]

    #Set up Writer
    i = 1
    for ele in outlines_dict:

        i += 1

        add_page_list = list(range(ele[0], ele[1]))

        pdfWriter = PdfFileWriter()
        for page_num in add_page_list:
            pdfWriter.addPage(pdf.getPage(page_num))

        with open("pdf_files/{}.pdf".format(outlines_dict[ele]), "wb") as ff:
            pdfWriter.write(ff)

    f.close()