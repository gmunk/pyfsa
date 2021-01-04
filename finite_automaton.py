from abc import ABC, abstractmethod
from collections import defaultdict


class FiniteAutomaton(ABC):
    """
    Abstract base class extended by all automaton classes.

    Attributes
    ----------
    states : set
        The finite set of states in the automaton.
    alphabet : set
        The finite alphabet used by the automaton.
    transition_mappings : dict
        The mappings of the automaton, this abstraction serves as the transition function in the formal mathematical
        definition of a finite automaton.
    start_state : str
        The designated start state.
    accepting_states : set
        Set of accepting states.
    """

    def __init__(self,
                 states=None,
                 alphabet=None,
                 transition_mappings=None,
                 start_state=None,
                 accepting_states=None):
        """
        Default constructor for all automaton classes.

        This constructor tries to follow the definition of an automaton as a formal mathematical object described by
        a five-tuple. Each automaton consists of a finite set of states (omitting the error state),
        finite alphabet, transition mappings, a designated start state and a set of accepting states.

        Parameters
        ----------
        states : set
            A set of states which the automaton is going to work with.
        alphabet : set
            A set describing the alphabet accepted by this automaton.
        transition_mappings : dict
            A dictionary describing the transitions the automaton takes based on the input it receives.
        start_state : str
            The starting state for the automaton.
        accepting_states: set
            A set of accepting states, if the automaton finishes its work in one of them,
            it means it has accepted the provided input.
        """
        self.states = states if states is not None else set()
        self.alphabet = alphabet if alphabet is not None else set()
        self.transition_mappings = transition_mappings if transition_mappings is not None else {}
        self.start_state = start_state
        self.accepting_states = accepting_states if accepting_states is not None else set()

        super(FiniteAutomaton, self).__init__()

    @abstractmethod
    def accepts(self, input_str):
        pass


class DeterministicFiniteAutomaton(FiniteAutomaton):
    """
    Implementation of a deterministic finite automaton (DFA).

    DFA is a finite automaton which has a single valued
    transition function which does not allow for epsilon transitions.

    Methods
    -------
    accepts(input_str)
        Check whether the automaton accepts the provided input string.
    """

    def accepts(self, input_str):

        current_state = self.start_state

        for i in input_str:
            current_state = self.transition_mappings.get(current_state, {}).get(i)
            if current_state is None:
                break

        return current_state in self.accepting_states


class NondeterministicFiniteAutomaton(FiniteAutomaton):
    """
    Implementation of a non-deterministic finite automaton (NFA).

    NFA is a finite automaton that allows epsilon transitions,
    furthermore its transition function is not single valued,
    states that have multiple transitions on the same input character are allowed.

    Attributes
    ----------
    states : set
        A set of states which the automaton is going to work with.
    alphabet : set
        A set describing the alphabet accepted by this automaton.
    transition_mappings : dict
        A dictionary describing the transitions the automaton takes based on the input it receives.
    start_state : str
        The starting state for the automaton.
    accepting_states: set
        A set of accepting states, if the automaton finishes its work in one of them,
        it means it has accepted the provided input.
    epsilon_closures: dict
        A dictionary of pre-computed epsilon-closures for each state in the automaton.
        An epsilon closure is the set of states that can be reached from a starting state
        by following epsilon transitions (plus the starting state).

    Methods
    -------
    accepts(input_str)
        Check whether the automaton accepts the provided input string.
    """
    def __init__(self,
                 states=None,
                 alphabet=None,
                 transition_mappings=None,
                 start_state=None,
                 accepting_states=None):
        super().__init__(states, alphabet, transition_mappings, start_state, accepting_states)
        self.epsilon_closures = self.__create_epsilon_closures(states)

    def accepts(self, input_str):
        current_states = {self.start_state}

        for i in input_str:
            current_states = {s for cs in current_states for ecs in self.epsilon_closures[cs] for s in
                              self.transition_mappings.get(ecs, {}).get(i, {})}

        return not current_states.isdisjoint(self.accepting_states)

    def __create_epsilon_closures(self, states):
        epsilon_predecessors = self.__create_epsilon_predecessors()

        epsilon_closures = {s: {s} for s in states}

        work_list = set(states)
        while work_list:
            state = work_list.pop()

            epsilon_targets = self.transition_mappings.get(state, {}).get("", set())
            epsilon_closure = {s for et in epsilon_targets for s in epsilon_closures[et]}

            if epsilon_closure != epsilon_closures[state]:
                epsilon_closures[state].update(epsilon_closure)
                work_list.union(epsilon_predecessors[state])

        return epsilon_closures

    def __create_epsilon_predecessors(self):
        epsilon_predecessors = defaultdict(set)

        for k, v in self.transition_mappings.items():
            if "" in v:
                for s in v[""]:
                    epsilon_predecessors[s].add(k)

        return epsilon_predecessors
