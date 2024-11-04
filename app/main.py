import sys
import os
import zlib
import hashlib


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
    elif command == "hash-object":
        option = sys.argv[2]
        if option == "-w":
            file_name = sys.argv[3]
            blob_sha = ''
            with open(file_name, 'r') as source_file, open('temp', 'wb') as temp_file:
                content = source_file.read()
                size = len(content.encode('utf-8'))
                blob = f'blob {size}\0{content}'.encode('utf-8')
                compressed_blob = zlib.compress(blob)
                temp_file.write(compressed_blob)                
                blob_sha = calculate_sha1(blob)
                print(blob_sha)
            # Create the target directory if it doesn't exist
            target_dir = f'.git/objects/{blob_sha[:2]}'
            os.makedirs(target_dir, exist_ok=True)

            # Rename the temporary file to the final destination
            os.rename('temp', f'{target_dir}/{blob_sha[2:]}')

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

def calculate_sha1(data):
    # Create a new sha1 hash object
    sha1_hash = hashlib.sha1()

    # Update the hash object with the bytes-like object
    sha1_hash.update(data) 

    # Get the hexadecimal digest of the hash
    return sha1_hash.hexdigest()

if __name__ == "__main__":
    main()
