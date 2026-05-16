"""
src.reduction_trace.py


"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ReductionOccurrence:
    rule_name: str
    host_key: str
    matched_subgraph: tuple[int, ...]


@dataclass(frozen=True)
class ReductionStep:
    before: LinearCombination
    occurrence: ReductionOccurrence
    replacement: LinearCombination
    after: LinearCombination


@dataclass
class ReductionTrace:
    input_graph: str
    steps: list[ReductionStep]
    result: LinearCombination
