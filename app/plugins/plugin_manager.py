"""
Plugin System for ERP
Allows extending functionality through plugins
"""

import os
import importlib
import inspect
from typing import Dict, List, Any, Callable
from pathlib import Path


class PluginInterface:
    """Base interface for all plugins"""
    
    def __init__(self):
        self.name = "Base Plugin"
        self.version = "1.0.0"
        self.description = "Base plugin interface"
        self.author = "Unknown"
    
    def initialize(self):
        """Called when plugin is loaded"""
        pass
    
    def activate(self):
        """Called when plugin is activated"""
        pass
    
    def deactivate(self):
        """Called when plugin is deactivated"""
        pass
    
    def get_menu_items(self) -> List[Dict[str, Any]]:
        """Return menu items to add to the application"""
        return []
    
    def get_widgets(self) -> List[Any]:
        """Return widgets to add to the application"""
        return []
    
    def on_event(self, event_name: str, data: Dict[str, Any]):
        """Handle application events"""
        pass


class PluginManager:
    """Manages loading, activation, and execution of plugins"""
    
    def __init__(self, plugins_dir: str = "app/plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginInterface] = {}
        self.active_plugins: Dict[str, PluginInterface] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
    
    def discover_plugins(self):
        """Discover all available plugins"""
        if not self.plugins_dir.exists():
            print(f"Plugins directory {self.plugins_dir} does not exist")
            return
        
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and not item.name.startswith('__'):
                self._load_plugin(item)
    
    def _load_plugin(self, plugin_path: Path):
        """Load a single plugin"""
        try:
            # Look for plugin.py file
            plugin_file = plugin_path / "plugin.py"
            if not plugin_file.exists():
                return
            
            # Import the plugin module
            module_name = f"app.plugins.{plugin_path.name}.plugin"
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, PluginInterface) and obj != PluginInterface:
                    plugin_instance = obj()
                    plugin_instance.initialize()
                    self.plugins[plugin_instance.name] = plugin_instance
                    print(f"Loaded plugin: {plugin_instance.name} v{plugin_instance.version}")
                    break
        
        except Exception as e:
            print(f"Error loading plugin from {plugin_path}: {e}")
    
    def activate_plugin(self, plugin_name: str):
        """Activate a plugin"""
        if plugin_name in self.plugins and plugin_name not in self.active_plugins:
            plugin = self.plugins[plugin_name]
            plugin.activate()
            self.active_plugins[plugin_name] = plugin
            print(f"Activated plugin: {plugin_name}")
            return True
        return False
    
    def deactivate_plugin(self, plugin_name: str):
        """Deactivate a plugin"""
        if plugin_name in self.active_plugins:
            plugin = self.active_plugins[plugin_name]
            plugin.deactivate()
            del self.active_plugins[plugin_name]
            print(f"Deactivated plugin: {plugin_name}")
            return True
        return False
    
    def get_plugin(self, plugin_name: str) -> PluginInterface:
        """Get a plugin by name"""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """Get all loaded plugins"""
        return self.plugins
    
    def get_active_plugins(self) -> Dict[str, PluginInterface]:
        """Get all active plugins"""
        return self.active_plugins
    
    def trigger_event(self, event_name: str, data: Dict[str, Any]):
        """Trigger an event for all active plugins"""
        for plugin in self.active_plugins.values():
            try:
                plugin.on_event(event_name, data)
            except Exception as e:
                print(f"Error in plugin {plugin.name} handling event {event_name}: {e}")
    
    def get_all_menu_items(self) -> List[Dict[str, Any]]:
        """Get menu items from all active plugins"""
        menu_items = []
        for plugin in self.active_plugins.values():
            menu_items.extend(plugin.get_menu_items())
        return menu_items
    
    def get_all_widgets(self) -> List[Any]:
        """Get widgets from all active plugins"""
        widgets = []
        for plugin in self.active_plugins.values():
            widgets.extend(plugin.get_widgets())
        return widgets


# Example Plugin Template
class ExamplePlugin(PluginInterface):
    """Example plugin demonstrating the plugin system"""
    
    def __init__(self):
        super().__init__()
        self.name = "Example Plugin"
        self.version = "1.0.0"
        self.description = "An example plugin for demonstration"
        self.author = "ERP Team"
    
    def initialize(self):
        """Initialize the plugin"""
        print(f"Initializing {self.name}")
    
    def activate(self):
        """Activate the plugin"""
        print(f"Activating {self.name}")
    
    def deactivate(self):
        """Deactivate the plugin"""
        print(f"Deactivating {self.name}")
    
    def get_menu_items(self):
        """Return menu items"""
        return [
            {
                'name': 'Example Action',
                'callback': self.example_action,
                'icon': None
            }
        ]
    
    def example_action(self):
        """Example action"""
        print("Example action executed!")
    
    def on_event(self, event_name: str, data: Dict[str, Any]):
        """Handle events"""
        if event_name == "invoice_created":
            print(f"Plugin received invoice_created event: {data}")


# Global plugin manager instance
_plugin_manager = None

def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
        _plugin_manager.discover_plugins()
    return _plugin_manager
