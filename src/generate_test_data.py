import json
from output_winner_stats import fetch_json, make_session
import numpy as np

np.random.seed(1337)

def generate_test_data():
    out_dir = "../test_data/"
    s = make_session()
    for game_type in ["V75"]:
        url = f"https://www.atg.se/services/racinginfo/v1/api/products/{game_type}"
        result_json = fetch_json(session=s, url=url)
        with open(out_dir + f"{game_type}_product.json", "w") as f:
            json.dump(result_json, f)

        # One game id example
        game_id = result_json["results"][0]["id"]
        game_json = fetch_json(session=s, url=f"https://www.atg.se/services/racinginfo/v1/api/games/{game_id}")
        with open(out_dir + f"{game_type}_game.json", "w") as f:
            json.dump(game_json, f)


def patch_race_json(path):
    fav_placements = []
    with open(path) as f:
        data = json.load(f)
    
    for race in data.get("races", []):
        starts = race["starts"]
        for i, start in enumerate(starts):
            if i == 0:  # force first horse to be fav
                start["pools"]["vinnare"]["odds"] = 100
                start["result"]["finishOrder"] = np.random.randint(low=1, high=5) 
                fav_placements.append(start["result"]["finishOrder"])
            else:
                start["pools"]["vinnare"]["odds"] = 9999
                start["result"]["finishOrder"] = i+2
    with open(path, "w") as f:
        json.dump(data, f)
    print(r"% Fav wins", 100*np.sum(np.array(fav_placements) == 1)/len(fav_placements))
    print("Median placement", np.median(fav_placements))
    print("Mean placement", np.mean(fav_placements))
    
def main():
    generate_test_data()
    patch_race_json("../test_data/V75_game.json")


if __name__ == "__main__":
    main()