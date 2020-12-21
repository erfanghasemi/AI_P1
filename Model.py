from collections import deque
from sys import maxsize
from copy import deepcopy


class Card:
    def __init__(self, color, number):
        self.color = color
        self.number = number

    def get_color(self):
        return self.color

    def get_number(self):
        return self.number

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.number == other.number and self.color == other.color

    def __str__(self):
        return str(self.number) + str(self.color)

    def __hash__(self):
        return hash((self.color, self.number))


class Batch:
    def __init__(self):
        self.cards_count = 0
        self.cards = deque()
        self.sorted_until = 0
        self.batch_color = None

    def is_empty(self):
        return self.cards_count == 0

    def update_sorted_index(self, operation, card: Card):
        if operation == "PUSH":
            if self.is_empty():
                self.sorted_until += 1
                self.cards_count += 1
                self.batch_color = card.color
            else:
                self.cards_count += 1
                color_match = (card.color == self.cards.__getitem__(self.cards_count-2).color) and (card.color == self.batch_color)
                number_match = card.number < self.cards.__getitem__(self.cards_count-2).number

                if number_match and color_match:
                    self.sorted_until += 1

        elif operation == "POP":
            if self.cards_count == 1:
                self.sorted_until -= 1
                self.cards_count -= 1
                self.batch_color = None
            else:
                self.cards_count -= 1
                color_match = card.color == self.cards.__getitem__(self.cards_count-1).color and (card.color == self.batch_color)
                number_match = card.number < self.cards.__getitem__(self.cards_count-1).number

                if number_match and color_match:
                    self.sorted_until -= 1

    def insert_card(self, card: Card):
        self.cards.append(card)
        self.update_sorted_index("PUSH", card)

    def pop_card(self):
        if self.is_empty():
            print("Batch is empty!:((")
            return -1
        card = self.cards.pop()
        self.update_sorted_index("POP", card)
        return card

    def is_sorted(self):
        return self.cards_count == self.sorted_until

    def last_card_number(self):
        if self.is_empty():
            return maxsize
        return self.cards.__getitem__(self.cards_count-1).number

    def __eq__(self, other):
        try:
            for i in range(self.cards.__len__()):
                if self.cards.__getitem__(i) == other.cards.__getitem__(i):
                    continue
                else:
                    return False
            return True
        except IndexError:
            return False

    def __str__(self):
        if self.cards.__len__() == 0:
            return "#"

        representation = ""
        for card in self.cards:
            representation += card.__str__() + " "
        return representation

    def __hash__(self):
        hash_value = 0
        for index in range(self.cards_count):
            hash_value += hash(self.cards[index]) * index
        return hash_value


class State:
    def __init__(self, batches_number: int, cost: int, batches: list, parent, f_value: int, transition: tuple):
        self.batches_number = batches_number
        self.cost = cost
        self.batches = batches
        self.parent = parent
        self.transition = transition
        self.f_value = f_value

    def goal_test(self):
        for batch in self.batches:
            if batch.is_sorted():
                continue
            else:
                return False
        return True

    def find_batch(self, target_batch: Batch):
        for index in range(self.batches_number):
            if target_batch == self.batches[index] and target_batch.cards_count == self.batches[index].cards_count:
                return index
        return -1

    def __str__(self):
        representation = ""
        for batch in self.batches:
            representation += batch.__str__() + "\n"
        return representation

    def next_states(self):
        next_states = []
        for batch_beginning in self.batches:
            if batch_beginning.is_empty():
                continue
            for batch_destination in self.batches:
                if int(batch_beginning.last_card_number()) < int(batch_destination.last_card_number()):
                    temp_batches = deepcopy(self.batches)

                    index_beginning = self.find_batch(batch_beginning)
                    index_destination = self.find_batch(batch_destination)

                    card = temp_batches[index_beginning].pop_card()
                    temp_batches[index_destination].insert_card(card)

                    new_state = State(self.batches_number, self.cost+1, temp_batches, self, self.f_value, (index_beginning+1, index_destination+1))
                    next_states.append(new_state)
        return next_states

    def __eq__(self, other):
        for index in range(self.batches_number):
            if self.batches[index] != other.batches[index]:
                return False
        return True

    def __hash__(self):
        hash_value = 0
        for batch in self.batches:
            hash_value += hash(batch)
        return hash_value


class IO:
    def __init__(self, goal_test: State = None, expanded_nodes: int = None, created_nodes: int = None):
        self.state = None
        self.batches = []
        self.batch = None
        self.card = None
        self.color_card = None
        self.number_card = None
        self.n = None
        self.m = None
        self.k = None
        self.expanded_nodes = expanded_nodes
        self.created_nodes = created_nodes
        self.goal_test = goal_test

    def read(self):
        self.k, self.m, self.n = map(int, input().split())
        for batch in range(self.k):
            line = input().split()
            self.batch = Batch()
            if line[0] == "#":
                self.batches.append(self.batch)
                continue

            for item in line:

                self.number_card = item[0]
                self.color_card = item[1]
                self.card = Card(self.color_card, self.number_card)
                self.batch.insert_card(self.card)

            self.batches.append(self.batch)
        self.state = State(self.k, 0, self.batches, None, 0, None)
        return self.state

    def write(self):
        print("\nAnswer : ")
        print(self.goal_test)
        print("\n-------------------------------------")
        print("\t\t\tInformation\n")
        print("Created nodes = "+str(self.created_nodes))
        print("Expanded nodes = " + str(self.expanded_nodes))
        print("Depth nodes = " + str(self.goal_test.cost))
        print("\n-------------------------------------")
        print("\t\t\tTransition\n")

        current_state = self.goal_test
        transition_stack = deque()
        for i in range(self.goal_test.cost):
            transition = "Top card in batch " + str(current_state.transition[0]) + " moved to batch " + str(current_state.transition[1])
            transition_stack.append(transition)
            current_state = current_state.parent

        for j in range(self.goal_test.cost):
            print(transition_stack.pop())

        print("-------------------------------------")