import sys
import os
import zlib
import hashlib
import time
import requests
import struct

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
    elif command == "clone":
        repo_url = sys.argv[2]
        local_dir = sys.argv[3]
        git_client = Git_Smart_Client(repo_url, local_dir)

        # Get refs
        git_client.fetch_refs()

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

class Git_Smart_Client:
    def __init__(self, repo_url, local_dir, branch = "master"):
        self.repo_url = repo_url
        self.local_dir = local_dir
        self.base_url = f"{repo_url}/info/refs?service=git-upload-pack"
        self.branch = branch

    def fetch_refs(self):
        """Request the references from the Git server."""
        print(f"Fetching refs from {self.base_url}...", file=sys.stderr)
        headers = {'Accept': 'application/x-git-upload-pack-advertisement'}
        
        response = requests.get(self.base_url, headers=headers, stream=True)
        
        if response.status_code == 200:
            print("Received refs data...", file=sys.stderr)
            self.parse_refs(response.content)
        else:
            print(f"Failed to fetch refs. HTTP Status Code: {response.status_code}", file=sys.stderr)
    
    def parse_refs(self, data):
        """Parse the refs data to extract the references (branches)."""
        # Convert the raw binary data into a UTF-8 string
        try:
            data_str = data.decode('utf-8')
        except UnicodeDecodeError:
            print("Error decoding refs data.")
            return
        
        # Split the data into lines
        lines = data_str.splitlines()

        # The first line contains the capabilities (for example, "multi_ack_detailed")
        capabilities = lines[0:2]
        print(f"Capabilities: {capabilities}")

        # The remaining lines contain the references in the format:
        # <sha1> <ref-name>
        refs = []
        for line in lines[2:-1]:
            # Split by space, get sha1 and reference name
            sha1, ref_name = line.split()
            refs.append((sha1, ref_name))

        # Output the available refs for the user
        print("Available references:")
        for sha1, ref_name in refs:
            print(f"{ref_name} -> {sha1}")

        # Find the reference for the desired branch (e.g., "refs/heads/main")
        target_ref = f"refs/heads/{self.branch}"
        for sha1, ref_name in refs:
            if ref_name == target_ref:
                print(f"Found target branch '{self.branch}' with commit {sha1}")
                # Fetch the objects associated with this ref (commit history, etc.)
                self.fetch_objects(sha1)  # Passing the commit hash for the target branch
                break
        else:
            print(f"Branch '{self.branch}' not found.")
    
    def fetch_objects(self, commit_sha1):
        """Request the objects for the given commit and unpack the packfile."""
        print(f"Fetching objects for commit {commit_sha1}...")
        
        # Construct the URL for fetching the objects (the "git-upload-pack" service)
        fetch_url = self.repo_url.rstrip(".git") + "/git-upload-pack"
        
        # Prepare the request body: a packet requesting objects related to the branch
        # The body of the request will include the desired commit sha1 and ref info
        request_body = self.create_request_body(commit_sha1)
        
        # Send the POST request with the request body to fetch objects
        response = requests.post(fetch_url, data=request_body, headers={'Content-Type': 'application/x-git-upload-pack-request'})
        
        if response.status_code == 200:
            print("Received packfile from server...")
            self.unpack_packfile(response.content)
        else:
            print(f"Failed to fetch objects. HTTP Status Code: {response.status_code}")
    
    def create_request_body(self, commit_sha1):
        """Create the request body to fetch objects for the given commit."""
        request_body = b""

        # First part: capabilities
        command = b"command=fetch"
        no_progress = b"0001no-progress"
        # request_body += struct.pack(">I", len(command) + 1) + command + struct.pack(">I", len(no_progress) + 1) + no_progress
        
        # "want" line: request for objects related to the commit sha1 and ref name
        ref_name = f"refs/heads/{self.branch}"
        want_line = f"want {commit_sha1}\n".encode('utf-8')
        request_body += self.encode_pkt_line(want_line)

        # Optional: Add "have" lines (commits we already know about)
        have_lines = []  # Add your 'have' lines here, for example, [(sha1, ref_name), ...]
        for sha1, ref_name in have_lines:
            have_line = f"have {sha1} {ref_name}\n".encode('utf-8')
            request_body += self.encode_pkt_line(have_line)

        # add the "0000" to indicate the end of the request stream
        done_flush = b"0000"
        request_body += done_flush

        # Finally, add "done" line
        done_line = b"0009done\n"
        request_body += done_line
        
        print(request_body)
        return request_body

    def encode_pkt_line(self, line):
        """Encode a single pkt-line with a length prefix (4 hex digits)."""
        length = len(line)
        length_hex = f"{length:04x}".encode('utf-8')  # Convert length to 4-digit hex
        return length_hex + line

    def unpack_packfile(self, packfile_data):
        """Unpack the packfile and simulate extracting objects."""
        print("Unpacking packfile...")
        
        # In a real implementation, this part would handle Git's delta compression
        # and the extraction of objects from the packfile.
        
        # For simulation, we'll just pretend the packfile is compressed with zlib.
        try:
            decompressed_data = zlib.decompress(packfile_data)
            print(f"Uncompressed data: {decompressed_data[:100]}")  # Print the first 100 bytes of data
        except zlib.error:
            print("Failed to decompress packfile data.")
            return

if __name__ == "__main__":
    main()
