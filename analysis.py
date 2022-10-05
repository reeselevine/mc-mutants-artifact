import argparse
import json

REVERSING_PO = "reversing_po"
WEAKENING_PO = "weakening_po"
WEAKENING_SW = "weakening_sw"
ALL = "all"
CAUGHT = "caught"
AVG_RATE = "avg_rate"


def load_stats(stats_path):
    """
    Load the file with the test run output
    """
    with open(stats_path, "r") as stats_file:
        dataset = json.loads(stats_file.read())
        return dataset

def per_test_stats(dataset):
    """
    Finds the number of tests caught and the max rate of weak behaviors per test, for the given dataset
    """
    result = {}
    for key in dataset:
        if key != "randomSeed":
            for testKey in dataset[key]:
                if testKey != "params":
                    value = dataset[key][testKey]["weak"]
                    time = dataset[key][testKey]["durationSeconds"]
                    rate = round(value/time, 3)
                    if testKey not in result or result[testKey][1] < rate:
                        result[testKey] = (key, rate)
    reversing_po_rates = []
    reversing_po_caught = 0
    weakening_po_rates = []
    weakening_po_caught = 0
    weakening_sw_rates = []
    weakening_sw_caught = 0
    for key in result:
        # Not the cleanest checking the key name, but reversing po mutants have "mutations" in their name
        if "Mutations" in key:
            reversing_po_rates.append(result[key][1])
            if result[key][1] > 0:
                reversing_po_caught += 1
        # Weakening po mutants have "coherency" in their name
        elif "Coherency" in key:
            weakening_po_rates.append(result[key][1])
            if result[key][1] > 0:
                weakening_po_caught += 1
        # if it's not one of the two mutants above, it must be a weakening sw mutant
        else:
            weakening_sw_rates.append(result[key][1])
            if result[key][1] > 0:
                weakening_sw_caught += 1
    all_rates = reversing_po_rates + weakening_po_rates + weakening_sw_rates
    to_return = dict()
    to_return[REVERSING_PO] = {AVG_RATE: round(sum(reversing_po_rates)/len(reversing_po_rates), 3), CAUGHT: reversing_po_caught}
    to_return[WEAKENING_PO] = {AVG_RATE: round(sum(weakening_po_rates)/len(weakening_po_rates), 3), CAUGHT: weakening_po_caught}
    to_return[WEAKENING_SW] = {AVG_RATE: round(sum(weakening_sw_rates)/len(weakening_sw_rates), 3), CAUGHT: weakening_sw_caught}
    to_return[ALL] = {AVG_RATE: round(sum(all_rates)/len(all_rates), 3), CAUGHT: reversing_po_caught + weakening_po_caught + weakening_sw_caught}
    return (to_return, all_rates)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", required=True,  help="""Analysis to perform.
                        mut-score: returns the mutation scores and average mutant death rates for a dataset.
                        merge: combine test environments across multiple datasets""")
    parser.add_argument("--stats_path", help="Path to the stats to analyze. For the mut-score action, must be a file. For the merge action, must be a directory.")
    args = parser.parse_args()
    if args.action == "mut-score":
        stats = load_stats(args.stats_path)
        result = per_test_stats(stats)[0]
        print(json.dumps(result, indent=4))

if __name__ == "__main__":
    main()
