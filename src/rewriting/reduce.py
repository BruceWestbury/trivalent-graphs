"""
src.rewriting.reduce.py

This module contains functions for reducing expressions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from algebra.linear_combinations import GraphKey, LinearCombination


@dataclass(frozen=True)
class Occurrence:
    """A cached occurrence of a rule inside a host graph."""

    data: dict

    def to_json(self) -> dict:
        return dict(self.data)


@dataclass(frozen=True)
class ReductionRule:
    """A cached oriented reduction rule."""

    name: str
    lhs_key: GraphKey


@dataclass(frozen=True)
class CachedReduction:
    """One cached application of a rule to a host graph."""

    host_key: GraphKey
    rule_name: str
    occurrence: Occurrence
    replacement: LinearCombination


@dataclass(frozen=True)
class ReductionStep:
    """One step in a reduction trace."""

    before: LinearCombination
    host_key: GraphKey
    coefficient: object
    rule_name: str
    occurrence: Occurrence
    replacement: LinearCombination
    after: LinearCombination

    def to_json(self) -> dict:
        return {
            "before": self.before.to_json(),
            "host": self.host_key,
            "coefficient": str(self.coefficient),
            "rule": self.rule_name,
            "occurrence": self.occurrence.to_json(),
            "replacement": self.replacement.to_json(),
            "after": self.after.to_json(),
        }


@dataclass(frozen=True)
class ReductionTrace:
    """A complete deterministic reduction trace."""

    initial: LinearCombination
    final: LinearCombination
    steps: list[ReductionStep]

    def to_json(self) -> dict:
        return {
            "initial": self.initial.to_json(),
            "final": self.final.to_json(),
            "steps": [step.to_json() for step in self.steps],
        }


class ReductionSystem:
    """Deterministic reducer using cached one-step reductions."""

    def __init__(
        self,
        rules: Iterable[ReductionRule],
        reductions: Iterable[CachedReduction],
    ):
        self.rules = list(rules)
        self.rule_order = {rule.name: i for i, rule in enumerate(self.rules)}

        self.reductions_by_host: dict[GraphKey, list[CachedReduction]] = {}

        for reduction in reductions:
            self.reductions_by_host.setdefault(reduction.host_key, []).append(reduction)

        for host_key, host_reductions in self.reductions_by_host.items():
            host_reductions.sort(
                key=lambda r: self.rule_order.get(r.rule_name, len(self.rule_order))
            )

    def first_reduction(self, graph_key: GraphKey) -> CachedReduction | None:
        """Return the first cached reduction for graph_key, if any."""
        reductions = self.reductions_by_host.get(graph_key, [])
        if not reductions:
            return None
        return reductions[0]

    def reduce_once(
        self,
        element: LinearCombination,
    ) -> tuple[LinearCombination, ReductionStep | None]:
        """Apply the first available reduction to the first reducible term."""

        for graph_key, coefficient in element.terms.items():
            reduction = self.first_reduction(graph_key)

            if reduction is None:
                continue

            before = element
            after = element.substitute(
                graph_key,
                coefficient * reduction.replacement,
            )

            step = ReductionStep(
                before=before,
                host_key=graph_key,
                coefficient=coefficient,
                rule_name=reduction.rule_name,
                occurrence=reduction.occurrence,
                replacement=reduction.replacement,
                after=after,
            )

            return after, step

        return element, None

    def reduce_element_with_trace(
        self,
        element: LinearCombination,
        max_steps: int = 10_000,
    ) -> ReductionTrace:
        """Reduce an element and record every reduction step."""

        current = element
        steps: list[ReductionStep] = []

        for _ in range(max_steps):
            current, step = self.reduce_once(current)

            if step is None:
                return ReductionTrace(
                    initial=element,
                    final=current,
                    steps=steps,
                )

            steps.append(step)

        raise RuntimeError(f"reduce_element_with_trace exceeded max_steps={max_steps}")
