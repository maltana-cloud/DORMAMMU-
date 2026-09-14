"""Bounded static engineering intelligence for DORMAMMU.

This module inspects supplied source text without importing or executing it. It
produces deterministic findings and dependency-impact hints. Findings are
advisory evidence only: they cannot edit code, run commands, grant authority,
or deploy anything.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping

_MAX_FILES = 128
_MAX_SOURCE_CHARS = 200_000
_MAX_FINDINGS = 256
_MAX_IMPORTS = 256
_MAX_TEXT = 512

@dataclass(frozen=True)
class EngineeringFinding:
    file_path: str
    kind: str
    severity: str
    message: str
    line: int = 0

@dataclass(frozen=True)
class EngineeringReport:
    scope_id: str
    files_analyzed: int
    source_digest: str
    findings: tuple[EngineeringFinding, ...]
    imports: tuple[tuple[str, tuple[str, ...]], ...]
    impacted_files: tuple[str, ...]
    @property
    def safe(self) -> bool:
        return not any(f.severity == "error" for f in self.findings)

class EngineeringIntelligence:
    """Analyze bounded Python source snapshots as untrusted engineering evidence."""
    def analyze(self, scope_id: str, files: Mapping[str, str]) -> EngineeringReport:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        if not isinstance(files, Mapping):
            raise TypeError("files must be a mapping")
        if len(files) > _MAX_FILES:
            raise ValueError("file count exceeds bound")
        findings: list[EngineeringFinding] = []
        imports: dict[str, tuple[str, ...]] = {}
        normalized: list[str] = []
        for path in sorted(files):
            source = files[path]
            if not isinstance(path, str) or not path.strip():
                raise ValueError("file paths are required")
            if not isinstance(source, str):
                raise TypeError("source must be text")
            if len(source) > _MAX_SOURCE_CHARS:
                findings.append(EngineeringFinding(path, "bound", "error", "source exceeds analysis size bound"))
                continue
            normalized.append(path + "\0" + source)
            if not path.endswith(".py"):
                continue
            try:
                tree = ast.parse(source, filename=path)
            except SyntaxError as exc:
                findings.append(EngineeringFinding(path, "syntax", "error", "syntax error: " + str(exc.msg)[:_MAX_TEXT], exc.lineno or 0))
                continue
            module_imports: list[str] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    module_imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    module_imports.append(node.module)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "eval":
                    findings.append(EngineeringFinding(path, "dynamic_execution", "error", "eval() requires security review", node.lineno))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "exec":
                    findings.append(EngineeringFinding(path, "dynamic_execution", "error", "exec() requires security review", node.lineno))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen"}:
                    findings.append(EngineeringFinding(path, "process_execution", "error", f"{node.func.attr}() requires security review", node.lineno))
            imports[path] = tuple(sorted(set(module_imports)))[:_MAX_IMPORTS]
        if len(findings) > _MAX_FINDINGS:
            findings = findings[:_MAX_FINDINGS]
        digest = sha256("\n".join(normalized).encode("utf-8")).hexdigest()
        changed_modules = {p.rsplit("/", 1)[-1].removesuffix(".py") for p in imports}
        impacted = sorted(path for path, deps in imports.items() if any(dep.rsplit(".", 1)[-1] in changed_modules for dep in deps))
        return EngineeringReport(scope_id.strip(), len(files), digest, tuple(findings), tuple(sorted(imports.items())), tuple(impacted))
