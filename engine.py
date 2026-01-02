import itertools
from typing import List
from player_model import Player

# def generate_basketball_rotations(
#     players: List[Player],
#     on_court: int = 5,
#     rotation_minutes: int = 5,
#     total_game_minutes: int = 32,
#     skill_weight: float = 0.7,
#     height_weight: float = 0.4,
#     minutes_weight: float = 2.5,
#     last_game_weight: float = 3.5,
# ):
#     rotations = []
#     total_rotations = total_game_minutes // rotation_minutes

#     avg_skill = sum(p.effective_skill for p in players) / len(players)
#     avg_height = sum(p.height for p in players) / len(players)

#     target_skill = avg_skill * on_court
#     target_height = avg_height * on_court

#     for _ in range(total_rotations):

#         best_group = None
#         best_score = float("inf")

#         # Players who played less last game + less this game get priority
#         candidate_pool = sorted(
#             players,
#             key=lambda p: (p.minutes_played, p.minutes_last_game)
#         )[: min(len(players), 10)]
#         avg_last_game = sum(p.minutes_last_game for p in players) / len(players)

#         for group in itertools.combinations(candidate_pool, on_court):

#             # 🔒 HARD RULE: no 3 straight rotations
#             if any(p.consecutive_rotations >= 2 for p in group):
#                 continue

#             skill_sum = sum(p.effective_skill for p in group)
#             height_sum = sum(p.height for p in group)
#             minutes_sum = sum(p.minutes_played for p in group)

#             skill_diff = abs(skill_sum - target_skill) / target_skill
#             height_diff = abs(height_sum - target_height) / target_height
#             minutes_penalty = minutes_sum / (on_court * total_game_minutes)

#             max_last_game = max(p.minutes_last_game for p in players) or 1

#             last_game_bonus = sum(
#                 (max_last_game - p.minutes_last_game) / max_last_game
#                 for p in group
#             ) / on_court

#             score = (
#                 skill_weight * skill_diff
#                 + height_weight * height_diff
#                 + minutes_weight * minutes_penalty
#                 - last_game_weight * last_game_bonus
#             )

#             if score < best_score:
#                 best_score = score
#                 best_group = group

#         # Safety fallback
#         if best_group is None:
#             best_group = tuple(candidate_pool[:on_court])

#         # -----------------------------
#         # Update state
#         # -----------------------------
#         for p in players:
#             if p in best_group:
#                 p.minutes_played += rotation_minutes
#                 p.consecutive_rotations += 1
#             else:
#                 p.consecutive_rotations = 0

#         rotations.append([p.name for p in best_group])

#     return rotations


def generate_basketball_rotations(
    players: List[Player],
    on_court: int = 5,
    rotation_minutes: int = 5,
    total_game_minutes: int = 32,
    min_minutes_per_player: int = 13,   # 👈 NEW
    skill_weight: float = 0.7,
    height_weight: float = 0.4,
    minutes_weight: float = 2.5,
    last_game_weight: float = 3.5,
):
    rotations = []
    total_rotations = total_game_minutes // rotation_minutes

    avg_skill = sum(p.effective_skill for p in players) / len(players)
    avg_height = sum(p.height for p in players) / len(players)

    target_skill = avg_skill * on_court
    target_height = avg_height * on_court

    for rotation_idx in range(total_rotations):

        best_group = None
        best_score = float("inf")

        # -----------------------------
        # HARD PRIORITY: players below min minutes
        # -----------------------------
        players_below_min = [
            p for p in players
            if p.minutes_played < min_minutes_per_player
        ]

        # Remaining rotations after this one
        remaining_rotations = total_rotations - rotation_idx - 1
        max_future_minutes = remaining_rotations * rotation_minutes

        # Players who MUST play now or they can’t reach min
        must_play = [
            p for p in players_below_min
            if p.minutes_played + max_future_minutes < min_minutes_per_player
        ]

        # Candidate pool (favor underplayed players)
        candidate_pool = sorted(
            players,
            key=lambda p: (p.minutes_played, p.minutes_last_game)
        )[: min(len(players), 10)]

        for group in itertools.combinations(candidate_pool, on_court):

            # 🔒 HARD RULES
            if any(p.consecutive_rotations >= 2 for p in group):
                continue

            # 🔒 MUST-PLAY enforcement
            if any(p not in group for p in must_play):
                continue

            skill_sum = sum(p.effective_skill for p in group)
            height_sum = sum(p.height for p in group)
            minutes_sum = sum(p.minutes_played for p in group)

            skill_diff = abs(skill_sum - target_skill) / target_skill
            height_diff = abs(height_sum - target_height) / target_height
            minutes_penalty = minutes_sum / (on_court * total_game_minutes)

            max_last_game = max(p.minutes_last_game for p in players) or 1
            last_game_bonus = sum(
                (max_last_game - p.minutes_last_game) / max_last_game
                for p in group
            ) / on_court

            # 🎯 BONUS for playing under-min players
            min_minutes_bonus = sum(
                max(0, min_minutes_per_player - p.minutes_played)
                for p in group
            ) / (min_minutes_per_player * on_court)

            score = (
                skill_weight * skill_diff
                + height_weight * height_diff
                + minutes_weight * minutes_penalty
                - last_game_weight * last_game_bonus
                - 2.0 * min_minutes_bonus   # 👈 strong incentive
            )

            if score < best_score:
                best_score = score
                best_group = group

        # Safety fallback
        if best_group is None:
            best_group = tuple(candidate_pool[:on_court])

        # -----------------------------
        # Update state
        # -----------------------------
        for p in players:
            if p in best_group:
                p.minutes_played += rotation_minutes
                p.consecutive_rotations += 1
            else:
                p.consecutive_rotations = 0

        rotations.append([p.name for p in best_group])

    return rotations