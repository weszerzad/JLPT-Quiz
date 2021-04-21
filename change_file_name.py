import os
for count, filename in enumerate(os.listdir("pdf_files")):
    src = "pdf_files/" + filename
    # print(src)

    filename = filename.replace("真题", " Test")
    if "封底" in filename:
        filename = filename.replace("封底", "Answer")

    dst = "pdf_files/" + filename
    # print(dst)

    os.rename(src, dst)