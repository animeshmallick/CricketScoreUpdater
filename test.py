import argparse
import sys

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

driver = common.open_cricket_score_page(series, match)
common.get_detailed_scorecard(series, match)
