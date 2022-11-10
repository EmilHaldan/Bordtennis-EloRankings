import os
import pandas as pd
from _datetime import datetime
import time
import plotly.express as px
from tabulate import tabulate
tabulate.PRESERVE_WHITESPACE = True
from collections import defaultdict
import random
import networkx as nx
from pyvis.network import Network
import webbrowser


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



def create_players_dict(players_list):
    players_dict = {x:{"matches_played": {}} for x in players_list}
    for main_player in players_list:
        for player in players_list:
            if main_player != player:
                players_dict[main_player]["matches_played"][player] = 0

    return players_dict


def calc_possible_new_matches(players_dict, main_player, local_matches_df):

    for idx,row in enumerate(local_matches_df.copy().iterrows()):
        row = row[1]
        game_id = idx+1
        player_A = row["Player A"]
        player_B = row["Player B"]

        if main_player in [player_A, player_B]:
            if main_player == player_A:
                players_dict[player_A]["matches_played"][player_B] += 1
            else: 
                players_dict[player_B]["matches_played"][player_A] += 1
            # try:
                
            # except KeyError:
            #     print("main_player: ", main_player)
            #     print("player_A: ", player_A)
            #     print("player_B: ", player_B)
            #     print("KeyError")
            #     print("")
            #     print("players_dict[main_player]: ", players_dict[main_player])
            #     print("")
            #     print("players_dict[player_B]: ", players_dict[player_B])
            #     exit()
            

    players_dict[main_player]["possible_matches"] = []
    players_dict[main_player]["same_match_threshold"] = 0
    players_dict[main_player]["same_match_threshold"] = 2 + sum(players_dict[main_player]["matches_played"].values()) / (6)
    for possible_opponent in players_dict[main_player]["matches_played"]:
        if players_dict[main_player]["matches_played"][possible_opponent] < (players_dict[main_player]["same_match_threshold"]):
            players_dict[main_player]["possible_matches"].append(possible_opponent)

    return players_dict

        

def calc_elo_for_match(elo_rating_df, player_A, player_B, score_A, score_B, game_id, game_time_stamp, K):
    """
    Calculate the Elo rating for a match between two players
    :param player_A: str name of player A
    :param player_B: str name of player B
    :param score_A: int score for player A
    :param score_B: int score for player B
    :return:
    """

    # set player name as index
    # print("")
    # print("elo_rating_df:" ,elo_rating_df)
    # print("")
    # elo_rating_df.set_index("Player", inplace=True)

    elo_A = elo_rating_df.loc[player_A, "Elo Rating"]
    elo_B = elo_rating_df.loc[player_B, "Elo Rating"]

    A_expected_score = expected(elo_A, elo_B)
    B_expected_score = expected(elo_B, elo_A)

    # get current month as int
    current_month = datetime.now().month
    current_year = datetime.now().year

    score_dict = {"2-0": (2, 0),
                 "2-1": (1.75, 0.25),
                 "0-2": (0, 2),
                 "1-2": (0.25, 1.75)}

    # score_dict = {"2-0": (2, 0),
    #               "2-1": (2, 0),
    #               "0-2": (0, 2),
    #               "1-2": (0, 2)}
    print(f"                GAME ID: {game_id}  Datetime: {game_time_stamp}   ")
    print(f"   Player A: {player_A:<14}   score: {score_A}-{score_B}         Player B: {player_B:<14}")
    # Converts score_A and score_B to values for adjust_elo_rating function
    if score_A == 2:
        if score_B == 1:
            score_A = score_dict["2-1"][0]*A_expected_score
            score_B = score_dict["2-1"][1]*B_expected_score
            # score_A = -score_B
        else:
            score_A = score_dict["2-0"][0]*A_expected_score
            score_B = score_dict["2-0"][1]*B_expected_score
            # score_A = -score_B

    elif score_B == 2:
        if score_A == 1:
            score_A = score_dict["1-2"][0]*A_expected_score
            score_B = score_dict["1-2"][1]*B_expected_score
        else:
            score_A = score_dict["0-2"][0]*A_expected_score
            score_B = score_dict["0-2"][1]*B_expected_score
    else:
        pass

    # new_elo_player_A = int(adjust_elo_rating(elo_A, A_expected_score, score_A, k=K))
    # new_elo_player_B = int(adjust_elo_rating(elo_B, B_expected_score, score_B, k=K))

    elo_diff_A = calc_elo_score(A_expected_score, score_A, k=K)
    elo_diff_B = calc_elo_score(B_expected_score, score_B, k=K)

    if score_A >= score_B:
        if elo_A > elo_B:
            elo_diff = min(abs(elo_diff_A), abs(elo_diff_B))
        else:
            elo_diff = max(abs(elo_diff_A), abs(elo_diff_B))
        elo_diff = int(elo_diff)
        new_elo_player_A = elo_A + elo_diff + 5 
        new_elo_player_B = elo_B - elo_diff
    else:
        if elo_A < elo_B:
            elo_diff = min(abs(elo_diff_A), abs(elo_diff_B))
        else:
            elo_diff = max(abs(elo_diff_A), abs(elo_diff_B))
        elo_diff = int(elo_diff)
        new_elo_player_A = elo_A - elo_diff
        new_elo_player_B = elo_B + elo_diff + 5

    print(f"   {player_A:<12} Old Elo: ", elo_A, "   New Elo: ", new_elo_player_A , "   Difference: ", new_elo_player_A - elo_A )
    print(f"   {player_B:<12} Old Elo: ", elo_B, "   New Elo: ", new_elo_player_B , "   Difference: ", new_elo_player_B - elo_B)

    return new_elo_player_A, new_elo_player_B


def read_players(filename = "players.txt"):
    with open(filename) as f:
        players = f.read().splitlines()
    if "" in players:
        players.remove("")
    if " " in players:
        players.remove(" ")
    return players


def create_random_matches(matches = 20):
    # Create a dataframe with 4 columns, player_A, player_B, score_A, score_B
    players = read_players(filename = "players.txt")
    df = pd.DataFrame(columns=["Player A", "Player B", "Score A", "Score B"])

    for i in range(matches):
        player_A = random.choice(players)
        player_B = random.choice(players)
        while player_A == player_B:
            player_B = random.choice(players)
        score_A = random.choice([0, 1, 2])
        if score_A != 2:
            score_B = 2
        else:
            score_B = random.choice([0, 1, 2])
        # Append the row to the dataframe
        df = df.append({"Player A": player_A, "Player B": player_B, "Score A": score_A, "Score B": score_B}, ignore_index=True)

        df.to_excel("Matches_test.xlsx", index=False)


def ensure_all_players_in_ratings_df(players_list, base_elo):
    """
    Re-writes the entire dataframe each time cause thats how its built
    If a player is not in the elo_rating_df, add them to the elo_rating_df with a base_elo rating

    :param players_list: list of players in the tournament
    :param base_elo: the starting Elo rating for all players
    """
    elo_rating_df = pd.DataFrame(columns = ["Elo Rating"], index = players_list)

    for player in players_list:
        if (player not in elo_rating_df.index) or str(elo_rating_df.loc[player, "Elo Rating"]) == "nan":
            # add player to elo_rating_df with index = player
            elo_rating_df.loc[player, "Elo Rating"] = base_elo

    if len(elo_rating_df) > len(players_list):
        # remove extra players from elo_rating_df if not in player_list
        for player in elo_rating_df.index:
            if player not in players_list:
                elo_rating_df = elo_rating_df.drop(player)
    else:
        pass
    # print("base_elo: ", base_elo)
    # print("elo_rating_df: ", elo_rating_df)

    elo_rating_df.to_excel("Players_rating.xlsx")

    # if file exists
    # if not os.path.isfile("Players_rating_history.xlsx"):
    # create new file for Players_rating_history
    elo_rating_history_df = pd.DataFrame(columns = ['Name', 'Elo Rating', 'timestamp', 'game id'])
    # iterate through players_list and add them to the dataframe with base_elo rating
    for player in players_list:
        elo_rating_history_df = elo_rating_history_df.append({"Name": player, "Elo Rating": base_elo, "timestamp": "placeholder", "game id": 0}, ignore_index=True)

    elo_rating_history_df.to_excel("Players_rating_history.xlsx", index=False)


def update_player_ratings(elo_rating_df, elo_rating_history_df, player_A, new_elo_player_A, player_B, new_elo_player_B, players_list, game_time_stamp):
    # elo_rating_df = pd.read_excel("Players_rating.xlsx", index_col=0)

    # update elo_rating_df for player_A and player_B
    elo_rating_df.loc[player_A, "Elo Rating"] = new_elo_player_A
    elo_rating_df.loc[player_B, "Elo Rating"] = new_elo_player_B

    # write elo_rating_df to excel file
    # elo_rating_df.to_excel("Players_rating.xlsx")#, index=False)

    # Adding history
    game_id = int((len(elo_rating_history_df) /2) - (len(players_list)/2) + 1.5)

    # datetime needs fixing for future use.
    str_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    str_timestamp = game_time_stamp

    elo_rating_history_df = elo_rating_history_df.append({"Name": player_A,
                                                          "Elo Rating": new_elo_player_A,
                                                          "timestamp": str_timestamp,
                                                          "game id" : game_id}, ignore_index=True)
    elo_rating_history_df = elo_rating_history_df.append({"Name": player_B,
                                                          "Elo Rating": new_elo_player_B,
                                                          "timestamp": str_timestamp,
                                                          "game id" : game_id}, ignore_index=True)

    # count empty cells at timestamp 
    empty_cells = elo_rating_history_df.loc[elo_rating_history_df["timestamp"] == "placeholder", "timestamp"].count()
    first_match_timestamp = elo_rating_history_df.loc[empty_cells,"timestamp"]
    elo_rating_history_df.loc[:empty_cells, "timestamp"] = first_match_timestamp[:5] + " 00:00"

    print("")
    return elo_rating_df,elo_rating_history_df


def calculate_elo_for_all(K=32, base_elo = 1500, test = True):
    # read players from file
    players_list = read_players()
    ensure_all_players_in_ratings_df(players_list, base_elo)

    # read matches from file (add condition for checking date and starting new season match file if needed  )
    if test:
        matches_df = pd.read_excel("Matches_test.xlsx")
    else:
        matches_df = pd.read_excel("Matches.xlsx")

    elo_rating_df = pd.read_excel("Players_rating.xlsx", index_col=0)
    elo_rating_history_df = pd.read_excel("Players_rating_history.xlsx")

    if len(matches_df) == 0:
        print("No matches found")
        return
    else:
        for idx,row in enumerate(matches_df.copy().iterrows()):
            row = row[1]
            game_id = idx+1
            player_A = row["Player A"]
            player_B = row["Player B"]
            score_A  = row["Score A"]
            score_B  = row["Score B"]
            game_time_stamp = row['Date'] + " " + row["Time"] 

            # Checking for validity
            players_dict = create_players_dict(players_list)
            players_dict = calc_possible_new_matches(players_dict, player_A, matches_df.loc[:idx])
            # print(f"idx: {idx}  players_dict: ", players_dict)
            
            


            if player_B in players_dict[player_A]['possible_matches']:
                new_elo_player_A, new_elo_player_B = calc_elo_for_match(elo_rating_df, player_A, player_B, score_A, score_B, game_id, game_time_stamp, K)
            
            else: 
                new_elo_player_A, new_elo_player_B = elo_rating_df.loc[player_A, "Elo Rating"], elo_rating_df.loc[player_B, "Elo Rating"]
                print(f"                GAME ID: {game_id}  Datetime: {game_time_stamp}   ")
                print(f"   Player A: {player_A:<14}   score: {score_A}-{score_B}         Player B: {player_B:<14}")
                print(f"   Match not included due to Anti-Farming" )
                

            print(f"   idx: {idx}  games with players A & B: ", players_dict[player_A]['matches_played'][player_B])
            print("   same_match_threshold: ", players_dict[player_A]['same_match_threshold'])
            print("")

            # insert players and matches into Players_rating.xlsx
            elo_rating_df, elo_rating_history_df = update_player_ratings(elo_rating_df, elo_rating_history_df, player_A, new_elo_player_A, player_B, new_elo_player_B, players_list, game_time_stamp)
        
    time.sleep(0.2)
    elo_rating_df.to_excel("Players_rating.xlsx")#, index=False)
    elo_rating_history_df.to_excel("Players_rating_history.xlsx", index=False)
    

def visualize_elo_history(open_browser = True):
    elo_rating_history_df = pd.read_excel("Players_rating_history.xlsx")
    # convert timestamp to datetime
    elo_rating_history_df["timestamp"] = pd.to_datetime(elo_rating_history_df["timestamp"], format="%d-%m %H:%M")

    # fig = px.line(elo_rating_history_df, x="timestamp", y="Elo Rating", color='Name', title="Elo Rankings over time",
    #               template="plotly_dark")
    # fig.show()

    fig1 = px.line(elo_rating_history_df, x="game id", y="Elo Rating", color='Name', title="Elo Rankings over time",
                  template="plotly_dark")
    # set grid for every 1 game
    fig1.update_xaxes(dtick=1)
    # add dots for every game
    fig1.update_traces(mode='markers+lines')
    if open_browser:
        # change figure size to fit browser
        fig1.show()
    else: 
        # Save html 
        fig1.update_layout(width=1400, height=750)
        # change 
        fig1.write_html("Elo_Rankings.html", auto_open=False)
        return fig1


def visualize_network(open_browser=True):
    players_list = read_players()
    matches_df = pd.read_excel("Matches.xlsx")
    elo_rating_df = pd.read_excel("Players_rating.xlsx", index_col=0)
    print("")

    players_dict = create_players_dict(players_list)
    for main_player in players_list:
        players_dict = calc_possible_new_matches(players_dict,main_player, matches_df)

    # Create a complete graph where each player is a node.
    # The weight of the edge should be the amount of games played between each player 

    G = nx.Graph()    

    for main_player in players_list:
        # if main_player == "Haldan":
        #     print("players_dict: ", players_dict)
        for player_2 in players_list:
            if main_player != player_2:
                try:
                    weight = players_dict[main_player]['matches_played'][player_2]
                    main_player_display_name = main_player + " (" + str(elo_rating_df.loc[main_player, "Elo Rating"]) + ")"
                    player_2_display_name = player_2 + " (" + str(elo_rating_df.loc[player_2, "Elo Rating"]) + ")"

                    if weight > 0:
                        if weight > max( players_dict[main_player]["same_match_threshold"], players_dict[player_2]["same_match_threshold"]):
                            G.add_edge(main_player_display_name, player_2_display_name, color='red', weight=weight)
                            print("   Player: ", main_player, "  Player 2: ", player_2, "  has", weight, "matches together")
                            print("   Local threshold for players: ", max( players_dict[main_player]["same_match_threshold"], players_dict[player_2]["same_match_threshold"]))
                            print("")
                        elif weight > max( players_dict[main_player]["same_match_threshold"], players_dict[player_2]["same_match_threshold"])*0.7:
                            G.add_edge(main_player_display_name, player_2_display_name, color='orange', weight=weight)
                        else: 
                            G.add_edge(main_player_display_name, player_2_display_name, color='green', weight=weight)
                    else:
                        pass
                        # if sum(players_dict[main_player]["matches_played"].values()):
                        #     if sum(players_dict[player_2]["matches_played"].values()):
                        #         G.add_edge(main_player, player_2, weight=0.1)

                except KeyError as e:
                    print("e: ", e)
                    print("main_player: ", main_player, "  player_2: ", player_2)
                    print("players_dict[main_player]['matches_played']: ", players_dict[main_player]['matches_played'])
                    print("")
                    print("players_dict[player_2]['matches_played']: ", players_dict[player_2]['matches_played'])
                    print("")
                    print(players_dict)
                    exit()

    #display(G) with networkx
    # nx.draw(G, with_labels=True, font_weight='bold')

    # Visualize the graph with the plotly libraray 
    if open_browser:
        net = Network(height="1400px", width="100%", bgcolor="#222222", font_color="white")
    else:
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")


    # set the physics layout of the network
    const_options = """{
    "physics": {
        "repulsion": {
        "gravitationalConstant": -30000,
        "springLength": 500,
        "springConstant": 0.045,
        "damping": 0.21,
        "avoidOverlap": 1
        },
        "maxVelocity": 7,
        "minVelocity": 0.75}}
        """
    net.set_options(const_options)

    #play with the physics:
    # net.show_buttons(filter_=['physics'])

    file_name = "network_of_valid_players.html"
    net.from_nx(G)

    net.save_graph(file_name)
    time.sleep(0.1)
    if open_browser:
        webbrowser.open(file_name, new=2)

    # Create a confusion matrix of allowed matches to play between each person.


def print_leader_board(test):
    players_list = read_players()
    elo_rating_df = pd.read_excel("Players_rating.xlsx", index_col=0)
    elo_rating_df = elo_rating_df.sort_values(by="Elo Rating", ascending=False)
    print("\n"*4)
    print("#"*30)
    print("\n"*3)

    elo_rating_df.reset_index(inplace=True)
    elo_rating_df.reset_index(inplace=True)
    elo_rating_df.rename(columns={"level_0": "Ranking", "index": "Name"}, inplace=True)

    elo_rating_df['Win Rate'] = 0.5
    elo_rating_df['Wins'] = 0
    elo_rating_df['Losses'] = 0
    elo_rating_df['Matches Played'] = 0

    if test:
        matches_df = pd.read_excel("Matches_test.xlsx")
    else:
        matches_df = pd.read_excel("Matches.xlsx")

    matches_dict = defaultdict(int)
    matches_won_dict = defaultdict(int)
    matches_lost_dict = defaultdict(int)
    matches_annulled_dict = defaultdict(int)
    for idx,row in enumerate(matches_df.copy().iterrows()):
        row = row[1]
        player_A = row["Player A"]
        player_B = row["Player B"]

        matches_dict[player_A] += 1
        matches_dict[player_B] += 1

        players_dict = create_players_dict(players_list)
        players_dict = calc_possible_new_matches(players_dict,player_A, matches_df.loc[:idx])

        if player_B in players_dict[player_A]['possible_matches']:
            if row["Score A"] > row["Score B"]:
                matches_won_dict[player_A] += 1
                matches_lost_dict[player_B] += 1
            else:
                matches_won_dict[player_B] += 1
                matches_lost_dict[player_A] += 1
        else: 
            matches_annulled_dict[player_A] += 1
            matches_annulled_dict[player_B] += 1

    for idx,row in enumerate(elo_rating_df.copy().iterrows()):
        row = row[1]
        player_name = row["Name"]

        if player_name in matches_dict:
            elo_rating_df.loc[idx, "Win Rate"] = matches_won_dict[player_name] / matches_dict[player_name]
            elo_rating_df.loc[idx, "Wins"] = matches_won_dict[player_name]
            elo_rating_df.loc[idx, "Losses"] = matches_lost_dict[player_name]
            elo_rating_df.loc[idx, "Anulled"] = matches_annulled_dict[player_name]
            elo_rating_df.loc[idx, "Matches Played"] = matches_dict[player_name]
        else:
            elo_rating_df.drop(elo_rating_df[elo_rating_df["Name"] == player_name].index, inplace=True)

    # Formatting DF
    elo_rating_df.reset_index(inplace=True)
    elo_rating_df.reset_index(inplace=True)
    elo_rating_df.drop(["Ranking", "index"], axis=1, inplace=True)
    elo_rating_df.rename(columns={"level_0": "Ranking"}, inplace=True)

    # Metrics
    mean_elo_rating = int(elo_rating_df['Elo Rating'].mean())
    total_matches = elo_rating_df['Matches Played'].sum()//2

    streamlit_table = elo_rating_df.copy()

    #  Redundant String formatting
    elo_rating_df["Ranking"] = ["       "+str(i+1)+"       " for i in elo_rating_df["Ranking"]]
    elo_rating_df['Name']    = ["       "+str(i)+"       " for i in elo_rating_df["Name"]]
    elo_rating_df['Elo Rating'] = ["       "+str(i)+"       " for i in elo_rating_df["Elo Rating"]]
    print(tabulate(elo_rating_df, headers='keys', tablefmt='rst', showindex=False))
    print("\n")
    print(f"     Mean Elo Rating: {mean_elo_rating}    Total Matches: {total_matches}    Matches pr. Person {2*total_matches/len(elo_rating_df):.2f}")
    print("\n"*2)
    print("#"*30)

    return streamlit_table





if __name__ == '__main__':

    test = False

    # test = True
    # pseudo_matches = 100
    # if test:
    #     create_random_matches(pseudo_matches)
    
    base_elo = 1500
    calculate_elo_for_all(K = 32, base_elo = base_elo, test = test)
    elo_rating_df = print_leader_board(test)
    visualize_elo_history()
    visualize_network()

