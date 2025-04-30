from typing import Any, Dict, List, Optional
from src.planning.plan_models import ToolSpec
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PluginManager:
    """
    A basic placeholder for a plugin manager.
    In a real system, this would handle loading, registering, and managing plugins.
    """

    def __init__(self):
        """
        Initializes an empty plugin manager.
        """
        self._plugins: Dict[str, Any] = {}
        logging.info("PluginManager component initialized.")

    def register_plugin(self, plugin_name: str, plugin_instance: Any):
        """
        Registers a plugin with the manager.

        Args:
            plugin_name: The unique name of the plugin.
            plugin_instance: An instance of the plugin.
        """
        if plugin_name in self._plugins:
            logging.warning(f"Plugin '{plugin_name}' is already registered. Overwriting.")
        self._plugins[plugin_name] = plugin_instance
        logging.info(f"Plugin '{plugin_name}' registered.")

    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """
        Retrieves a registered plugin by name.

        Args:
            plugin_name: The name of the plugin to retrieve.

        Returns:
            The plugin instance, or None if not found.
        """
        plugin = self._plugins.get(plugin_name)
        if plugin is None:
            logging.warning(f"Attempted to retrieve non-existent plugin: {plugin_name}")
        return plugin

    def list_plugins(self) -> List[str]:
        """
        Lists the names of all registered plugins.

        Returns:
            A list of plugin names.
        """
        return list(self._plugins.keys())

    def unregister_plugin(self, plugin_name: str):
        """
        Unregisters a plugin.

        Args:
            plugin_name: The name of the plugin to unregister.
        """
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]
            logging.info(f"Plugin '{plugin_name}' unregistered.")
        else:
            logging.warning(f"Attempted to unregister non-existent plugin: {plugin_name}")

    def get_tool_specs(self) -> List[ToolSpec]:
            """
            Retrieves a list of ToolSpec objects for all registered plugins.
            Currently generates placeholder specs.

            Returns:
                A list of ToolSpec objects.
            """
            tool_specs = []
            for plugin_name in self._plugins.keys():
                # Create a basic ToolSpec using the registration name
                spec = ToolSpec(
                    id=plugin_name,
                    name=plugin_name,
                    description=f"Placeholder tool: {plugin_name}",
                    input_schema=None,  # Placeholder
                    output_schema=None  # Placeholder
                )
                tool_specs.append(spec)
            return tool_specs
# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    class DummyPlugin:
        def run(self):
            print("DummyPlugin is running.")

    plugin_manager = PluginManager()

    # Register a dummy plugin
    dummy_plugin_instance = DummyPlugin()
    plugin_manager.register_plugin("dummy_feature", dummy_plugin_instance)

    # List plugins
    print(f"\nRegistered plugins: {plugin_manager.list_plugins()}")

    # Retrieve and use a plugin
    retrieved_plugin = plugin_manager.get_plugin("dummy_feature")
    if retrieved_plugin:
        retrieved_plugin.run()

    # Attempt to retrieve a non-existent plugin
    non_existent_plugin = plugin_manager.get_plugin("another_feature")
    print(f"Retrieved non-existent plugin: {non_existent_plugin}")

    # Unregister a plugin
    plugin_manager.unregister_plugin("dummy_feature")
    print(f"\nRegistered plugins after unregistering: {plugin_manager.list_plugins()}")

    # Attempt to unregister a non-existent plugin
    plugin_manager.unregister_plugin("another_feature")