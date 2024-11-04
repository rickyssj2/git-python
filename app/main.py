import sys
import os
import zlib


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # Uncomment this block to pass the first stage
    
    command = sys.argv[1]    
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file":
        option = sys.argv[2]
        if option == "-p":
            blob_sha = sys.argv[3]
            with open(f".git/objects/{blob_sha[:2]}/{blob_sha[2:]}", 'rb') as compressed_file:
                object_type, size, content = parse_blob(compressed_file)
                print(content, end='')
    else:
        raise RuntimeError(f"Unknown command #{command}")


def parse_blob(compressed_file):
    compressed_data = compressed_file.read()
    decompressed_data = zlib.decompress(compressed_data)
    object_type_end_index = decompressed_data.index(b' ')
    size_end_index = decompressed_data.index(b'\x00')

    object_type = decompressed_data[:object_type_end_index].decode('utf-8')
    size = decompressed_data[object_type_end_index + 1: size_end_index].decode('utf-8')
    content = decompressed_data[size_end_index + 1:].decode('utf-8')

    return object_type, size, content

if __name__ == "__main__":
    main()
