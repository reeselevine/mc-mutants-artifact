from analysis import *

DIR = "correlation_analysis"

def main():
    intel_stats = load_stats(DIR + "/intel.json")
    intel_corr = json.loads(correlate(intel_stats).to_json())["CoRR Default"]["RR Mutations Default"]
    amd_stats = load_stats(DIR + "/amd.json")
    amd_corr = json.loads(correlate(amd_stats).to_json())["Message Passing Barrier Variant"]["Message Passing Barrier Variant 2"]
    nvidia_stats = load_stats(DIR + "/nvidia.json")
    nvidia_corr = json.loads(correlate(nvidia_stats).to_json())["Message Passing Coherency One-Loc"]["Message Passing Coherency"]

    print("Vendor: Intel, Test: CoRR, Mutant: Reversing po, Correlation: {}".format(intel_corr))
    print("Vendor: AMD, Test: MP-relacq, Mutant: Weakening sw, Correlation: {}".format(amd_corr))
    print("Vendor: NVIDIA, Test: MP-CO, Mutant: Weakening po, Correlation: {}".format(nvidia_corr))

if __name__ == "__main__":
    main()
