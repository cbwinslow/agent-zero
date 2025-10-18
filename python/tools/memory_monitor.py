"""
Memory Monitor Tool

This tool allows the agent to control and interact with the automatic memory monitoring system.
"""

from python.helpers.tool import Tool, Response
from python.helpers import memory_monitor
from python.helpers.print_style import PrintStyle


class MemoryMonitor(Tool):
    """
    Tool for managing the automatic memory monitoring system.
    
    Supported methods:
    - start: Start the memory monitor
    - stop: Stop the memory monitor
    - status: Get current status and statistics
    - short_term: View short-term memories
    - pending: View pending long-term memories
    - configure: Update monitor configuration
    """
    
    async def execute(self, **kwargs):
        """
        Execute the memory monitor tool.
        
        Args:
            **kwargs: Tool arguments including 'method' and method-specific parameters
        """
        # Get the memory monitor instance
        monitor = memory_monitor.get_memory_monitor()
        
        # Get method from args
        method = self.args.get("method", "status")
        
        if method == "start":
            return await self._start_monitor(monitor, **kwargs)
        elif method == "stop":
            return await self._stop_monitor(monitor, **kwargs)
        elif method == "status":
            return await self._get_status(monitor, **kwargs)
        elif method == "short_term":
            return await self._get_short_term(monitor, **kwargs)
        elif method == "pending":
            return await self._get_pending(monitor, **kwargs)
        elif method == "configure":
            return await self._configure(monitor, **kwargs)
        else:
            return Response(
                message=f"Unknown method '{method}'. Available methods: start, stop, status, short_term, pending, configure",
                break_loop=False
            )
    
    async def _start_monitor(self, monitor, **kwargs):
        """Start the memory monitor"""
        try:
            monitor.start()
            message = "Memory monitor started successfully"
            PrintStyle(font_color="green", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="Memory Monitor",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to start memory monitor: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _stop_monitor(self, monitor, **kwargs):
        """Stop the memory monitor"""
        try:
            monitor.stop()
            message = "Memory monitor stopped"
            PrintStyle(font_color="yellow", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="Memory Monitor",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to stop memory monitor: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _get_status(self, monitor, **kwargs):
        """Get monitor status and statistics"""
        try:
            stats = monitor.get_statistics()
            
            message = "# Memory Monitor Status\n\n"
            message += f"**Running**: {'Yes' if stats['is_running'] else 'No'}\n"
            message += f"**Model**: {monitor.model_name}\n"
            message += f"**Importance Threshold**: {monitor.importance_threshold}\n\n"
            
            message += "## Statistics\n"
            message += f"- Events Processed: {stats['events_processed']}\n"
            message += f"- Memories Saved: {stats['memories_saved']}\n"
            message += f"- Short-term Count: {stats['short_term_count']}\n"
            message += f"- Long-term Count: {stats['long_term_count']}\n\n"
            
            message += "## Current State\n"
            message += f"- Queue Size: {stats['queue_size']}\n"
            message += f"- Active Short-term: {stats['short_term_active']}\n"
            message += f"- Pending Long-term: {stats['pending_long_term']}\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Memory Monitor Status",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to get status: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _get_short_term(self, monitor, **kwargs):
        """Get short-term memories"""
        try:
            memories = monitor.get_short_term_memories()
            
            if not memories:
                message = "No active short-term memories"
            else:
                message = f"# Short-term Memories ({len(memories)})\n\n"
                
                for idx, mem in enumerate(memories[:10], 1):  # Show top 10
                    message += f"## {idx}. {' | '.join(mem.categories)}\n"
                    message += f"**Importance**: {mem.importance:.2f}\n"
                    message += f"**Type**: {mem.memory_type.value}\n"
                    message += f"**Time**: {mem.timestamp.strftime('%H:%M:%S')}\n"
                    message += f"**Content**: {mem.content[:200]}\n"
                    if mem.keywords:
                        message += f"**Keywords**: {', '.join(mem.keywords[:5])}\n"
                    message += "\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Short-term Memories",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to get short-term memories: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _get_pending(self, monitor, **kwargs):
        """Get pending long-term memories"""
        try:
            memories = monitor.get_pending_long_term()
            
            if not memories:
                message = "No pending long-term memories"
            else:
                message = f"# Pending Long-term Memories ({len(memories)})\n\n"
                
                for idx, mem in enumerate(memories[:10], 1):  # Show top 10
                    message += f"## {idx}. {' | '.join(mem.categories)}\n"
                    message += f"**Importance**: {mem.importance:.2f}\n"
                    message += f"**Type**: {mem.memory_type.value}\n"
                    message += f"**Time**: {mem.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    message += f"**Content**: {mem.content[:200]}\n"
                    if mem.keywords:
                        message += f"**Keywords**: {', '.join(mem.keywords[:5])}\n"
                    message += "\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Pending Long-term Memories",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to get pending memories: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _configure(self, monitor, **kwargs):
        """Configure monitor settings"""
        try:
            # Get configuration parameters
            importance_threshold = self.args.get("importance_threshold")
            auto_save = self.args.get("auto_save")
            short_term_ttl = self.args.get("short_term_ttl")
            
            changes = []
            
            if importance_threshold is not None:
                monitor.importance_threshold = float(importance_threshold)
                changes.append(f"Importance threshold set to {importance_threshold}")
            
            if auto_save is not None:
                monitor.enable_auto_save = bool(auto_save)
                changes.append(f"Auto-save {'enabled' if auto_save else 'disabled'}")
            
            if short_term_ttl is not None:
                monitor.short_term_ttl = int(short_term_ttl)
                changes.append(f"Short-term TTL set to {short_term_ttl} seconds")
            
            if not changes:
                message = "No configuration changes specified. Available parameters: importance_threshold, auto_save, short_term_ttl"
            else:
                message = "Memory monitor configuration updated:\n" + "\n".join(f"- {c}" for c in changes)
            
            PrintStyle(font_color="green", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Memory Monitor Configuration",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to configure monitor: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
