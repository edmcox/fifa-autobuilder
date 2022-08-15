import matplotlib

matplotlib.use("Agg")
import re
from bs4 import BeautifulSoup
import json
import networkx as nx
import math
import itertools
from itertools import permutations, repeat
import re
import matplotlib.pyplot as plt
import copy
import cloudscraper
import math
import os
from os import path


def chemistry_checker(futbin_squad, subs=False, top_n=10):

    # web scraper - takes a futbin squad and extracts the player information

    scraper = cloudscraper.create_scraper()

    html = scraper.get(futbin_squad).text
    soup = BeautifulSoup(html, "html.parser")

    player_list = []
    sub_list = []

    urls = soup.findAll("div", {"class": "cardetails"})

    for url in urls[:11]:
        player_list.append(
            "https://www.futbin.com"
            + re.findall('"([^"]*)"', str(url).split("\n")[1])[0]
        )

    urls = soup.findAll("div", {"class": "card cardnum added"})
    for url in urls:
        try:
            sub_list.append(
                "https://www.futbin.com"
                + re.findall('"([^"]*)"', str(url).split("\n")[5])[0]
            )
        except:
            break

    player_dicts = {}

    for player in player_list:
        html = scraper.get(player).text
        soup = BeautifulSoup(html, "html.parser")

        name = soup.find("div", {"class": "pcdisplay-name"}).text

        temp_dict = {}

        temp_dict["Position"] = soup.find("div", {"class": "pcdisplay-pos"}).text
        temp_dict["Rating"] = soup.find("div", {"class": "pcdisplay-rat"}).text

        table = soup.find("table", {"class": "table-info"})

        data_types = ["Club", "Nation", "League", "Revision"]

        for row in table.findAll("tr"):
            try:
                data_type = row.find("th").text
                data = row.find("td").text
                if data_type in data_types:
                    temp_dict[data_type] = data.strip()
            except:
                pass

        player_dicts[name] = temp_dict

    sub_dicts = {}

    for player in sub_list:
        html = scraper.get(player).text
        soup = BeautifulSoup(html, "html.parser")

        name = soup.find("div", {"class": "pcdisplay-name"}).text

        temp_dict = {}

        temp_dict["Position"] = soup.find("div", {"class": "pcdisplay-pos"}).text
        temp_dict["Rating"] = soup.find("div", {"class": "pcdisplay-rat"}).text

        table = soup.find("table", {"class": "table-info"})
        data_types = ["Club", "Nation", "League", "Revision"]

        for row in table.findAll("tr"):
            try:
                data_type = row.find("th").text
                data = row.find("td").text
                if data_type in data_types:
                    temp_dict[data_type] = data.strip()
            except:
                pass

        sub_dicts[name] = temp_dict

    # adds subs player data if sub=True

    if subs == False:
        players_list = [player_dicts]
    else:
        player_dicts.update(sub_dicts)
        players_list = []
        for subset in itertools.combinations(player_dicts, 11):
            temp = {}
            for name in subset:
                temp[name] = player_dicts[name]

            players_list.append(temp)

    if len(player_dicts) > 17:
        return "Too many subsitutes. Max = 6"

    # link strength calculator function

    def calc_link_strength(player_1, player_2):
        if player_1["Club"] == "Icons" and player_2["Club"] == "Icons":
            if player_1["Nation"] == player_2["Nation"]:
                link_strength = 3
            else:
                link_strength = 2

        elif player_1["Club"] == "Icons" or player_2["Club"] == "Icons":
            if player_1["Nation"] == player_2["Nation"]:
                link_strength = 2
            else:
                link_strength = 1

        else:
            if (
                player_1["Nation"] != player_2["Nation"]
                and player_1["League"] != player_2["League"]
                and player_1["Club"] != player_2["Club"]
            ):
                link_strength = 0
            elif (
                player_1["Nation"] == player_2["Nation"]
                and player_1["League"] != player_2["League"]
                and player_1["Club"] != player_2["Club"]
            ):
                link_strength = 1
            elif (
                player_1["Nation"] != player_2["Nation"]
                and player_1["League"] == player_2["League"]
                and player_1["Club"] != player_2["Club"]
            ):
                link_strength = 1
            elif (
                player_1["Nation"] != player_2["Nation"]
                and player_1["League"] != player_2["League"]
                and player_1["Club"] == player_2["Club"]
            ):
                link_strength = 2
            elif (
                player_1["Nation"] == player_2["Nation"]
                and player_1["League"] == player_2["League"]
                and player_1["Club"] != player_2["Club"]
            ):
                link_strength = 2
            elif (
                player_1["Nation"] == player_2["Nation"]
                and player_1["League"] != player_2["League"]
                and player_1["Club"] == player_2["Club"]
            ):
                link_strength = 2
            elif (
                player_1["Nation"] != player_2["Nation"]
                and player_1["League"] == player_2["League"]
                and player_1["Club"] == player_2["Club"]
            ):
                link_strength = 2
            elif (
                player_1["Nation"] == player_2["Nation"]
                and player_1["League"] == player_2["League"]
                and player_1["Club"] == player_2["Club"]
            ):
                link_strength = 3

        return link_strength

    # position categories of each position

    pos_category = {
        "Central": [
            "ST",
            "CF",
            "CAM",
            "CM",
            "CDM",
            "LAM",
            "RAM",
            "LCM",
            "RCM",
            "LST",
            "RST",
            "LDM",
            "RDM",
        ],
        "Left": ["LF", "LW", "LM"],
        "Right": ["RF", "RW", "RM"],
        "Left Back": ["LB", "LWB"],
        "Right Back": ["RB", "RWB"],
        "Centre Back": ["CB", "LCB", "RCB"],
        "Goalkeeper": ["GK"],
    }

    # load in formation metadata

    with open("formations.json") as f:
        formations_json = json.load(f)

    poss_combs = len(players_list) * len(formations_json)

    comb_list = []
    for players in players_list:

        player_pos = {}

        for key in pos_category.keys():
            player_pos[key] = {"count": 0, "players": []}

        for player in players:
            for pos in pos_category.keys():
                if players[player]["Position"] in pos_category[pos]:
                    player_pos[pos]["count"] += 1
                    player_pos[pos]["players"].append(player)
                    break

        for formation in formations_json:

            formation_pos = {}
            for key in pos_category.keys():
                formation_pos[key] = {"count": 0, "pos": []}

            for f_pos in list(formations_json[formation]["pos"].keys()):
                for pos in pos_category.keys():
                    if f_pos in pos_category[pos]:
                        formation_pos[pos]["count"] += 1
                        formation_pos[pos]["pos"].append(f_pos)
                        break

            # check to see whether formation positions matches available player positions

            match = True
            for pos_cat in formation_pos:
                if formation_pos[pos_cat]["count"] != player_pos[pos_cat]["count"]:
                    match = False
                    break

            # assigns player to formation and calculates individual/team chemistry and team rating

            if match == True:
                G = nx.Graph()

                G.add_edges_from(formations_json[formation]["edges"])
                graph_pos = formations_json[formation]["pos"]

                combinations = []

                for item in player_pos:
                    if player_pos[item]["count"] != 1:
                        if not combinations:
                            combinations = list(
                                list(zip(r, p))
                                for (r, p) in zip(
                                    repeat(player_pos[item]["players"]),
                                    permutations(formation_pos[item]["pos"]),
                                )
                            )
                            length = len(combinations)
                        else:
                            copy_comb = combinations[:]
                            for i in range(
                                math.factorial(player_pos[item]["count"]) - 1
                            ):
                                for j in range(length):
                                    combinations.append(copy_comb[i][:])

                            additions = list(
                                list(zip(r, p))
                                for (r, p) in zip(
                                    repeat(player_pos[item]["players"]),
                                    permutations(formation_pos[item]["pos"]),
                                )
                            )

                            nxt = 0
                            for add in additions:
                                for i in range(nxt, (nxt + length)):
                                    combinations[i] += add

                                nxt += length

                for item in player_pos:
                    if player_pos[item]["count"] == 1:
                        for comb in combinations:
                            comb.append(
                                (
                                    player_pos[item]["players"][0],
                                    formation_pos[item]["pos"][0],
                                )
                            )

                for comb in combinations:
                    temp_comb = {
                        "players": [],
                        "formation": formation,
                        "chemistry": 0,
                        "rating": 0,
                        "full_chem": 0,
                    }
                    for player_1 in comb:
                        player_dict = {"name": player_1[0], "pos": player_1[1]}
                        temp_comb["rating"] += int(players[player_1[0]]["Rating"]) / 11
                        linked_pos = list(dict(G.adj[player_1[1]]).keys())
                        links = 0
                        for pos in linked_pos:
                            for player_2 in comb:
                                if player_2[1] == pos:
                                    links += calc_link_strength(
                                        players[player_1[0]], players[player_2[0]]
                                    )

                        if links / len(linked_pos) > 1.6:
                            player_dict["chemistry"] = 10
                            temp_comb["chemistry"] += 10
                        elif (
                            links / len(linked_pos) <= 1.6
                            and links / len(linked_pos) >= 1
                        ):
                            player_dict["chemistry"] = 9
                            temp_comb["chemistry"] += 9
                        elif (
                            links / len(linked_pos) <= 1
                            and links / len(linked_pos) >= 0.3
                        ):
                            player_dict["chemistry"] = 6
                            temp_comb["chemistry"] += 6
                        elif links / len(linked_pos) < 0.3:
                            player_dict["chemistry"] = 3
                            temp_comb["chemistry"] += 3

                        if player_dict["chemistry"] < 9:
                            temp_comb["full_chem"] += 1

                        temp_comb["players"].append(player_dict)

                    if temp_comb["chemistry"] > 100:
                        temp_comb["chemistry"] = 100

                    temp_comb["rating"] += temp_comb["chemistry"]

                    comb_list.append(temp_comb)

    if not comb_list:
        return "No suitable formations"
    else:

        # sort solutions by team chemistry and plot top_n best solutions

        best_comb_chem = sorted(comb_list, key=lambda i: i["chemistry"], reverse=True)

        width = 6 if top_n == 1 else 12

        fig = plt.figure(figsize=(width, (5 * math.ceil(top_n / 2))))

        rank = 0
        for i in range(top_n):
            rank += 1
            best_comb = best_comb_chem[rank - 1]

            G = nx.Graph()

            G.add_edges_from(formations_json[best_comb["formation"]]["edges"])
            graph_pos = copy.copy(formations_json[best_comb["formation"]]["pos"])

            mapping = {}
            for player in best_comb["players"]:
                txt = "{player:} ({chemistry:})"
                mapping[player["pos"]] = txt.format(
                    player=player["name"], chemistry=player["chemistry"]
                )
                graph_pos[
                    txt.format(player=player["name"], chemistry=player["chemistry"])
                ] = graph_pos.pop(player["pos"])

            H = nx.relabel_nodes(G, mapping)

            cols = 1 if top_n == 1 else 2

            ax = fig.add_subplot(math.ceil(top_n / 2), cols, int(i + 1))
            nx.draw(
                H,
                graph_pos,
                with_labels=True,
                node_color="r",
                font_weight="bold",
                font_size=10,
            )
            ax.text(
                0.05,
                0.05,
                str(
                    "Formation: {}\nChemistry: {}\nRating: {}\nPlayers off chem: {}"
                ).format(
                    best_comb["formation"],
                    best_comb["chemistry"],
                    int(best_comb["rating"]),
                    best_comb["full_chem"],
                ),
                size=10,
                ha="left",
                transform=ax.transAxes,
            )
            ax.set_title(rank, loc="left", fontsize=20)

        if not os.path.exists("static/images"):
            os.mkdir("static/images")

        plt.savefig("static/images/plot.png", bbox_inches="tight")
        return poss_combs
