import re
import requests
import argparse
import datetime
import matplotlib.pyplot as plt
import numpy as np
from statistics import mode, median, mean, pstdev

ORDER = "Numerical Order"
NUM_BINS = 50
CURRENT_DATE = str(datetime.datetime.now().strftime("%Y/%m/%d"))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--ascending', action='store_true', default=False, help='Print and plot stats in ascending order by frequency.')
    parser.add_argument('-d', '--descending', action='store_true', default=False, help='Print and plot stats in descending order by frequency.')
    parser.add_argument('--nosave', action='store_true', default=False, help='Don\'t save a raw numbers file.')
    parser.add_argument('-b', '--bins', nargs=1, default=[50], help='Number of bins for plotting histograms. Default: 50')
    parser.add_argument('--filename', nargs=1, default=['raw_numbers.txt'], help='Filename to save raw numbers file as. Default: \'raw_numbers.txt\'')
    return parser.parse_args()

def get_file():
    page = requests.get('https://www.calottery.com/sitecore/content/Miscellaneous/download-numbers/?GameName=fantasy-5&Order=No')
    # Fix line endings
    txt_file = str(page.content).replace(r'\r', '\r')
    txt_file = txt_file.replace(r'\n', '\n')
    return txt_file

def build_histogram_and_write_to_file(lines, out_file):
    # Initialize histogram
    histogram = {}
    for i in range(39):
        histogram[str(i + 1)] = 0
    histogram["sum"] = 0
    line_sums = []
    line_means = []
    line_stdevs = []

    for line in lines:
        numbers = re.findall(r'\d+', line)[3:]
        numbers_int = [*map(int, numbers)]
        line_sum = sum(numbers_int)
        if line_sum <= 0:
            continue
        histogram["sum"] += line_sum
        line_sums.append(line_sum)
        line_means.append(mean(numbers_int))
        line_stdevs.append(pstdev(numbers_int))
        for i, word in enumerate(numbers):
            histogram[word] += 1
            if out_file is not None:
                out_file.write(word)
                if i < 4:
                    out_file.write(',')
                else:
                    out_file.write('\n')
    histogram["line_sums"] = sorted(line_sums)
    histogram["line_means"] = sorted(line_means)
    histogram["line_stdevs"] = sorted(line_stdevs)
    return histogram

def print_stats(histogram_items, histogram_dict, ascend_hist, tot_cnt, tot_sum, daily_sums, daily_means, daily_stdevs, current_numbers):
    cnt_min = ascend_hist[0]
    cnt_max = ascend_hist[-1]
    cnt_med = (ascend_hist[19][1] + ascend_hist[20][1]) / 2
    cnt_mode = mode(histogram_dict.values())
    cnt_stdev = pstdev(histogram_dict.values())
    print("Number: Count (% of total)")
    for val in histogram_items:
        print("{:^6}: {:^5} ({:^.3f}%)".format(val[0], val[1], (val[1] / tot_cnt)*100))
    print("")
    print("Total Number Count: {}\n".format(tot_cnt))
    print("Count Max   : #{:<7}: {} ({:.3f}%)".format(cnt_max[0], cnt_max[1], (cnt_max[1] / tot_cnt)*100))
    print("Count Min.  : #{:<7}: {} ({:.3f}%)".format(cnt_min[0], cnt_min[1], (cnt_min[1] / tot_cnt)*100))
    print("Count Mean  : {:.3f} ({:.3f}%)".format(tot_cnt / 39, (1 / 39)*100))
    print("Count Median: {:.3f} ({:.3f}%)".format(cnt_med, (cnt_med / tot_cnt)*100))
    print("Count Mode  : {}     ({:.3f}%)".format(cnt_mode, (cnt_mode / tot_cnt)*100))
    print("Count Stdev.: {:.3f}   ({:.3f}%)\n".format(cnt_stdev, (cnt_stdev / tot_cnt)*100))

    print("Numbers Total Sum     : {}".format(tot_sum))
    print("Numbers Total Sum Mean: {:.3f}\n".format(tot_sum / tot_cnt))

    mean_daily_means = mean(daily_means)
    stdev_daily_means = pstdev(daily_means)
    daily_means_rounded = [*map(lambda x: round(x, 1), daily_means)]
    print("Numbers Daily Mean Max   : {:.3f}".format(daily_means[-1]))
    print("Numbers Daily Mean Min.  : {:.3f}".format(daily_means[0]))
    print("Numbers Daily Mean Mean  : {:.3f}".format(mean_daily_means))
    print("Numbers Daily Mean Median: {:.3f}".format(median(daily_means)))
    print("Numbers Daily Mean Mode  : {:.3f}".format(mode(daily_means)))
    print("Numbers Daily Mean Rounded Mode  : {:.3f}".format(mode(daily_means_rounded)))
    print("Numbers Daily Mean Stdev.: {:.3f}".format(stdev_daily_means))
    print("Numbers Daily Mean Rounded Stdev.: {}\n".format(pstdev(daily_means_rounded)))

    mean_daily_stdevs = mean(daily_stdevs)
    stdev_daily_stdevs = pstdev(daily_stdevs)
    daily_stdevs_rounded = [*map(lambda x: round(x, 1), daily_stdevs)]
    print("Numbers Daily Stdev. Max           : {:.3f}".format(daily_stdevs[-1]))
    print("Numbers Daily Stdev. Min.          : {:.3f}".format(daily_stdevs[0]))
    print("Numbers Daily Stdev. Mean          : {:.3f}".format(mean_daily_stdevs))
    print("Numbers Daily Stdev. Median        : {:.3f}".format(median(daily_stdevs)))
    print("Numbers Daily Stdev. Mode          : {:.3f}".format(mode(daily_stdevs)))
    print("Numbers Daily Stdev. Rounded Mode  : {:.3f}".format(mode(daily_stdevs_rounded)))
    print("Numbers Daily Stdev. Stdev.        : {:.3f}".format(stdev_daily_stdevs))
    print("Numbers Daily Stdev. Rounded Stdev.: {}\n".format(pstdev(daily_stdevs_rounded)))

    daily_sums_means = [*map(lambda x: (x/5), daily_sums)]
    daily_sums_rounded_means = [*map(lambda x: round(x, 1), daily_sums_means)]
    print("Numbers Daily Sum Max                : {}".format(daily_sums[-1]))
    print("Numbers Daily Sum Min.               : {}".format(daily_sums[0]))
    print("Numbers Daily Sum Median             : {:.3f}".format(median(daily_sums)))
    print("Numbers Daily Sum Mean               : {:.3f}".format(mean(daily_sums)))
    print("Numbers Daily Sum Mode               : {}".format(mode(daily_sums)))
    print("Numbers Daily Sum Stdev.             : {:.3f}".format(pstdev(daily_sums)))
    print("Numbers Daily Sum Mean Mode          : {}".format(mode(daily_sums_means)))
    print("Numbers Daily Sum Rounded Mean Mode  : {}".format(mode(daily_sums_rounded_means)))
    print("Numbers Daily Sum Mean Stdev.        : {:.3f}".format(pstdev(daily_sums_means)))
    print("Numbers Daily Sum Rounded Mean Stdev.: {}\n".format(pstdev(daily_sums_rounded_means)))

    print("Last Winning Numbers: {}".format(" ".join(current_numbers)))
    for num in current_numbers:
        print("{:>2}: {} ({:.3f}%)".format(num, histogram_dict[num], (histogram_dict[num] / tot_cnt)*100))

    current_numbers_int = [*map(int, current_numbers)]
    current_num_sum = sum(current_numbers_int)
    current_num_mean = current_num_sum / 5
    current_num_stdev = pstdev(current_numbers_int)
    print("\nLast Winning Numbers Day Sum   : {}".format(current_num_sum))
    print("Last Winning Numbers Day Mean  : {:.3f}".format(current_num_mean))
    print("Last Winning Numbers Day Stdev.: {:.3f}".format(current_num_stdev))

    histogram_lists = [*map(list, zip(*histogram_items))]
    cnt_mean = mean(histogram_lists[1])
    plt.figure(0)
    plt.bar(histogram_lists[0], histogram_lists[1], width=0.75, edgecolor='black', linewidth=0.9)
    plt.axhline(cnt_mean, label="Mean: {:.3f}".format(cnt_mean), linestyle="--", color="red")
    plt.title(CURRENT_DATE+": ["+",".join(current_numbers)+"]")
    plt.suptitle("All Winning Numbers Counts ({})".format(ORDER))
    plt.legend(loc=0, fontsize="small")
    plt.xlabel("Number")
    plt.ylabel("Total")

    stdevs_daily_stdevs = [*map(lambda x: mean_daily_stdevs + x*stdev_daily_stdevs,  [-3,-2,-1,1,2,3])]
    figure_1, plots = plt.subplots(2, 1, gridspec_kw = {'height_ratios':[1, 4]}, sharex=True)
    figure_1.suptitle("Daily Winning Numbers Stdevs. (bins={})".format(NUM_BINS))
    figure_1.subplots_adjust(hspace=0)
    plots[0].set_title(CURRENT_DATE+": ["+(",".join(current_numbers))+"]")
    plots[0].boxplot(daily_stdevs, vert=False)
    plots[1].hist(daily_stdevs, edgecolor='black', bins=NUM_BINS)
    plots[1].set_ylabel("Total")
    plots[1].set_xlabel("Daily Stdev.")
    plots[1].axvline(mean(daily_stdevs), label="Mean: {:.3f}".format(mean(daily_stdevs)), linestyle="--", color="red", linewidth=0.9)
    plots[1].axvline(median(daily_stdevs), label="Median: {:.3f}".format(median(daily_stdevs)), linestyle="--", color="#00FF00", linewidth=0.9)
    plots[1].axvline(mode(daily_stdevs_rounded), label="Rounded Mode: {}".format(mode(daily_stdevs_rounded)), linestyle="--", color="#FF8C00", linewidth=0.9)
    plots[1].axvline(current_num_stdev, label="Last Winning Stdev.: {:.3f}".format(current_num_stdev), linestyle="-.", color="#9932CC", linewidth=1)
    for i, stdev_stdev in enumerate(stdevs_daily_stdevs):
        if i == 0:
            plots[1].axvline(stdev_stdev, linestyle="-", label="Stdev.", color="#2F4F4F", linewidth=0.9)
        else:
            plots[1].axvline(stdev_stdev, linestyle="-", color="#2F4F4F", linewidth=0.9)
    plots[1].legend(loc=0, fontsize="small")

    stdevs_mean_daily_means = [*map(lambda x: mean_daily_means + x*stdev_daily_means,  [-3,-2,-1,1,2,3])]
    figure_2, plots = plt.subplots(2, 1, gridspec_kw = {'height_ratios':[1, 4]}, sharex=True)
    figure_2.suptitle("Daily Winning Numbers Means (bins={})".format(NUM_BINS))
    figure_2.subplots_adjust(hspace=0)
    plots[0].set_title(CURRENT_DATE+": ["+(",".join(current_numbers))+"]")
    plots[0].boxplot(daily_means, vert=False)
    plots[1].hist(daily_means, edgecolor='black', bins=NUM_BINS)
    plots[1].set_ylabel("Total")
    plots[1].set_xlabel("Daily Mean")
    plots[1].axvline(mean_daily_means, label="Mean: {:.3f}".format(mean_daily_means), linestyle="--", color="red", linewidth=0.9)
    plots[1].axvline(mode(daily_means_rounded), label="Rounded Mode: {}".format(mode(daily_means_rounded)), linestyle="--", color="#FF8C00", linewidth=0.9)
    plots[1].axvline(median(daily_means), label="Median: {:.3f}".format(median(daily_means)), linestyle="--", color="#00FF00", linewidth=0.9)
    plots[1].axvline(current_num_mean, label="Last Winning Mean: {:.3f}".format(current_num_mean), linestyle="-.", color="#9932CC", linewidth=1)
    for i, mean_stdev in enumerate(stdevs_mean_daily_means):
        if i == 0:
            plots[1].axvline(mean_stdev, linestyle="-", label="Stdev.", color="#2F4F4F", linewidth=0.9)
        else:
            plots[1].axvline(mean_stdev, linestyle="-", color="#2F4F4F", linewidth=0.9)
    plots[1].legend(loc=0, fontsize="small")

    plt.show()

#### MAIN ####
def main():
    global NUM_BINS, ORDER
    args = get_args()
    NUM_BINS = int(args.bins[0])

    print("--------------------------\n{:^26}\n--------------------------".format("Fantasy 5 | " + CURRENT_DATE))

    # Get txt file
    lotto_file = get_file()
    lines = lotto_file.split('\n')

    # Extract numbers from txt file to build histogram & save raw_numbers file
    raw_numbers = None
    if args.nosave == False:
        raw_numbers = open(args.filename[0], 'w')
    histogram = build_histogram_and_write_to_file(lines[5:], raw_numbers)
    if args.nosave == False:
        raw_numbers.close()

    tot_sum = histogram.pop("sum", None)
    daily_sums = histogram.pop("line_sums", None)
    daily_means = histogram.pop("line_means", None)
    daily_stdevs = histogram.pop("line_stdevs", None)

    # Sort histogram, ascending
    hist_ascend = sorted(histogram.items(), key=lambda x: x[1])
    if args.ascending == True or args.descending == True:
        sorted_hist = hist_ascend
        ORDER = "Ascending Order"
        if args.descending == True:
            ORDER = "Descending Order"
            sorted_hist.reverse() # Descending order
    else:
        sorted_hist = histogram.items()

    # Get total numbers
    tot = 0
    for val in sorted_hist:
        tot += val[1]

    print_stats(sorted_hist, histogram, hist_ascend, tot, tot_sum, daily_sums, daily_means, daily_stdevs, re.findall(r'\d+', lines[5])[3:])

if __name__ == "__main__":
    main()
