from __future__ import annotations
import re

CONNECTOR_CHARS = set("-.<>|o*")
LABEL_INFIX_RE = re.compile(r"([-.o<>*]+)\|[^|]+\|")

DECLARATION_RE = re.compile(r"^\s*(Class|CLASS|Interface|INTERFACE)\b")
INLINE_INHERIT_RE = re.compile(r"^\s*(class|interface)\s+([A-Za-z0-9_]+)\s+(extends|implements|:)\s+([A-Za-z0-9_,\s]+)\s*(\{?)", re.IGNORECASE)
CONNECTOR_RE = re.compile(r'^(\s*\S+)\s+"([^"]+)"\s+(\S+)(.*)$')
RELATIONSHIP_RE = re.compile(r"\b\S+\s+[-.o*]+[<>|]?[-.o*]*\s+\S+")
PLACEHOLDER_PHRASES = (
    "rest of your code remains the same",
    "rest of the code remains the same",
    "rest of your code remains unchanged",
)
DROP_DIRECTIVE_PREFIXES = (
    "!include",         # drop !include / !includeurl from class diagrams
    "includeurl",
    "layout ",          # e.g., "Layout horizontal tree" from C4
    "layout_",          # generic layout directives
)

def sanitize_plantuml(plantuml: str) -> str:
    """
    Apply lightweight normalization to reduce common syntax errors emitted by LLMs.
    Currently:
      * force `Class`/`Interface` declarations to lowercase `class`/`interface`
      * rewrite inline inheritance (`class Foo extends Bar`) into connector statements
      * remove quotes around relationship connectors such as "o--"
      * drop placeholder ellipsis lines like "... (The rest of your code remains the same)"
    """
    if not plantuml:
        return plantuml

    print("[PlantUML sanitizer] Normalizing diagram before validation.")

    lines = plantuml.splitlines()
    cleaned_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        line_relationships: list[str] = []

        # Remove LLM placeholders that break PlantUML syntax.
        if _is_placeholder_line(stripped):
            continue

        # Drop extraneous directives (e.g., C4 includes/layout) that break class diagrams.
        if _is_extraneous_directive(stripped):
            continue

        # Normalize declaration keyword casing
        if DECLARATION_RE.match(line):
            line = line.replace("Class", "class").replace("CLASS", "class").replace("Interface", "interface").replace("INTERFACE", "interface")

        # Expand inline inheritance/interfaces into connectors
        match = INLINE_INHERIT_RE.match(line)
        if match:
            keyword, cls_name, relation, parents, brace = match.groups()
            normalized = f"{keyword.lower()} {cls_name}"
            if not brace.strip():
                normalized += " {"
            else:
                normalized += brace if brace.strip() == "{" else " {"
            line = normalized
            for parent in parents.split(","):
                parent = parent.strip()
                if not parent:
                    continue
                rel = relation.lower()
                kw = keyword.lower()
                if rel in ("implements",):
                    line_relationships.append(f"{cls_name} ..|> {parent}")
                elif rel == "extends":
                    connector = "--|>" if kw == "class" else "..|>"
                    line_relationships.append(f"{cls_name} {connector} {parent}")
                elif rel == ":":
                    line_relationships.append(f"{cls_name} --|> {parent}")

        # Remove inline status markers like -->|success|
        line = _strip_arrow_infix_labels(line)

        # Remove quotes around connectors like "o--"
        line = _strip_connector_quotes(line)

        cleaned_lines.append(line)
        cleaned_lines.extend(line_relationships)

    sanitized = "\n".join(cleaned_lines)

    # Guardrail: if we ever reduced relationship lines, fall back to the original
    # to avoid accidentally dropping associations/dependencies.
    if _count_relationships(sanitized) < _count_relationships(plantuml):
        print("[PlantUML sanitizer] Relationship lines decreased after sanitization; using original diagram to preserve associations.")
        return plantuml

    return sanitized

def _strip_connector_quotes(line: str) -> str:
    match = CONNECTOR_RE.match(line)
    if not match:
        return line
    left, connector, right, suffix = match.groups()
    if connector and all(ch in CONNECTOR_CHARS for ch in connector):
        return f"{left} {connector} {right}{suffix}"
    return line

def _strip_arrow_infix_labels(line: str) -> str:
    # Converts patterns like -->|success| into plain -->, dropping the label.
    return LABEL_INFIX_RE.sub(r"\1", line)

def _count_relationships(plantuml: str) -> int:
    return sum(1 for ln in plantuml.splitlines() if RELATIONSHIP_RE.search(ln))

def _is_placeholder_line(line: str) -> bool:
    """
    Drop common ellipsis placeholders the LLM sometimes emits instead of repeating
    the unchanged diagram body.
    """
    lower = line.lower()
    if not lower.startswith("..."):
        return False
    return any(phrase in lower for phrase in PLACEHOLDER_PHRASES)


def _is_extraneous_directive(line: str) -> bool:
    """
    Removes directives commonly emitted from other UML styles (e.g., C4 includes/layouts).
    """
    lower = line.lower()
    return any(lower.startswith(prefix) for prefix in DROP_DIRECTIVE_PREFIXES)
