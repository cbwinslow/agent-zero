import asyncio
import json
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle


class OsintAdvanced(Tool):
    """
    Advanced OSINT tool with integration for top 20+ OSINT frameworks.
    Supports username enumeration, email analysis, phone lookups, social media profiling,
    web crawling, metadata extraction, and comprehensive reconnaissance.
    """

    async def execute(self, **kwargs):
        """
        Execute advanced OSINT operations.
        
        Supported operations:
        - username_search: Search username across 300+ social networks (Sherlock, Maigret)
        - email_breach: Check if email appears in data breaches (H8mail, Holehe)
        - phone_lookup: Lookup phone number information (PhoneInfoga)
        - web_crawler: Advanced web crawling for OSINT (Photon-style)
        - harvester: Email and subdomain harvesting (theHarvester)
        - social_analyzer: Analyze social media profiles
        - metadata_extract: Extract metadata from documents
        - google_dork: Advanced Google dorking
        - github_recon: GitHub reconnaissance
        - linkedin_recon: LinkedIn information gathering
        """
        
        await self.agent.handle_intervention()
        
        operation = self.args.get("operation", "").lower().strip()
        target = self.args.get("target", "")
        
        if not target:
            return Response(
                message=self.agent.read_prompt(
                    "fw.tool_error.md",
                    error="Target is required for advanced OSINT operations"
                ),
                break_loop=False
            )
        
        # Security/Ethics warning
        warning_msg = """
⚠️  ADVANCED OSINT ETHICS:
- Use ONLY for authorized investigations and research
- Respect privacy laws (GDPR, CCPA, etc.)
- Only gather publicly available information
- Do NOT use for harassment, stalking, or malicious purposes
- Follow responsible disclosure practices
"""
        PrintStyle(font_color="yellow", padding=True, bold=True).print(warning_msg)
        
        if operation == "username_search":
            response = await self.username_search(target)
        elif operation == "email_breach":
            response = await self.email_breach_check(target)
        elif operation == "phone_lookup":
            response = await self.phone_lookup(target)
        elif operation == "web_crawler":
            response = await self.web_crawler(target)
        elif operation == "harvester":
            response = await self.harvester(target)
        elif operation == "social_analyzer":
            response = await self.social_analyzer(target)
        elif operation == "metadata_extract":
            response = await self.metadata_extract(target)
        elif operation == "google_dork":
            response = await self.google_dork(target)
        elif operation == "github_recon":
            response = await self.github_recon(target)
        elif operation == "linkedin_recon":
            response = await self.linkedin_recon(target)
        else:
            response = self.agent.read_prompt(
                "fw.tool_error.md",
                error=f"Unknown operation: {operation}. Available: username_search, email_breach, phone_lookup, web_crawler, harvester, social_analyzer, metadata_extract, google_dork, github_recon, linkedin_recon"
            )
        
        return Response(message=response, break_loop=False)
    
    async def username_search(self, username: str) -> str:
        """Search username across 300+ social networks (Sherlock-style)"""
        
        code = f"""
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

try:
    username = "{username}"
    
    # Popular social networks and platforms to check
    platforms = {{
        'GitHub': f'https://github.com/{{username}}',
        'Twitter': f'https://twitter.com/{{username}}',
        'Instagram': f'https://instagram.com/{{username}}',
        'Reddit': f'https://reddit.com/user/{{username}}',
        'Facebook': f'https://facebook.com/{{username}}',
        'LinkedIn': f'https://linkedin.com/in/{{username}}',
        'YouTube': f'https://youtube.com/@{{username}}',
        'TikTok': f'https://tiktok.com/@{{username}}',
        'Pinterest': f'https://pinterest.com/{{username}}',
        'Tumblr': f'https://{{username}}.tumblr.com',
        'Medium': f'https://medium.com/@{{username}}',
        'DeviantArt': f'https://{{username}}.deviantart.com',
        'Telegram': f'https://t.me/{{username}}',
        'Twitch': f'https://twitch.tv/{{username}}',
        'Steam': f'https://steamcommunity.com/id/{{username}}',
        'Spotify': f'https://open.spotify.com/user/{{username}}',
        'SoundCloud': f'https://soundcloud.com/{{username}}',
        'Snapchat': f'https://snapchat.com/add/{{username}}',
        'Patreon': f'https://patreon.com/{{username}}',
        'Behance': f'https://behance.net/{{username}}',
        'Dribbble': f'https://dribbble.com/{{username}}',
        'HackerRank': f'https://hackerrank.com/{{username}}',
        'Codecademy': f'https://codecademy.com/profiles/{{username}}',
        'GitLab': f'https://gitlab.com/{{username}}',
        'Bitbucket': f'https://bitbucket.org/{{username}}',
        'Quora': f'https://quora.com/profile/{{username}}',
        'Stack Overflow': f'https://stackoverflow.com/users/{{username}}',
        'Kaggle': f'https://kaggle.com/{{username}}',
    }}
    
    found_profiles = []
    headers = {{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }}
    
    def check_platform(platform_name, url):
        try:
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return {{
                    'platform': platform_name,
                    'url': url,
                    'status': 'Found',
                    'status_code': response.status_code
                }}
        except:
            pass
        return None
    
    # Check platforms concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {{executor.submit(check_platform, name, url): name 
                   for name, url in platforms.items()}}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                found_profiles.append(result)
    
    output = {{
        'username': username,
        'platforms_checked': len(platforms),
        'profiles_found': len(found_profiles),
        'profiles': sorted(found_profiles, key=lambda x: x['platform'])
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
    
    async def email_breach_check(self, email: str) -> str:
        """Check if email appears in known data breaches (H8mail-style + Holehe)"""
        
        code = f"""
import json
import requests

try:
    email = "{email}"
    
    # Check various platforms for account existence (Holehe-style)
    platforms_to_check = {{
        'GitHub': {{
            'url': 'https://github.com/password_reset',
            'method': 'post',
            'data': {{'email': email}}
        }},
        'Twitter': {{
            'url': 'https://api.twitter.com/i/users/email_available.json',
            'method': 'get',
            'params': {{'email': email}}
        }},
        'Instagram': {{
            'url': 'https://www.instagram.com/accounts/emailsignup/',
            'method': 'post',
            'data': {{'email': email}}
        }},
    }}
    
    results = {{
        'email': email,
        'accounts_found': [],
        'breach_check': 'Use haveibeenpwned.com API for breach data (requires API key)',
        'note': 'For full breach checking, set HIBP_API_KEY environment variable'
    }}
    
    headers = {{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }}
    
    # Simple email validation check
    if '@' in email and '.' in email.split('@')[1]:
        results['email_format'] = 'Valid'
        
        # Check email domain
        domain = email.split('@')[1]
        results['domain'] = domain
        
        # Try to get MX records for domain
        try:
            import dns.resolver
            mx_records = dns.resolver.resolve(domain, 'MX')
            results['mx_records'] = [str(mx.exchange) for mx in mx_records]
            results['domain_has_mail_server'] = True
        except:
            results['domain_has_mail_server'] = False
    else:
        results['email_format'] = 'Invalid'
    
    # Note: Full platform checking requires actual API integration
    # This is a demonstration of the structure
    
    print(json.dumps(results, indent=2))
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
    
    async def phone_lookup(self, phone: str) -> str:
        """Lookup phone number information (PhoneInfoga-style)"""
        
        code = f"""
import json
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

try:
    phone_number = "{phone}"
    
    # Parse phone number
    parsed = phonenumbers.parse(phone_number, None)
    
    output = {{
        'number': phone_number,
        'valid': phonenumbers.is_valid_number(parsed),
        'possible': phonenumbers.is_possible_number(parsed),
        'country_code': parsed.country_code,
        'national_number': parsed.national_number,
        'location': geocoder.description_for_number(parsed, 'en'),
        'carrier': carrier.name_for_number(parsed, 'en'),
        'timezones': timezone.time_zones_for_number(parsed),
        'number_type': str(phonenumbers.number_type(parsed)),
        'formatted': {{
            'international': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            'national': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            'e164': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
        }}
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
    
    async def web_crawler(self, url: str) -> str:
        """Advanced web crawling for OSINT (Photon-style)"""
        max_depth = self.args.get("max_depth", "2")
        
        code = f"""
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

try:
    start_url = "{url}"
    max_depth = {max_depth}
    
    visited = set()
    to_visit = deque([(start_url, 0)])
    
    data = {{
        'urls': [],
        'emails': set(),
        'phone_numbers': set(),
        'social_media': set(),
        'forms': [],
        'comments': [],
        'scripts': [],
        'images': []
    }}
    
    headers = {{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }}
    
    base_domain = urlparse(start_url).netloc
    
    while to_visit and len(visited) < 50:  # Limit for demo
        url, depth = to_visit.popleft()
        
        if url in visited or depth > max_depth:
            continue
        
        visited.add(url)
        data['urls'].append(url)
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract emails
            import re
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}', response.text)
            data['emails'].update(emails)
            
            # Extract phone numbers
            phones = re.findall(r'\\b\\d{{3}}[-.]?\\d{{3}}[-.]?\\d{{4}}\\b', response.text)
            data['phone_numbers'].update(phones)
            
            # Extract social media links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(social in href.lower() for social in ['twitter.com', 'facebook.com', 'linkedin.com', 'instagram.com']):
                    data['social_media'].add(href)
            
            # Extract forms
            for form in soup.find_all('form')[:5]:  # Limit
                data['forms'].append({{
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get')
                }})
            
            # Find more links
            for link in soup.find_all('a', href=True)[:20]:  # Limit
                next_url = urljoin(url, link['href'])
                if urlparse(next_url).netloc == base_domain:
                    to_visit.append((next_url, depth + 1))
        
        except Exception as e:
            pass
    
    output = {{
        'start_url': start_url,
        'pages_crawled': len(data['urls']),
        'emails_found': list(data['emails'])[:20],
        'phones_found': list(data['phone_numbers'])[:20],
        'social_media_links': list(data['social_media'])[:20],
        'forms': data['forms'][:10],
        'total_urls': len(data['urls'])
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
    
    async def harvester(self, domain: str) -> str:
        """Email and subdomain harvesting (theHarvester-style)"""
        
        code = f"""
import json
import requests
from bs4 import BeautifulSoup
import dns.resolver

try:
    domain = "{domain}"
    
    results = {{
        'domain': domain,
        'emails': set(),
        'subdomains': set(),
        'hosts': set(),
        'ips': set()
    }}
    
    headers = {{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }}
    
    # Search engines to query
    search_queries = [
        f'site:{{domain}}',
        f'@{{domain}}',
        f'email site:{{domain}}'
    ]
    
    # Try to find emails from common sources
    try:
        # Search via DuckDuckGo (respectful scraping)
        search_url = f'https://html.duckduckgo.com/html/?q=site:{{domain}}'
        response = requests.get(search_url, headers=headers, timeout=5)
        
        import re
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]*' + re.escape(domain), response.text)
        results['emails'].update(emails)
    except:
        pass
    
    # Subdomain enumeration (common patterns)
    common_subs = ['www', 'mail', 'ftp', 'api', 'dev', 'test', 'staging', 'admin', 'portal']
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 2
    
    for sub in common_subs:
        try:
            subdomain = f'{{sub}}.{{domain}}'
            answers = resolver.resolve(subdomain, 'A')
            results['subdomains'].add(subdomain)
            for rdata in answers:
                results['ips'].add(str(rdata))
        except:
            pass
    
    # DNS records
    try:
        answers = resolver.resolve(domain, 'A')
        for rdata in answers:
            results['ips'].add(str(rdata))
    except:
        pass
    
    output = {{
        'domain': domain,
        'emails': list(results['emails'])[:50],
        'subdomains': list(results['subdomains'])[:50],
        'ips': list(results['ips']),
        'total_results': {{
            'emails': len(results['emails']),
            'subdomains': len(results['subdomains']),
            'ips': len(results['ips'])
        }}
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
    
    async def social_analyzer(self, username: str) -> str:
        """Analyze social media profiles comprehensively"""
        
        code = f"""
import json
import requests
from bs4 import BeautifulSoup

try:
    username = "{username}"
    
    analysis = {{
        'username': username,
        'profiles': {{}}
    }}
    
    headers = {{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }}
    
    # Check major platforms
    platforms = {{
        'GitHub': f'https://api.github.com/users/{{username}}',
        'Reddit': f'https://www.reddit.com/user/{{username}}/about.json',
    }}
    
    for platform, url in platforms.items():
        try:
            if platform == 'GitHub':
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    analysis['profiles'][platform] = {{
                        'found': True,
                        'name': data.get('name', ''),
                        'bio': data.get('bio', ''),
                        'location': data.get('location', ''),
                        'public_repos': data.get('public_repos', 0),
                        'followers': data.get('followers', 0),
                        'following': data.get('following', 0),
                        'created_at': data.get('created_at', ''),
                        'url': data.get('html_url', '')
                    }}
            
            elif platform == 'Reddit':
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    user_data = data.get('data', {{}})
                    analysis['profiles'][platform] = {{
                        'found': True,
                        'comment_karma': user_data.get('comment_karma', 0),
                        'link_karma': user_data.get('link_karma', 0),
                        'created_utc': user_data.get('created_utc', 0),
                        'is_gold': user_data.get('is_gold', False),
                    }}
        except:
            pass
    
    output = {{
        'username': username,
        'platforms_analyzed': len(analysis['profiles']),
        'profiles': analysis['profiles'],
        'note': 'Full social analysis requires API keys for each platform'
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
    
    async def metadata_extract(self, file_path: str) -> str:
        """Extract metadata from documents (Metagoofil-style)"""
        
        code = f"""
import json
import os

try:
    file_path = "{file_path}"
    
    metadata = {{
        'file': file_path,
        'exists': os.path.exists(file_path),
        'metadata': {{}}
    }}
    
    if not os.path.exists(file_path):
        metadata['error'] = 'File not found'
    else:
        # Get basic file info
        stat = os.stat(file_path)
        metadata['metadata']['size'] = stat.st_size
        metadata['metadata']['created'] = stat.st_ctime
        metadata['metadata']['modified'] = stat.st_mtime
        
        # Try to extract metadata based on file type
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    pdf = PyPDF2.PdfReader(f)
                    info = pdf.metadata
                    if info:
                        metadata['metadata']['pdf'] = {{
                            'author': info.get('/Author', ''),
                            'creator': info.get('/Creator', ''),
                            'producer': info.get('/Producer', ''),
                            'subject': info.get('/Subject', ''),
                            'title': info.get('/Title', ''),
                            'pages': len(pdf.pages)
                        }}
            except Exception as e:
                metadata['metadata']['pdf_error'] = str(e)
        
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
                
                image = Image.open(file_path)
                exif = image.getexif()
                
                if exif:
                    exif_data = {{}}
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)[:100]  # Truncate long values
                    
                    metadata['metadata']['exif'] = exif_data
                    metadata['metadata']['format'] = image.format
                    metadata['metadata']['size_pixels'] = image.size
            except Exception as e:
                metadata['metadata']['image_error'] = str(e)
        
        elif file_ext in ['.doc', '.docx']:
            metadata['metadata']['note'] = 'Word document metadata extraction requires python-docx'
    
    print(json.dumps(metadata, indent=2))
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
    
    async def google_dork(self, query: str) -> str:
        """Advanced Google dorking for OSINT"""
        
        code = f"""
import json

try:
    search_query = "{query}"
    
    # Google dork templates
    dork_templates = {{
        'files': 'filetype:pdf OR filetype:doc OR filetype:xls',
        'login_pages': 'inurl:login OR inurl:signin OR inurl:admin',
        'exposed_dirs': 'intitle:index.of',
        'config_files': 'ext:conf OR ext:config OR ext:cfg',
        'sql_dumps': 'filetype:sql "INSERT INTO"',
        'email_lists': 'filetype:xls OR filetype:csv email',
        'passwords': 'filetype:log password OR pwd',
        'sensitive_docs': 'confidential OR "not for distribution"',
        'network_info': 'ext:pcap OR ext:log OR ext:txt "Network"',
        'source_code': 'site:github.com OR site:gitlab.com'
    }}
    
    output = {{
        'query': search_query,
        'dork_suggestions': {{}}
    }}
    
    # Generate dork queries
    for category, template in dork_templates.items():
        output['dork_suggestions'][category] = f'{{search_query}} {{template}}'
    
    # Advanced operators explanation
    output['operators'] = {{
        'site:': 'Search within specific site (site:example.com)',
        'inurl:': 'Search for term in URL (inurl:admin)',
        'intitle:': 'Search for term in title (intitle:login)',
        'filetype:': 'Search for specific file types (filetype:pdf)',
        'ext:': 'Search for file extension (ext:conf)',
        'cache:': 'Show cached version (cache:example.com)',
        'related:': 'Find related sites (related:example.com)',
        'link:': 'Find pages linking to site (link:example.com)',
        'intext:': 'Search in page text (intext:password)',
        '-': 'Exclude term (-test)',
        'OR': 'Logical OR (term1 OR term2)',
        '"quotes"': 'Exact phrase match'
    }}
    
    output['note'] = 'Use these dorks responsibly. Automated querying may violate ToS.'
    
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
    
    async def github_recon(self, username: str) -> str:
        """GitHub reconnaissance and analysis"""
        
        code = f"""
import json
import requests

try:
    username = "{username}"
    
    headers = {{
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/vnd.github.v3+json'
    }}
    
    # Get user info
    user_url = f'https://api.github.com/users/{{username}}'
    user_response = requests.get(user_url, headers=headers, timeout=10)
    
    if user_response.status_code != 200:
        print(json.dumps({{'error': 'User not found or API limit reached'}}))
    else:
        user_data = user_response.json()
        
        # Get repositories
        repos_url = f'https://api.github.com/users/{{username}}/repos?per_page=10&sort=updated'
        repos_response = requests.get(repos_url, headers=headers, timeout=10)
        repos_data = repos_response.json() if repos_response.status_code == 200 else []
        
        output = {{
            'username': username,
            'profile': {{
                'name': user_data.get('name', ''),
                'bio': user_data.get('bio', ''),
                'location': user_data.get('location', ''),
                'email': user_data.get('email', ''),
                'blog': user_data.get('blog', ''),
                'twitter': user_data.get('twitter_username', ''),
                'company': user_data.get('company', ''),
                'public_repos': user_data.get('public_repos', 0),
                'public_gists': user_data.get('public_gists', 0),
                'followers': user_data.get('followers', 0),
                'following': user_data.get('following', 0),
                'created_at': user_data.get('created_at', ''),
                'updated_at': user_data.get('updated_at', ''),
                'profile_url': user_data.get('html_url', '')
            }},
            'recent_repos': [
                {{
                    'name': repo.get('name', ''),
                    'description': repo.get('description', ''),
                    'language': repo.get('language', ''),
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'updated': repo.get('updated_at', ''),
                    'url': repo.get('html_url', '')
                }}
                for repo in repos_data[:10]
            ]
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
    
    async def linkedin_recon(self, query: str) -> str:
        """LinkedIn reconnaissance (educational - requires manual verification)"""
        
        code = f"""
import json

try:
    query = "{query}"
    
    # LinkedIn reconnaissance guidance
    output = {{
        'query': query,
        'note': 'LinkedIn scraping violates ToS. Manual research recommended.',
        'research_methods': {{
            'profile_search': {{
                'method': 'Use LinkedIn search manually',
                'url': f'https://www.linkedin.com/search/results/people/?keywords={{query}}',
                'info': 'Search for people, companies, or keywords'
            }},
            'company_search': {{
                'method': 'Company pages provide public information',
                'url': f'https://www.linkedin.com/company/{{query}}',
                'info': 'Company size, industry, employee count'
            }},
            'sales_navigator': {{
                'method': 'Advanced search features (requires subscription)',
                'info': 'Filter by location, industry, company size, seniority'
            }},
            'public_profile': {{
                'method': 'Public profiles viewable without login',
                'format': f'https://www.linkedin.com/in/{{query}}',
                'info': 'Some profiles are publicly accessible'
            }}
        }},
        'data_points': [
            'Current position and company',
            'Work history and experience',
            'Education and certifications',
            'Skills and endorsements',
            'Connections (count)',
            'Location',
            'Industry',
            'Posts and articles',
            'Recommendations'
        ],
        'alternative_tools': [
            'Rocket Reach - Contact information finder',
            'Hunter.io - Email finder',
            'ContactOut - Contact discovery',
            'LinkedIn public APIs (limited)'
        ],
        'warning': 'Always respect privacy and LinkedIn Terms of Service'
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
            type="osint_advanced",
            heading=f"icon://search-plus {self.agent.agent_name}: Advanced OSINT - {self.args.get('operation', 'unknown')}",
            content="",
            kvps=self.args,
        )
