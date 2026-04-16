import streamlit as st
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfObject
from pathlib import Path
from io import BytesIO

st.title("📄 Fill First PDF Field Only")

# -------------------------
# PDF PATH (FIXES FILE ERROR)
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
pdf_path = BASE_DIR / "f13614c 2025.pdf"

if not pdf_path.exists():
    st.error(f"PDF not found: {pdf_path}")
    st.stop()

# -------------------------
# READ PDF
# -------------------------
pdf = PdfReader(str(pdf_path))

# -------------------------
# EXTRACT FIELDS
# -------------------------
fields = []

for page in pdf.pages:
    if page.Annots:
        for annot in page.Annots:
            if annot.T:
                key = annot.T[1:-1]
                fields.append((key, annot))

if not fields:
    st.error("No editable fields found in PDF.")
    st.stop()

# ONLY FIRST FIELD
first_key, first_annot = fields[0]

st.write("### First field detected:")
st.code(first_key)

# -------------------------
# INPUT
# -------------------------
value = st.text_input("Enter value for first field")

# -------------------------
# SUBMIT
# -------------------------
if st.button("Generate PDF"):

    # enable appearance update
    if "/AcroForm" in pdf.Root:
        pdf.Root.AcroForm.update(
            PdfDict(NeedAppearances=PdfObject("true"))
        )

    # fill ONLY first field
    first_annot.update(
        PdfDict(V=str(value), AS=str(value))
    )
    first_annot.AP = None

    # write output
    output = BytesIO()
    PdfWriter().write(output, pdf)
    output.seek(0)

    st.success("Done!")

    st.download_button(
        "⬇ Download PDF",
        data=output,
        file_name="filled.pdf",
        mime="application/pdf"
    )