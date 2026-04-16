import streamlit as st
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from io import BytesIO

st.title("🧾 IRS 13614-C Visual Form Overlay Editor")

# -------------------------
# LOAD PDF AS IMAGE
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
pdf_path = BASE_DIR / "f13614c 2025.pdf"

pages = convert_from_path(str(pdf_path), dpi=200)

st.write(f"Pages loaded: {len(pages)}")

page_num = st.selectbox("Select page", range(len(pages)))

page_image = pages[page_num]

st.image(page_image, caption="PDF Page", use_container_width=True)

# -------------------------
# TEXT OVERLAY INPUTS
# -------------------------
st.subheader("Add Text Overlay")

if "overlays" not in st.session_state:
    st.session_state.overlays = []

text = st.text_input("Text")
x = st.number_input("X position", min_value=0, max_value=2000, value=100)
y = st.number_input("Y position", min_value=0, max_value=3000, value=100)

if st.button("Add Text"):
    st.session_state.overlays.append({
        "page": page_num,
        "text": text,
        "x": x,
        "y": y
    })

st.write("### Current Overlays")
st.json(st.session_state.overlays)

# -------------------------
# GENERATE FINAL PDF
# -------------------------
if st.button("Generate PDF"):
    output_images = []

    for i, img in enumerate(pages):
        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)

        for item in st.session_state.overlays:
            if item["page"] == i:
                draw.text((item["x"], item["y"]), item["text"], fill="black")

        output_images.append(img)

    buffer = BytesIO()
    output_images[0].save(
        buffer,
        format="PDF",
        save_all=True,
        append_images=output_images[1:]
    )
    buffer.seek(0)

    st.download_button(
        "⬇️ Download Filled PDF",
        data=buffer,
        file_name="filled_13614c_overlay.pdf",
        mime="application/pdf"
    )