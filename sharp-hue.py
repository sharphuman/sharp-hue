import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# --- 1. CONFIG & BRANDING (The SharpHuman Style Guide) ---
st.set_page_config(
    page_title="SharpHuman // Hue Shift",
    page_icon="🧠",
    layout="centered"
)

# Custom CSS to force the "Neon/Black" aesthetic
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #050505;
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Text Colors */
    h1, h2, h3 {
        color: #00ff9d !important; /* Neon Green */
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    p, label, .stMarkdown {
        color: #e0e0e0 !important;
    }

    /* Buttons */
    div.stButton > button {
        background-color: transparent;
        color: #00ff9d;
        border: 2px solid #00ff9d;
        border-radius: 0px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #00ff9d;
        color: #000000;
        box-shadow: 0 0 15px #00ff9d;
    }
    
    /* Loading Bar */
    .stProgress > div > div > div > div {
        background-color: #bd00ff;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC ENGINE ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def apply_gradient_map(gray_image, color_start, color_end):
    # Normalize image to 0-1 float
    norm = gray_image.astype(float) / 255.0
    
    # Linear Interpolation
    r = color_start[0] + (color_end[0] - color_start[0]) * norm
    g = color_start[1] + (color_end[1] - color_start[1]) * norm
    b = color_start[2] + (color_end[2] - color_start[2]) * norm
    
    # Merge back to BGR
    result = cv2.merge((b, g, r))
    return np.clip(result, 0, 255).astype(np.uint8)

# --- 3. UI LAYOUT ---
st.title("SharpHuman // Neural Color")
st.markdown("Injecting gradient maps into visual assets.")

# PRESETS
presets = {
    "Cyberpunk Classic": ("#0011ff", "#ff00dd"),  # Deep Blue -> Hot Pink
    "Matrix Code":       ("#003300", "#00ff41"),  # Dark Green -> Bright Green
    "Vaporwave":         ("#5500ff", "#00ffff"),  # Purple -> Cyan
    "Inferno":           ("#550000", "#ffcc00"),  # Dark Red -> Gold
    "Deep Freeze":       ("#000033", "#0088ff"),  # Black-Blue -> Ice Blue
    "SharpHuman Official": ("#050505", "#00ff9d"), # Black -> Neon Green
}

col1, col2 = st.columns(2)
with col1:
    mode = st.selectbox("Select Aesthetic Preset", ["Custom"] + list(presets.keys()))

if mode != "Custom":
    c1_hex, c2_hex = presets[mode]
    # We hide the pickers but keep the logic clean
    # showing small colored blocks instead would be cool, but simple for now
else:
    c1_hex = st.color_picker("Shadow Tone", "#0000ff")
    c2_hex = st.color_picker("Highlight Tone", "#ff00ff")

uploaded_file = st.file_uploader("Drop the Neon Asset", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    try:
        # Load Image safely
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1) # 1 forces loading as color

        # CRITICAL FIX: Handle PNG Transparency
        # If the image has 4 channels (RGBA), convert to 3 channels (BGR)
        # otherwise bitwise operations crash.
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # PROCESS
        # 1. Mask Background (Keep black pixels black)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Threshold: anything brighter than 15/255 is considered "Neon"
        _, mask = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)

        # 2. Prepare Colors
        c1_rgb = hex_to_rgb(c1_hex)
        c2_rgb = hex_to_rgb(c2_hex)

        # 3. Apply Gradient
        gradient_img = apply_gradient_map(gray, c1_rgb, c2_rgb)

        # 4. Masking
        # Only apply the gradient where the mask is active
        final_img = cv2.bitwise_and(gradient_img, gradient_img, mask=mask)

        # DISPLAY (Converted to RGB for browser)
        # using 'use_container_width' to fix the deprecation warning
        st.image(cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB), caption="Neural Grade Applied", use_container_width=True)

        # DOWNLOAD
        result_pil = Image.fromarray(cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB))
        buf = io.BytesIO()
        result_pil.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="Download Asset",
            data=byte_im,
            file_name="sharphuman_graded.png",
            mime="image/png"
        )
    except Exception as e:
        st.error(f"Processing Error: {e}")
        st.info("Try uploading a standard JPG or PNG file.")
