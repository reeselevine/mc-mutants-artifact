import argparse
import json
import math
import csv
import pandas
from os import listdir, remove

REVERSING_PO = "reversing_po"
WEAKENING_PO = "weakening_po"
WEAKENING_SW = "weakening_sw"
ALL = "all"
CAUGHT = "caught"
AVG_RATE = "avg_rate"
VERY_LARGE_RATE = 10000000000

class MaxReprTests:

    def __init__(self, rep_tests, min_rate, test_iter):
        self.rep_tests = rep_tests
        self.min_rate = min_rate
        self.test_iter = test_iter

    def better_than(self, other):
        if self.rep_tests == other.rep_tests:
            return self.min_rate > other.min_rate
        else:
            return self.rep_tests > other.rep_tests

class DeviceStats:

    def __init__(self, device, data):
        self.device = device
        self.data = data

def load_stats(stats_path):
    """
    Load the file with the test run output
    """
    with open(stats_path, "r") as stats_file:
        dataset = json.loads(stats_file.read())
        return dataset

def load_all_stats(stats_dir):
    """
    Load all stats files in the specified directory
    """
    all_stats = []
    for stats_file in listdir(stats_dir):
        all_stats.append(DeviceStats(stats_file.split(".")[0], load_stats(stats_dir + "/" + stats_file)))
    return all_stats

def correlate(dataset):
    """
    Converts a stats json file to a csv, for use with python data science modules, then finds
    the correlation between the weak behaviors of the tests in the dataset.
    """
    data_file = open("temp.csv", 'w')
    csv_writer = csv.writer(data_file)
    first = True
    for key in dataset:
        if key != "randomSeed":
            row = []
            if first:
                for test_key in dataset[key]:
                    if test_key != "params":
                        row.append(test_key)
                first = False
                csv_writer.writerow(row)
                row = []
            for test_key in dataset[key]:
                if test_key != "params":
                    row.append(dataset[key][test_key]["weak"])
            csv_writer.writerow(row)
    data_file.close()
    df = pandas.read_csv("temp.csv")
    remove("temp.csv")
    return df.corr()

def calculate_rate(stats, test_iter, test_key):
    value = stats[test_iter][test_key]["weak"]
    time = stats[test_iter][test_key]["durationSeconds"]
    rate = round(value/time, 3)
    return rate

def get_ceiling_rate(reproducibility, time_budget):
    num_weak_behaviors = math.ceil(-math.log(1 - reproducibility))
    return num_weak_behaviors/time_budget

def merge_test_environments(all_stats, rep, budget):
    """
    Merge environments on a per test basis, finding the one that maximizes the number of reproducible tests
    """
    ceiling_rate = get_ceiling_rate(rep, budget)
    initial_best = MaxReprTests(0, VERY_LARGE_RATE, '0')
    tests = {}
    for test_key in all_stats[0].data["0"]:
        if test_key != "params":
            tests[test_key] = initial_best
    for test_iter in all_stats[0].data:
        if test_iter != "randomSeed":
            for test_key in tests.keys():
                result = MaxReprTests(0, VERY_LARGE_RATE, test_iter)
                for stats in all_stats:
                    rate = calculate_rate(stats.data, test_iter, test_key)
                    if rate >= ceiling_rate:
                        result.rep_tests += 1
                    if rate > 0:
                        result.min_rate = min(result.min_rate, rate)
                if result.better_than(tests[test_key]):
                    tests[test_key] = result
    rep_tests = 0
    for (test_key, res) in tests.items():
        for stats in all_stats:
            if calculate_rate(stats.data, res.test_iter, test_key) >= ceiling_rate:
                rep_tests += 1
    return rep_tests

def per_test_stats(dataset):
    """
    Finds the number of tests caught and the max rate of weak behaviors per test, for the given dataset
    """
    result = {}
    for test_iter in dataset:
        if test_iter != "randomSeed":
            for test_key in dataset[test_iter]:
                if test_key != "params":
                    rate = calculate_rate(dataset, test_iter, test_key)
                    if test_key not in result or result[test_key] < rate:
                        result[test_key] = rate
    reversing_po_rates = []
    reversing_po_caught = 0
    weakening_po_rates = []
    weakening_po_caught = 0
    weakening_sw_rates = []
    weakening_sw_caught = 0
    for key in result:
        # Not the cleanest checking the key name, but reversing po mutants have "mutations" in their name
        if "Mutations" in key:
            reversing_po_rates.append(result[key])
            if result[key]> 0:
                reversing_po_caught += 1
        # Weakening po mutants have "coherency" in their name
        elif "Coherency" in key:
            weakening_po_rates.append(result[key])
            if result[key] > 0:
                weakening_po_caught += 1
        # if it's not one of the two mutants above, it must be a weakening sw mutant
        else:
            weakening_sw_rates.append(result[key])
            if result[key] > 0:
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
    parser.add_argument("--action", required=True, help="""Analysis to perform.
                        mutation-score: returns the mutation scores and average mutant death rates for a dataset.
                        merge: combine test environments across multiple datasets
                        correation: show the correlation between the weak behaviors of tests in the dataset""")
    parser.add_argument("--stats_path", required=True, help="Path to the stats to analyze. For the mutation-score and correlation actions, must be a file. For the merge action, must be a directory.")
    parser.add_argument("--rep", default="99.999", help="Level of reproducibility (merge action).")
    parser.add_argument("--budget", default="4", help="Time budget per test (seconds) (merge action)")
    args = parser.parse_args()
    if args.action == "mutation-score":
        stats = load_stats(args.stats_path)
        result = per_test_stats(stats)[0]
        print(json.dumps(result, indent=4))
    elif args.action == "merge":
        all_stats = load_all_stats(args.stats_path)
        rep_tests = merge_test_environments(all_stats, float(args.rep)/100, float(args.budget))
        print("Number of Reproducible Tests: {}".format(rep_tests))
    elif args.action == "correlation":
        stats = load_stats(args.stats_path)
        correlation = correlate(stats)
        print(correlation)

if __name__ == "__main__":
    main()
