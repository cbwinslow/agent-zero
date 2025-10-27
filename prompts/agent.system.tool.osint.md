### osint_tool

perform open source intelligence gathering
gather publicly available information ethically
select "operation" arg: "shodan_search" "subdomain_enum" "dns_lookup" "whois_lookup" "censys_search" "passive_dns"
specify "target" arg: domain, IP, or search query
for shodan_search/censys_search: optional "api_key" or use environment variables
output: JSON with gathered intelligence data
usage:

1. shodan search

~~~json
{
    "thoughts": [
        "Need to find internet-connected devices...",
        "Using Shodan API...",
    ],
    "headline": "Searching Shodan for target devices",
    "tool_name": "osint_tool",
    "tool_args": {
        "operation": "shodan_search",
        "target": "apache",
        "api_key": ""
    }
}
~~~

2. subdomain enumeration

~~~json
{
    "thoughts": [
        "Need to discover subdomains...",
        "Using DNS enumeration...",
    ],
    "headline": "Enumerating subdomains for domain",
    "tool_name": "osint_tool",
    "tool_args": {
        "operation": "subdomain_enum",
        "target": "example.com"
    }
}
~~~

3. dns lookup

~~~json
{
    "thoughts": [
        "Need DNS records...",
        "Performing DNS lookup...",
    ],
    "headline": "Looking up DNS records",
    "tool_name": "osint_tool",
    "tool_args": {
        "operation": "dns_lookup",
        "target": "example.com",
        "record_types": "A,AAAA,MX,NS,TXT"
    }
}
~~~

4. whois lookup

~~~json
{
    "thoughts": [
        "Need domain registration info...",
        "Performing WHOIS lookup...",
    ],
    "headline": "Performing WHOIS lookup",
    "tool_name": "osint_tool",
    "tool_args": {
        "operation": "whois_lookup",
        "target": "example.com"
    }
}
~~~

5. censys search

~~~json
{
    "thoughts": [
        "Need to search Censys database...",
        "Using Censys API...",
    ],
    "headline": "Searching Censys for internet assets",
    "tool_name": "osint_tool",
    "tool_args": {
        "operation": "censys_search",
        "target": "services.service_name: HTTP",
        "api_id": "",
        "api_secret": ""
    }
}
~~~
