import cv2
import numpy as np

def recolor_to_blue(image_path, output_path):
    # 1. Load the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image from {image_path}")
        return

    # 2. Convert to HSV color space
    # HSV (Hue, Saturation, Value) separates color from brightness.
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 3. Define the target Blue Hue
    # In OpenCV's HSV scale, Hue is 0-180. Blue is around 120.
    blue_hue_value = 120
    
    # 4. Create a mask for colored pixels
    # We want to change pixels that have color (Saturation > 0) and brightness (Value > 0).
    # This avoids changing the pure black background.
    lower_threshold = np.array([0, 1, 1]) # Any hue, at least some saturation and brightness
    upper_threshold = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_threshold, upper_threshold)

    # 5. Apply the new Hue only to the masked area
    # We set the Hue (channel 0) to our blue value where the mask is active.
    hsv[:, :, 0] = np.where(mask > 0, blue_hue_value, hsv[:, :, 0])

    # 6. Convert back to BGR (standard image format)
    new_img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # 7. Save the result
    cv2.imwrite(output_path, new_img)
    print(f"Success! Blue image saved to {output_path}")

# --- Run the function ---
# Make sure 'image_0.png' is the name of your downloaded image file.
input_image = 'image_0.png'
output_image = 'neon_city_blue.png'

recolor_to_blue(input_image, output_image)
