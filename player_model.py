from dataclasses import dataclass

@dataclass
class Player:
    name: str
    height: float
    dribbling: float
    shooting: float
    passing: float
    defense: float
    athleticism: float
    minutes_last_game: int = 0

    # runtime tracking (needed by engine)
    minutes_played: int = 0
    consecutive_rotations: int = 0

    @property
    def effective_skill(self) -> float:
        return (self.dribbling + self.shooting + self.passing + self.defense + self.athleticism) / 5.0