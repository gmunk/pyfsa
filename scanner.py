from finite_automaton import NFA


def create_nfa(regex: str) -> NFA:
    nfa_stack = []

    for c in regex:
        a = NFA.from_concatenation(nfa_stack.pop(-2), nfa_stack.pop()) if c == "?" \
                else NFA.from_union(nfa_stack.pop(-2), nfa_stack.pop()) if c == "|" \
                else NFA.from_kleene_closure(nfa_stack.pop()) if c == "*" \
                else NFA.from_symbol(c)
        nfa_stack.append(a)

    return nfa_stack.pop()
