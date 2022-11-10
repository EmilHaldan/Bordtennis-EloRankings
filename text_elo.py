def expected(A, B):
    """
    Calculate expected score of A in a match against B

    :param A: Elo rating for player A
    :param B: Elo rating for player B
    """
    return 1 / (1 + 10 ** ((B - A) / 400))


def calc_elo_score(exp, score, k=32):
# def adjust_elo_rating(old, exp, score, k=32):
    """
    Calculate the new Elo rating for a player

    :param exp: The expected score for this match
    :param score: The actual score for this match
    :param k: The k-factor for Elo (default: 32)
    """
    return k * (score - exp)


player_a_elo = 1600
player_b_elo = 1400
exp_a = expected(player_a_elo, player_b_elo)
exp_b = expected(player_b_elo, player_a_elo)

print("expected(A, B):", exp_a)
print("expected(B, A):", exp_b)
print("")
print("calc_elo_score(exp, score=1, k=32):", calc_elo_score(exp_a, 1))
print("calc_elo_score(exp, score=0, k=32):", calc_elo_score(exp_a, 0))
print("calc_elo_score(exp, score=1, k=32):", calc_elo_score(exp_b, 1))
print("calc_elo_score(exp, score=0, k=32):", calc_elo_score(exp_b, 0))
print("")
print("calc_elo_score(exp_a, score=0.75*2, k=32):", calc_elo_score(exp_a, exp_a*2))
print("calc_elo_score(exp_a, score=0.75*0, k=32):", calc_elo_score(exp_a, exp_a*0))
print("calc_elo_score(exp_b, score=0.75*2, k=32):", calc_elo_score(exp_b, 0.75*2))
print("calc_elo_score(exp_b, score=0.75*0, k=32):", calc_elo_score(exp_b, 0.75*0))

