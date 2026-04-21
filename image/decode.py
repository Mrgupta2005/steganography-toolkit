from PIL import Image

def decode_image(path):
    img = Image.open(path)
    pixels = list(img.getdata())

    binary = ""

    for pixel in pixels:
        r, g, b = pixel
        binary += str(r & 1)

    bytes_data = [binary[i:i+8] for i in range(0, len(binary), 8)]

    result = bytearray()

    for byte in bytes_data:
        if byte == '11111110':
            break
        result.append(int(byte, 2))

    return bytes(result)