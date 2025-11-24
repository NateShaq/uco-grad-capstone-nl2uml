from __future__ import annotations

import os
import logging
from typing import Iterable, List, Optional, Sequence

import requests

from app.infrastructure.internal.agent_registry import AgentRegistry

logger = logging.getLogger(__name__)


def _parse_models(value: Optional[Iterable[str] | str]) -> List[str]:
    """
    Normalize comma or list-based model definitions into a clean list.
    """
    if value is None:
        return []
    if isinstance(value, str):
        tokens = value.replace(";", ",").split(",")
        return [token.strip() for token in tokens if token.strip()]
    return [str(item).strip() for item in value if str(item).strip()]

def _extract_diagram_type_marker(prompt: str) -> Optional[str]:
    """
    Look for an explicit 'DiagramType: <type>' marker in the prompt.
    """
    import re
    match = re.search(r"diagramtype\s*:\s*([a-z_]+)", prompt, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return None


@AgentRegistry.register("ollama-pipeline")
class MultiOllamaPipelineClient:
    """
    Chains multiple Ollama models to improve PlantUML quality:
      1) Ideation model rewrites/structures the user prompt.
      2) UML model produces PlantUML code.
      3) Optional validator model fixes obvious syntax issues.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        ideation_models: Optional[Sequence[str] | str] = None,
        uml_models: Optional[Sequence[str] | str] = None,
        validator_models: Optional[Sequence[str] | str] = None,
        timeout_seconds: int = 180,
        **_: object,
    ):
        self.host = (host or os.getenv("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")
        self.ideation_models = _parse_models(
            ideation_models or os.getenv("OLLAMA_IDEATION_MODELS") or "deepseek-coder-v2:latest, llama3.1:70b"
        )
        self.uml_models = _parse_models(
            uml_models or os.getenv("OLLAMA_UML_MODELS") or "llama3-code:latest, codellama:7b"
        )
        self.validator_models = _parse_models(
            validator_models or os.getenv("OLLAMA_VALIDATION_MODELS") or ""
        )
        self.timeout_seconds = timeout_seconds
        self.debug = (os.getenv("OLLAMA_PIPELINE_DEBUG") or "").lower() in ("1", "true", "yes", "on")

    # --- internal helpers -------------------------------------------------
    def _post(self, model: str, prompt: str) -> str:
        url = f"{self.host}/api/generate"
        data = {"stream": False, "model": model, "prompt": prompt}
        resp = requests.post(url, json=data, timeout=self.timeout_seconds)
        resp.raise_for_status()
        return resp.json().get("response", "")

    def _generate_with_candidates(self, models: List[str], prompt: str) -> str:
        errors = []
        for model in models:
            try:
                result = self._post(model, prompt)
                if self.debug:
                    logger.info("[ollama-pipeline] model=%s output_preview=%s", model, (result[:400] + ("..." if len(result) > 400 else "")))
                return result
            except Exception as exc:  # keep going to the next available model
                errors.append(f"{model}: {exc}")
        raise RuntimeError(f"All Ollama model attempts failed: {' | '.join(errors)}")

    @staticmethod
    def _extract_plantuml(text: str) -> str:
        """
        Extract PlantUML when wrapped in fences; otherwise return the raw text.
        """
        if not text:
            return text
        lower = text.lower()
        start = lower.find("@startuml")
        end = lower.find("@enduml")
        if start != -1 and end != -1:
            return text[start : end + len("@enduml")]
        return text.strip()

    def _validate_with_llm(self, plantuml: str, original_prompt: str, analyst_notes: str) -> str:
        if not self.validator_models:
            return plantuml

        validation_prompt = (
            "You are a PlantUML syntax validator. If the provided UML is valid, return it unchanged.\n"
            "If it is malformed or missing @startuml/@enduml, fix the syntax and return only the corrected PlantUML.\n\n"
            f"Original user prompt:\n{original_prompt}\n\n"
            f"Analyst notes:\n{analyst_notes}\n\n"
            f"PlantUML candidate:\n{plantuml}"
        )
        try:
            return self._extract_plantuml(
                self._generate_with_candidates(self.validator_models, validation_prompt)
            )
        except Exception:
            # If validation fails, fallback to the unvalidated version.
            return plantuml

    # --- agent interface --------------------------------------------------
    def generate(self, prompt: str) -> str:
        """
        Generic text generation using the ideation list (or UML list as fallback).
        """
        candidates = self.ideation_models or self.uml_models
        return self._generate_with_candidates(candidates, prompt)

    def prompt_to_uml(self, prompt: str, diagram_type: Optional[str] = None, pipeline_prompts: Optional[dict] = None) -> str:
        # Respect provided diagram_type/pipeline prompts first; otherwise infer.
        diagram_hint = (pipeline_prompts or {}).get("diagram_type") or diagram_type or self._detect_diagram_type(prompt)
        ideation_prompt = (pipeline_prompts or {}).get("ideation_prompt")
        uml_prompt_template = (pipeline_prompts or {}).get("uml_prompt")
        uml_prompt_uses_notes = (pipeline_prompts or {}).get("uml_prompt_uses_analyst_notes", False)

        # Non-class diagrams: use provided UML prompt or generic builder, skip ideation.
        if diagram_hint != "class":
            direct_prompt = uml_prompt_template or self._build_non_class_prompt(prompt, diagram_hint)
            plantuml = self._extract_plantuml(self._generate_with_candidates(self.uml_models, direct_prompt))
            if self.debug:
                logger.info("[ollama-pipeline] plantuml_candidate=%s", plantuml)
            return self._validate_with_llm(plantuml, prompt, analyst_notes="")

        # Class diagrams: run ideation unless explicitly skipped.
        effective_ideation = ideation_prompt or self._default_class_ideation_prompt(prompt)
        analyst_notes = self._generate_with_candidates(
            self.ideation_models or self.uml_models, effective_ideation
        )
        if self.debug:
            logger.info("[ollama-pipeline] ideation_notes=%s", analyst_notes)

        uml_prompt_text = uml_prompt_template or self._default_class_uml_prompt()
        if uml_prompt_uses_notes or ("{analyst_notes}" in uml_prompt_text):
            uml_prompt_text = uml_prompt_text.format(analyst_notes=analyst_notes, original_prompt=prompt)

        plantuml = self._extract_plantuml(self._generate_with_candidates(self.uml_models, uml_prompt_text))
        if self.debug:
            logger.info("[ollama-pipeline] plantuml_candidate=%s", plantuml)

        # Stage 3: optional LLM-based syntax validation/fixing.
        return self._validate_with_llm(plantuml, prompt, analyst_notes)

    def explain_model(self, model: str) -> str:
        explain_prompt = f"Explain this UML model briefly:\n\n{model}"
        return self.generate(explain_prompt)

    def render_model(self, model: str) -> str:
        return model

    # --- helpers for diagram type detection ------------------------------
    @staticmethod
    def _detect_diagram_type(prompt: str) -> str:
        """
        Best-effort inference of requested diagram type from the prompt text.
        Defaults to class.
        """
        lowered = prompt.lower()
        # Explicit marker override (e.g., "DiagramType: sequence")
        marker = _extract_diagram_type_marker(prompt)
        if marker:
            return marker
        if "sequence diagram" in lowered or "sequence flow" in lowered:
            return "sequence"
        if "use case diagram" in lowered or "use-case diagram" in lowered:
            return "use_case"
        if "activity diagram" in lowered:
            return "activity"
        if "component diagram" in lowered:
            return "component"
        if "state diagram" in lowered or "state machine" in lowered:
            return "state"
        return "class"

    @staticmethod
    def _build_non_class_prompt(user_prompt: str, diagram_type: str) -> str:
        """
        Build a type-specific PlantUML instruction for non-class diagrams.
        """
        base = (
            "You are an expert PlantUML diagram generator.\n"
            "Output ONLY valid PlantUML wrapped by @startuml and @enduml.\n"
            "Do NOT include markdown fences or explanations.\n"
        )
        if diagram_type == "sequence":
            type_rules = (
                "Generate a PlantUML SEQUENCE diagram.\n"
                "- Define participants explicitly (no spaces in aliases).\n"
                "- Include only participants that send/receive messages.\n"
                "- Keep focus on key interactions and lifelines.\n"
            )
        elif diagram_type == "use_case":
            type_rules = (
                "Generate a PlantUML USE CASE diagram.\n"
                "- Include actors, use cases, and their associations.\n"
                "- Prefer concise naming; no extra commentary.\n"
            )
        elif diagram_type == "activity":
            type_rules = (
                "Generate a PlantUML ACTIVITY diagram.\n"
                "- Use start/end, decisions, forks, and activities clearly.\n"
            )
        elif diagram_type == "component":
            type_rules = (
                "Generate a PlantUML COMPONENT diagram.\n"
                "- Include components, interfaces/ports, and dependencies.\n"
            )
        elif diagram_type == "state":
            type_rules = (
                "Generate a PlantUML STATE diagram.\n"
                "- Include states, transitions, and guards where relevant.\n"
            )
        else:
            type_rules = "Generate the requested diagram type.\n"

        return (
            f"{base}{type_rules}\n"
            f"Original request:\n{user_prompt}\n"
        )

    @staticmethod
    def _default_class_ideation_prompt(prompt: str) -> str:
        return (
            "You are a senior software architect.\n"
            "Given a short natural-language description of a software system, you MUST respond in a strict JSON structure that describes the domain model and key use cases.\n"
            "DO NOT write explanations, only valid JSON.\n\n"
            "JSON format:\n"
            "{\n"
            '  \"boundedContexts\": [\n'
            "    {\n"
            '      \"name\": \"string\",\n'
            '      \"description\": \"string\",\n'
            '      \"entities\": [\n'
            "        {\n"
            '          \"name\": \"string\",\n'
            '          \"description\": \"string\",\n'
            '          \"attributes\": [\n'
            '            { \"name\": \"string\", \"type\": \"string\", \"description\": \"string\" }\n'
            "          ],\n"
            '          \"operations\": [\n'
            '            { \"name\": \"string\", \"description\": \"string\" }\n'
            "          ]\n"
            "        }\n"
            "      ],\n"
            '      \"valueObjects\": [\n'
            '        { \"name\": \"string\", \"description\": \"string\" }\n'
            "      ],\n"
            '      \"services\": [\n'
            "        {\n"
            '          \"name\": \"string\",\n'
            '          \"description\": \"string\",\n'
            '          \"operations\": [\n'
            '            { \"name\": \"string\", \"description\": \"string\" }\n'
            "          ]\n"
            "        }\n"
            "      ],\n"
            '      \"relationships\": [\n'
            "        {\n"
            '          \"from\": \"string\",\n'
            '          \"to\": \"string\",\n'
            '          \"type\": \"association|aggregation|composition|inheritance\",\n'
            '          \"description\": \"string\"\n'
            "        }\n"
            "      ],\n"
            '      \"useCases\": [\n'
            "        {\n"
            '          \"name\": \"string\",\n'
            '          \"primaryActor\": \"string\",\n'
            '          \"summary\": \"string\"\n'
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Now analyze the following system description and return ONLY JSON in that format, no extra text.\n\n"
            f"{prompt}"
        )

    @staticmethod
    def _default_class_uml_prompt() -> str:
        return (
            "You are an expert PlantUML Class Diagram generator.\n"
            "Your task is to take a JSON description of a domain model and output ONLY valid PlantUML code for a class diagram.\n"
            "RULES:\n"
            "1. Output MUST be:\n"
            "   @startuml\n"
            "   ...classes and relations...\n"
            "   @enduml\n\n"
            "2. Do NOT include markdown fences or explanations.\n"
            "3. Every class must come from an \"entities\" or \"services\" entry.\n"
            "4. Map JSON to UML like this:\n"
            "   - entities → class\n"
            "   - services → class with «service» stereotype\n"
            "   - attributes → fields\n"
            "   - operations → methods\n"
            "   - relationships.type:\n"
            "       - association  → A --> B\n"
            "       - aggregation  → A o-- B\n"
            "       - composition  → A *-- B\n"
            "       - inheritance  → A <|-- B\n\n"
            "5. Use simple types (string, int, decimal, date, boolean) as-is.\n"
            "6. Validate the UML for syntactic correctness before returning.\n\n"
            "Here is the JSON domain model:\n"
            "{analyst_notes}\n\n"
            "The model outputs:"
        )

    def refine_model(self, model: str, feedback: str) -> str:
        refine_prompt = (
            "You are refining an existing PlantUML diagram based on feedback.\n"
            "Apply the feedback, ensure valid syntax, and return only the updated PlantUML between @startuml and @enduml.\n\n"
            f"Current PlantUML:\n{model}\n\n"
            f"Feedback:\n{feedback}"
        )
        updated = self._extract_plantuml(self._generate_with_candidates(self.uml_models, refine_prompt))
        if self.debug:
            logger.info("[ollama-pipeline] refined_candidate=%s", updated)
        return self._validate_with_llm(updated, feedback, model)

    def generate_code(self, model: str) -> str:
        """
        Optional compatibility hook; reuse UML models to translate diagrams into code.
        """
        code_prompt = (
            "Convert the PlantUML diagram into clean, well-structured code. "
            "Choose reasonable defaults for types and keep output concise.\n\n"
            f"PlantUML:\n{model}"
        )
        return self._generate_with_candidates(self.uml_models, code_prompt)
