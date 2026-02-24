# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Logging utilities for aiconfigurator."""

import logging
import os
import re
import sys


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log output.

    Colors:
    - Header (time, [aiconfigurator], filename) in grey
    - Log level icon ([I], [W], [E], [D]) based on level:
      - INFO: Blue
      - WARNING: Yellow
      - ERROR: Red
      - DEBUG: Cyan
    - Message stays white (default)
    """

    # ANSI color codes
    GREY = "\033[90m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if colors should be disabled (e.g., when output is redirected)
        self.use_colors = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

    def format(self, record):
        # Get the base formatted message
        log_message = super().format(record)

        if not self.use_colors:
            return log_message

        # Handle different log formats
        # Format 1: "HH:MM:SS [aiconfigurator] [L] [filename:line] message"
        # Format 2: "LEVELNAME YYYY-MM-DD HH:MM:SS,mmm filename:line] message"
        # Format 3: "LEVELNAME HH:MM:SS filename:line] message"

        # Check if format contains [aiconfigurator] (format 1)
        if "[aiconfigurator]" in log_message:
            parts = log_message.split(" ", 3)
            if len(parts) >= 4:
                time_part = parts[0]
                aiconfig_part = parts[1]
                level_part = parts[2]  # [L]
                rest = parts[3]

                bracket_end = rest.find("]")
                if bracket_end != -1:
                    filename_part = rest[: bracket_end + 1]
                    message_part = rest[bracket_end + 1 :].lstrip()  # Skip "]" and any whitespace

                    colored_header = f"{self.GREY}{time_part} {aiconfig_part} {filename_part}{self.RESET}"
                    level_char = level_part[1] if len(level_part) > 1 else " "
                    colored_level = self._color_level(level_char, level_part)
                    return f"{colored_header} {colored_level} {message_part}"

        # Handle format 2 and 3: "LEVELNAME TIMESTAMP filename:line] message"
        else:
            # Find the first space after levelname
            first_space = log_message.find(" ")
            if first_space == -1:
                return log_message

            levelname_part = log_message[:first_space]
            rest_after_level = log_message[first_space + 1 :]

            # Find where filename starts (look for pattern like "filename:line]")
            # The timestamp ends before the filename, which starts with a word character
            # Match pattern: filename (word chars, dots, underscores, hyphens), colon, digits, closing bracket
            filename_match = re.search(r"[\w\.\-]+:\d+]", rest_after_level)
            if filename_match:
                time_part = rest_after_level[: filename_match.start()].rstrip()
                filename_and_rest = rest_after_level[filename_match.start() :]

                bracket_end = filename_and_rest.find("]")
                if bracket_end != -1:
                    filename_part = filename_and_rest[: bracket_end + 1]
                    message_part = filename_and_rest[bracket_end + 1 :].lstrip()

                    colored_header = f"{self.GREY}{time_part} {filename_part}{self.RESET}"
                    level_char = levelname_part[0] if levelname_part else " "
                    colored_level = self._color_level(level_char, levelname_part)
                    return f"{colored_level} {colored_header} {message_part}"

        return log_message

    def _color_level(self, level_char, level_part):
        """Color the log level based on the first character."""
        color_map = {
            "I": self.BLUE,
            "W": self.YELLOW,
            "E": self.RED,
            "D": self.CYAN,
        }
        if level_char in color_map:
            return f"{color_map[level_char]}{level_part}{self.RESET}"
        return level_part
