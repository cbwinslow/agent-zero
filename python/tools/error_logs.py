"""
Error Logs Tool

This tool allows the agent to:
- View error statistics and history
- Find solutions for specific errors
- Get error prevention recommendations
- Mark errors as resolved with solutions
"""

from python.helpers.tool import Tool, Response
from python.helpers import error_tracker
from python.helpers.print_style import PrintStyle


class ErrorLogs(Tool):
    """
    Tool for managing and viewing error logs.
    
    Supported methods:
    - statistics: View error statistics
    - search: Search for errors by type or category
    - solutions: Get solutions for a specific error
    - recommendations: Get error prevention recommendations
    - resolve: Mark an error as resolved with a solution
    """
    
    async def execute(self, **kwargs):
        """
        Execute the error logs tool.
        
        Args:
            **kwargs: Tool arguments including 'method' to specify the operation
        """
        # Get the error tracker instance
        tracker = error_tracker.get_error_tracker()
        
        # Get method from args
        method = self.args.get("method", "statistics")
        
        if method == "statistics":
            return await self._get_statistics(tracker, **kwargs)
        elif method == "search":
            return await self._search_errors(tracker, **kwargs)
        elif method == "solutions":
            return await self._get_solutions(tracker, **kwargs)
        elif method == "recommendations":
            return await self._get_recommendations(tracker, **kwargs)
        elif method == "resolve":
            return await self._resolve_error(tracker, **kwargs)
        else:
            return Response(
                message=f"Unknown method '{method}'. Available methods: statistics, search, solutions, recommendations, resolve",
                break_loop=False
            )
    
    async def _get_statistics(self, tracker, **kwargs):
        """Get error statistics"""
        stats = tracker.get_statistics()
        
        # Format the statistics for display
        message = "# Error Statistics\n\n"
        message += f"**Total Errors**: {stats['total_errors']}\n"
        message += f"**Unique Errors**: {stats['unique_errors']}\n"
        message += f"**Resolved**: {stats['resolved_count']}\n"
        message += f"**Resolution Rate**: {stats['resolution_rate']:.1%}\n\n"
        
        # By category
        if stats['by_category']:
            message += "## Errors by Category\n"
            for category, count in sorted(stats['by_category'].items(), key=lambda x: x[1], reverse=True):
                message += f"- **{category}**: {count}\n"
            message += "\n"
        
        # By type
        if stats['by_type']:
            message += "## Errors by Type\n"
            for error_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True)[:10]:
                message += f"- **{error_type}**: {count}\n"
            message += "\n"
        
        # Most frequent errors
        if stats['most_frequent']:
            message += "## Most Frequent Errors\n"
            for idx, error in enumerate(stats['most_frequent'][:5], 1):
                resolved_text = "✓ Resolved" if error['resolved'] else "✗ Unresolved"
                message += f"{idx}. **{error['error_type']}** ({error['count']} occurrences) - {resolved_text}\n"
                message += f"   ID: `{error['error_id']}` - {error['error_message']}\n\n"
        
        PrintStyle(font_color="cyan", padding=True).print(message)
        self.agent.context.log.log(
            type="info",
            heading="Error Statistics",
            content=message
        )
        
        return Response(message=message, break_loop=False)
    
    async def _search_errors(self, tracker, **kwargs):
        """Search for errors by type or category"""
        error_type = self.args.get("error_type")
        category = self.args.get("category")
        
        if not error_type and not category:
            return Response(
                message="Please specify either 'error_type' or 'category' to search",
                break_loop=False
            )
        
        # Filter errors
        matching_errors = []
        for error in tracker.errors.values():
            if error_type and error.error_type == error_type:
                matching_errors.append(error)
            elif category and error.category == category:
                matching_errors.append(error)
        
        if not matching_errors:
            message = f"No errors found matching the criteria"
        else:
            message = f"# Found {len(matching_errors)} matching error(s)\n\n"
            
            # Sort by occurrence count
            matching_errors.sort(key=lambda x: x.occurrence_count, reverse=True)
            
            for idx, error in enumerate(matching_errors[:10], 1):
                resolved_text = "✓ Resolved" if error.resolved else "✗ Unresolved"
                message += f"{idx}. **{error.error_type}** ({error.occurrence_count} occurrences) - {resolved_text}\n"
                message += f"   ID: `{error.error_id}`\n"
                message += f"   Category: {error.category}\n"
                message += f"   Message: {error.error_message[:100]}\n"
                if error.solutions:
                    message += f"   Solutions: {len(error.solutions)}\n"
                message += "\n"
        
        PrintStyle(font_color="cyan", padding=True).print(message)
        self.agent.context.log.log(
            type="info",
            heading="Error Search Results",
            content=message
        )
        
        return Response(message=message, break_loop=False)
    
    async def _get_solutions(self, tracker, **kwargs):
        """Get solutions for a specific error ID"""
        error_id = self.args.get("error_id")
        
        if not error_id:
            return Response(
                message="Please specify 'error_id' to get solutions",
                break_loop=False
            )
        
        error = tracker.errors.get(error_id)
        
        if not error:
            return Response(
                message=f"Error with ID '{error_id}' not found",
                break_loop=False
            )
        
        message = f"# Solutions for Error {error_id}\n\n"
        message += f"**Type**: {error.error_type}\n"
        message += f"**Category**: {error.category}\n"
        message += f"**Occurrences**: {error.occurrence_count}\n"
        message += f"**Message**: {error.error_message}\n\n"
        
        if error.solutions:
            message += "## Solutions\n"
            for idx, solution in enumerate(error.solutions, 1):
                message += f"{idx}. {solution['solution']}\n"
                message += f"   Applied: {solution['timestamp']}\n\n"
        else:
            message += "No solutions recorded for this error yet.\n"
        
        PrintStyle(font_color="cyan", padding=True).print(message)
        self.agent.context.log.log(
            type="info",
            heading=f"Solutions for {error_id}",
            content=message
        )
        
        return Response(message=message, break_loop=False)
    
    async def _get_recommendations(self, tracker, **kwargs):
        """Get error prevention recommendations"""
        category = self.args.get("category")
        
        recommendations = tracker.get_prevention_recommendations(category)
        
        message = "# Error Prevention Recommendations\n\n"
        if category:
            message += f"For category: **{category}**\n\n"
        
        for idx, rec in enumerate(recommendations, 1):
            message += f"{idx}. {rec}\n"
        
        PrintStyle(font_color="cyan", padding=True).print(message)
        self.agent.context.log.log(
            type="info",
            heading="Error Prevention Recommendations",
            content=message
        )
        
        return Response(message=message, break_loop=False)
    
    async def _resolve_error(self, tracker, **kwargs):
        """Mark an error as resolved with a solution"""
        error_id = self.args.get("error_id")
        solution = self.args.get("solution")
        
        if not error_id or not solution:
            return Response(
                message="Please specify both 'error_id' and 'solution' to mark as resolved",
                break_loop=False
            )
        
        error = tracker.errors.get(error_id)
        
        if not error:
            return Response(
                message=f"Error with ID '{error_id}' not found",
                break_loop=False
            )
        
        # Add the solution
        from datetime import datetime, timezone
        error.solutions.append({
            "solution": solution,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        error.resolved = True
        
        # Save to database
        tracker._save_errors()
        
        message = f"Error {error_id} marked as resolved with solution:\n{solution}"
        
        PrintStyle(font_color="green", padding=True).print(message)
        self.agent.context.log.log(
            type="info",
            heading=f"Error {error_id} Resolved",
            content=message
        )
        
        return Response(message=message, break_loop=False)
