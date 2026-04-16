import streamlit as st
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfObject
from pathlib import Path
import re
from io import BytesIO

st.title("📄 IRS 13614-C Auto Form Filler")

# -------------------------
# LOAD PDF
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
pdf_path = BASE_DIR / "f13614c 2025.pdf"

pdf = PdfReader(str(pdf_path))

# -------------------------
# AUTO LABEL FUNCTION
# -------------------------
def make_label(name):
    name = re.sub(r"\[\d+\]", "", name)
    name = name.replace(".", " ").replace("_", " ")
    name = re.sub(r"(?<!^)(?=[A-Z])", " ", name)
    return " ".join(name.split()).title()

# -------------------------
# EXTRACT FIELDS
# -------------------------
fields = {}

for page in pdf.pages:
    if page.Annots:
        for annot in page.Annots:
            if annot.T:
                key = annot.T[1:-1]
                fields[key] = annot

if not fields:
    st.error("No fillable fields found in PDF.")
    st.stop()

# -------------------------
# STREAMLIT FORM
# -------------------------
user_inputs = {}

with st.form("form"):
    st.subheader("Fill IRS Form")

    for raw_name in sorted(fields.keys()):
        label = make_label(raw_name)
        user_inputs[raw_name] = st.text_input(label, key=raw_name)

    submitted = st.form_submit_button("Generate PDF")

# -------------------------
# GENERATE + WRITE PDF (ONLY ON SUBMIT)
# -------------------------
if submitted:

    # FORCE APPEARANCE UPDATE (CRITICAL)
    if "/AcroForm" in pdf.Root:
        pdf.Root.AcroForm.update(
            PdfDict(NeedAppearances=PdfObject("true"))
        )

    # WRITE VALUES INTO PDF
    for page in pdf.pages:
        if page.Annots:
            for annot in page.Annots:
                if annot.T:
                    key = annot.T[1:-1]

                    if key in user_inputs:
                        value = user_inputs[key]

                        annot.update(
                            PdfDict(
                                V=str(value),
                                AS=str(value)
                            )
                        )

                        annot.AP = None

    # -------------------------
    # EXPORT PDF TO MEMORY
    # -------------------------
    output = BytesIO()
    PdfWriter().write(output, pdf)
    output.seek(0)

    st.success("PDF generated successfully!")

    st.download_button(
        "⬇️ Download Filled 13614-C",
        data=output,
        file_name="filled_13614c.pdf",
        mime="application/pdf"
    )