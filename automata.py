from collections import deque


EPSILON = ""


class NFA:
    def __init__(self):
        self.states = []
        self.edges = []
        self.start = None
        self.finals = set()

    def new_state(self):
        state = len(self.states)
        self.states.append(state)
        return state

    def add_edge(self, source, label, target):
        self.edges.append((source, label, target))


def thompson(regex):
    text = "".join(regex.split())
    position = 0
    nfa = NFA()

    # every parse function returns the (start, end) of the piece it built
    def read_atom():
        nonlocal position
        if position == len(text):
            raise ValueError("Expected a symbol or an opening parenthesis.")
        char = text[position]
        position += 1
        if char == "(":
            fragment = read_union()
            if position == len(text) or text[position] != ")":
                raise ValueError("Missing closing parenthesis.")
            position += 1
            return fragment
        if not (char.isalnum() or char in "ε∅"):
            raise ValueError(f"Unexpected character: {char!r}")
        start = nfa.new_state()
        end = nfa.new_state()
        if char != "∅":
            nfa.add_edge(start, EPSILON if char == "ε" else char, end)
        return start, end

    def read_star():
        nonlocal position
        start, end = read_atom()
        while position < len(text) and text[position] == "*":
            position += 1
            new_start = nfa.new_state()
            new_end = nfa.new_state()
            nfa.add_edge(new_start, EPSILON, start)
            nfa.add_edge(new_start, EPSILON, new_end)
            nfa.add_edge(end, EPSILON, start)
            nfa.add_edge(end, EPSILON, new_end)
            start, end = new_start, new_end
        return start, end

    def read_concat():
        if position == len(text) or text[position] in "|)":
            raise ValueError("Empty branch: write ε if you mean the empty word.")
        start, end = read_star()
        while position < len(text) and text[position] not in "|)":
            next_start, next_end = read_star()
            nfa.add_edge(end, EPSILON, next_start)
            end = next_end
        return start, end

    def read_union():
        nonlocal position
        start, end = read_concat()
        while position < len(text) and text[position] == "|":
            position += 1
            right_start, right_end = read_concat()
            new_start = nfa.new_state()
            new_end = nfa.new_state()
            nfa.add_edge(new_start, EPSILON, start)
            nfa.add_edge(new_start, EPSILON, right_start)
            nfa.add_edge(end, EPSILON, new_end)
            nfa.add_edge(right_end, EPSILON, new_end)
            start, end = new_start, new_end
        return start, end

    nfa.start, end = read_union()
    if position != len(text):
        raise ValueError(f"Unexpected character: {text[position]!r}")
    nfa.finals = {end}
    return nfa


def degrees(nfa):
    incoming = {q: 0 for q in nfa.states}
    outgoing = {q: 0 for q in nfa.states}
    for source, label, target in nfa.edges:
        outgoing[source] += 1
        incoming[target] += 1
    return incoming, outgoing


def make_2_nfa(nfa):
    result = NFA()
    for q in nfa.states:
        result.new_state()
    result.start = nfa.start
    result.finals = set(nfa.finals)

    # edge ids so each end of an edge can be moved on its own
    sources = [source for source, label, target in nfa.edges]
    targets = [target for source, label, target in nfa.edges]
    incoming = {q: [] for q in nfa.states}
    outgoing = {q: [] for q in nfa.states}
    for edge_id, (source, label, target) in enumerate(nfa.edges):
        outgoing[source].append(edge_id)
        incoming[target].append(edge_id)

    def attach(root, edge_ids, direction, low=0, high=None):
        if high is None:
            high = len(edge_ids)
        if high - low <= 2:
            for i in range(low, high):
                edge_id = edge_ids[i]
                if direction == "out":
                    sources[edge_id] = root
                else:
                    targets[edge_id] = root
            return

        middle = (low + high) // 2
        for begin, end in ((low, middle), (middle, high)):
            if end - begin == 1:
                attach(root, edge_ids, direction, begin, end)
            else:
                helper = result.new_state()
                if direction == "out":
                    result.add_edge(root, EPSILON, helper)
                else:
                    result.add_edge(helper, EPSILON, root)
                attach(helper, edge_ids, direction, begin, end)

    for q in nfa.states:
        attach(q, outgoing[q], "out")
        attach(q, incoming[q], "in")

    for edge_id, (source, label, target) in enumerate(nfa.edges):
        result.add_edge(sources[edge_id], label, targets[edge_id])
    return result


def alphabet(nfa):
    return sorted({label for source, label, target in nfa.edges if label != EPSILON})


def epsilon_closure(nfa, states):
    reached = set(states)
    todo = list(reached)
    while todo:
        state = todo.pop()
        for source, label, target in nfa.edges:
            if source == state and label == EPSILON and target not in reached:
                reached.add(target)
                todo.append(target)
    return frozenset(reached)


def remove_epsilon(nfa):
    result = NFA()
    keep = [nfa.start] + sorted({t for s, a, t in nfa.edges if a != EPSILON} - {nfa.start})
    number = {q: result.new_state() for q in keep}
    result.start = number[nfa.start]
    for q in keep:
        closure = epsilon_closure(nfa, {q})
        if closure & nfa.finals:
            result.finals.add(number[q])
        for label, target in sorted({(a, t) for s, a, t in nfa.edges if s in closure and a != EPSILON}):
            result.add_edge(number[q], label, number[target])
    return result


def step(nfa, states, char):
    next_states = set()
    for source, label, target in nfa.edges:
        if source in states and label == char:
            next_states.add(target)
    return epsilon_closure(nfa, next_states)


def accepts(nfa, word):
    active = epsilon_closure(nfa, {nfa.start})
    for char in word:
        active = step(nfa, active, char)
    return bool(active & nfa.finals)


def to_dfa(nfa):
    dfa = NFA()
    first = epsilon_closure(nfa, {nfa.start})
    subsets = [first]
    number = {first: dfa.new_state()}
    dfa.start = 0
    todo = deque([first])
    while todo:
        active = todo.popleft()
        source = number[active]
        if active & nfa.finals:
            dfa.finals.add(source)
        for char in alphabet(nfa):
            following = step(nfa, active, char)
            if following not in number:
                number[following] = dfa.new_state()
                subsets.append(following)
                todo.append(following)
            dfa.add_edge(source, char, number[following])
    return dfa, subsets


def minimize_dfa(dfa):
    letters = alphabet(dfa)
    transition = {(s, a): t for s, a, t in dfa.edges}
    groups = [set(dfa.finals), set(dfa.states) - dfa.finals]
    groups = [group for group in groups if group]
    while True:
        group_of = {q: i for i, group in enumerate(groups) for q in group}
        new_groups = []
        for group in groups:
            buckets = {}
            for q in sorted(group):
                behavior = tuple(group_of[transition[q, a]] for a in letters)
                buckets.setdefault(behavior, set()).add(q)
            new_groups.extend(buckets.values())
        if len(new_groups) == len(groups):
            break
        groups = new_groups

    groups.sort(key=lambda group: (dfa.start not in group, min(group)))
    group_of = {q: i for i, group in enumerate(groups) for q in group}
    result = NFA()
    for group in groups:
        result.new_state()
    result.start = group_of[dfa.start]
    result.finals = {group_of[q] for q in dfa.finals}
    for i, group in enumerate(groups):
        representative = min(group)
        for char in letters:
            result.add_edge(i, char, group_of[transition[representative, char]])
    return result


def equivalent(left, right):
    first = (epsilon_closure(left, {left.start}),
             epsilon_closure(right, {right.start}))
    todo = deque([(first, "")])
    seen = {first}
    letters = sorted(set(alphabet(left)) | set(alphabet(right)))
    while todo:
        (a, b), word = todo.popleft()
        if bool(a & left.finals) != bool(b & right.finals):
            return False, word
        for char in letters:
            pair = (step(left, a, char), step(right, b, char))
            if pair not in seen:
                seen.add(pair)
                todo.append((pair, word + char))
    return True, None


def high_degree_example(branches=4):
    nfa = NFA()
    nfa.start = nfa.new_state()
    middle = nfa.new_state()
    end = nfa.new_state()
    nfa.finals = {end}
    for i in range(branches):
        before = nfa.new_state()
        after = nfa.new_state()
        nfa.add_edge(nfa.start, EPSILON, before)
        nfa.add_edge(before, "a", middle)
        nfa.add_edge(middle, "b", after)
        nfa.add_edge(after, EPSILON, end)
    return nfa
