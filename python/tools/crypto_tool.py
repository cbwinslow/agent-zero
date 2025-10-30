import asyncio
import json
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle


class CryptoTool(Tool):
    """
    Cryptography and hash analysis tool.
    Supports hash identification, encoding/decoding, and basic cryptographic operations.
    """

    async def execute(self, **kwargs):
        """
        Execute cryptographic operations.
        
        Supported operations:
        - hash_identify: Identify hash type
        - hash_crack: Attempt to crack hash (requires wordlist)
        - encode: Encode text (base64, hex, etc.)
        - decode: Decode text
        - generate_hash: Generate hash from input
        - password_strength: Analyze password strength
        """
        
        await self.agent.handle_intervention()
        
        operation = self.args.get("operation", "").lower().strip()
        
        if operation == "hash_identify":
            response = await self.hash_identify()
        elif operation == "encode":
            response = await self.encode_text()
        elif operation == "decode":
            response = await self.decode_text()
        elif operation == "generate_hash":
            response = await self.generate_hash()
        elif operation == "password_strength":
            response = await self.password_strength()
        elif operation == "hash_crack":
            response = await self.hash_crack()
        else:
            response = self.agent.read_prompt(
                "fw.tool_error.md",
                error=f"Unknown operation: {operation}"
            )
        
        return Response(message=response, break_loop=False)
    
    async def hash_identify(self) -> str:
        """Identify hash type"""
        hash_value = self.args.get("hash", "")
        
        code = f"""
import json
import hashlib

try:
    hash_value = "{hash_value}"
    hash_len = len(hash_value)
    
    hash_types = []
    
    # Common hash length patterns
    if hash_len == 32:
        hash_types.append({{"type": "MD5", "bits": 128}})
    elif hash_len == 40:
        hash_types.append({{"type": "SHA-1", "bits": 160}})
    elif hash_len == 56:
        hash_types.append({{"type": "SHA-224", "bits": 224}})
    elif hash_len == 64:
        hash_types.extend([
            {{"type": "SHA-256", "bits": 256}},
            {{"type": "SHA3-256", "bits": 256}}
        ])
    elif hash_len == 96:
        hash_types.append({{"type": "SHA-384", "bits": 384}})
    elif hash_len == 128:
        hash_types.extend([
            {{"type": "SHA-512", "bits": 512}},
            {{"type": "SHA3-512", "bits": 512}}
        ])
    
    # Check for special formats
    if hash_value.startswith('$2a$') or hash_value.startswith('$2b$'):
        hash_types.append({{"type": "bcrypt", "description": "Adaptive hash function"}})
    elif hash_value.startswith('$6$'):
        hash_types.append({{"type": "SHA-512 crypt", "description": "Unix password"}})
    elif hash_value.startswith('$5$'):
        hash_types.append({{"type": "SHA-256 crypt", "description": "Unix password"}})
    
    output = {{
        'hash': hash_value[:50] + '...' if len(hash_value) > 50 else hash_value,
        'length': hash_len,
        'possible_types': hash_types if hash_types else [{{"type": "Unknown", "note": "Hash length not recognized"}}]
    }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    async def encode_text(self) -> str:
        """Encode text"""
        text = self.args.get("text", "")
        encoding = self.args.get("encoding", "base64").lower()
        
        code = f"""
import json
import base64

try:
    text = "{text}"
    encoding_type = "{encoding}"
    
    if encoding_type == "base64":
        encoded = base64.b64encode(text.encode()).decode()
    elif encoding_type == "hex":
        encoded = text.encode().hex()
    elif encoding_type == "url":
        import urllib.parse
        encoded = urllib.parse.quote(text)
    else:
        encoded = "Unknown encoding type"
    
    output = {{
        'original': text[:50] + '...' if len(text) > 50 else text,
        'encoding': encoding_type,
        'encoded': encoded
    }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    async def decode_text(self) -> str:
        """Decode text"""
        text = self.args.get("text", "")
        encoding = self.args.get("encoding", "base64").lower()
        
        code = f"""
import json
import base64

try:
    text = "{text}"
    encoding_type = "{encoding}"
    
    if encoding_type == "base64":
        decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
    elif encoding_type == "hex":
        decoded = bytes.fromhex(text).decode('utf-8', errors='ignore')
    elif encoding_type == "url":
        import urllib.parse
        decoded = urllib.parse.unquote(text)
    else:
        decoded = "Unknown encoding type"
    
    output = {{
        'encoded': text[:50] + '...' if len(text) > 50 else text,
        'encoding': encoding_type,
        'decoded': decoded
    }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    async def generate_hash(self) -> str:
        """Generate hash from input"""
        text = self.args.get("text", "")
        hash_type = self.args.get("hash_type", "sha256").lower()
        
        code = f"""
import json
import hashlib

try:
    text = "{text}"
    hash_type = "{hash_type}"
    
    data = text.encode()
    
    hashes = {{}}
    
    if hash_type == "all":
        hashes['md5'] = hashlib.md5(data).hexdigest()
        hashes['sha1'] = hashlib.sha1(data).hexdigest()
        hashes['sha256'] = hashlib.sha256(data).hexdigest()
        hashes['sha512'] = hashlib.sha512(data).hexdigest()
    else:
        if hasattr(hashlib, hash_type):
            hash_func = getattr(hashlib, hash_type)
            hashes[hash_type] = hash_func(data).hexdigest()
        else:
            hashes['error'] = f"Hash type {{hash_type}} not supported"
    
    output = {{
        'text': text[:50] + '...' if len(text) > 50 else text,
        'hashes': hashes
    }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    async def password_strength(self) -> str:
        """Analyze password strength"""
        password = self.args.get("password", "")
        
        code = f"""
import json
import re

try:
    password = "{password}"
    
    # Analyze password characteristics
    length = len(password)
    has_lowercase = bool(re.search(r'[a-z]', password))
    has_uppercase = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{{}}|<>]', password))
    
    # Calculate strength score
    score = 0
    score += min(length * 4, 40)  # Length (max 40 points)
    score += 10 if has_lowercase else 0
    score += 10 if has_uppercase else 0
    score += 15 if has_digit else 0
    score += 25 if has_special else 0
    
    # Penalize common patterns
    if re.search(r'(.)\\1{{2,}}', password):  # Repeated characters
        score -= 10
    if re.search(r'(012|123|234|345|456|567|678|789|890)', password):  # Sequential
        score -= 10
    
    # Determine strength category
    if score >= 80:
        strength = "Very Strong"
    elif score >= 60:
        strength = "Strong"
    elif score >= 40:
        strength = "Moderate"
    elif score >= 20:
        strength = "Weak"
    else:
        strength = "Very Weak"
    
    output = {{
        'length': length,
        'characteristics': {{
            'lowercase': has_lowercase,
            'uppercase': has_uppercase,
            'digits': has_digit,
            'special_chars': has_special
        }},
        'score': score,
        'strength': strength,
        'recommendations': []
    }}
    
    # Add recommendations
    if length < 12:
        output['recommendations'].append("Increase length to at least 12 characters")
    if not has_lowercase or not has_uppercase:
        output['recommendations'].append("Include both lowercase and uppercase letters")
    if not has_digit:
        output['recommendations'].append("Include at least one digit")
    if not has_special:
        output['recommendations'].append("Include at least one special character")
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    async def hash_crack(self) -> str:
        """Attempt to crack hash using wordlist"""
        hash_value = self.args.get("hash", "")
        wordlist = self.args.get("wordlist", "common")
        hash_type = self.args.get("hash_type", "md5")
        
        warning = """
⚠️  WARNING: Hash cracking should only be performed:
- On your own hashes
- For educational purposes
- With proper authorization
Unauthorized password cracking is ILLEGAL.
"""
        PrintStyle(font_color="red", padding=True).print(warning)
        
        # Create a small common password list for testing
        code = f"""
import json
import hashlib

try:
    target_hash = "{hash_value}"
    hash_type = "{hash_type}"
    
    # Small common password list for demonstration
    common_passwords = [
        "password", "123456", "12345678", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey",
        "dragon", "master", "sunshine", "princess", "football"
    ]
    
    found = None
    attempts = 0
    
    for password in common_passwords:
        attempts += 1
        if hash_type == "md5":
            test_hash = hashlib.md5(password.encode()).hexdigest()
        elif hash_type == "sha1":
            test_hash = hashlib.sha1(password.encode()).hexdigest()
        elif hash_type == "sha256":
            test_hash = hashlib.sha256(password.encode()).hexdigest()
        else:
            print(json.dumps({{'error': 'Unsupported hash type'}}))
            break
        
        if test_hash == target_hash:
            found = password
            break
    
    output = {{
        'hash': target_hash[:20] + '...',
        'hash_type': hash_type,
        'attempts': attempts,
        'found': found,
        'status': 'CRACKED' if found else 'NOT FOUND',
        'note': 'Using limited common password list. Full cracking requires extensive wordlists.'
    }}
    
    print(json.dumps(output, indent=2))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
        
        from python.tools.code_execution_tool import CodeExecution
        code_tool = CodeExecution(
            agent=self.agent,
            name="code_execution_tool",
            method=None,
            args={"runtime": "python", "code": code, "session": 0},
            message="",
            loop_data=self.loop_data
        )
        result = await code_tool.execute()
        return result.message
    
    def get_log_object(self):
        return self.agent.context.log.log(
            type="crypto",
            heading=f"icon://key {self.agent.agent_name}: Cryptography - {self.args.get('operation', 'unknown')}",
            content="",
            kvps=self.args,
        )
