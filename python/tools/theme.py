"""
Theme Management Tool

This tool allows the agent to manage visual themes and color schemes.
"""

from python.helpers.tool import Tool, Response
from python.helpers import theme
from python.helpers.print_style import PrintStyle


class ThemeTool(Tool):
    """
    Tool for managing visual themes and colors.
    
    Supported methods:
    - list: List available themes
    - current: Show current theme
    - switch: Switch to a different theme
    - colors: Show color palette for current theme
    - export: Export current theme to a file
    - import: Import a theme from a file
    """
    
    async def execute(self, **kwargs):
        """
        Execute the theme tool.
        
        Args:
            **kwargs: Tool arguments including 'method' and method-specific parameters
        """
        # Get the theme manager instance
        theme_mgr = theme.get_theme_manager()
        
        # Get method from args
        method = self.args.get("method", "current")
        
        if method == "list":
            return await self._list_themes(theme_mgr, **kwargs)
        elif method == "current":
            return await self._current_theme(theme_mgr, **kwargs)
        elif method == "switch":
            return await self._switch_theme(theme_mgr, **kwargs)
        elif method == "colors":
            return await self._show_colors(theme_mgr, **kwargs)
        elif method == "export":
            return await self._export_theme(theme_mgr, **kwargs)
        elif method == "import":
            return await self._import_theme(theme_mgr, **kwargs)
        else:
            return Response(
                message=f"Unknown method '{method}'. Available methods: list, current, switch, colors, export, import",
                break_loop=False
            )
    
    async def _list_themes(self, theme_mgr, **kwargs):
        """List available themes"""
        try:
            themes = theme_mgr.list_themes()
            
            message = "# Available Themes\n\n"
            for theme_name in themes:
                is_current = theme_name == theme_mgr.current_theme.name
                marker = "→ " if is_current else "  "
                message += f"{marker}**{theme_name}**\n"
            
            message += "\n## Theme Descriptions\n\n"
            message += "- **dark**: Classic dark theme with vibrant colors\n"
            message += "- **light**: Light theme for bright environments\n"
            message += "- **monokai**: Popular Monokai color scheme\n"
            message += "- **dracula**: Dark theme with pastel colors\n"
            message += "- **nord**: Arctic-inspired color palette\n"
            message += "- **solarized_dark**: Solarized dark theme\n"
            message += "- **solarized_light**: Solarized light theme\n"
            message += "- **gruvbox**: Retro groove color scheme\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Available Themes",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to list themes: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _current_theme(self, theme_mgr, **kwargs):
        """Show current theme"""
        try:
            current = theme_mgr.current_theme
            
            message = f"# Current Theme: {current.name}\n\n"
            message += "## Settings\n"
            message += f"- Bold Headings: {'Yes' if current.bold_headings else 'No'}\n"
            message += f"- Italic Thoughts: {'Yes' if current.italic_thoughts else 'No'}\n"
            message += f"- Underline Links: {'Yes' if current.underline_links else 'No'}\n"
            message += f"- Padding Messages: {'Yes' if current.padding_messages else 'No'}\n"
            message += f"- Show Timestamps: {'Yes' if current.show_timestamps else 'No'}\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Current Theme",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to get current theme: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _switch_theme(self, theme_mgr, **kwargs):
        """Switch to a different theme"""
        theme_name = self.args.get("theme_name")
        
        if not theme_name:
            return Response(
                message="Please specify 'theme_name' to switch to",
                break_loop=False
            )
        
        try:
            success = theme_mgr.switch_theme(theme_name)
            
            if success:
                message = f"Successfully switched to theme '{theme_name}'"
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"Theme '{theme_name}' not found. Use 'list' method to see available themes."
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="Theme Switch",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to switch theme: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _show_colors(self, theme_mgr, **kwargs):
        """Show color palette"""
        try:
            palette = theme_mgr.current_theme.palette
            
            message = f"# Color Palette: {theme_mgr.current_theme.name}\n\n"
            
            # Group colors by category
            categories = {
                "Primary Colors": ["primary", "secondary", "accent"],
                "Background & Foreground": ["background", "foreground"],
                "Messages": ["user_message", "agent_message", "system_message"],
                "Status": ["success", "warning", "error", "info", "debug"],
                "Tools & Code": ["tool_execution", "code_execution", "code_output"],
                "Memory": ["memory_save", "memory_load", "knowledge"],
                "Reasoning": ["reasoning", "thoughts"],
                "Highlights": ["highlight", "emphasis"],
                "UI Elements": ["border", "separator", "link", "reference"],
            }
            
            for category, components in categories.items():
                message += f"## {category}\n"
                for component in components:
                    color = getattr(palette, component, None)
                    if color:
                        # Format component name nicely
                        display_name = component.replace("_", " ").title()
                        message += f"- **{display_name}**: `{color}`\n"
                message += "\n"
            
            PrintStyle(font_color="cyan", padding=True).print(message)
            self.agent.context.log.log(
                type="info",
                heading="Color Palette",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to show colors: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _export_theme(self, theme_mgr, **kwargs):
        """Export current theme to a file"""
        output_path = self.args.get("output_path")
        
        if not output_path:
            return Response(
                message="Please specify 'output_path' for the exported theme",
                break_loop=False
            )
        
        try:
            theme_mgr.export_theme(output_path)
            message = f"Successfully exported theme to {output_path}"
            PrintStyle(font_color="green", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="Theme Export",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to export theme: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
    
    async def _import_theme(self, theme_mgr, **kwargs):
        """Import a theme from a file"""
        input_path = self.args.get("input_path")
        
        if not input_path:
            return Response(
                message="Please specify 'input_path' for the theme to import",
                break_loop=False
            )
        
        try:
            success = theme_mgr.import_theme(input_path)
            
            if success:
                message = f"Successfully imported theme from {input_path}"
                PrintStyle(font_color="green", padding=True).print(message)
            else:
                message = f"Failed to import theme from {input_path}"
                PrintStyle(font_color="red", padding=True).print(message)
            
            self.agent.context.log.log(
                type="info",
                heading="Theme Import",
                content=message
            )
            
            return Response(message=message, break_loop=False)
            
        except Exception as e:
            error_msg = f"Failed to import theme: {e}"
            PrintStyle(font_color="red", padding=True).print(error_msg)
            return Response(message=error_msg, break_loop=False)
