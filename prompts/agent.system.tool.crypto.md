### crypto_tool

cryptography and hash analysis operations
perform hash identification encoding decoding password analysis
WARNING: only use for authorized testing and educational purposes
select "operation" arg: "hash_identify" "encode" "decode" "generate_hash" "password_strength" "hash_crack"
output: JSON with results
usage:

1. identify hash type

~~~json
{
    "thoughts": [
        "Need to identify hash type...",
        "Using hash identification...",
    ],
    "headline": "Identifying hash type",
    "tool_name": "crypto_tool",
    "tool_args": {
        "operation": "hash_identify",
        "hash": "5d41402abc4b2a76b9719d911017c592"
    }
}
~~~

2. encode text

~~~json
{
    "thoughts": [
        "Need to encode data...",
        "Using base64 encoding...",
    ],
    "headline": "Encoding text to base64",
    "tool_name": "crypto_tool",
    "tool_args": {
        "operation": "encode",
        "text": "hello world",
        "encoding": "base64"
    }
}
~~~

3. decode text

~~~json
{
    "thoughts": [
        "Need to decode data...",
        "Using base64 decoding...",
    ],
    "headline": "Decoding base64 text",
    "tool_name": "crypto_tool",
    "tool_args": {
        "operation": "decode",
        "text": "aGVsbG8gd29ybGQ=",
        "encoding": "base64"
    }
}
~~~

4. generate hash

~~~json
{
    "thoughts": [
        "Need to generate hash...",
        "Calculating SHA-256...",
    ],
    "headline": "Generating SHA-256 hash",
    "tool_name": "crypto_tool",
    "tool_args": {
        "operation": "generate_hash",
        "text": "password123",
        "hash_type": "sha256"
    }
}
~~~

5. analyze password strength

~~~json
{
    "thoughts": [
        "Need to check password strength...",
        "Analyzing characteristics...",
    ],
    "headline": "Analyzing password strength",
    "tool_name": "crypto_tool",
    "tool_args": {
        "operation": "password_strength",
        "password": "MyP@ssw0rd123"
    }
}
~~~

6. crack hash (demo only)

~~~json
{
    "thoughts": [
        "Attempting to crack hash...",
        "Using common wordlist...",
    ],
    "headline": "Attempting hash crack with common passwords",
    "tool_name": "crypto_tool",
    "tool_args": {
        "operation": "hash_crack",
        "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
        "hash_type": "md5",
        "wordlist": "common"
    }
}
~~~
