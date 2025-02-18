# Git-Like Repository Implementation

This project is a simple implementation of a Git-like version control system. It allows for basic functionality such as initializing a repository, creating commits, reading objects (blobs, trees, commits), and cloning repositories. It works with basic operations related to object storage and retrieval using hashing, compression, and data manipulation.

## Features

- Initialize a Git-like repository structure.
- Create and retrieve objects (blobs, trees, commits).
- Display object contents with `cat-file`.
- Hash and store files as objects with `hash-object`.
- List files in a commit or tree with `ls-tree`.
- Write a new tree with `write-tree`.
- Create a new commit with `commit-tree`.
- Clone a remote repository and fetch objects.

## Setup & Installation

### Prerequisites

Ensure you have the following installed:
- Python 3.x
- Required Python packages (can be installed via `pip`)

## What I Learned
Through this project, I gained practical experience and knowledge about:

- **File Handling and Compression:** I learned how to work with file systems, handle file contents, and use zlib for compression and decompression to store objects efficiently.
- **Object Storage:** I implemented a system that mimics how Git stores different objects (blobs, trees, and commits) using hashes and compression.
- **Hashing and Identifiers:** I got hands-on experience with creating unique identifiers using hashing algorithms (SHA-1), which is a critical part of version control systems.
- **Python Programming:** I honed my Python skills, particularly in file handling, working with binary data, and implementing custom data structures to manage the repository.
- **Understanding Git Internals:** I gained insights into how Git works internally, including how it manages objects, commits, and trees. This helped me understand Git’s design and its efficient storage mechanisms.
- **Building a Version Control System:** I learned the complexity of building a version control system and how various components (objects, trees, commits) interact with each other.

