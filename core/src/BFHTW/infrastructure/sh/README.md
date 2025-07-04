# SSH Key Management

This repository contains files related to SSH key management for users. It includes user information and their associated public SSH keys, which are essential for secure access to servers and services.

## Contents

The folder contains the following files:

- `users.json`: A JSON file that stores user details, including usernames and their associated public SSH keys.
- `ssh-keys.txt`: A plain text file that lists SSH keys in a simple format, associating each key with a username.

## File Descriptions

### `users.json`
This file contains an array of user objects. Each user object includes:
- `username`: The username of the individual.
- `public_keys`: An array of public SSH keys associated with the user. Each key is represented as a string.

**Example Structure:**
```json
[
    {
        "username": "steven",
        "public_keys": [
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDNlyJ6NOrZQxHMy0VOteclI6iYsZb0X95svaxCSKyEVjsnF3qFUIzaZGF7f6T+X2kUMsMteQPJ3AyHSgfgljfgaw6kk5Zq36FkrdNEsi1EVVEhVc1QpEKNq2eSnmfHUIUAStlwp0kjlJ15FIV26lRAdDyOjvH+W0bWs5iQ1LwEHAABXk0J5o/GlDAE45EY+qvow0tcbS9tOh73gT+1VgnAMg7652cFLniIV10wDjVjKJ2Wr4q4b1vAXBC9s9tZktjAtRiZccn/JwTwUwl6jB8mXHvMPveJALXek4vNPDbrFF6+LuAD/rXGVGHlkmXNIXoJut3a3uBBm+LNAoalsnAVeYRsY3N0Yw8nbtewdJtS4NOnjX38qqNhfHsmAoaJjTFb/iYmMKZmjAvQC2nnS4CBZ5WhfBjW1eSwxBKDnP2m8BJmDhtr1NswXCXrwnlGc1LGPqywW8xYONrPgegPSmy71rlO35umI49s7Lr+D07EQRifPzwa6RY3+f6NJAxpEmh1nk8xk2GIgRisSd0+zxJpPjid/RQUmuFmgMzTXHMc/qzqvSGjAOTmzPompXdcJY3Of84pNwEVGL3+wViMUEgXAI4HdU/q6Dk5nyZhnaNbmKSmknZA/eIJJmjWydpY/jIxLuBZrYkauH43lyzzfPd4gDrLDURworFcTcqe1XaLJw== steven@fartsicorn.dev"
        ]
    }
]
```

### `ssh-keys.txt`
This file contains a simple list of usernames and their corresponding public SSH keys, formatted as follows:
- Each line contains a username followed by a colon and the public key string.

**Example Entry:**
```
steven:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDNlyJ6NOrZQxHMy0VOteclI6iYsZb0X95svaxCSKyEVjsnF3qFUIzaZGF7f6T+X2kUMsMteQPJ3AyHSgfgljfgaw6kk5Zq36FkrdNEsi1EVVEhVc1QpEKNq2eSnmfHUIUAStlwp0kjlJ15FIV26lRAdDyOjvH+W0bWs5iQ1LwEHAABXk0J5o/GlDAE45EY+qvow0tcbS9tOh73gT+1VgnAMg7652cFLniIV10wDjVjKJ2Wr4q4b1vAXBC9s9tZktjAtRiZccn/JwTwUwl6jB8mXHvMPveJALXek4vNPDbrFF6+LuAD/rXGVGHlkmXNIXoJut3a3uBBm+LNAoalsnAVeYRsY3N0Yw8nbtewdJtS4NOnjX38qqNhfHsmAoaJjTFb/iYmMKZmjAvQC2nnS4CBZ5WhfBjW1eSwxBKDnP2m8BJmDhtr1NswXCXrwnlGc1LGPqywW8xYONrPgegPSmy71rlO35umI49s7Lr+D07EQRifPzwa6RY3+f6NJAxpEmh1nk8xk2GIgRisSd0+zxJpPjid/RQUmuFmgMzTXHMc/qzqvSGjAOTmzPompXdcJY3Of84pNwEVGL3+wViMUEgXAI4HdU/q6Dk5nyZhnaNbmKSmknZA/eIJJmjWydpY/jIxLuBZrYkauH43lyzzfPd4gDrLDURworFcTcqe1XaLJw== steven@fartsicorn.dev
```

## Usage

This repository can be used for managing SSH keys for users in a structured manner. The JSON format allows for easy integration with applications that require user authentication, while the text file format provides a simple way to view and edit keys manually.