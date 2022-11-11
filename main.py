import streamlit as st
import streamlit.components.v1 as components
from calc_elo import calculate_elo_for_all, print_leader_board, visualize_elo_history, visualize_network, read_players
import time
from datetime import datetime
import pandas as pd

test = False
base_elo = 1500

calculate_elo_for_all(K = 32, base_elo = base_elo, test = test)
elo_rating_df = print_leader_board(test)
plotly_fig = visualize_elo_history(open_browser = False)
visualize_network(open_browser = False)

def insert_game_result(player_1, player_2, player_1_score, player_2_score):
    
    matches_df = pd.read_excel("Matches.xlsx")
    # write to excel
    # get current time and date
    now = datetime.now()

    now_metrics = {"day" : str(now.day),
                   "month" : str(now.month),
                   "hour" : str(now.hour),
                   "minute" : str(now.minute)}

    for key,val in now_metrics.items():
        if len(val) == 1:
            now_metrics[key] = val

    date =  now_metrics['day'] + "-" + now_metrics['month'] 
    time =  now_metrics['hour']  + ":" + now_metrics['minute'] 
    matches_df = matches_df.append({"Player A": player_1, "Player B": player_2, "Score A": player_1_score, 
                                    "Score B": player_2_score, "Date": date  , "Time": time}, ignore_index=True)

    for col in matches_df.columns:
        if "Unnamed" in col:
            matches_df = matches_df.drop(col, axis = 1)
    matches_df.to_excel("Matches.xlsx", index=False)

    # print("matches_df.tail(5)\n", matches_df.tail(5))
    

def validate_names(player_1, player_2):
    players = read_players()
    if (player_1 in players) and (player_2 in players):
        return True
    else:
        return False


### Streamlit stuff

# set the width of the page to 800px 
st.set_page_config(layout="wide")#, width=800, initial_sidebar_state="expanded")
siteHeader = st.container()
insert_match = st.container()
show_last_5_matches = st.container()
visualize_graph_section = st.container()
leader_board_section = st.container()
leader_board_section_2 = st.container()
elo_rating_history_section = st.container()

show_5_matches = True
text_header = "Show last 5 matches"


with siteHeader:
    st.title('Bordtennis Elo-Ratings')
    # st.text('Some text here')

with insert_match:
    st.header('Insert Game Results')
    # st.text('dashbdak Some text here')

    with st.form("Game Results", clear_on_submit = True):
        player_1_name_insert  = st.text_input('Player 1 Name')
        player_1_score_insert = st.selectbox('Player 1', [0,1,2])
        player_2_name_insert  = st.text_input('Player 2 Name')
        player_2_score_insert = st.selectbox('Player 2', [0,1,2])

        # Every form must have a submit button.
        # st.text('Only press the button once!')
        submitted = st.form_submit_button('Confirm Game Results')
        if submitted and (player_1_name_insert != '') and (player_2_name_insert != '') and (player_1_score_insert != player_2_score_insert):
            if validate_names(player_1_name_insert, player_2_name_insert):
                st.write('Game submitted! If the submission was a mistake, please write the date and time of the game to Haldan :)') 
                insert_game_result(player_1_name_insert, player_2_name_insert, 
                                   player_1_score_insert, player_2_score_insert)
                time.sleep(2)
            else: 
                st.write('ERROR: Please enter valid names!')
                time.sleep(2)
        elif submitted and (player_1_name_insert == '') or (player_2_name_insert == ''):
            pass
        else: 
            st.write('ERROR: Please fill in all fields and make sure that the scores are appropriate')
            time.sleep(2)

with show_last_5_matches:
    with st.form("Matches", clear_on_submit = False):
        if show_5_matches:
            text_header = "Show last 5 matches"
            st.header(text_header)
            show_all_matches = st.form_submit_button('Show All Matches')
            matches_df_5 = pd.read_excel("Matches.xlsx").tail(5)
            st.table(matches_df_5.reindex(index=matches_df_5.index[::-1]))
        elif show_all_matches:
            text_header = "Show all matches"
            st.header(text_header)
            show_5_matches = st.form_submit_button('Hide All Matches')
            matches_df = pd.read_excel("Matches.xlsx")
            st.table(matches_df.reindex(index=matches_df.index[::-1]))
        

with visualize_graph_section:
    st.header('A network showing who can play against who')
    st.text('Red: The threshold for consecuive matches with the same oppenent has been met')
    st.text('     Additional matches will not change the elo rating! ')
    st.text('Orange: The threshold for consecuive matches with the same oppenent is getting close')
    st.text('Green: You can play against this player without worries')
    HtmlFile = open("network_of_valid_players.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height = 750)#, width = 800)

with leader_board_section:
    st.header('Current Leader Board')
    # st.text('Add something cool here ')

    # change data types of columns in elo_rating_df
    elo_rating_df['Anulled'] = elo_rating_df['Anulled'].astype(int)
    st.table(elo_rating_df)


with elo_rating_history_section:
    st.header('History of Elo-Ratings')
    # st.text('Some more text here ')
    st.plotly_chart(plotly_fig, use_container_width=True)#, width = 800)