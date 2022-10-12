# Artifact for "MC Mutants: Evaluating and Improving Testing for Memory Consistency Specifications"

## Introduction
This repository includes information for reproducing and verifying the results in the "MC Mutants" ASPLOS 2023 paper. For more information on terminology and techniques referenced here, please refer to the paper itself.

The workflow in this guide consists of two parts: collecting and analyzing results. On the collection side, we provide the means to run the exact experiments included in the paper. However, the four devices included are all on personal computers that we cannot give direct access to. Therefore, we encourage reviewers to run the experiments on their own device, or on similar devices to the ones in the paper if they have access to them.

On the analysis side, we include the results from running the experiments on the four devices in the paper, as well as the analysis tools we used to generate the main figures in the paper. Additionally, reviewers can use the analysis tools to check the results of their own data collection, and we'd encourage them to send us the results!

## Data Collection

All of the results used in the paper were collected using WebGPU, which runs from the browser. We have built and are hosting a website https://gpuharbor.ucsc.edu/webgpu-mem-testing, which runs the code used to collect the data for the paper directly from the browser. Currently, only Google Chrome supports running WebGPU from non-beta browsers, so we would encourage reviewers to use Chrome when visiting this website. 

The tabs on the left side of the page contain links to many different litmus tests. Each include the ability to set parameters, run different configurations, and see results. To run the experiments included in the paper, go to the [Tuning Suite](https://gpuharbor.ucsc.edu/webgpu-mem-testing/tuning/) tab. There, you will see four preset buttons, "SITE Baseline", "SITE", "PTE Baseline", and "PTE". These presets correspond to the four environments described in Section 5.1 of the paper. Don't worry about setting any other parameters; once you've clicked the preset you'd like to run, press the "Start Tuning" button. When the experiment is complete, the results are available for download as a json file from the "All Runs: Statistics" button.

Similarily, the buttons under the "Correlation Tests" heading can be used to replicate the correlation study in the paper (assuming access to the GPUs used). Each will run the same configuration used in the paper, and the results analysis below can be used to check the correlations between the conformance tests and mutants.

Along with using the hosted version of the website, it is possible to set up and run the code locally. The code is located here: https://github.com/reeselevine/webgpu-litmus, and includes instructions for setting it up. As the hosted version of the website uses an origin trial token from Google to allow WebGPU to run on non-beta versions of Chrome, running it locally requires using the beta [Chrome Canary](https://www.google.com/chrome/canary/).

## Result Analysis

All of the data collected and included in the paper are also included in this repository. Specifically, the folders `site_baseline`, `site`, `pte_baseline`, and `pte` contain the results for each of the four devices. `correlation_analysis` contains the results of running the mutants and the kernel that observes a bug in the three devices described in Section 5.4 of the paper.

The scripts that we use to analyze the results are written in python, and require `matplotlib`, `numpy`, and `pandas` to be installed.

To generate the graphs included in Figure 5 of the paper, run `mk_figure5.py`. The resulting pdfs will be written to the `figures/` directory. Similarily, `mk_figure6.py` creates Figure 6, and `mk_table4.py` prints out the data included in Table 4 of the paper. We will now describe the algorithms we use to generate these figures.

The other file included in this repository, `analysis.py`, contains code for parsing the results of a tuning run. There are three different analyses that can be performed. To see the possible command line arguments, run `python3 analysis.py -h`.

#### Mutation Scores and Mutant Death Rates

Given a result file (e.g. `pte/amd.json`), running `python3 analysis.py --action mutation-score --stats_path pte/amd.json` will print out the number of mutants that were caught by the tuning run, as well as the average mutant death rate. These numbers are broken down by mutant category and combined across all categories, as shown in Figure 5 of the paper.

#### Merging Test Environments

Given a directory of result files (e.g. `pte`), running `python3 analysis.py --action merge --stats_path pte` will print out the number of tests in the PTE datasets that are reproducible across the four devices at a given reproducibility score target and time budget, as described in Section 4.2 of the paper. In fact, the function `merge_test_environments` in `analysis.py` implements Algorithm 1 of the paper, combining environments on a per test basis. To change the reproducibility score target and time budget, command line arguments `--rep` and `--budget` can be used. Therefore, `python3 analysis.py --action merge --stats_path pte --rep 99.999 --budget 4` will find the number of tests that can be reproduced with 99.999% confidence at a time budget of 4 seconds per test.

#### Correlation Analysis
Given a result file (e.g. `correlation_analysis/amd.json`), running `python3 analysis.py --action correlation --stats_path correlation_analysis/amd.json` will print out a table showing the correlation between the number of weak behaviors (or bugs observed) per test in the dataset. For example, the result of the above command is a 4x4 table showing the correlation between an unmutated conformance test, `Message Passing Barrier Variant`, and its three mutants, as defined by Mutator 3 in Section 3.3 of the paper. Notice that while not all the tests are highly correlated, there is a 96.7% correlation between the mutant `Message Passing Barrier Variant 2` and the conformance test, which is the number reported in Table 4 of the paper for this bug. While we only use correlation analysis in our paper to show the relation between observing bugs in conformance tests and weak behaviors in mutants, it can also be used to show general correlation between any pairs of tests in a dataset.
