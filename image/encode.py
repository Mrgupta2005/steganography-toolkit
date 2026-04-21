from PIL import Image

def encode_image(input_path, output_path, data):
    img = Image.open(input_path)
    pixels = list(img.getdata())

    binary = ''.join(format(b, '08b') for b in data) + '11111110'

    new_pixels = []
    idx = 0

    for pixel in pixels:
        if len(pixel) == 4:
            r, g, b, a = pixel
        else:
            r, g, b = pixel
            a = None

        if idx < len(binary):
            r = (r & ~1) | int(binary[idx])
            idx += 1

        if a is not None:
            new_pixels.append((r, g, b, a))
        else:
            new_pixels.append((r, g, b))

    img.putdata(new_pixels)
    img.save(output_path)