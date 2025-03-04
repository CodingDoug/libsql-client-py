from __future__ import annotations
from typing import Any, List, Optional, cast
from typing_extensions import TypedDict
import aiohttp
import urllib.parse

from .client import Client, InArgs, InStatement, LibsqlError, Transaction
from .config import _Config
from .hrana import proto
from .hrana.convert import (
    _stmt_to_proto, _result_set_from_proto,
    _batch_to_proto, _batch_results_from_proto,
)
from .result import ResultSet

def _create_http_client(config: _Config) -> HttpClient:
    assert config.scheme in ("http", "https")
    url = urllib.parse.urlunparse((
        config.scheme, config.authority, config.path,
        "", "", "",
    ))
    return HttpClient(url, auth_token=config.auth_token)

class HttpClient(Client):
    _session: aiohttp.ClientSession
    _url: str

    def __init__(self, url: str, *, auth_token: Optional[str] = None):
        headers = {"authorization": f"Bearer {auth_token}"}
        self._session = aiohttp.ClientSession(headers=headers)
        self._url = url

    async def execute(self, stmt: InStatement, args: InArgs = None) -> ResultSet:
        request: _ExecuteReq = {
            "stmt": _stmt_to_proto(stmt, args),
        }
        response = await self._send("POST", "v1/execute", request)
        proto_res = cast(_ExecuteResp, response)["result"]
        return _result_set_from_proto(proto_res)

    async def batch(self, stmts: List[InStatement]) -> List[ResultSet]:
        request: _BatchReq = {
            "batch": _batch_to_proto(stmts),
        }
        response = await self._send("POST", "v1/batch", request)
        proto_res = cast(_BatchResp, response)["result"]
        return _batch_results_from_proto(proto_res, len(stmts))

    def transaction(self) -> Transaction:
        raise LibsqlError(
            "The HTTP client does not support transactions. "
            "Please use a libsql:, ws: or wss: URL, so that the client connects using a WebSocket.",
            "TRANSACTIONS_NOT_SUPPORTED",
        )

    async def close(self) -> None:
        await self._session.close()

    @property
    def closed(self) -> bool:
        return self._session.closed

    async def _send(self, method: str, path: str, request_body: Any) -> Any:
        url = urllib.parse.urljoin(self._url, path)
        async with self._session.request(method, url, json=request_body) as resp:
            if not resp.ok:
                if resp.content_type == "application/json":
                    resp_json = await resp.json()
                    if "message" in resp_json:
                        message = resp_json["message"]
                        code = resp_json.get("code") or "UNKNOWN"
                        raise LibsqlError(message, code)
                elif resp.content_type == "text/plain":
                    resp_text = await resp.text()
                    raise LibsqlError(
                        f"Server returned HTTP status {resp.status} and error: {resp_text!r}",
                        "SERVER_ERROR",
                    )
                raise LibsqlError(f"Server returned HTTP status {resp.status}", "SERVER_ERROR")

            return await resp.json()

_ExecuteReq = TypedDict("_ExecuteReq", {
    "stmt": proto.Stmt,
})
_ExecuteResp = TypedDict("_ExecuteResp", {
    "result": proto.StmtResult,
})

_BatchReq = TypedDict("_BatchReq", {
    "batch": proto.Batch,
})
_BatchResp = TypedDict("_BatchResp", {
    "result": proto.BatchResult,
})
