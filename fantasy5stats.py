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
    line_count_means = []
    line_count_stdevs = []
    numbers_arr = []

    for line in lines:
        numbers = re.findall(r'\d+', line)[3:]
        numbers_int = [*map(int, numbers)]
        line_sum = sum(numbers_int)
        if line_sum <= 0:
            continue
        numbers_arr.append(numbers)
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
    for line in numbers_arr:
        line_cnts = [*map(lambda x: histogram[x], line)]
        line_count_means.append(mean(line_cnts))
        line_count_stdevs.append(pstdev(line_cnts))

    histogram["line_sums"] = sorted(line_sums)
    histogram["line_means"] = sorted(line_means)
    histogram["line_stdevs"] = sorted(line_stdevs)
    histogram["line_count_means"] = sorted(line_count_means)
    histogram["line_count_stdevs"] = sorted(line_count_stdevs)
    return histogram

def print_stats_list(label, list, mean_list, mode_list_rounded, stdev_list, list_rounded):
    print("{:<36}: {:.3f}".format(label+" Max", list[-1]))
    print("{:<36}: {:.3f}".format(label+" Min.", list[0]))
    print("{:<36}: {:.3f}".format(label+" Mean", mean_list))
    print("{:<36}: {:.3f}".format(label+" Median", median(list)))
    print("{:<36}: {:.3f}".format(label+" Mode", mode(list)))
    print("{:<36}: {:.3f}".format(label+" Rounded Mode", mode_list_rounded))
    print("{:<36}: {:.3f}".format(label+" Stdev.", stdev_list))
    print("{:<36}: {:.3f}\n".format(label+" Rounded Stdev.", pstdev(list_rounded)))

def plot_histogram(title, xlabel, factor, list, mean_list, stdev_list, mode_list_rounded, current_num, current_num_in):
    stdevs_list = [*map(lambda x: mean_list + x*stdev_list,  [-3,-2,-1,1,2,3])]
    f, plots = plt.subplots(2, 1, gridspec_kw = {'height_ratios':[1, 4]}, sharex=True)
    f.suptitle(title+" (bins={})".format(NUM_BINS))
    f.subplots_adjust(hspace=0)
    plots[0].set_title(CURRENT_DATE+": ["+(",".join(current_num))+"]")
    plots[0].boxplot(list, vert=False)
    plots[1].hist(list, edgecolor='black', bins=NUM_BINS)
    plots[1].set_ylabel("Total")
    plots[1].set_xlabel(xlabel)
    plots[1].axvline(mean_list, label="Mean: {:.3f}".format(mean_list), linestyle="--", color="red", linewidth=0.9)
    plots[1].axvline(median(list), label="Median: {:.3f}".format(median(list)), linestyle="--", color="#00FF00", linewidth=0.9)
    plots[1].axvline(mode_list_rounded, label="Rounded Mode: {}".format(mode_list_rounded), linestyle="--", color="#FF8C00", linewidth=0.9)
    plots[1].axvline(current_num_in, label="Last Winning {}: {:.3f}".format(factor, current_num_in), linestyle="-.", color="#9932CC", linewidth=1)
    for i, fac in enumerate(stdevs_list):
        if i == 0:
            plots[1].axvline(fac, linestyle="-", label="Stdev.", color="#2F4F4F", linewidth=0.9)
        else:
            plots[1].axvline(fac, linestyle="-", color="#2F4F4F", linewidth=0.9)
    plots[1].legend(loc=0, fontsize="small")

def print_stats(histogram_items, histogram_dict, ascend_hist, tot_cnt, tot_sum,
                daily_sums, daily_means, daily_stdevs, daily_count_means, daily_count_stdevs, current_numbers):
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
    mode_daily_means_rounded = mode(daily_means_rounded)
    print_stats_list("Numbers Daily Mean", daily_means, mean_daily_means,
                      mode_daily_means_rounded, stdev_daily_means, daily_means_rounded)

    mean_daily_stdevs = mean(daily_stdevs)
    stdev_daily_stdevs = pstdev(daily_stdevs)
    daily_stdevs_rounded = [*map(lambda x: round(x, 1), daily_stdevs)]
    mode_daily_stdevs_rounded = mode(daily_stdevs_rounded)
    print_stats_list("Numbers Daily Stdev.", daily_stdevs, mean_daily_stdevs,
                      mode_daily_stdevs_rounded, stdev_daily_stdevs, daily_stdevs_rounded)

    daily_sums_means = [*map(lambda x: (x/5), daily_sums)]
    daily_sums_rounded_means = [*map(lambda x: round(x, 1), daily_sums_means)]
    print_stats_list("Numbers Daily Sum", daily_sums, mean(daily_sums),
                      mode(daily_sums_rounded_means), pstdev(daily_sums_means), daily_sums_rounded_means)

    mean_daily_cnt_mean = mean(daily_count_means)
    stdev_daily_cnt_mean = pstdev(daily_count_means)
    median_daily_cnt_mean = median(daily_count_means)
    daily_count_means_rounded = [*map(lambda x: round(x, 1), daily_count_means)]
    mode_daily_cnt_mean_rounded = mode(daily_count_means_rounded)
    print_stats_list("Numbers Count Mean", daily_count_means, mean_daily_cnt_mean,
                      mode_daily_cnt_mean_rounded, stdev_daily_cnt_mean, daily_count_means_rounded)

    mean_daily_cnt_stdev = mean(daily_count_stdevs)
    stdev_daily_cnt_stdev = pstdev(daily_count_stdevs)
    median_daily_cnt_stdev = median(daily_count_stdevs)
    daily_count_stdevs_rounded = [*map(lambda x: round(x, 1), daily_count_stdevs)]
    mode_daily_cnt_stdev_rounded = mode(daily_count_stdevs_rounded)
    print_stats_list("Numbers Count Stdev.", daily_count_stdevs, mean_daily_cnt_stdev,
                      mode_daily_cnt_stdev_rounded, stdev_daily_cnt_stdev, daily_count_stdevs_rounded)

    print("Last Winning Numbers: {}".format(" ".join(current_numbers)))
    for num in current_numbers:
        print("{:>2}: {} ({:.3f}%)".format(num, histogram_dict[num], (histogram_dict[num] / tot_cnt)*100))

    current_numbers_int = [*map(int, current_numbers)]
    current_numbers_freqs = [*map(lambda x: histogram_dict[x], current_numbers)]
    current_num_sum = sum(current_numbers_int)
    current_num_mean = current_num_sum / 5
    current_num_stdev = pstdev(current_numbers_int)
    current_num_cnt_mean = mean(current_numbers_freqs)
    current_num_cnt_stdev = pstdev(current_numbers_freqs)
    print("\nLast Winning Numbers Day Sum        : {}".format(current_num_sum))
    print("Last Winning Numbers Day Mean       : {:.3f}".format(current_num_mean))
    print("Last Winning Numbers Day Stdev.     : {:.3f}".format(current_num_stdev))
    print("Last Winning Numbers Day Count Mean.: {:.3f}".format(current_num_cnt_mean))

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

    plot_histogram("Daily Winning Numbers Stdevs.", "Daily Stdev.", "Stdev.", daily_stdevs, mean_daily_stdevs,
                    stdev_daily_stdevs, mode(daily_stdevs_rounded), current_numbers, current_num_stdev)
    plot_histogram("Daily Winning Numbers Means", "Daily Mean", "Mean", daily_means, mean_daily_means,
                    stdev_daily_means, mode_daily_means_rounded, current_numbers, current_num_mean)
    plot_histogram("Daily Winning Numbers Frequencies Means", "Daily Mean Frequency", "Mean Freq.",
                    daily_count_means, mean_daily_cnt_mean, stdev_daily_cnt_mean,
                    mode_daily_cnt_mean_rounded, current_numbers, current_num_cnt_mean)
    plot_histogram("Daily Winning Frequencies Stdevs.", "Daily Frequency Stdev.", "Mean Freq.",
                    daily_count_stdevs, mean_daily_cnt_stdev, stdev_daily_cnt_stdev,
                    mode_daily_cnt_stdev_rounded, current_numbers, current_num_cnt_stdev)

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
    daily_count_means = histogram.pop("line_count_means", None)
    daily_count_stdevs = histogram.pop("line_count_stdevs", None)

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

    print_stats(sorted_hist, histogram, hist_ascend, tot, tot_sum, daily_sums, daily_means,
                daily_stdevs, daily_count_means, daily_count_stdevs, re.findall(r'\d+', lines[5])[3:])

if __name__ == "__main__":
    main()
