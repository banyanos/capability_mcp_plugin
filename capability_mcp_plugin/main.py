#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Gateway dispatch entry points for Capability MCP Plugin.

Provides ``dispatch_graphql`` for the gateway route manifest. The plugin
shares the MCP Protocol Plugin's Config singleton (``mcp_protocol_plugin``)
for persistence and tool-loading infrastructure, while defining its own
GraphQL schema surface for Banyanos-shaped capability-MCP queries and
mutations.
"""
from __future__ import print_function

__author__ = "bibow"

import logging
from typing import Any, Dict

from graphene import Schema
from silvaengine_utility import Graphql

from .schema import Query, Mutations, type_class


class CapabilityMCPPlugin(Graphql):
    """Thin GraphQL handler for the Capability MCP surface.

    Relies on ``mcp_protocol_plugin.handlers.config:Config`` for DB backend,
    RLS context, and MCP configuration state. Only the GraphQL schema is
    owned here; all persistence and tool-invocation logic lives in the
    handler/query/mutation modules copied from ``mcp_daemon_engine``.
    """

    def __init__(self, logger: logging.Logger, **setting: Dict[str, Any]) -> None:
        Graphql.__init__(self, logger, **setting)
        self.logger = logger
        self.setting = setting

    def capability_mcp_graphql(self, **params: Dict[str, Any]) -> Any:
        """Execute a capability-MCP GraphQL request."""
        self._apply_partition_defaults(params)
        partition_key = params.get("partition_key") or params.get(
            "context", {}
        ).get("partition_key")

        # Set RLS tenant context when running on PostgreSQL backend.
        # The Config singleton comes from mcp_protocol_plugin, which manages
        # the DB session and RLS lifecycle.
        if partition_key:
            try:
                from mcp_protocol_plugin.handlers.config import Config

                if Config.DB_BACKEND == "postgresql":
                    Config._set_rls_context(partition_key)
            except ImportError:
                pass

        try:
            return self.execute(self.__class__.build_graphql_schema(), **params)
        finally:
            try:
                from mcp_protocol_plugin.handlers.config import Config

                if Config.DB_BACKEND == "postgresql" and Config.db_session:
                    Config.db_session.remove()
            except ImportError:
                pass

    def _apply_partition_defaults(self, params: Dict[str, Any]) -> None:
        """Backfill partition_key, endpoint_id, and part_id into params."""
        from silvaengine_daemon.partitioning import apply_partition_defaults

        apply_partition_defaults(params, self.setting)

    @staticmethod
    def build_graphql_schema() -> Schema:
        return Schema(
            query=Query,
            mutation=Mutations,
            types=type_class(),
        )


# ---------------------------------------------------------------------------
# Module-level dispatch functions for gateway integration
# ---------------------------------------------------------------------------


def _engine() -> CapabilityMCPPlugin:
    """Create a short-lived plugin instance using the shared Config."""
    from mcp_protocol_plugin.handlers.config import Config

    return CapabilityMCPPlugin(Config.get_logger(), **Config.get_setting())


def dispatch_graphql(**params: Dict[str, Any]) -> Any:
    """Gateway dispatch entry point for Capability MCP GraphQL.

    Requires ``mcp_protocol_plugin.handlers.config:Config`` to have been
    initialized by gateway startup (the MCP protocol plugin's module
    route entry initializes it).
    """
    return _engine().capability_mcp_graphql(**params)


__all__ = ["CapabilityMCPPlugin", "dispatch_graphql"]