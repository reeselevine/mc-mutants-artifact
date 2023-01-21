import matplotlib.pyplot as plt
import numpy as np
from analysis import *
from os import mkdir, path

INTEL = "intel"
AMD = "amd"
NVIDIA = "nvidia"
M1 = "m1"
devices = [INTEL, AMD, NVIDIA, M1]
figure_labels = ["Intel", "AMD", "NVIDIA", "M1"]

SITE_BASELINE = "site_baseline"
SITE_BASELINE_COLOR = "#66c2a5"
SITE = "site"
SITE_COLOR = "#fc8d62"
PTE_BASELINE = "pte_baseline"
PTE_BASELINE_COLOR = "#8da0cb"
PTE = "pte"
PTE_COLOR = "#e78ac3"
environments = [SITE_BASELINE, SITE, PTE_BASELINE, PTE]

REVERSING_PO_TESTS = 8
WEAKENING_PO_TESTS = 6
WEAKENING_SW_TESTS = 18
ALL_TESTS = 32

def per_device_stats(environment):
    result = dict()
    all_rates = []
    all_caught = 0
    for device in devices:
        dataset = load_stats("{}/{}.json".format(environment, device))
        (stats, rates) = per_test_stats(dataset)
        result[device] = stats
        all_rates += rates
        all_caught += stats[ALL][CAUGHT]
    result[ALL] = {AVG_RATE: round(sum(all_rates)/len(all_rates), 3), CAUGHT: all_caught}
    return result

def all_stats():
    result = dict()
    all_rates = []
    for e in environments:
        result[e] = per_device_stats(e)
    return result

def pct(data, total):
    return data/total * 100

def mutation_score_subfigure(stats, mutant_type, num_tests, fig_name, per_device=True):
    site_baseline_score = []
    site_score = []
    pte_baseline_score = []
    pte_score = []
    if per_device:
        for device in devices:
            site_baseline_score.append(pct(stats[SITE_BASELINE][device][mutant_type][CAUGHT], num_tests))
            site_score.append(pct(stats[SITE][device][mutant_type][CAUGHT], num_tests))
            pte_baseline_score.append(pct(stats[PTE_BASELINE][device][mutant_type][CAUGHT], num_tests))
            pte_score.append(pct(stats[PTE][device][mutant_type][CAUGHT], num_tests))
    else:
        site_baseline_score.append(pct(stats[SITE_BASELINE][ALL][CAUGHT], num_tests))
        site_score.append(pct(stats[SITE][ALL][CAUGHT], num_tests))
        pte_baseline_score.append(pct(stats[PTE_BASELINE][ALL][CAUGHT], num_tests))
        pte_score.append(pct(stats[PTE][ALL][CAUGHT], num_tests))

    pct_labels = ["0%", "20%", "40%", "60%", "80%", "100%"]
    if per_device:
        x = np.arange(len(figure_labels))
        labels = figure_labels
    else:
        x = np.arange(1)
        labels = ["Total"]
    y = np.arange(0, 110, 20)
    width = 0.2
    fig, ax = plt.subplots(1, 1, figsize=(5, 2))
    ax.bar(x - 1.5 * width, site_baseline_score, width, label="Naive", color=SITE_BASELINE_COLOR)
    ax.bar(x - .5 * width, site_score, width, label="Prior SOTA", color=SITE_COLOR)
    ax.bar(x + .5 * width, pte_baseline_score, width, label="My work", color=PTE_BASELINE_COLOR)
    ax.bar(x + 1.5 * width, pte_score, width, label="Synergized", color=PTE_COLOR)
    ax.set_ylim([0, 100])
    ax.set_yticks(y, pct_labels, fontsize=10)
    ax.set_xticks(x, labels)
    ax.set_ylabel("TE Effectiveness", fontsize=10)
    fig.legend(loc=(0.01, 0.87), fontsize=10, ncol=4)
    plt.tight_layout(rect=[0, 0, 1, .93])
    plt.savefig("figures/figure5{}.png".format(fig_name))

def avg_mutant_death_rate_subfigure(stats, mutant_type, fig_name, per_device=True):
    site_baseline_rates = []
    site_rates = []
    pte_baseline_rates = []
    pte_rates = []
    if per_device:
        for device in devices:
            site_baseline_rates.append(stats[SITE_BASELINE][device][mutant_type][AVG_RATE])
            site_rates.append(stats[SITE][device][mutant_type][AVG_RATE])
            pte_baseline_rates.append(stats[PTE_BASELINE][device][mutant_type][AVG_RATE])
            pte_rates.append(stats[PTE][device][mutant_type][AVG_RATE])
    else:
        site_baseline_rates.append(stats[SITE_BASELINE][ALL][AVG_RATE])
        site_rates.append(stats[SITE][ALL][AVG_RATE])
        pte_baseline_rates.append(stats[PTE_BASELINE][ALL][AVG_RATE])
        pte_rates.append(stats[PTE][ALL][AVG_RATE])

    log_labels = ["0", "1", "10", "100", "1,000", "10,000", "100,000"]
    if per_device:
        x = np.arange(len(figure_labels))
        labels = figure_labels
    else:
        x = np.arange(1)
        labels = ["Total"]
    y = [0, 1, 10, 100, 1000, 10000, 100000]
    width = 0.2
    fig, ax = plt.subplots(1, 1, figsize=(5, 2))
    ax.bar(x - 1.5 * width, site_baseline_rates, width, label="SITE Baseline", color=SITE_BASELINE_COLOR)
    ax.bar(x - .5 * width, site_rates, width, label="SITE", color=SITE_COLOR)
    ax.bar(x + .5 * width, pte_baseline_rates, width, label="PTE Baseline", color=PTE_BASELINE_COLOR)
    ax.bar(x + 1.5 * width, pte_rates, width, label="PTE", color=PTE_COLOR)
    ax.set_yscale('symlog')
    ax.set_yticks(y, log_labels, fontsize=10)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Mutant Death Rate (sec)", fontsize=10)
    fig.legend(loc=(0.01, 0.87), fontsize=10, ncol=4)
    plt.tight_layout(rect=[0, 0, 1, .93])
    plt.savefig("figures/figure5{}.pdf".format(fig_name))

def main():
    stats = all_stats()
    if not path.exists("figures"):
        mkdir("figures")
    mutation_score_subfigure(stats, REVERSING_PO, REVERSING_PO_TESTS, "a")
    avg_mutant_death_rate_subfigure(stats, REVERSING_PO, "b")
    mutation_score_subfigure(stats, WEAKENING_PO, WEAKENING_PO_TESTS, "c")
    avg_mutant_death_rate_subfigure(stats, WEAKENING_PO, "d")
    mutation_score_subfigure(stats, WEAKENING_SW, WEAKENING_SW_TESTS, "e")
    avg_mutant_death_rate_subfigure(stats, WEAKENING_SW, "f")
    mutation_score_subfigure(stats, ALL, ALL_TESTS, "g")
    avg_mutant_death_rate_subfigure(stats, ALL, "h")
    mutation_score_subfigure(stats, "N/A", ALL_TESTS * len(devices), "i", False)
    avg_mutant_death_rate_subfigure(stats, "N/A", "j", False)

if __name__ == "__main__":
    main()
