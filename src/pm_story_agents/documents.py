"""Validated review documents. A revision is always a complete replacement."""

from __future__ import annotations

import json
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DocumentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Evidence(DocumentModel):
    source: Literal["design", "transcript", "product"]
    quote: str = Field(min_length=8)


class Requirement(DocumentModel):
    text: str = Field(min_length=5)
    evidence: list[Evidence] = Field(min_length=1)


class Criterion(DocumentModel):
    given: str = Field(min_length=5)
    when: str = Field(min_length=5)
    then: str = Field(min_length=5)
    evidence: list[Evidence] = Field(min_length=1)


class Title(DocumentModel):
    id: str = Field(pattern=r"^ST-\d{3}$")
    title: str = Field(min_length=5)
    statement: str = Field(min_length=10)


class TitleSet(DocumentModel):
    stories: list[Title] = Field(min_length=1, max_length=20)
    scope_notes: list[str] = Field(default_factory=list)


class Story(Title):
    requirements: list[Requirement] = Field(min_length=1)
    acceptance_criteria: list[Criterion] = Field(min_length=1)
    open_questions: list[str]


class StorySet(DocumentModel):
    stories: list[Story] = Field(min_length=1, max_length=20)


def parse_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```json") and text.endswith("```"):
        text = text[7:-3].strip()
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object.")
    return value


def _ids(document: TitleSet | StorySet) -> set[str]:
    ids = [story.id for story in document.stories]
    if len(ids) != len(set(ids)):
        raise ValueError("Every story must have a unique stable ID.")
    return set(ids)


def validate_titles(raw: str) -> str:
    document = TitleSet.model_validate(parse_json(raw))
    _ids(document)
    return document.model_dump_json(indent=2)


def _normalized(value: str) -> str:
    return " ".join(value.split())


def validate_stories(raw: str, titles: str, sources: dict[str, str]) -> str:
    document = StorySet.model_validate(parse_json(raw))
    expected = _ids(TitleSet.model_validate(parse_json(titles)))
    actual = _ids(document)
    if actual != expected:
        raise ValueError(
            f"Full story set required. Missing IDs: {sorted(expected - actual)}; "
            f"unapproved IDs: {sorted(actual - expected)}."
        )
    for story in document.stories:
        for item in [*story.requirements, *story.acceptance_criteria]:
            for evidence in item.evidence:
                if _normalized(evidence.quote) not in _normalized(sources[evidence.source]):
                    raise ValueError(
                        f"{story.id}: evidence quote is not present in the supplied {evidence.source} source."
                    )
    return document.model_dump_json(indent=2)


def story_metrics(stories: str, sources: dict[str, str]) -> dict:
    document = StorySet.model_validate(parse_json(stories))
    requirements = [item for story in document.stories for item in story.requirements]
    criteria = [item for story in document.stories for item in story.acceptance_criteria]
    citations = [e for item in [*requirements, *criteria] for e in item.evidence]
    verified = sum(_normalized(e.quote) in _normalized(sources[e.source]) for e in citations)
    return {
        "stories": len(document.stories),
        "requirements": len(requirements),
        "criteria": len(criteria),
        "open_questions": sum(len(story.open_questions) for story in document.stories),
        "verified_quotes": verified,
        "total_quotes": len(citations),
        "child_node_verification": "not_performed",
        "quality_lift": "not_measured",
    }


def markdown_export(raw: str) -> str:
    document = StorySet.model_validate(parse_json(raw))
    lines = ["# PM story review", "", "Draft output. Jira publishing disabled.", ""]
    for story in document.stories:
        lines += [f"## {story.id} - {story.title}", "", story.statement, "", "### Requirements", ""]
        for requirement in story.requirements:
            lines.append(f"- {requirement.text}")
            lines += [f"  - {e.source}: {e.quote}" for e in requirement.evidence]
        lines += ["", "### Acceptance criteria", ""]
        for number, criterion in enumerate(story.acceptance_criteria, 1):
            lines += [
                f"{number}. **Given** {criterion.given}",
                f"   **When** {criterion.when}",
                f"   **Then** {criterion.then}",
            ]
            lines += [f"   - {e.source}: {e.quote}" for e in criterion.evidence]
        lines += ["", "### Open questions", ""]
        lines += [f"- {question}" for question in story.open_questions] or ["None recorded."]
        lines.append("")
    return "\n".join(lines)


def source_screen_ids(design: str) -> list[str]:
    return sorted(set(re.findall(r"\bAPPT-\d{3}\b", design)))
