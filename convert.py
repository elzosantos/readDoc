import fitz # PyMuPDF

pdf_filename = "História_do_Brasil.pdf"
txt_filename = "historia.txt"

with fitz.open(pdf_filename) as doc:
    text = ""
    for page in doc:
        text += page.get_text()

with open(txt_filename, "w", encoding="utf-8") as txt_file:
    txt_file.write(text)

print(f"Texto extraído de '{pdf_filename}' e salvo em '{txt_filename}'")