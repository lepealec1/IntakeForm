import streamlit as st
import os
from io import BytesIO

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


# -------------------------
# APP SETUP
# -------------------------
st.title("PDF Overlay Builder (Working Version)")

if "placed_items" not in st.session_state:
    st.session_state.placed_items = []


# -------------------------
# LOAD PDF
# -------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
default_pdf = os.path.join(base_dir, "f13614c.pdf")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
use_local = st.checkbox("Use local PDF", value=False)

pdf_bytes = None

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    st.success("Using uploaded PDF")

elif use_local and os.path.exists(default_pdf):
    with open(default_pdf, "rb") as f:
        pdf_bytes = f.read()
    st.success("Using local PDF")

else:
    st.warning("No PDF loaded")


# -------------------------
# ADD TEXT
# -------------------------
st.subheader("Add Text")

text = st.text_input("Text", "Hello World")
x = st.number_input("X", value=100)
y = st.number_input("Y", value=700)
page = st.number_input("Page (0-based)", value=0, min_value=0)

if st.button("Add Text"):
    st.session_state.placed_items.append({
        "text": text,
        "x": x,
        "y": y,
        "page": page
    })


# -------------------------
# SHOW ITEMS
# -------------------------
st.subheader("Items")

for i, item in enumerate(st.session_state.placed_items):
    st.write(f"{i+1}. '{item['text']}' at ({item['x']}, {item['y']}) page {item['page']}")


# -------------------------
# GENERATE PDF
# -------------------------
if pdf_bytes and st.button("Generate PDF"):

    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        writer = PdfWriter()

        # copy pages
        for p in reader.pages:
            writer.add_page(p)

        overlays = {}

        # -------------------------
        # BUILD OVERLAYS
        # -------------------------
        for item in st.session_state.placed_items:

            page_num = item["page"]
            text = item["text"]
            x = item["x"]
            y = item["y"]

            if page_num not in overlays:
                buffer = BytesIO()
                c = canvas.Canvas(buffer)
                overlays[page_num] = (buffer, c)
            else:
                buffer, c = overlays[page_num]

            c.drawString(float(x), float(y), text)

        # -------------------------
        # FINALIZE + MERGE
        # -------------------------
        for page_num, (buffer, c) in overlays.items():

            c.save()          # CRITICAL
            buffer.seek(0)

            overlay_pdf = PdfReader(buffer)

            if page_num < len(writer.pages):
                writer.pages[page_num].merge_page(
                    overlay_pdf.pages[0]
                )

        # -------------------------
        # OUTPUT
        # -------------------------
        output = BytesIO()
        writer.write(output)
        output.seek(0)

        st.download_button(
            "Download PDF",
            data=output,
            file_name="output.pdf",
            mime="application/pdf"
        )

        st.success("PDF generated successfully!")

    except Exception as e:
        st.error(f"Error: {e}")