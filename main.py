import sys
import argparse
import math
import time

from common import Common
common = Common()

parser = argparse.ArgumentParser(description="SeriesID and MatchID from Command Line")
parser.add_argument("--series", type=str, default="ipl-2025-1449924", help="Enter Series ID")
parser.add_argument("--match", type=str, help="Enter Match ID")
args = parser.parse_args()

if not args.match or len(args.match) == 0:
    print("Please provide Match ID.")
    sys.exit()

series= args.series
match = args.match

attempt = 1
prev_score = {}
prev_detailed_score = {}
driver = common.open_cricket_score_page(series, match)
while True:
    try:
        print(f"Attempt : {attempt}")
        attempt += 1
        if attempt % 20 == 0:
            print("Refreshing Browser")
            driver = common.open_cricket_score_page(series, match)
        else:
            time.sleep(3)

        teams = common.get_teams_name()
        if teams is None:
            raise Exception("Teams not found")

        team1_runs, team1_wickets, team1_over = common.get_score_from_page(teams[0])
        team2_runs, team2_wickets, team2_over = common.get_score_from_page(teams[1])
        innings = 1 if team2_over is None else 2
        over = team1_over if innings == 1 else team2_over
        match_status = "Not Yet Started" if team1_over is None else "live"
        match_additional_details = common.get_match_additional_details()
        for details in match_additional_details:
            if 'won' in details:
                match_details = 'completed'
        partnership = common.get_partnership()
        last_batsman = common.get_last_batsman()
        last_wicket_at = common.get_last_wicket_at()
        batsmen1 = common.get_batsmen(1)
        batsmen2 = common.get_batsmen(2)
        bowler1 = common.get_bowler(1)
        bowler2 = common.get_bowler(2)
        #common.open_overs_page(series, match)
        #last_over = common.get_balls_from_over(innings, math.ceil(over))
        last_over = common.get_last_balls()
        team1_score = {
            'runs' :  team1_runs,
            'wickets' : team1_wickets,
            'over' : team1_over
        }
        team2_score = {
            'runs' :  team2_runs,
            'wickets' : team2_wickets,
            'over' : team2_over
        }
        batsmen = {
            'batsman1': {
                'name': batsmen1[0],
                'runs': batsmen1[1],
                'balls':  batsmen1[2],
                'fours': batsmen1[3],
                'sixes': batsmen1[4]
            },
            'batsman2': {
                'name': batsmen2[0],
                'runs': batsmen2[1],
                'balls':  batsmen2[2],
                'fours': batsmen2[3],
                'sixes': batsmen2[4]
            }
        }
        bowler = {
            'bowler1': {
                'name': bowler1[0],
                'overs': bowler1[1],
                'maidens': bowler1[2],
                'runs': bowler1[3],
                'wickets': bowler1[4]
            },
            'bowler2': {
                'name': bowler2[0],
                'overs': bowler2[1],
                'maidens': bowler2[2],
                'runs': bowler2[3],
                'wickets': bowler2[4]
            }
        }

        payload = {
            "id": f"dummy_series&&{match}",
            "ballId": int((int(over) * 6) + (over - int(over)) * 10),
            "batsmen": [
                {
                    "name": batsmen1[0],
                    "runs": 0 if batsmen1[1] is None else int(batsmen1[1]),
                    "balls": 0 if batsmen1[2] is None else int(batsmen1[2])
                },
                {
                    "name": batsmen2[0],
                    "runs": 0 if batsmen2[1] is None else int(batsmen2[1]),
                    "balls": 0 if batsmen2[2] is None else int(batsmen2[2])
                }
            ],
            "bowler": {
                "name": bowler1[0],
                "overs": float(bowler1[1]) if bowler1[1] else 0,
                "runs": int(bowler1[3]) if bowler1[3] else 0,
                "wickets": int(bowler1[4]) if bowler1[4] else 0
            },
            "innings": innings,
            "lastBalls": last_over,
            "matchId": match,
            "message": match_additional_details[0] if len(match_additional_details) > 0 else "",
            "over": math.ceil(over),
            "overId": int(innings * 100 + math.ceil(over)),
            "partnership": partnership,
            "seriesId": "dummy_series",
            "source": "dummy_score",
            "status": "Live" if match_status == "live" else "Completed",
            "team1": {
                "name": teams[0],
                "runs": team1_runs,
                "wickets": team1_wickets,
                "overs": team1_over
            },
            "team2": {
                "name": teams[1],
                "runs": team2_runs,
                "wickets": team2_wickets,
                "overs": team2_over
            }
        }


        print(payload, "\n")
        if prev_score !=  payload:
            response = common.save_score_to_db(payload)
            if response.status_code == 201:
                prev_score = payload
            print("Save Scorecard : " + ("Success" if response.status_code == 201 else "Failed"))
        else:
            print("No change in score")

        # response = common.get_detailed_scorecard(series, match)
        # if prev_detailed_score != response:
        #     response = common.save_detailed_scorecard(response)
        #     if response.status_code == 201:
        #         prev_detailed_score = response
        #     print("Save Detailed Scorecard : " + ("Success" if response.status_code == 201 else "Failed"))
        # else:
        #     print("No change in detailed scorecard")
        print("=====================================================================\n")
    except Exception as e:
        print(e)
        print("=====================================================================\n")
        # if driver is not None:
        #     driver.close()

