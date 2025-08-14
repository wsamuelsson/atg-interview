import requests 
import pandas as pd  
import math 
import argparse
import json 
from typing import Callable
class APIError(Exception):
    pass

def make_session() -> requests.Session:
    return requests.Session()

def fetch_json(session: requests.Session, url:str) -> dict:
    try:
        r = session.get(url)
        return r.json()
    except ValueError as e:
        raise APIError(e)

def _fetch_json_from_disk(session: requests.Session, url: str, data_dir="../test_data/") -> dict:
    """Load JSON from disk. Use for testing only"""
    with open(data_dir + '/' + 'V75_game.json') as f:
        return json.load(f)
def extract_race_ids(recent_races_result:list, n_races:int) -> list:
    """
    Function to return the id of the n_races recent races. 
    """
    race_ids = []
    for race in range(n_races):
        race_ids.append(recent_races_result[race]['id'])
    return race_ids

def get_horse_name(start: list) -> str:
    """Returns horse name as string"""
    return start['horse']['name']

def get_placement(result: dict) -> int:
    """Returns the placement from finishOrder or none if there is no finish, or if horse was dq"""
    try:
        if 'disqualified' in result['result'].keys():
            return None  
        return result['result']['finishOrder']
    except KeyError as e:
        return None

def get_starters_v_odds_and_placement(race: dict) -> dict:
    """Returns a dict of starters (horses), mapping to a tuple: (odds of winning, placement)"""
    starts = race['starts']
    v_odds = {}
    for start in starts:
        odds = start['pools']['vinnare']['odds']
        placement = get_placement(start)
        v_odds[get_horse_name(start=start)] = (odds, placement)
    return v_odds 

def get_n_favourites(v_odds: dict, n:int ) -> list:
    """Returns the top n favorites given dict of form horse_name: (odds, placement)"""
    sorted_items = sorted(
        v_odds.items(),
        key=lambda item: item[1][0] if (item[1][0] not in (None, 0)) else math.inf
    )
    # Take top n
    return [{'name': item[0], 'odds':item[1][0], 'placement': item[1][1]} for item in sorted_items[:n]]

def get_race_statistics(game_types:list, race_data: pd.DataFrame) -> pd.DataFrame:
    """Function which returns favourite win %, median favourite placement, and mean favourite placement
        for each game type
    """
    rows = []
    column_headers = ['game_type', 
                     r'% fav wins', 
                     'median fav finish', 
                     'mean fav finish']
    
    for game_type in game_types:
        game_type_mask = race_data["game_type"].str.upper() == game_type.upper()
        game_type_data = race_data[game_type_mask]
        win_pct = 100*game_type_data['fav_won'].mean() #Multiply with 100 to get in percent
        median_finish = game_type_data['fav_placement'].median()
        mean_finish = game_type_data['fav_placement'].mean()
        
        rows.append({'game_type':game_type, 
                     r'% fav wins': win_pct, 
                     'median fav finish': median_finish, 
                     'mean fav finish': mean_finish})
                
    return pd.DataFrame(data=rows, columns=column_headers)

def get_race_data(session: requests.Session, base_url_games:str , column_headers:list, game_types:list, recent_races:dict, fetcher: Callable) -> pd.DataFrame:
    rows = []
    for game_type in game_types:
        ids = recent_races[game_type]
        for id in ids:
            race_url = base_url_games + id
            json_race_data = fetcher(session=session, url=race_url)
            
            races = json_race_data['races']
            for i, race in enumerate(races):   
                v_odds = get_starters_v_odds_and_placement(race)
                faves = get_n_favourites(v_odds, n=3)
                
                rows.append({'race': i, 'game_type':game_type, 
                             'fav_name':faves[0]['name'], 'second_fav_name': faves[1]['name'], 'third_fav_name': faves[2]['name'], 
                            'fav_odds': faves[0]['odds'], 'second_fav_odds': faves[1]['odds'], 'third_fav_odds': faves[2]['odds'], 
                            'fav_placement': faves[0]['placement'], 'fav_won': int(faves[0]['placement'] == 1)})                
    return   pd.DataFrame(columns=column_headers, data=rows)

def get_recent_n_races(session: requests.Session, base_url_product:str, game_types: list, n_races=3) -> dict:
    recent_races = {}
    for game_type in game_types:
        #completed races in results
        result_url  = base_url_product + game_type
        result_json = fetch_json(session=session, url=result_url)
        recent_races[game_type] = extract_race_ids(recent_races_result=result_json['results'], n_races=n_races)
    return recent_races
    
def main(test):
    fetcher = _fetch_json_from_disk if test else fetch_json
    s = make_session()
    game_types = ['V75'] if test else ['V75', 'GS75', 'V86', 'V64', 'V65', 'V5', 'V4', 'V3', 'dd', 'ld']
    
    base_url_product = r"https://www.atg.se/services/racinginfo/v1/api/products/"
    base_url_games   = r"https://www.atg.se/services/racinginfo/v1/api/games/"


    column_headers = ['race', 'game_type', 'fav_name', 
                    'second_fav_name', 'third_fav_name', 
                    'fav_odds', 'second_fav_odds', 'third_fav_odds', 
                    'fav_placement', 'fav_won']
    
    recent_races = get_recent_n_races(session=s, base_url_product=base_url_product, game_types=game_types)
         
    race_data = get_race_data(session=s, base_url_games=base_url_games, column_headers=column_headers, 
                              game_types=game_types, recent_races=recent_races, fetcher=fetcher)
    print(race_data)

    race_stats = get_race_statistics(game_types=game_types, race_data=race_data)
    print(race_stats)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=lambda x: x.lower() == "true", default=False,
                        help="Run in test mode with local JSON instead of live API.")
    args = parser.parse_args()
    main(test=args.test)