#!/usr/bin/env python3
"""Convert the drf-spectacular OpenAPI file into a Postman v2.1 collection (+ environment)."""
import json
import re
import sys
import uuid

import yaml

src, dst = sys.argv[1], sys.argv[2]
spec = yaml.safe_load(open(src, encoding="utf-8"))
schemas = spec.get("components", {}).get("schemas", {})


def resolve(s, depth=0):
    if not isinstance(s, dict) or depth > 4:
        return {}
    if "$ref" in s:
        return resolve(schemas.get(s["$ref"].split("/")[-1], {}), depth + 1)
    if "allOf" in s:
        out = {"type": "object", "properties": {}}
        for part in s["allOf"]:
            out["properties"].update(resolve(part, depth + 1).get("properties", {}))
        return out
    return s


def example(s, depth=0):
    s = resolve(s, depth)
    t = s.get("type")
    if "enum" in s:
        return s["enum"][0]
    if t == "object" or "properties" in s:
        return {k: example(v, depth + 1) for k, v in s.get("properties", {}).items() if not resolve(v, depth + 1).get("readOnly") and not v.get("readOnly")}
    if t == "array":
        return [example(s.get("items", {}), depth + 1)]
    if t == "integer":
        return 1
    if t == "number":
        return 1.5
    if t == "boolean":
        return True
    fmt = s.get("format")
    return {"date": "2026-01-31", "date-time": "2026-01-31T09:00:00Z", "email": "user@example.com", "binary": ""}.get(fmt, "string")


def url_obj(path, params):
    raw = "{{base_url}}" + re.sub(r"{(\w+)}", r":\1", path)
    q = [{"key": p["name"], "value": "", "disabled": True} for p in params if p["in"] == "query"]
    v = [{"key": p["name"], "value": "1"} for p in params if p["in"] == "path"]
    return {"raw": raw, "host": ["{{base_url}}"], "path": [x for x in re.sub(r"{(\w+)}", r":\1", path).split("/") if x],
            "query": q, "variable": v}


folders = {}
for path, ops in spec["paths"].items():
    for method, op in ops.items():
        if method not in ("get", "post", "put", "patch", "delete"):
            continue
        tag = (op.get("tags") or ["misc"])[0]
        params = op.get("parameters", [])
        item = {"name": op.get("summary") or f"{method.upper()} {path}",
                "request": {"method": method.upper(), "header": [], "url": url_obj(path, params),
                            "description": op.get("description", "")}}
        public = op.get("security") == [{}] or path.endswith("/login/") or path.endswith("/refresh/") or path == "/api/health/"
        if public:
            item["request"]["auth"] = {"type": "noauth"}
        body = (op.get("requestBody") or {}).get("content", {})
        if "application/json" in body:
            item["request"]["header"].append({"key": "Content-Type", "value": "application/json"})
            item["request"]["body"] = {"mode": "raw", "raw": json.dumps(example(body["application/json"].get("schema", {})), indent=2),
                                       "options": {"raw": {"language": "json"}}}
        elif "multipart/form-data" in body:
            props = resolve(body["multipart/form-data"].get("schema", {})).get("properties", {})
            item["request"]["body"] = {"mode": "formdata", "formdata": [
                {"key": k, "type": "file" if v.get("format") == "binary" else "text", "value": ""} for k, v in props.items()
                if not v.get("readOnly")]}
        if path.endswith("/auth/login/") and method == "post":
            item["request"]["body"]["raw"] = json.dumps({"email": "admin@oilops.com", "password": "OilOps@2026!"}, indent=2)
            item["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": [
                "const r = pm.response.json();",
                "if (r.access) { pm.collectionVariables.set('access_token', r.access); pm.collectionVariables.set('refresh_token', r.refresh); }"]}}]
        if path.endswith("/auth/refresh/") and method == "post":
            item["request"]["body"]["raw"] = json.dumps({"refresh": "{{refresh_token}}"}, indent=2)
            item["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": [
                "const r = pm.response.json();",
                "if (r.access) { pm.collectionVariables.set('access_token', r.access); if (r.refresh) pm.collectionVariables.set('refresh_token', r.refresh); }"]}}]
        folders.setdefault(tag, []).append(item)

order = ["auth"] + sorted(t for t in folders if t != "auth")
collection = {
    "info": {"_postman_id": str(uuid.uuid4()), "name": "OilOps Pro API", "description": spec["info"].get("description", ""),
             "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
    "auth": {"type": "bearer", "bearer": [{"key": "token", "value": "{{access_token}}", "type": "string"}]},
    "variable": [{"key": "base_url", "value": "http://localhost:8000"}, {"key": "access_token", "value": ""},
                 {"key": "refresh_token", "value": ""}, {"key": "device_key", "value": "dev-device-key"}],
    "item": [{"name": t, "item": folders[t]} for t in order if t in folders],
}
json.dump(collection, open(dst, "w"), indent=2)
print(f"{sum(len(v) for v in folders.values())} requests in {len(folders)} folders -> {dst}")
