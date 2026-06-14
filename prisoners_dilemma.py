"""
Iterated Prisoner's Dilemma Simulation
Translated from NetLogo (Uri Wilensky, 2002) to Python.

Strategies:
  - random:      Cooperate or defect with 50/50 chance each round.
  - cooperate:   Always cooperate.
  - defect:      Always defect.
  - tit-for-tat: Start cooperative; mirror whatever the partner did last time.
  - unforgiving: Cooperate until partner defects once; defect forever after.
  - unknown:     Defaults to tit-for-tat (customise as you like!).

Payoff matrix (row = self, col = partner):
                Partner cooperates  Partner defects
  Self cooperates        3                 0
  Self defects           5                 1
"""

import random
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict


# ---------------------------------------------------------------------------
# Payoff constants
# ---------------------------------------------------------------------------
PAYOFF = {
    (False, False): 3,   # both cooperate
    (True,  False): 5,   # self defects, partner cooperates
    (False, True):  0,   # self cooperates, partner defects
    (True,  True):  1,   # both defect
}


# ---------------------------------------------------------------------------
# Turtle (agent)
# ---------------------------------------------------------------------------
@dataclass
class Turtle:
    who: int                            # unique ID
    strategy: str
    score: int = 0
    partnered: bool = False
    partner: Optional["Turtle"] = None
    defect_now: bool = False
    partner_defected: bool = False
    # history[other_who] = did they defect last time? (False = no / cooperated)
    partner_history: dict = field(default_factory=lambda: defaultdict(bool))


# ---------------------------------------------------------------------------
# Strategy: select action
# ---------------------------------------------------------------------------
def select_action(t: Turtle) -> None:
    s = t.strategy
    if s == "random":
        t.defect_now = random.random() < 0.5
    elif s == "cooperate":
        t.defect_now = False
    elif s == "defect":
        t.defect_now = True
    elif s in ("tit-for-tat", "unknown"):
        t.partner_defected = t.partner_history[t.partner.who]
        t.defect_now = t.partner_defected
    elif s == "unforgiving":
        t.partner_defected = t.partner_history[t.partner.who]
        t.defect_now = t.partner_defected


# ---------------------------------------------------------------------------
# History update after each round
# ---------------------------------------------------------------------------
def update_history(t: Turtle) -> None:
    s = t.strategy
    if s == "random":
        pass  # no history used
    elif s == "cooperate":
        pass
    elif s == "defect":
        pass
    elif s in ("tit-for-tat", "unknown"):
        t.partner_history[t.partner.who] = t.partner_defected
    elif s == "unforgiving":
        # only update if partner defected (permanent grudge)
        if t.partner_defected:
            t.partner_history[t.partner.who] = True


# ---------------------------------------------------------------------------
# Payoff
# ---------------------------------------------------------------------------
def get_payoff(t: Turtle) -> None:
    t.partner_defected = t.partner.defect_now
    t.score += PAYOFF[(t.defect_now, t.partner_defected)]


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
class PrisonersDilemma:
    def __init__(
        self,
        n_random: int = 0,
        n_cooperate: int = 0,
        n_defect: int = 0,
        n_tit_for_tat: int = 0,
        n_unforgiving: int = 0,
        n_unknown: int = 0,
    ):
        self.strategy_counts = {
            "random":      n_random,
            "cooperate":   n_cooperate,
            "defect":      n_defect,
            "tit-for-tat": n_tit_for_tat,
            "unforgiving": n_unforgiving,
            "unknown":     n_unknown,
        }
        self.turtles: list[Turtle] = []
        self.tick = 0
        self._setup()

    # -----------------------------------------------------------------------
    def _setup(self) -> None:
        who = 0
        for strategy, count in self.strategy_counts.items():
            for _ in range(count):
                self.turtles.append(Turtle(who=who, strategy=strategy))
                who += 1
        self.tick = 0

    # -----------------------------------------------------------------------
    def _partner_up(self) -> list[tuple[Turtle, Turtle]]:
        """Randomly pair unpaired turtles (like the NetLogo spatial partnering)."""
        unpartnered = [t for t in self.turtles]
        random.shuffle(unpartnered)
        pairs = []
        while len(unpartnered) >= 2:
            a = unpartnered.pop()
            b = unpartnered.pop()
            a.partnered = True
            b.partnered = True
            a.partner = b
            b.partner = a
            pairs.append((a, b))
        return pairs

    # -----------------------------------------------------------------------
    def go(self) -> dict:
        """Run one tick (round) of the simulation. Returns per-strategy scores."""
        # Release previous partnerships
        for t in self.turtles:
            t.partnered = False
            t.partner = None

        # Form new pairs
        pairs = self._partner_up()

        # All partnered turtles select an action
        partnered = [t for t in self.turtles if t.partnered]
        for t in partnered:
            select_action(t)

        # Play the round: get payoffs then update histories
        for t in partnered:
            get_payoff(t)
        for t in partnered:
            update_history(t)

        self.tick += 1
        return self.scores()

    # -----------------------------------------------------------------------
    def scores(self) -> dict:
        """Return total score per strategy."""
        result = {}
        for strategy in self.strategy_counts:
            agents = [t for t in self.turtles if t.strategy == strategy]
            result[strategy] = sum(t.score for t in agents)
        return result

    # -----------------------------------------------------------------------
    def avg_scores(self) -> dict:
        """Return average score per turtle for each strategy."""
        result = {}
        for strategy, count in self.strategy_counts.items():
            if count == 0:
                result[strategy] = 0.0
            else:
                agents = [t for t in self.turtles if t.strategy == strategy]
                result[strategy] = sum(t.score for t in agents) / count
        return result

    # -----------------------------------------------------------------------
    def run(self, ticks: int = 100, verbose: bool = True) -> dict:
        """Run the simulation for a given number of ticks."""
        for i in range(ticks):
            scores = self.go()
            if verbose:
                avg = self.avg_scores()
                active = {k: f"{v:.1f}" for k, v in avg.items() if self.strategy_counts[k] > 0}
                print(f"Tick {self.tick:>4}: avg scores {active}")
        return self.avg_scores()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Iterated Prisoner's Dilemma ===\n")

    sim = PrisonersDilemma(
        n_random=5,
        n_cooperate=5,
        n_defect=5,
        n_tit_for_tat=5,
        n_unforgiving=5,
    )

    final_avg = sim.run(ticks=50, verbose=True)

    print("\n=== Final Average Scores (per turtle) ===")
    for strategy, avg in sorted(final_avg.items(), key=lambda x: -x[1]):
        count = sim.strategy_counts[strategy]
        if count > 0:
            print(f"  {strategy:<14}: {avg:>7.1f}  (n={count})")
