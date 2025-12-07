import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.title("SharpHuman: Neon Blue Converter")

# 1. File Uploader
uploaded_file = st.file_uploader("Upload your Neon City Image", type=['jpg', 'png', 'jpeg'])

if uploaded_file is not None:
    # Convert the file to an OpenCV image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    # 2. Process the Image (The Blue Shift)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Target: Electric Blue (Hue ~120)
    target_hue = 120
    
    # Mask: Select non-black pixels (brightness > 10)
    lower_black = np.array([0, 10, 10])
    upper_black = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_black, upper_black)

    # Apply the shift
    hsv[:, :, 0] = np.where(mask > 0, target_hue, hsv[:, :, 0])
    
    # Convert back to BGR then to RGB for Streamlit display
    final_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    final_rgb = cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB)

    # 3. Show Result
    st.image(final_rgb, caption="Processed Blue Version", use_column_width=True)

    # 4. Create Download Button
    # Convert back to PIL to save to memory buffer
    result_pil = Image.fromarray(final_rgb)
    buf = io.BytesIO()
    result_pil.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Download Blue Image",
        data=byte_im,
        file_name="sharphuman_blue.png",
        mime="image/png"
    )
