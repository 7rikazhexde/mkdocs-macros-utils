"""
MkDocs Macros Cards Debug Logger Module
"""

import logging
from typing import Optional, Any, Dict
from mkdocs_macros.plugin import MacrosPlugin


class DebugLogger:
    """
    Class to control debug logging

    Create a logger specific to each module to flexibly control debug settings
    """

    @classmethod
    def create_logger(
        cls, module_name: str, env: Optional[MacrosPlugin] = None
    ) -> "DebugLogger":
        """
        Create loggers based on preferences

        Args: (str): Module name of the logger
            module_name (str): Logger module name
            env (Optional[MacrosPlugin], optional): MkDocs macro environment. Defaults to None.

        Returns: Args: module_name (str): Module name of the logger.
            DebugLogger: Debug logger instance initialized.
        """
        # Get debug configuration
        debug_config = cls._get_debug_config(env)

        # Get module-specific debug configuration (default is false)
        module_debug = debug_config.get(module_name, False)

        return cls(module_name, module_debug)

    @classmethod
    def _get_debug_config(cls, env: Optional[MacrosPlugin] = None) -> Dict[str, bool]:
        """
        Get debug settings

        Args:.
            env (Optional[MacrosPlugin], optional): MkDocs macro environment. Defaults to None.

        Returns:
            Dict[str, bool]: Debug settings
        """
        if not env:
            return {}

        # Get extra.debug settings
        debug_config = env.variables.get("extra", {}).get("debug", {})

        return {
            "link_card": debug_config.get("link_card", False),
            "gist_codeblock": debug_config.get("gist_codeblock", False),
            "x_twitter_card": debug_config.get("x_twitter_card", False),
        }

    def __init__(self, module_name: str, enabled: bool = False) -> None:
        """
        Initializing Loggers

        Args: (str): Initialize the logger
            module_name (str): Module name
            enabled (bool, optional): enable or disable debug logging. Defaults to False.
        """
        self.logger = logging.getLogger(f"mkdocs.plugins.macros-utils.{module_name}")
        self.logger.setLevel(logging.DEBUG if enabled else logging.WARNING)
        self.enabled = enabled

    def log(self, message: str, data: Optional[Any] = None) -> None:
        """
        Output debugging information

        Args: Outputs debugging information.
            message (str): log message
            data (Optional[Any], optional): additional log data. Defaults to None.
        """
        if not self.enabled:
            return

        self.logger.debug(f"{message}")
        if data is not None:
            # Convert data to string and output
            data_str = str(data) if not isinstance(data, str) else data
            self.logger.debug(f"        {data_str}")
