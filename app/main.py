import sys
import os
import zlib
import hashlib
import time

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)
    
    command = sys.argv[1]    
    option = ''
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
                decompressed_data = zlib.decompress(compressed_file.read())
                object_type, size, content = parse_blob(decompressed_data)
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
    elif command =="ls-tree":
        option = sys.argv[2]
        if option == "--name-only":
            tree_sha = sys.argv[3]
            with open(f".git/objects/{tree_sha[:2]}/{tree_sha[2:]}", 'rb') as compressed_file:
                decompressed_data = zlib.decompress(compressed_file.read())
                print(decompressed_data, file=sys.stderr)
                object_type, size, content = parse_tree(decompressed_data)                
                for c in content:
                    print(c['name'])
        else:
            # TODO: implement ls-tree without the --name-only option
            tree_sha = sys.argv[2]
    elif command == "write-tree":
        print(write_tree(os.getcwd()))
    elif command == "commit-tree":
        tree_sha = sys.argv[2]
        commit_sha = sys.argv[4]
        message = sys.argv[6]

        content = f'tree {tree_sha}\nparent {commit_sha}\nauthor Aryan <aryanpandey048@gmail.com> {int(time.time())} +0000\ncommitter Aryan <aryanpandey048@gmail.com> {int(time.time())}\n\n{message}\n'
        size = len(content.encode('utf-8'))
        commit_object = f'commit {size}\0 {content}'.encode('utf-8')
        commit_sha = calculate_sha1(commit_object)
        print(commit_object, file=sys.stderr)
        print(commit_sha)
        os.makedirs(f".git/objects/{commit_sha[:2]}", exist_ok=True)
        with open(f".git/objects/{commit_sha[:2]}/{commit_sha[2:]}", "wb") as f:
            f.write(zlib.compress(commit_object))
    else:
        raise RuntimeError(f"Unknown command #{command}")


def parse_blob(decompressed_data):
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

def parse_tree(decompressed_data):
    object_type_end_index = decompressed_data.index(b' ')
    size_end_index = decompressed_data.index(b'\x00')

    object_type = decompressed_data[:object_type_end_index].decode('utf-8')
    size = decompressed_data[object_type_end_index + 1: size_end_index].decode('utf-8')
    content = []
    i = size_end_index + 1
    while i < int(size):
        mode_end_index = decompressed_data.index(b' ', i)
        name_end_index = decompressed_data.index(b'\x00', i)
        sha_end_index = name_end_index + 21

        object = {}
        object['mode'] = decompressed_data[i:mode_end_index].decode('utf-8')
        object['name'] = decompressed_data[mode_end_index + 1: name_end_index].decode('utf-8')        
        object['sha'] = decompressed_data[name_end_index + 1: sha_end_index]

        content.append(object)
        i = name_end_index + 21

    return object_type, size, content

def create_blob_entry(path, write=True):
    with open(path, "rb") as f:
        data = f.read()
    header = f"blob {len(data)}\0".encode("utf-8")
    store = header + data
    sha = hashlib.sha1(store).hexdigest()
    if write:
        os.makedirs(f".git/objects/{sha[:2]}", exist_ok=True)
        with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f:
            f.write(zlib.compress(store))
    return sha

def write_tree(path: str):
    if os.path.isfile(path):
        return create_blob_entry(path)
    contents = sorted(
        os.listdir(path),
        key=lambda x: x if os.path.isfile(os.path.join(path, x)) else f"{x}/",
    )
    s = b""
    for item in contents:
        if item == ".git":
            continue
        full = os.path.join(path, item)
        if os.path.isfile(full):
            s += f"100644 {item}\0".encode()
        else:
            s += f"40000 {item}\0".encode()
        sha1 = int.to_bytes(int(write_tree(full), base=16), length=20, byteorder="big")
        s += sha1
    s = f"tree {len(s)}\0".encode() + s
    sha1 = hashlib.sha1(s).hexdigest()
    os.makedirs(f".git/objects/{sha1[:2]}", exist_ok=True)
    with open(f".git/objects/{sha1[:2]}/{sha1[2:]}", "wb") as f:
        f.write(zlib.compress(s))
    return sha1

if __name__ == "__main__":
    main()
