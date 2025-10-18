"""
Theme and Color Customization System for Agent Zero

This module provides a flexible theme system that allows users to customize
the visual appearance of Agent Zero's terminal output and UI.

Features:
- Predefined color themes (dark, light, solarized, monokai, etc.)
- Custom color palettes
- User preferences persistence
- Theme switching at runtime
- Component-specific color overrides
"""

import json
import os
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
from python.helpers import files


class ThemeName(Enum):
    """Predefined theme names"""
    DARK = "dark"
    LIGHT = "light"
    SOLARIZED_DARK = "solarized_dark"
    SOLARIZED_LIGHT = "solarized_light"
    MONOKAI = "monokai"
    DRACULA = "dracula"
    NORD = "nord"
    GRUVBOX = "gruvbox"
    CUSTOM = "custom"


@dataclass
class ColorPalette:
    """
    Color palette for a theme.
    
    Defines colors for various UI components and message types.
    Colors can be specified as:
    - Named colors (e.g., "red", "blue")
    - Hex codes (e.g., "#FF0000", "#0000FF")
    """
    # Primary colors
    primary: str = "#00BFFF"  # Deep sky blue
    secondary: str = "#32CD32"  # Lime green
    accent: str = "#FFD700"  # Gold
    
    # Background and foreground
    background: str = "#000000"  # Black
    foreground: str = "#FFFFFF"  # White
    
    # Message types
    user_message: str = "#87CEEB"  # Sky blue
    agent_message: str = "#98FB98"  # Pale green
    system_message: str = "#FFE4B5"  # Moccasin
    
    # Status colors
    success: str = "#008000"  # Green
    warning: str = "#FFA500"  # Orange
    error: str = "#FF0000"  # Red
    info: str = "#0000FF"  # Blue
    debug: str = "#808080"  # Gray
    
    # Tool and code
    tool_execution: str = "#9370DB"  # Medium purple
    code_execution: str = "#4682B4"  # Steel blue
    code_output: str = "#B0C4DE"  # Light steel blue
    
    # Memory and knowledge
    memory_save: str = "#FFB6C1"  # Light pink
    memory_load: str = "#DDA0DD"  # Plum
    knowledge: str = "#F0E68C"  # Khaki
    
    # Reasoning and thinking
    reasoning: str = "#b3ffd9"  # Light green (existing color)
    thoughts: str = "#ADD8E6"  # Light blue
    
    # Highlights and emphasis
    highlight: str = "#FFFF00"  # Yellow
    emphasis: str = "#FF69B4"  # Hot pink
    
    # Borders and separators
    border: str = "#696969"  # Dim gray
    separator: str = "#A9A9A9"  # Dark gray
    
    # Links and references
    link: str = "#00CED1"  # Dark turquoise
    reference: str = "#BA55D3"  # Medium orchid


@dataclass
class Theme:
    """
    Complete theme definition including palette and styling preferences.
    
    Attributes:
        name: Theme name
        palette: Color palette for this theme
        bold_headings: Whether to make headings bold
        italic_thoughts: Whether to italicize agent thoughts
        underline_links: Whether to underline links
        padding_messages: Whether to add padding between messages
        show_timestamps: Whether to show timestamps in output
    """
    name: str
    palette: ColorPalette
    bold_headings: bool = True
    italic_thoughts: bool = True
    underline_links: bool = True
    padding_messages: bool = True
    show_timestamps: bool = False


class ThemeManager:
    """
    Manages themes and user preferences.
    
    Provides methods to:
    - Load and save themes
    - Switch between themes
    - Customize color palettes
    - Export/import themes
    - Apply themes to PrintStyle
    """
    
    # Built-in themes
    BUILTIN_THEMES: Dict[ThemeName, ColorPalette] = {
        ThemeName.DARK: ColorPalette(
            primary="#00BFFF",
            secondary="#32CD32",
            accent="#FFD700",
            background="#000000",
            foreground="#FFFFFF",
            user_message="#87CEEB",
            agent_message="#98FB98",
            system_message="#FFE4B5",
            success="#00FF00",
            warning="#FFA500",
            error="#FF0000",
            info="#0000FF",
            debug="#808080",
            tool_execution="#9370DB",
            code_execution="#4682B4",
            code_output="#B0C4DE",
            memory_save="#FFB6C1",
            memory_load="#DDA0DD",
            knowledge="#F0E68C",
            reasoning="#b3ffd9",
            thoughts="#ADD8E6",
            highlight="#FFFF00",
            emphasis="#FF69B4",
            border="#696969",
            separator="#A9A9A9",
            link="#00CED1",
            reference="#BA55D3",
        ),
        
        ThemeName.LIGHT: ColorPalette(
            primary="#0066CC",
            secondary="#228B22",
            accent="#DAA520",
            background="#FFFFFF",
            foreground="#000000",
            user_message="#4682B4",
            agent_message="#2E8B57",
            system_message="#8B4513",
            success="#006400",
            warning="#FF8C00",
            error="#DC143C",
            info="#00008B",
            debug="#696969",
            tool_execution="#8A2BE2",
            code_execution="#191970",
            code_output="#4169E1",
            memory_save="#C71585",
            memory_load="#9932CC",
            knowledge="#B8860B",
            reasoning="#2E8B57",
            thoughts="#4169E1",
            highlight="#FFD700",
            emphasis="#FF1493",
            border="#A9A9A9",
            separator="#D3D3D3",
            link="#0000EE",
            reference="#8B008B",
        ),
        
        ThemeName.MONOKAI: ColorPalette(
            primary="#66D9EF",  # Monokai blue
            secondary="#A6E22E",  # Monokai green
            accent="#FD971F",  # Monokai orange
            background="#272822",  # Monokai background
            foreground="#F8F8F2",  # Monokai foreground
            user_message="#66D9EF",
            agent_message="#A6E22E",
            system_message="#E6DB74",  # Monokai yellow
            success="#A6E22E",
            warning="#FD971F",
            error="#F92672",  # Monokai pink/red
            info="#66D9EF",
            debug="#75715E",  # Monokai comment
            tool_execution="#AE81FF",  # Monokai purple
            code_execution="#66D9EF",
            code_output="#F8F8F2",
            memory_save="#F92672",
            memory_load="#AE81FF",
            knowledge="#E6DB74",
            reasoning="#A6E22E",
            thoughts="#66D9EF",
            highlight="#E6DB74",
            emphasis="#F92672",
            border="#49483E",
            separator="#75715E",
            link="#66D9EF",
            reference="#AE81FF",
        ),
        
        ThemeName.DRACULA: ColorPalette(
            primary="#8BE9FD",  # Cyan
            secondary="#50FA7B",  # Green
            accent="#FFB86C",  # Orange
            background="#282A36",  # Background
            foreground="#F8F8F2",  # Foreground
            user_message="#8BE9FD",
            agent_message="#50FA7B",
            system_message="#F1FA8C",  # Yellow
            success="#50FA7B",
            warning="#FFB86C",
            error="#FF5555",  # Red
            info="#8BE9FD",
            debug="#6272A4",  # Comment
            tool_execution="#BD93F9",  # Purple
            code_execution="#8BE9FD",
            code_output="#F8F8F2",
            memory_save="#FF79C6",  # Pink
            memory_load="#BD93F9",
            knowledge="#F1FA8C",
            reasoning="#50FA7B",
            thoughts="#8BE9FD",
            highlight="#F1FA8C",
            emphasis="#FF79C6",
            border="#44475A",
            separator="#6272A4",
            link="#8BE9FD",
            reference="#BD93F9",
        ),
        
        ThemeName.NORD: ColorPalette(
            primary="#88C0D0",  # Nord frost cyan
            secondary="#A3BE8C",  # Nord aurora green
            accent="#EBCB8B",  # Nord aurora yellow
            background="#2E3440",  # Nord polar night
            foreground="#ECEFF4",  # Nord snow storm
            user_message="#88C0D0",
            agent_message="#A3BE8C",
            system_message="#EBCB8B",
            success="#A3BE8C",
            warning="#EBCB8B",
            error="#BF616A",  # Nord aurora red
            info="#88C0D0",
            debug="#4C566A",  # Nord polar night lighter
            tool_execution="#B48EAD",  # Nord aurora purple
            code_execution="#81A1C1",  # Nord frost blue
            code_output="#D8DEE9",  # Nord snow storm darker
            memory_save="#BF616A",
            memory_load="#B48EAD",
            knowledge="#EBCB8B",
            reasoning="#A3BE8C",
            thoughts="#88C0D0",
            highlight="#EBCB8B",
            emphasis="#BF616A",
            border="#3B4252",
            separator="#4C566A",
            link="#88C0D0",
            reference="#B48EAD",
        ),
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the theme manager.
        
        Args:
            config_path: Path to theme configuration file
        """
        if config_path is None:
            config_path = files.get_abs_path("conf", "theme.json")
        
        self.config_path = config_path
        self.current_theme: Theme = self._load_theme()
    
    def _load_theme(self) -> Theme:
        """Load theme from configuration file or use default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                
                # Reconstruct ColorPalette from saved data
                palette_data = data.get('palette', {})
                palette = ColorPalette(**palette_data)
                
                # Reconstruct Theme
                theme = Theme(
                    name=data.get('name', 'custom'),
                    palette=palette,
                    bold_headings=data.get('bold_headings', True),
                    italic_thoughts=data.get('italic_thoughts', True),
                    underline_links=data.get('underline_links', True),
                    padding_messages=data.get('padding_messages', True),
                    show_timestamps=data.get('show_timestamps', False),
                )
                return theme
            except Exception as e:
                print(f"Warning: Failed to load theme configuration: {e}")
                return self._get_default_theme()
        else:
            return self._get_default_theme()
    
    def _get_default_theme(self) -> Theme:
        """Get the default theme (dark)"""
        return Theme(
            name=ThemeName.DARK.value,
            palette=self.BUILTIN_THEMES[ThemeName.DARK]
        )
    
    def save_theme(self, theme: Optional[Theme] = None):
        """
        Save theme to configuration file.
        
        Args:
            theme: Theme to save (uses current theme if not provided)
        """
        if theme is None:
            theme = self.current_theme
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Convert to dict for JSON serialization
        theme_dict = {
            'name': theme.name,
            'palette': asdict(theme.palette),
            'bold_headings': theme.bold_headings,
            'italic_thoughts': theme.italic_thoughts,
            'underline_links': theme.underline_links,
            'padding_messages': theme.padding_messages,
            'show_timestamps': theme.show_timestamps,
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(theme_dict, f, indent=2)
    
    def switch_theme(self, theme_name: str) -> bool:
        """
        Switch to a different theme.
        
        Args:
            theme_name: Name of the theme to switch to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to match with built-in themes
            for theme_enum in ThemeName:
                if theme_enum.value == theme_name:
                    palette = self.BUILTIN_THEMES.get(theme_enum)
                    if palette:
                        self.current_theme = Theme(
                            name=theme_name,
                            palette=palette
                        )
                        self.save_theme()
                        return True
            
            return False
        except Exception as e:
            print(f"Failed to switch theme: {e}")
            return False
    
    def get_color(self, component: str) -> str:
        """
        Get color for a specific component.
        
        Args:
            component: Component name (e.g., "user_message", "error")
            
        Returns:
            Color code (hex or name)
        """
        return getattr(self.current_theme.palette, component, "#FFFFFF")
    
    def list_themes(self) -> list[str]:
        """Get list of available theme names"""
        return [theme.value for theme in ThemeName if theme != ThemeName.CUSTOM]
    
    def export_theme(self, output_path: str):
        """
        Export current theme to a file.
        
        Args:
            output_path: Path to save the exported theme
        """
        theme_dict = {
            'name': self.current_theme.name,
            'palette': asdict(self.current_theme.palette),
            'bold_headings': self.current_theme.bold_headings,
            'italic_thoughts': self.current_theme.italic_thoughts,
            'underline_links': self.current_theme.underline_links,
            'padding_messages': self.current_theme.padding_messages,
            'show_timestamps': self.current_theme.show_timestamps,
        }
        
        with open(output_path, 'w') as f:
            json.dump(theme_dict, f, indent=2)
    
    def import_theme(self, input_path: str) -> bool:
        """
        Import theme from a file.
        
        Args:
            input_path: Path to the theme file to import
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
            
            palette_data = data.get('palette', {})
            palette = ColorPalette(**palette_data)
            
            self.current_theme = Theme(
                name=data.get('name', 'imported'),
                palette=palette,
                bold_headings=data.get('bold_headings', True),
                italic_thoughts=data.get('italic_thoughts', True),
                underline_links=data.get('underline_links', True),
                padding_messages=data.get('padding_messages', True),
                show_timestamps=data.get('show_timestamps', False),
            )
            
            self.save_theme()
            return True
        except Exception as e:
            print(f"Failed to import theme: {e}")
            return False


# Global theme manager instance
_global_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """
    Get the global theme manager instance.
    
    Returns:
        The global ThemeManager instance
    """
    global _global_theme_manager
    if _global_theme_manager is None:
        _global_theme_manager = ThemeManager()
    return _global_theme_manager


def get_color(component: str) -> str:
    """
    Convenience function to get a color for a component.
    
    Args:
        component: Component name
        
    Returns:
        Color code
    """
    return get_theme_manager().get_color(component)
