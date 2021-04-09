import itertools
import json
from pathlib import Path
from collections import defaultdict
from typing import Optional, DefaultDict

Transitions = Optional[DefaultDict[str, set["State"]]]
EpsilonTransitions = Optional[list["State"]]

EPSILON_TRANSITION_TOKEN = "EPS"


class State:
    """A representation of a state in a finite automaton.

    For the purposes of this project a state is comprised of a label,
    a dictionary of the possible, outward transitions,
    and a list of the possible, outward epsilon transitions. This helps when the basic NFAs of
    Thompson's construction are created, the whole process reduces to setting pointers to initial and accepting states
    plus addition of epsilon transitions, where necessary.

    Attributes
    ----------
    label : str
        Label of this state.
    transitions : DefaultDict[str, set[State]]
        Outward transitions of this note, a set of states for each character which has a transition.
    epsilon_transitions : list[State]
        Outward epsilon transitions of this node.

    """
    def __init__(self, label: str, transitions: Transitions = None,
                 epsilon_transitions: EpsilonTransitions = None) -> None:
        self.label = label
        self.transitions = transitions if transitions is not None else defaultdict(set)
        self.epsilon_transitions = epsilon_transitions if epsilon_transitions is not None else []

    def __repr__(self) -> str:
        return "State(label={label})".format(
            label=self.label, transitions=self.transitions, epsilon_transitions=self.epsilon_transitions)

    def add_transition(self, symbol: str, state: "State") -> None:
        """Adds one transition to the dict of outward transitions.

        Parameters
        ----------
        symbol : str
            Symbol which the new transition is going to be performed on.
        state : State
            State which the new transitions is pointing to.

        """
        self.transitions[symbol].add(state)

    def add_epsilon_transition(self, state: "State") -> None:
        """Adds one epsilon transition to the list of epsilon transitions.

        Parameters
        ----------
        state : State
            State which the new epsilon transitions is pointing to.

        """
        self.epsilon_transitions.append(state)

    def add_epsilon_transitions(self, states: list["State"]) -> None:
        """Adds multiple epsilon transitions to the list of epsilon transitions.

        Parameters
        ----------
        states : list["State"]
            List of states of new epsilon transitions.

        """
        self.epsilon_transitions.extend(states)

    def get_epsilon_closure(self) -> set["State"]:
        """Creates a set of all the states (including this one),
        reachable from this state, by following epsilon transitions.

        Returns
        -------
        set[State]
            Set of states reached by following epsilon transitions. This state is also included.
        """
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