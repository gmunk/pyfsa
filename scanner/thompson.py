from collections import deque

from fa import NFA, State


LPAREN = "("
RPAREN = ")"
CONCATENATION = "."
ALTERNATION = "|"
CLOSURE = "*"
OPERATORS = {ALTERNATION, CLOSURE}
SPECIAL_CHARS = OPERATORS.union({LPAREN, RPAREN, CONCATENATION})
PRECEDENCE = {
    CLOSURE: 1,
    CONCATENATION: 2,
    ALTERNATION: 3,
    LPAREN: 4,
    RPAREN: 4
}


def format_regex(regex: str) -> str:
    """Formats a regex by inserting an explicit concatenation operator.

    Parameters
    ----------
    regex : str
        Regex to be formatted.

    Returns
    -------
    str
        Formatted regex with explicit concatenation operators, where appropriate.
    """
    def should_concatenate(a, b):
        return a != LPAREN and b != RPAREN and a != ALTERNATION and b not in OPERATORS

    return "".join([c + "." if i + 1 < len(regex) and should_concatenate(c, regex[i + 1])
                    else c for i, c in enumerate(regex)])


def convert_to_postfix(regex: str) -> str:
    """Converts a regex to postfix notation using the Shunting-Yard algorithm.

    This is a simplified version of the algorithm since the scope of the conversion is much smaller.
    Chapter 2 of the book talks about three operators - closure, concatenation and alternation, therefore they are
    the ones handled here. This function expects that the input regex has been formatted with explicit concatenation
    operators.

    Parameters
    ----------
    regex : str
        Infix regex, formatted with explicit concatenation operators.

    Returns
    -------
    str
        Regex converted to postfix notation.
    """
    output = deque()
    operators = []

    for c in regex:
        if c not in SPECIAL_CHARS:
            output.append(c)
        elif c == LPAREN:
            operators.append(c)
        elif c == RPAREN:
            while True:
                o = operators.pop()

                if o == LPAREN:
                    break

                output.append(o)
        else:
            while True:
                if operators and PRECEDENCE[operators[-1]] <= PRECEDENCE[c]:
                    output.append(operators.pop())
                else:
                    operators.append(c)

                    break

    output.extend(operators[::-1])

    return "".join(output)


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
