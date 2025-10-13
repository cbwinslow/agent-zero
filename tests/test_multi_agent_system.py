#!/usr/bin/env python3
"""
Validation script for multi-agent memory system
Tests basic functionality of the implementation
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from python.helpers.print_style import PrintStyle

_PRINTER = PrintStyle(italic=True, font_color="yellow", padding=True)


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        _PRINTER.print(f"✓ {description}: {filepath}")
        return True
    else:
        _PRINTER.print(f"✗ {description}: {filepath} (NOT FOUND)")
        return False


def check_import(module_path, description):
    """Check if a module can be imported"""
    try:
        __import__(module_path)
        _PRINTER.print(f"✓ {description}: {module_path}")
        return True
    except ImportError as e:
        _PRINTER.print(f"✗ {description}: {module_path} (ERROR: {e})")
        return False


def validate_setup():
    """Validate the multi-agent memory system setup"""
    _PRINTER.print("=" * 60)
    _PRINTER.print("Multi-Agent Memory System Validation")
    _PRINTER.print("=" * 60)
    
    checks = []
    
    # Check core files
    _PRINTER.print("\n1. Checking core files...")
    checks.append(check_file_exists(
        "python/helpers/memory_mcp_server.py",
        "Memory MCP Server"
    ))
    checks.append(check_file_exists(
        "python/helpers/multi_agent_coordinator.py",
        "Multi-Agent Coordinator"
    ))
    checks.append(check_file_exists(
        "python/tools/multi_agent_delegation.py",
        "Multi-Agent Delegation Tool"
    ))
    checks.append(check_file_exists(
        "run_memory_mcp.py",
        "Memory MCP Server Runner"
    ))
    checks.append(check_file_exists(
        "setup_memory_mcp.py",
        "Setup Script"
    ))
    
    # Check configuration files
    _PRINTER.print("\n2. Checking configuration files...")
    checks.append(check_file_exists(
        "example.env",
        "Example Environment File"
    ))
    checks.append(check_file_exists(
        "conf/mcp_memory_server.json",
        "MCP Memory Server Config"
    ))
    checks.append(check_file_exists(
        "docker/run/docker-compose.yml",
        "Docker Compose"
    ))
    
    # Check agent profiles
    _PRINTER.print("\n3. Checking agent profiles...")
    profiles = ["researcher", "developer", "analyst", "planner", "executor"]
    for profile in profiles:
        profile_path = f"agents/{profile}/_context.md"
        checks.append(check_file_exists(
            profile_path,
            f"Agent Profile: {profile}"
        ))
    
    # Check documentation
    _PRINTER.print("\n4. Checking documentation...")
    checks.append(check_file_exists(
        "docs/multi_agent_memory_system.md",
        "Documentation"
    ))
    checks.append(check_file_exists(
        "QUICK_START_MULTI_AGENT.md",
        "Quick Start Guide"
    ))
    checks.append(check_file_exists(
        "prompts/agent.system.tool.multi_agent.md",
        "Multi-Agent Tool Prompt"
    ))
    
    # Check Python imports
    _PRINTER.print("\n5. Checking Python imports...")
    checks.append(check_import(
        "python.helpers.memory_mcp_server",
        "Memory MCP Server Module"
    ))
    checks.append(check_import(
        "python.helpers.multi_agent_coordinator",
        "Multi-Agent Coordinator Module"
    ))
    checks.append(check_import(
        "python.tools.multi_agent_delegation",
        "Multi-Agent Delegation Tool Module"
    ))
    
    # Check dependencies
    _PRINTER.print("\n6. Checking dependencies...")
    required_packages = [
        ("fastmcp", "FastMCP"),
        ("pydantic", "Pydantic"),
        ("langchain_core", "LangChain Core"),
    ]
    
    for package, name in required_packages:
        checks.append(check_import(package, f"Package: {name}"))
    
    # Summary
    _PRINTER.print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        _PRINTER.print(f"✓ All {total} validation checks passed!")
        _PRINTER.print("\nThe multi-agent memory system is properly installed.")
        _PRINTER.print("\nNext steps:")
        _PRINTER.print("1. Copy example.env to .env and configure your API keys")
        _PRINTER.print("2. Run: python setup_memory_mcp.py")
        _PRINTER.print("3. Start Agent Zero: docker-compose up -d")
        return 0
    else:
        _PRINTER.print(f"✗ {total - passed} of {total} checks failed")
        _PRINTER.print("\nPlease fix the issues above before proceeding.")
        return 1


def test_basic_functionality():
    """Test basic functionality of the components"""
    _PRINTER.print("\n" + "=" * 60)
    _PRINTER.print("Testing Basic Functionality")
    _PRINTER.print("=" * 60)
    
    try:
        # Test MultiAgentCoordinator imports and basic structure
        _PRINTER.print("\n1. Testing MultiAgentCoordinator...")
        from python.helpers.multi_agent_coordinator import (
            MultiAgentCoordinator,
            TaskDecomposer,
            AgentTask,
            CoordinationStrategy
        )
        
        # Test enums
        strategies = [s for s in CoordinationStrategy]
        _PRINTER.print(f"✓ Found {len(strategies)} coordination strategies: {[s.value for s in strategies]}")
        
        # Test TaskDecomposer
        _PRINTER.print("\n2. Testing TaskDecomposer...")
        decomposer = TaskDecomposer()
        test_task = "Research AI trends and implement a summary generator"
        profiles = ["researcher", "developer", "analyst"]
        tasks = decomposer.decompose(test_task, profiles)
        _PRINTER.print(f"✓ Task decomposition created {len(tasks)} subtasks")
        for task in tasks:
            _PRINTER.print(f"  - {task.agent_profile}: {task.message[:50]}...")
        
        # Test memory MCP server structure
        _PRINTER.print("\n3. Testing Memory MCP Server...")
        from python.helpers.memory_mcp_server import memory_mcp
        _PRINTER.print(f"✓ Memory MCP Server initialized: {memory_mcp.name}")
        
        tools = [t for t in memory_mcp._tools.keys()]
        _PRINTER.print(f"✓ Found {len(tools)} MCP tools:")
        for tool in tools:
            _PRINTER.print(f"  - {tool}")
        
        _PRINTER.print("\n" + "=" * 60)
        _PRINTER.print("✓ Basic functionality tests passed!")
        return 0
        
    except Exception as e:
        _PRINTER.print(f"\n✗ Error during functionality tests: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main validation function"""
    # Run validation
    validation_result = validate_setup()
    
    if validation_result == 0:
        # Run functionality tests
        functionality_result = test_basic_functionality()
        return functionality_result
    
    return validation_result


if __name__ == "__main__":
    sys.exit(main())
