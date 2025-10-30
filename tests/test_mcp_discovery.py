#!/usr/bin/env python3
"""
Test script to verify MCP Server Discovery functionality.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.helpers.mcp_discovery import MCPServerDiscovery
import json


def test_discovery_initialization():
    """Test that discovery module initializes correctly."""
    print("🧪 Testing Discovery Initialization")
    print("=" * 40)
    
    try:
        discovery = MCPServerDiscovery()
        print("✅ MCPServerDiscovery initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False


def test_npm_discovery():
    """Test npm server discovery."""
    print("\n🧪 Testing npm Discovery")
    print("=" * 40)
    
    try:
        discovery = MCPServerDiscovery()
        servers = discovery.discover_npm_servers()
        
        if len(servers) > 0:
            print(f"✅ Discovered {len(servers)} npm servers")
            print(f"   Sample server: {servers[0]['name']}")
            return True
        else:
            print("⚠️  No npm servers discovered")
            return False
            
    except Exception as e:
        print(f"❌ npm discovery failed: {e}")
        return False


def test_github_discovery():
    """Test GitHub server discovery."""
    print("\n🧪 Testing GitHub Discovery")
    print("=" * 40)
    
    try:
        discovery = MCPServerDiscovery()
        # Note: GitHub discovery might fail without token or due to rate limits
        servers = discovery.discover_github_servers()
        
        print(f"ℹ️  Discovered {len(servers)} GitHub servers")
        if len(servers) > 0:
            print(f"   Sample server: {servers[0]['name']}")
        else:
            print("   (No GitHub servers found - this may be normal without token)")
        return True
            
    except Exception as e:
        print(f"❌ GitHub discovery failed: {e}")
        return False


def test_docker_discovery():
    """Test Docker Hub server discovery."""
    print("\n🧪 Testing Docker Hub Discovery")
    print("=" * 40)
    
    try:
        discovery = MCPServerDiscovery()
        servers = discovery.discover_docker_servers()
        
        if len(servers) > 0:
            print(f"✅ Discovered {len(servers)} Docker servers")
            print(f"   Sample server: {servers[0]['name']}")
            return True
        else:
            print("⚠️  No Docker servers discovered")
            return False
            
    except Exception as e:
        print(f"❌ Docker discovery failed: {e}")
        return False


def test_search_functionality():
    """Test search functionality."""
    print("\n🧪 Testing Search Functionality")
    print("=" * 40)
    
    try:
        discovery = MCPServerDiscovery()
        # Force discovery first
        discovery.discover_all(force_refresh=True)
        
        # Test search
        results = discovery.search_servers('github')
        print(f"✅ Search for 'github' found {len(results)} servers")
        
        # Test source filter
        npm_results = discovery.search_servers('', source='npm')
        print(f"✅ Filter by 'npm' found {len(npm_results)} servers")
        
        return True
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False


def test_config_generation():
    """Test server configuration generation."""
    print("\n🧪 Testing Configuration Generation")
    print("=" * 40)
    
    try:
        discovery = MCPServerDiscovery()
        servers = discovery.discover_all(force_refresh=False)
        
        if len(servers) == 0:
            print("⚠️  No servers available for testing")
            return False
        
        # Test with an npm server
        npm_server = next((s for s in servers if s['source'] == 'npm'), None)
        if npm_server:
            config = discovery.generate_server_config(npm_server)
            print(f"✅ Generated config for npm server: {npm_server['name']}")
            print(f"   Command: {config.get('command')}")
            print(f"   Args: {config.get('args')}")
        
        # Test with a docker server
        docker_server = next((s for s in servers if s['source'] == 'docker'), None)
        if docker_server:
            config = discovery.generate_server_config(docker_server)
            print(f"✅ Generated config for docker server: {docker_server['name']}")
            print(f"   Command: {config.get('command')}")
        
        return True
            
    except Exception as e:
        print(f"❌ Config generation failed: {e}")
        return False


def test_cache():
    """Test caching functionality."""
    print("\n🧪 Testing Cache Functionality")
    print("=" * 40)
    
    try:
        discovery = MCPServerDiscovery()
        
        # First discovery (should cache)
        print("   Discovering servers (first time)...")
        servers1 = discovery.discover_all(force_refresh=True)
        
        # Second discovery (should use cache)
        print("   Discovering servers (from cache)...")
        servers2 = discovery.discover_all(force_refresh=False)
        
        if len(servers1) == len(servers2):
            print(f"✅ Cache working correctly ({len(servers2)} servers)")
            return True
        else:
            print(f"⚠️  Cache mismatch: {len(servers1)} vs {len(servers2)}")
            return False
            
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 MCP Server Discovery Test Suite")
    print("=" * 45)
    print()
    
    tests = [
        ("Initialization", test_discovery_initialization),
        ("npm Discovery", test_npm_discovery),
        ("GitHub Discovery", test_github_discovery),
        ("Docker Hub Discovery", test_docker_discovery),
        ("Search Functionality", test_search_functionality),
        ("Config Generation", test_config_generation),
        ("Cache Functionality", test_cache),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 45)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
