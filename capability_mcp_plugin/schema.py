#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Capability MCP Plugin — GraphQL schema.

Aggregates capability-MCP-specific queries, mutations, and types into a
standalone graphene Schema. Only capability_mcp fields are included —
this plugin does not define native MCP catalog types (those live in
``mcp_protocol_plugin``).
"""
from __future__ import print_function

__author__ = "bibow"

from typing import Any, Dict, List, Type

from graphene import (
    Field,
    ID,
    Int,
    ObjectType,
    ResolveInfo,
    Schema,
    String,
)

from .mutations.capability_mcp import (
    CheckCapabilityCustomMcpGitPackageVersion,
    GenerateCapabilityCustomMcpUploadUrl,
    InvokeCapabilityMcpTool,
    RefreshCapabilityCustomMcpGitPackage,
    RegisterCapabilityCustomMcpGitPackage,
    RegisterCapabilityCustomMcpPackage,
    RegisterCapabilityCustomMcpPackageBase64,
    RegisterCapabilityMcp,
    RegisterCapabilityRemoteMcp,
    TestCapabilityMcpTool,
    UnregisterCapabilityMcp,
)
from .queries.capability_mcp import (
    resolve_capability_mcp_invocation_list,
    resolve_capability_mcp_provider,
    resolve_capability_mcp_provider_list,
    resolve_capability_mcp_server,
    resolve_capability_mcp_server_tools,
    resolve_capability_mcp_tool,
    resolve_capability_mcp_tool_list,
)
from .types.capability_mcp import (
    CapabilityMcpGitVersionInfo,
    CapabilityMcpInvocation,
    CapabilityMcpInvocationConnection,
    CapabilityMcpProvider,
    CapabilityMcpProviderConnection,
    CapabilityMcpRegistrationPayload,
    CapabilityMcpSyncStats,
    CapabilityMcpTool,
    CapabilityMcpToolConnection,
    CapabilityMcpTransport,
    CapabilityMcpUnregistrationPayload,
)


def type_class() -> List[Type[ObjectType]]:
    """Return all GraphQL types that need explicit schema registration.

    graphene.Schema requires types not directly referenced in Query or
    Mutation fields to be listed here so introspection can discover them.
    """
    return [
        CapabilityMcpTransport,
        CapabilityMcpProvider,
        CapabilityMcpProviderConnection,
        CapabilityMcpTool,
        CapabilityMcpToolConnection,
        CapabilityMcpSyncStats,
        CapabilityMcpRegistrationPayload,
        CapabilityMcpGitVersionInfo,
        CapabilityMcpUnregistrationPayload,
        CapabilityMcpInvocation,
        CapabilityMcpInvocationConnection,
    ]


class Query(ObjectType):
    """Capability MCP Plugin root Query — provider/server/tool/invocation
    read views shaped for Banyanos clients."""

    # --- Provider / MCP Server queries ---
    capability_mcp_provider = Field(
        CapabilityMcpProvider,
        id=ID(required=True),
    )

    capability_mcp_provider_list = Field(
        CapabilityMcpProviderConnection,
        page_number=Int(required=False),
        limit=Int(required=False),
        transport=CapabilityMcpTransport(required=False),
        status=String(required=False),
        keyword=String(required=False),
    )

    capability_mcp_server = Field(
        CapabilityMcpProvider,
        id=ID(required=True),
    )

    capability_mcp_server_tools = Field(
        CapabilityMcpToolConnection,
        id=ID(required=True),
        page_number=Int(required=False),
        limit=Int(required=False),
    )

    # --- Tool queries ---
    capability_mcp_tool = Field(
        CapabilityMcpTool,
        id=ID(required=True),
    )

    capability_mcp_tool_list = Field(
        CapabilityMcpToolConnection,
        page_number=Int(required=False),
        limit=Int(required=False),
        provider_id=ID(required=False),
        status=String(required=False),
        keyword=String(required=False),
    )

    # --- Invocation queries ---
    capability_mcp_invocation_list = Field(
        CapabilityMcpInvocationConnection,
        page_number=Int(required=False),
        limit=Int(required=False),
        tool_name=String(required=False),
        status=String(required=False),
    )

    # --- Resolvers ---
    def resolve_capability_mcp_provider(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ):
        return resolve_capability_mcp_provider(info, **kwargs)

    def resolve_capability_mcp_provider_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ):
        return resolve_capability_mcp_provider_list(info, **kwargs)

    def resolve_capability_mcp_server(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ):
        return resolve_capability_mcp_server(info, **kwargs)

    def resolve_capability_mcp_server_tools(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ):
        return resolve_capability_mcp_server_tools(info, **kwargs)

    def resolve_capability_mcp_tool(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ):
        return resolve_capability_mcp_tool(info, **kwargs)

    def resolve_capability_mcp_tool_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ):
        return resolve_capability_mcp_tool_list(info, **kwargs)

    def resolve_capability_mcp_invocation_list(
        self, info: ResolveInfo, **kwargs: Dict[str, Any]
    ):
        return resolve_capability_mcp_invocation_list(info, **kwargs)


class Mutations(ObjectType):
    """Capability MCP Plugin root Mutation — registration, invocation,
    and deregistration operations."""

    # Unified face-outside register (recommended for Banyanos clients):
    register_capability_mcp = RegisterCapabilityMcp.Field()
    # Individual register mutations (backward compat / strict-arg enforcement):
    register_capability_remote_mcp = RegisterCapabilityRemoteMcp.Field()
    generate_capability_custom_mcp_upload_url = (
        GenerateCapabilityCustomMcpUploadUrl.Field()
    )
    register_capability_custom_mcp_package = (
        RegisterCapabilityCustomMcpPackage.Field()
    )
    register_capability_custom_mcp_package_base64 = (
        RegisterCapabilityCustomMcpPackageBase64.Field()
    )
    register_capability_custom_mcp_git_package = (
        RegisterCapabilityCustomMcpGitPackage.Field()
    )
    refresh_capability_custom_mcp_git_package = (
        RefreshCapabilityCustomMcpGitPackage.Field()
    )
    check_capability_custom_mcp_git_package_version = (
        CheckCapabilityCustomMcpGitPackageVersion.Field()
    )
    invoke_capability_mcp_tool = InvokeCapabilityMcpTool.Field()
    test_capability_mcp_tool = TestCapabilityMcpTool.Field()
    unregister_capability_mcp = UnregisterCapabilityMcp.Field()


def build_schema() -> Schema:
    """Build and return the capability MCP graphene Schema."""
    return Schema(
        query=Query,
        mutation=Mutations,
        types=type_class(),
    )