"""Tool schemas, handlers, and registry for the observability MCP server."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass

from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_obs.observability import ObservabilityClient


class NoArgs(BaseModel):
    """Empty input model for tools that don't need user arguments."""


class LogsSearchArgs(BaseModel):
    query: str = Field(
        description=(
            "LogsQL query string, e.g. "
            '\'service.name:"Learning Management Service" severity:ERROR _time:1h\' '
            "or any LogsQL expression."
        ),
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Max log entries to return (default 50).",
    )


class LogsErrorCountArgs(BaseModel):
    service: str = Field(
        default="Learning Management Service",
        description='Service name to check, e.g. "Learning Management Service".',
    )
    minutes: int = Field(
        default=60,
        ge=1,
        le=1440,
        description="Time window in minutes (default 60).",
    )


class TracesListArgs(BaseModel):
    service: str = Field(
        default="Learning Management Service",
        description='Service name, e.g. "Learning Management Service".',
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Max traces to return (default 10).",
    )


class TracesGetArgs(BaseModel):
    trace_id: str = Field(
        description="Trace ID to fetch, e.g. 'ae37ebd54705de3240024557154cdc34'.",
    )


# ── Return types ──────────────────────────────────────────────────


class LogsResult(BaseModel):
    entries: list[dict]
    count: int


class EmptyResult(BaseModel):
    message: str


class ErrorCountResult(BaseModel):
    counts: list[dict[str, int | str]]


class TracesListResult(BaseModel):
    traces: list[dict]
    count: int


class TraceResult(BaseModel):
    trace: dict


# ── Handlers ──────────────────────────────────────────────────────


ToolPayload = BaseModel | Sequence[BaseModel]
ToolHandler = Callable[[ObservabilityClient, BaseModel], Awaitable[ToolPayload]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    model: type[BaseModel]
    handler: ToolHandler

    def as_tool(self) -> Tool:
        schema = self.model.model_json_schema()
        schema.pop("$defs", None)
        schema.pop("title", None)
        return Tool(name=self.name, description=self.description, inputSchema=schema)


async def _logs_search(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    if not isinstance(args, LogsSearchArgs):
        raise TypeError(f"Expected {LogsSearchArgs.__name__}, got {type(args).__name__}")
    results = await client.search_logs(args.query, limit=args.limit)
    if not results:
        return EmptyResult(message="No log entries found for the given query.")
    return LogsResult(entries=results, count=len(results))


async def _logs_error_count(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    if not isinstance(args, LogsErrorCountArgs):
        raise TypeError(
            f"Expected {LogsErrorCountArgs.__name__}, got {type(args).__name__}"
        )
    return ErrorCountResult(
        counts=await client.count_errors(service=args.service, minutes=args.minutes)
    )


async def _traces_list(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    if not isinstance(args, TracesListArgs):
        raise TypeError(f"Expected {TracesListArgs.__name__}, got {type(args).__name__}")
    traces = await client.list_traces(args.service, limit=args.limit)
    if not traces:
        return EmptyResult(message=f"No recent traces found for service '{args.service}'.")
    return TracesListResult(traces=traces, count=len(traces))


async def _traces_get(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    if not isinstance(args, TracesGetArgs):
        raise TypeError(f"Expected {TracesGetArgs.__name__}, got {type(args).__name__}")
    trace = await client.get_trace(args.trace_id)
    if trace is None:
        return EmptyResult(message=f"No trace found with ID '{args.trace_id}'.")
    return TraceResult(trace=trace)


# ── Registry ──────────────────────────────────────────────────────


TOOL_SPECS = (
    ToolSpec(
        "logs_search",
        "Search VictoriaLogs using a LogsQL query. Use filters like "
        "service.name, severity, event, and _time range. "
        "Example query: 'service.name:\"Learning Management Service\" severity:ERROR _time:10m'",
        LogsSearchArgs,
        _logs_search,
    ),
    ToolSpec(
        "logs_error_count",
        "Count ERROR-level log entries per service over a time window. "
        "Use this first to quickly check whether there are recent errors "
        "before diving into individual log entries.",
        LogsErrorCountArgs,
        _logs_error_count,
    ),
    ToolSpec(
        "traces_list",
        "List recent traces for a service from VictoriaTraces. "
        "Returns trace IDs, operation names, and durations.",
        TracesListArgs,
        _traces_list,
    ),
    ToolSpec(
        "traces_get",
        "Fetch a full trace by its trace ID. Use this after finding a "
        "trace_id in log entries to see the detailed span hierarchy.",
        TracesGetArgs,
        _traces_get,
    ),
)

TOOLS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}
