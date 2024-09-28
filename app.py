import streamlit as st
import http.client
import cv2
import numpy as np
from PIL import Image

# Helper function to call the handwriting OCR API
def call_handwriting_api(image_bytes):
    conn = http.client.HTTPSConnection("pen-to-print-handwriting-ocr.p.rapidapi.com")
    
    boundary = "----011000010111000001101001"
    
    # Prepare the payload properly with the image content
    payload = (
        f"--{boundary}\r\n"
        "Content-Disposition: form-data; name=\"srcImg\"; filename=\"image.jpg\"\r\n"
        "Content-Type: image/jpeg\r\n\r\n"
    ).encode("utf-8") + image_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")
    
    headers = {
        'x-rapidapi-key': "2a9c405c14mshc66d154f6b62900p1551d6jsn8c3e9ee14c79",
        'x-rapidapi-host': "pen-to-print-handwriting-ocr.p.rapidapi.com",
        'Content-Type': f"multipart/form-data; boundary={boundary}"
    }

    conn.request("POST", "/recognize/", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    return data.decode("utf-8")

# Function to format and display the detected text
def display_detected_text(text):
    st.markdown(
        f"""
        <div style="border:2px solid #4CAF50; padding: 10px; border-radius: 5px;">
            <h3 style="color:#4CAF50;">Detected Text:</h3>
            <p style="font-family:Courier; font-size:16px;">{text}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Streamlit pages
def home_page():
    st.title("Welcome to Handwriting OCR App")
    st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio.")

def upload_page():
    st.title("Upload Handwriting Image")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_column_width=True)

        # Convert image to bytes
        img_bytes = uploaded_file.getvalue()
        result = call_handwriting_api(img_bytes)
        
        # Assuming the result is a JSON string like in the example
        import json
        result_data = json.loads(result)
        
        # Extracting the text to display
        detected_text = result_data.get("value", "No text detected.")
        
        # Display the formatted result
        display_detected_text(detected_text)

def webcam_page():
    st.title("Webcam Handwriting Detection")

    # Initialize webcam
    run = st.checkbox("Run Webcam", key="run_webcam")

    FRAME_WINDOW = st.image([])

    camera = cv2.VideoCapture(0)

    # Capture button placed outside the loop
    capture_button = st.button("Capture", key="capture_button")

    while run:
        # Try to capture a frame from the webcam
        ret, frame = camera.read()
        
        # Check if the frame is captured correctly
        if not ret:
            st.write("Error: Failed to capture image from webcam.")
            continue
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(frame)

        if capture_button:
            # Convert the frame to bytes and send to API
            _, img_encoded = cv2.imencode('.jpg', frame)
            img_bytes = img_encoded.tobytes()
            result = call_handwriting_api(img_bytes)
            
            # Assuming the result is a JSON string like in the example
            import json
            result_data = json.loads(result)
            
            # Extracting the text to display
            detected_text = result_data.get("value", "No text detected.")
            
            # Display the formatted result
            display_detected_text(detected_text)

    else:
        st.write("Stopped")

    camera.release()



# Streamlit page navigation
st.sidebar.title("Navigation")
options = st.sidebar.radio("Select a page:", ["Home", "Upload Image"]) #"Webcam"

if options == "Home":
    home_page()
elif options == "Upload Image":
    upload_page()
# elif options == "Webcam":
#     webcam_page()
