import itertools
import json
from pathlib import Path
from collections import defaultdict
from typing import Optional

Transitions = Optional[defaultdict[str, set["State"]]]
EpsilonTransitions = Optional[list["State"]]

EPSILON_TRANSITION_TOKEN = "EPS"


class State:
    def __init__(self, label: str, transitions: Transitions = None,
                 epsilon_transitions: EpsilonTransitions = None) -> None:
        self.label = label
        self.transitions = transitions if transitions is not None else defaultdict(set)
        self.epsilon_transitions = epsilon_transitions if epsilon_transitions is not None else []

    def __repr__(self) -> str:
        return "State(label={label})".format(
            label=self.label, transitions=self.transitions, epsilon_transitions=self.epsilon_transitions)

    def add_transition(self, symbol: str, state: "State") -> None:
        self.transitions[symbol].add(state)

    def add_epsilon_transition(self, state: "State") -> None:
        self.epsilon_transitions.append(state)

    def add_epsilon_transitions(self, states: list["State"]) -> None:
        self.epsilon_transitions.extend(states)

    def get_epsilon_closure(self) -> set["State"]:
        return {self, *self.epsilon_transitions,
                *list(itertools.chain(*[e.get_epsilon_closure() for e in self.epsilon_transitions]))}


class NFA:
    def __init__(self, states: set[State], alphabet: set[str], initial_state: State, accepting_states: set[State]):
        self.states = states
        self.alphabet = alphabet
        self.initial_state = initial_state
        self.accepting_states = accepting_states

        self.epsilon_closures = self.__create_epsilon_closures()

    def __repr__(self) -> str:
        return "NFA(states={states}, alphabet={alphabet}, initial_state={initial_state}, " \
               "accepting_states={accepting_states})".format(states=self.states, alphabet=self.alphabet,
                                                             initial_state=self.initial_state,
                                                             accepting_states=self.accepting_states)

    @classmethod
    def from_json_file(cls, filepath: Path) -> "NFA":
        with open(filepath, 'r') as f:
            data = json.load(f)

            states = {s: State(s) for s in data["states"]}
            accepting_states = {states[s] for s in data["accepting_states"]}

            for t in data["transitions"]:
                if t["symbol"] == EPSILON_TRANSITION_TOKEN:
                    states[t["from"]].add_epsilon_transition(states[t["to"]])
                else:
                    states[t["from"]].add_transition(t["symbol"], states[t["to"]])

            print(states.values())

            return cls(states=set(states.values()),
                       alphabet=set(data["alphabet"]),
                       initial_state=states[data["initial_state"]],
                       accepting_states=accepting_states)

    def accepts(self, input_str: str) -> bool:
        current_states = {self.initial_state}

        for s in input_str:
            current_states = {t for c in current_states for e in self.epsilon_closures[c.label] for t in
                              e.transitions.get(s, {})}

        return not current_states.isdisjoint(self.accepting_states)

    def __create_epsilon_closures(self):
        return {s.label: s.get_epsilon_closure() for s in self.states}


def build_symbol_nfa(s: str) -> NFA:
    initial, accepting = State("initial_{symbol}".format(symbol=s)), State("accepting_{symbol}".format(symbol=s))

    initial.add_transition(s, accepting)

    return NFA(states={initial, accepting}, alphabet={s}, initial_state=initial, accepting_states={accepting})


def build_concatenation_nfa(first: NFA, second: NFA) -> NFA:
    for s in first.accepting_states:
        s.add_epsilon_transition(second.initial_state)

    return NFA(states=first.states.union(second.states),
               alphabet=first.alphabet.union(second.alphabet),
               initial_state=first.initial_state,
               accepting_states=second.accepting_states)


def build_union_nfa(first: NFA, second: NFA) -> NFA:
    initial, accepting = State("initial_union",
                               epsilon_transitions=[first.initial_state, second.initial_state]), \
                         State("accepting_union")

    for sf, ss in zip(first.accepting_states, second.accepting_states):
        sf.add_epsilon_transition(accepting)
        ss.add_epsilon_transition(accepting)

    return NFA(states=first.states.union(second.states).union({initial, accepting}),
               alphabet=first.alphabet.union(second.alphabet),
               initial_state=initial,
               accepting_states={accepting})


def build_closure_nfa(source: NFA) -> NFA:
    accepting = State("accepting_closure")
    initial = State("initial_closure", epsilon_transitions=[source.initial_state, accepting])

    for s in source.accepting_states:
        s.add_epsilon_transitions([source.initial_state, accepting])

    return NFA(states=source.states.union({initial, accepting}),
               alphabet=source.alphabet,
               initial_state=initial,
               accepting_states={accepting})
