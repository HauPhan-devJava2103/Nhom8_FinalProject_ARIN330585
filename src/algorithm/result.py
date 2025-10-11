from dataclasses import dataclass
from model.node import Node

@dataclass(frozen=True)
class Result:
    node: Node
    number_of_explored_states: int
    cost: int = 0
