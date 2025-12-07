import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# --- 1. AESTHETIC LOGIC ENGINE ---
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def apply_gradient_map(gray_image, color_start, color_end):
    """
    This uses Linear Interpolation (Lerp) to blend two colors 
    based on how bright the pixel is.
    Darker pixels -> Color Start
    Brighter pixels -> Color End
    """
    # Normalize image to 0-1 float
    norm = gray_image.astype(float) / 255.0
    
    # Create the color channels
    # Formula: Result = Start + (End - Start) * Intensity
    r = color_start[0] + (color_end[0] - color_start[0]) * norm
    g = color_start[1] + (color_end[1] - color_start[1]) * norm
    b = color_start[2] + (color_end[2] - color_start[2]) * norm
    
    # Merge back to an image
    result = cv2.merge((b, g, r)) # OpenCV uses BGR
    return np.clip(result, 0, 255).astype(np.uint8)

# --- 2. STREAMLIT UI ---
st.set_page_config(page_title="SharpHuman: Neural Color", layout="centered")

st.title("SharpHuman // Neural Color Grade")
st.markdown("""
<style>
    body {color: #00ff9d; background-color: black;}
</style>
*Injecting gradient maps into visual assets.*
""", unsafe_allow_html=True)

# PRESETS
presets = {
    "Cyberpunk Classic": ("#0011ff", "#ff00dd"),  # Deep Blue to Hot Pink
    "Matrix Code":       ("#003300", "#00ff41"),  # Dark Green to Bright Green
    "Vaporwave":         ("#5500ff", "#00ffff"),  # Purple to Cyan
    "Inferno":           ("#550000", "#ffcc00"),  # Dark Red to Gold
    "Deep Freeze":       ("#000033", "#0088ff"),  # Black-Blue to Ice Blue
}

# CONTROLS
col1, col2 = st.columns(2)
with col1:
    mode = st.selectbox("Select Aesthetic Preset", ["Custom"] + list(presets.keys()))

if mode != "Custom":
    c1_hex, c2_hex = presets[mode]
    color1 = st.color_picker("Shadow Tone", c1_hex, disabled=True)
    color2 = st.color_picker("Highlight Tone", c2_hex, disabled=True)
else:
    color1 = st.color_picker("Shadow Tone (Darker Neon)", "#0000ff")
    color2 = st.color_picker("Highlight Tone (Brighter Neon)", "#ff00ff")

# UPLOAD
uploaded_file = st.file_uploader("Drop the Neon Asset", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    # Read Image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # PROCESS:
    # 1. Create a Mask for the background (Pure black stays pure black)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

    # 2. Convert Hex to RGB integers
    c1_rgb = hex_to_rgb(color1)
    c2_rgb = hex_to_rgb(color2)

    # 3. Apply the Gradient Map
    # This colors the gray image based on the two colors
    gradient_img = apply_gradient_map(gray, c1_rgb, c2_rgb)

    # 4. Re-apply the Black Background
    # We blacklist the background pixels so they don't turn "Shadow Tone" color
    final_img = cv2.bitwise_and(gradient_img, gradient_img, mask=mask)

    # DISPLAY
    st.image(cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB), caption="Neural Grade Applied", use_column_width=True)

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
