import matplotlib.pyplot as plt
import numpy as np
from analysis import *
from os import mkdir, path

def str_to_float(s):
    split = s.split("/")
    if len(split) == 2:
        return float(split[0])/float(split[1])
    else:
        return float(split[0])

def pct(data, total):
    return data/total * 100

def main():
    labels = ["1/1024", "1/512", "1/256", "1/128", "1/64", "1/32", "1/16", "1/8", "1/4", "1/2", "1", "2", "4", "8", "16", "32", "64"]
    total_tests = 128

    site_stats = load_all_stats("site")
    pte_stats = load_all_stats("pte")

    site_95 = []
    site_59s = []
    pte_95 = []
    pte_59s = []
    for l in labels:
        budget = str_to_float(l)
        site_95.append(pct(merge_test_environments(site_stats, .95, budget), total_tests))
        site_59s.append(pct(merge_test_environments(site_stats, .99999, budget), total_tests))
        pte_95.append(pct(merge_test_environments(pte_stats, .95, budget), total_tests))
        pte_59s.append(pct(merge_test_environments(pte_stats, .99999, budget), total_tests))

    pct_labels = ["0%", "20%", "40%", "60%", "80%", "100%"]
    site_95_color = "#66c2a5"
    site_59s_color = "#fc8d62"
    pte_95_color = "#8da0cb"
    pte_59s_color = "#e78ac3"
    x = np.arange(len(labels))
    y = np.arange(0, 110, 20)
    width = 0.2
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))

    ax.bar(x - 1.5 * width, site_95, width, label="SITE 95% Rep", color=site_95_color)
    ax.bar(x - .5 * width, site_59s, width, label="SITE 99.999% Rep", color=site_59s_color)
    ax.bar(x + .5 * width, pte_95, width, label="PTE 95% Rep", color=pte_95_color)
    ax.bar(x + 1.5 * width, pte_59s, width, label="PTE 99.999% Rep", color=pte_59s_color)
    ax.set_ylim([0, 100])
    ax.set_xticks(x, labels, fontsize=10, rotation=45)
    ax.set_yticks(y, pct_labels, fontsize=12)
    ax.set_ylabel("Mutation Score", fontsize=12)
    ax.set_xlabel("Per Test Budget (sec)", fontsize=12)

    fig.legend(loc=(0.17, 0.71), fontsize=10, ncol=1)
    plt.tight_layout(rect=[0,0,1,1])
    if not path.exists("figures"):
        mkdir("figures")
    plt.savefig("figures/figure6.pdf")

if __name__ == "__main__":
    main()
