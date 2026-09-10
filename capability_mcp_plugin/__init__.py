# -*- coding: utf-8 -*-
"""Capability MCP Plugin — Banyanos capability-facing MCP compatibility layer.

This plugin ports the capability-MCP-specific code from ``mcp_daemon_engine``
into a standalone package. It depends on ``silvaengine_daemon`` for shared
daemon runtime behavior and on ``mcp_protocol_plugin`` for native MCP catalog
and runtime operations.
"""
from __future__ import annotations

__author__ = "bibow"