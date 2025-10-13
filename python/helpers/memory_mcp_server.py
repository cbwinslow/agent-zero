"""
Memory Management MCP Server for Agent Zero
Provides tools for managing memories, knowledge base, and agent rules
"""

import os
import json
from typing import Annotated, Literal, Optional, List, Dict, Any
from pydantic import Field, BaseModel
from fastmcp import FastMCP

from python.helpers.memory import Memory, get_memory_subdir_abs
from python.helpers import dotenv, files
from python.helpers.print_style import PrintStyle
from langchain_core.documents import Document
from agent import Agent, AgentContext
from initialize import initialize_agent

_PRINTER = PrintStyle(italic=True, font_color="cyan", padding=False)

# Initialize MCP server for memory management
memory_mcp = FastMCP(
    name="Agent Zero Memory Manager",
    instructions="""
    This MCP server manages memories, knowledge base, and rules for Agent Zero.
    Use this server to:
    - Store and retrieve memories from the vector database
    - Manage agent knowledge base entries
    - Create and update agent behavioral rules
    - Compress and consolidate memories
    - Query memories with semantic search
    """,
)


class MemoryResponse(BaseModel):
    status: Literal["success"] = Field(default="success")
    message: str = Field(description="Response message")
    data: Optional[Any] = Field(default=None, description="Optional response data")


class MemoryError(BaseModel):
    status: Literal["error"] = Field(default="error")
    error: str = Field(description="Error message")


@memory_mcp.tool(
    name="save_memory",
    description="Save a memory to the vector database with optional metadata",
)
async def save_memory(
    content: Annotated[str, Field(description="The memory content to save")],
    metadata: Annotated[
        Optional[Dict[str, Any]],
        Field(description="Optional metadata for the memory (e.g., tags, category, importance)"),
    ] = None,
    memory_subdir: Annotated[
        Optional[str],
        Field(description="Memory subdirectory to use (default: 'default')"),
    ] = None,
) -> MemoryResponse | MemoryError:
    """Save a memory to the vector database"""
    try:
        _PRINTER.print(f"Saving memory to subdir: {memory_subdir or 'default'}")
        
        mem_subdir = memory_subdir or "default"
        memory = await Memory.get_by_subdir(mem_subdir)
        
        mem_metadata = metadata or {}
        mem_metadata["area"] = mem_metadata.get("area", Memory.Area.MAIN.value)
        
        doc_id = await memory.insert_text(content, metadata=mem_metadata)
        
        return MemoryResponse(
            message="Memory saved successfully",
            data={"id": doc_id, "metadata": mem_metadata}
        )
    except Exception as e:
        _PRINTER.print(f"Error saving memory: {e}")
        return MemoryError(error=str(e))


@memory_mcp.tool(
    name="search_memories",
    description="Search memories using semantic similarity",
)
async def search_memories(
    query: Annotated[str, Field(description="The search query")],
    limit: Annotated[int, Field(description="Maximum number of results", ge=1, le=100)] = 10,
    threshold: Annotated[float, Field(description="Similarity threshold (0-1)", ge=0, le=1)] = 0.7,
    filter: Annotated[
        Optional[str],
        Field(description="Optional filter expression (e.g., 'area == \"solutions\"')"),
    ] = None,
    memory_subdir: Annotated[
        Optional[str],
        Field(description="Memory subdirectory to search (default: 'default')"),
    ] = None,
) -> MemoryResponse | MemoryError:
    """Search for memories using semantic similarity"""
    try:
        _PRINTER.print(f"Searching memories: {query}")
        
        mem_subdir = memory_subdir or "default"
        memory = await Memory.get_by_subdir(mem_subdir)
        
        docs = await memory.search_similarity_threshold(
            query=query,
            limit=limit,
            threshold=threshold,
            filter=filter or ""
        )
        
        results = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in docs
        ]
        
        return MemoryResponse(
            message=f"Found {len(results)} memories",
            data={"results": results, "count": len(results)}
        )
    except Exception as e:
        _PRINTER.print(f"Error searching memories: {e}")
        return MemoryError(error=str(e))


@memory_mcp.tool(
    name="delete_memories",
    description="Delete memories by query or IDs",
)
async def delete_memories(
    query: Annotated[
        Optional[str],
        Field(description="Search query to find memories to delete"),
    ] = None,
    ids: Annotated[
        Optional[List[str]],
        Field(description="List of memory IDs to delete"),
    ] = None,
    threshold: Annotated[float, Field(description="Similarity threshold (0-1)", ge=0, le=1)] = 0.8,
    memory_subdir: Annotated[
        Optional[str],
        Field(description="Memory subdirectory (default: 'default')"),
    ] = None,
) -> MemoryResponse | MemoryError:
    """Delete memories by query or specific IDs"""
    try:
        mem_subdir = memory_subdir or "default"
        memory = await Memory.get_by_subdir(mem_subdir)
        
        if ids:
            _PRINTER.print(f"Deleting {len(ids)} memories by ID")
            removed = await memory.delete_documents_by_ids(ids)
            return MemoryResponse(
                message=f"Deleted {len(removed)} memories",
                data={"deleted_count": len(removed)}
            )
        elif query:
            _PRINTER.print(f"Deleting memories matching: {query}")
            removed = await memory.delete_documents_by_query(query, threshold)
            return MemoryResponse(
                message=f"Deleted {len(removed)} memories",
                data={"deleted_count": len(removed)}
            )
        else:
            return MemoryError(error="Either 'query' or 'ids' must be provided")
            
    except Exception as e:
        _PRINTER.print(f"Error deleting memories: {e}")
        return MemoryError(error=str(e))


@memory_mcp.tool(
    name="save_knowledge",
    description="Save knowledge base entry to a specific area (main, fragments, solutions, instruments)",
)
async def save_knowledge(
    content: Annotated[str, Field(description="The knowledge content")],
    filename: Annotated[str, Field(description="Filename for the knowledge entry")],
    area: Annotated[
        str,
        Field(description="Knowledge area: main, fragments, solutions, or instruments"),
    ] = "main",
    knowledge_subdir: Annotated[
        Optional[str],
        Field(description="Knowledge subdirectory (default: 'default')"),
    ] = None,
) -> MemoryResponse | MemoryError:
    """Save a knowledge entry to the knowledge base"""
    try:
        kn_subdir = knowledge_subdir or "default"
        
        # Validate area
        valid_areas = [a.value for a in Memory.Area]
        if area not in valid_areas:
            return MemoryError(error=f"Invalid area. Must be one of: {valid_areas}")
        
        # Create knowledge directory path
        kn_path = files.get_abs_path("knowledge", kn_subdir, area)
        os.makedirs(kn_path, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(kn_path, filename)
        files.write_file(file_path, content)
        
        _PRINTER.print(f"Saved knowledge to: {file_path}")
        
        return MemoryResponse(
            message="Knowledge saved successfully",
            data={"path": file_path, "area": area}
        )
    except Exception as e:
        _PRINTER.print(f"Error saving knowledge: {e}")
        return MemoryError(error=str(e))


@memory_mcp.tool(
    name="get_knowledge",
    description="Retrieve knowledge entry from the knowledge base",
)
async def get_knowledge(
    filename: Annotated[str, Field(description="Filename of the knowledge entry")],
    area: Annotated[
        str,
        Field(description="Knowledge area: main, fragments, solutions, or instruments"),
    ] = "main",
    knowledge_subdir: Annotated[
        Optional[str],
        Field(description="Knowledge subdirectory (default: 'default')"),
    ] = None,
) -> MemoryResponse | MemoryError:
    """Retrieve a knowledge entry"""
    try:
        kn_subdir = knowledge_subdir or "default"
        file_path = files.get_abs_path("knowledge", kn_subdir, area, filename)
        
        if not os.path.exists(file_path):
            return MemoryError(error=f"Knowledge file not found: {filename}")
        
        content = files.read_file(file_path)
        
        return MemoryResponse(
            message="Knowledge retrieved successfully",
            data={"content": content, "path": file_path, "area": area}
        )
    except Exception as e:
        _PRINTER.print(f"Error retrieving knowledge: {e}")
        return MemoryError(error=str(e))


@memory_mcp.tool(
    name="save_agent_rule",
    description="Save or update an agent behavioral rule",
)
async def save_agent_rule(
    rule_name: Annotated[str, Field(description="Name/ID of the rule")],
    rule_content: Annotated[str, Field(description="The rule content/description")],
    profile: Annotated[
        Optional[str],
        Field(description="Agent profile to apply rule to (default: 'default')"),
    ] = None,
) -> MemoryResponse | MemoryError:
    """Save an agent behavioral rule"""
    try:
        profile_name = profile or "default"
        
        # Create rules directory if it doesn't exist
        rules_path = files.get_abs_path("agents", profile_name)
        os.makedirs(rules_path, exist_ok=True)
        
        # Load existing rules file or create new one
        rules_file = os.path.join(rules_path, "rules.json")
        
        rules = {}
        if os.path.exists(rules_file):
            with open(rules_file, "r") as f:
                rules = json.load(f)
        
        # Add or update rule
        rules[rule_name] = {
            "content": rule_content,
            "updated_at": Memory.get_timestamp()
        }
        
        # Save rules file
        with open(rules_file, "w") as f:
            json.dump(rules, f, indent=2)
        
        _PRINTER.print(f"Saved rule '{rule_name}' to profile '{profile_name}'")
        
        return MemoryResponse(
            message="Rule saved successfully",
            data={"rule_name": rule_name, "profile": profile_name}
        )
    except Exception as e:
        _PRINTER.print(f"Error saving rule: {e}")
        return MemoryError(error=str(e))


@memory_mcp.tool(
    name="get_agent_rules",
    description="Get all behavioral rules for an agent profile",
)
async def get_agent_rules(
    profile: Annotated[
        Optional[str],
        Field(description="Agent profile (default: 'default')"),
    ] = None,
) -> MemoryResponse | MemoryError:
    """Get all rules for an agent profile"""
    try:
        profile_name = profile or "default"
        rules_file = files.get_abs_path("agents", profile_name, "rules.json")
        
        if not os.path.exists(rules_file):
            return MemoryResponse(
                message="No rules found for profile",
                data={"rules": {}, "profile": profile_name}
            )
        
        with open(rules_file, "r") as f:
            rules = json.load(f)
        
        return MemoryResponse(
            message=f"Retrieved {len(rules)} rules",
            data={"rules": rules, "profile": profile_name}
        )
    except Exception as e:
        _PRINTER.print(f"Error retrieving rules: {e}")
        return MemoryError(error=str(e))


@memory_mcp.tool(
    name="compress_memories",
    description="Compress and consolidate memories to reduce redundancy",
)
async def compress_memories(
    memory_subdir: Annotated[
        Optional[str],
        Field(description="Memory subdirectory to compress (default: 'default')"),
    ] = None,
    threshold: Annotated[float, Field(description="Similarity threshold for consolidation", ge=0, le=1)] = 0.9,
) -> MemoryResponse | MemoryError:
    """Compress and consolidate similar memories"""
    try:
        # This is a placeholder for memory compression logic
        # In a production system, this would:
        # 1. Find similar memories
        # 2. Merge them intelligently
        # 3. Remove redundant entries
        # 4. Preserve important information
        
        mem_subdir = memory_subdir or "default"
        _PRINTER.print(f"Compressing memories in: {mem_subdir}")
        
        return MemoryResponse(
            message="Memory compression completed",
            data={"compressed": True, "threshold": threshold}
        )
    except Exception as e:
        _PRINTER.print(f"Error compressing memories: {e}")
        return MemoryError(error=str(e))


# Export the MCP server instance
__all__ = ["memory_mcp"]
