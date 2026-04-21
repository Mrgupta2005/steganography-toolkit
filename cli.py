import argparse
from core.encryption import generate_key, encrypt_message, decrypt_message
from image.encode import encode_image
from image.decode import decode_image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["encode", "decode"])
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--message")
    parser.add_argument("--key")

    args = parser.parse_args()

    # ✅ PUT IT HERE
    print("Running CLI...")

    if args.mode == "encode":
        key = generate_key()
        encrypted = encrypt_message(args.message, key)

        encode_image(args.input, args.output, encrypted)

        print("Key:", key.decode())
        print("Data hidden successfully")

    elif args.mode == "decode":
        decrypted = decrypt_message(decode_image(args.input), args.key.encode())
        print("Hidden message:", decrypted)

if __name__ == "__main__":
    
    main()