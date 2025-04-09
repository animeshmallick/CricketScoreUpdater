import json
import time
import sys
import argparse
import math

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

driver = None
attempt = 1
while True:
    try:
        start_time = time.time()
        print(f"Attempt : {attempt}")

        driver = common.open_cricket_score_page(series, match)

        teams = common.get_teams_name()
        team1_runs, team1_wickets, team1_over = common.get_score_from_page(teams[0])
        team2_runs, team2_wickets, team2_over = common.get_score_from_page(teams[1])
        innings = 1 if team2_over is None else 2
        over = team1_over if innings == 1 else team2_over

        batsmen1 = common.get_batsmen(1)
        batsmen2 = common.get_batsmen(2)
        bowler = common.get_bowler(1)

        partnership = common.get_partnership()
        last_batsman = common.get_last_batsman()
        last_wicket_at = common.get_last_wicket_at()
        common.open_overs_page(series, match)
        last_over = common.get_balls_from_over(innings, math.ceil(over))

        payload = common.get_secondary_payload_data(series, match, partnership, last_batsman, last_wicket_at, last_over, bowler, batsmen1, batsmen1)
        response = common.save_score_to_db(payload)
        print(f"Scorecard Saved in {(time.time() - start_time):.2f}sec with status : " + ("Success" if response.status_code == 201 else "Failed"))

        start_time = time.time()
        response = common.get_detailed_scorecard(series, match)
        print(f"Detailed Scorecard Saved in {(time.time() - start_time):.2f}sec with status : " + ("Success" if response.status_code == 201 else "Failed"))
        print("=====================================================================\n")
    except Exception as e:
        print("=====================================================================\n")
        if driver is not None:
            driver.close()
    attempt += 1