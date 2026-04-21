import streamlit as st
from PIL import Image
import tempfile
import numpy as np
import matplotlib.pyplot as plt

from core.encryption import generate_key, encrypt_message, decrypt_message
from image.encode import encode_image
from image.decode import decode_image

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Steganography Toolkit", layout="centered")

st.title("🔐 Multi-Format Steganography Toolkit")

# ---------------- FUNCTIONS ----------------
def plot_histogram(image, title):
    img_array = np.array(image)

    fig, ax = plt.subplots()

    colors = ['red', 'green', 'blue']

    for i, color in enumerate(colors):
        ax.hist(img_array[:, :, i].flatten(), bins=256, color=color, alpha=0.5)

    ax.set_title(title)
    return fig

def calculate_capacity(image):
    width, height = image.size
    return (width * height * 3) // 8  # bytes


def detect_stego(image):
    pixels = list(image.getdata())
    bits = []

    for pixel in pixels[:5000]:
        r, g, b = pixel
        bits.append(r & 1)

    ones = sum(bits)
    zeros = len(bits) - ones

    if abs(ones - zeros) < len(bits) * 0.1:
        return "⚠️ Possible hidden data detected"
    return "✅ Image appears normal"


def encode_text(text, secret):
    binary = ''.join(format(ord(c), '08b') for c in secret)

    encoded = ""
    idx = 0

    for char in text:
        encoded += char
        if idx < len(binary):
            if binary[idx] == '0':
                encoded += '\u200B'
            else:
                encoded += '\u200C'
            idx += 1

    return encoded


def decode_text(text):
    binary = ""

    for char in text:
        if char == '\u200B':
            binary += '0'
        elif char == '\u200C':
            binary += '1'

    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]

    result = ""
    for c in chars:
        if len(c) == 8:
            result += chr(int(c, 2))

    return result


# ---------------- TABS ----------------

tabs = st.tabs(["🖼 Image Stego", "🔍 Detection", "📝 Text Stego"])

# ================= IMAGE STEGO =================
with tabs[0]:
    st.header("🖼 Image Steganography")

    mode = st.radio("Choose Mode", ["Encode", "Decode"])

    # -------- ENCODE --------
    if mode == "Encode":
        uploaded_file = st.file_uploader("Upload Image", type=["png", "bmp"])

        if uploaded_file:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Image", use_column_width=True)

            capacity = calculate_capacity(image)
            st.info(f"📊 Max capacity: {capacity} bytes")

            message = st.text_area("Enter Secret Message")

            if st.button("Encode Image"):
                if not message:
                    st.warning("Please enter a message")
                else:
                    key = generate_key()
                    encrypted = encrypt_message(message, key)

                    if len(encrypted) > capacity:
                        st.error("❌ Message too large for this image")
                    else:
                        temp_input = tempfile.NamedTemporaryFile(delete=False)
                        temp_input.write(uploaded_file.read())

                        output_path = temp_input.name + "_out.png"

                        encode_image(temp_input.name, output_path, encrypted)

                        st.success("✅ Data hidden successfully")
                        st.code(key.decode(), language="text")

                        with open(output_path, "rb") as f:
                            st.download_button(
                                "⬇ Download Image", f, file_name="output.png"
                            )

    # -------- DECODE --------
    else:
        uploaded_file = st.file_uploader("Upload Encoded Image", type=["png", "bmp"])
        key = st.text_input("Enter Key")

        if uploaded_file:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Decode Image"):
            if not uploaded_file or not key:
                st.warning("Please upload image and enter key")
            else:
                temp_input = tempfile.NamedTemporaryFile(delete=False)
                temp_input.write(uploaded_file.read())

                try:
                    decrypted = decrypt_message(
                        decode_image(temp_input.name),
                        key.encode()
                    )
                    st.success("🔓 Hidden Message:")
                    st.write(decrypted)
                except:
                    st.error("❌ Invalid key or no hidden data")


# ================= DETECTION =================
with tabs[1]:
    st.header("🔍 Steganography Detection")

    uploaded_file = st.file_uploader("Upload Image for Analysis", type=["png", "bmp"])

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Analyze Image"):
            result = detect_stego(image)
            st.info(result)


# ================= TEXT STEGO =================
with tabs[2]:
    st.header("📝 Text Steganography (Zero-Width)")

    mode = st.radio("Mode", ["Encode", "Decode"], key="text_mode")

    # -------- ENCODE --------
    if mode == "Encode":
        cover_text = st.text_area("Enter Cover Text")
        secret = st.text_input("Secret Message")

        if st.button("Encode Text"):
            if not cover_text or not secret:
                st.warning("Enter both cover text and secret message")
            else:
                result = encode_text(cover_text, secret)
                st.success("Encoded Text:")
                st.code(result)

    # -------- DECODE --------
    else:
        text = st.text_area("Paste Text")

        if st.button("Decode Text"):
            result = decode_text(text)
            st.success("Hidden Message:")
            st.write(result)