import re
import requests
import argparse
import datetime
import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from statistics import median, mean, pstdev
from scipy.stats import mode

ORDER = "Numerical Order"
NUM_BINS = 50
CURRENT_DATE = str(datetime.datetime.now().strftime("%Y/%m/%d"))
F5_STDEV = 1
GENERATE_NUMS = False

def check_cond(t1, t2, t3, t4, cond1, cond2, cond3, cond4):
    return t1 == cond1 and t2 == cond2 and t3 == cond3 and t4 == cond4

def my_mode(arr):
    return mode(arr)[0][0]

def get_args():
    global NUM_BINS, ORDER, F5_STDEV, GENERATE_NUMS
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--ascending', action='store_true', default=False, help='Print and plot stats in ascending order by frequency.')
    parser.add_argument('-d', '--descending', action='store_true', default=False, help='Print and plot stats in descending order by frequency.')
    parser.add_argument('-g', '--generate', action='store_true', default=False, help='Skip plotting & prompt user for generating numbers in SD.')
    parser.add_argument('--nosave', action='store_true', default=False, help='Don\'t save a raw numbers file.')
    parser.add_argument('-b', '--bins', nargs=1, default=[50], help='Number of bins for plotting histograms. Default: 50')
    parser.add_argument('--stdev', nargs=1, default=[1], help='+/- Stdev. to use for figure 5 and option -c. Default: 1')
    parser.add_argument('--savefile', action='store_true', default=False, help='Save the calottery .txt file as fantasy5results.txt. Default: False')
    parser.add_argument('--uselocal', action='store_true', default=False, help='Use local fantasy5results.txt file from --savefile, instead of fetch. Default: False')
    parser.add_argument('--nonverbose', action='store_true', default=False, help='No output. Default: False')
    args = parser.parse_args()
    NUM_BINS = int(args.bins[0])
    F5_STDEV = float(args.stdev[0])
    GENERATE_NUMS = bool(args.generate)
    return args

def get_fantasy5_file():
    page = requests.get('https://www.calottery.com/sitecore/content/Miscellaneous/download-numbers/?GameName=fantasy-5&Order=No')
    # Fix line endings
    return str(page.content).replace(r'\r', '\r').replace(r'\n', '\n')

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
    histogram["all_lines"] = [*map(lambda x: [*map(int, x)], numbers_arr)]
    return histogram

def print_stats_list(label, list, mean_list, mode_list_rounded, stdev_list, list_rounded):
    print("{:<36}: {:.3f}".format(label+" Max", list[-1]))
    print("{:<36}: {:.3f}".format(label+" Min.", list[0]))
    print("{:<36}: {:.3f}".format(label+" Mean", mean_list))
    print("{:<36}: {:.3f}".format(label+" Median", median(list)))
    print("{:<36}: {:.3f}".format(label+" Mode", my_mode(list)))
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

def print_stats(histogram_items, histogram_dict, ascend_hist, tot_cnt, tot_sum, daily_sums, daily_means,
                daily_stdevs, daily_count_means, daily_count_stdevs, current_numbers, all_lines, nonverbose):
    cnt_min = ascend_hist[0]
    cnt_max = ascend_hist[-1]
    cnt_med = (ascend_hist[19][1] + ascend_hist[20][1]) / 2
    cnt_mode = my_mode(list(histogram_dict.values()))

    cnt_stdev = pstdev(histogram_dict.values())
    if nonverbose == False:
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
    daily_means_rounded = [*map(lambda x: round(x, 2), daily_means)]
    mode_daily_means_rounded = my_mode(daily_means_rounded)
    if nonverbose == False:
        print_stats_list("Numbers Daily Mean", daily_means, mean_daily_means,
                          mode_daily_means_rounded, stdev_daily_means, daily_means_rounded)

    mean_daily_stdevs = mean(daily_stdevs)
    stdev_daily_stdevs = pstdev(daily_stdevs)
    daily_stdevs_rounded = [*map(lambda x: round(x, 2), daily_stdevs)]
    mode_daily_stdevs_rounded = my_mode(daily_stdevs_rounded)
    if nonverbose == False:
        print_stats_list("Numbers Daily Stdev.", daily_stdevs, mean_daily_stdevs,
                          mode_daily_stdevs_rounded, stdev_daily_stdevs, daily_stdevs_rounded)

    daily_sums_means = [*map(lambda x: (x/5), daily_sums)]
    daily_sums_rounded_means = [*map(lambda x: round(x, 2), daily_sums_means)]
    if nonverbose == False:
        print_stats_list("Numbers Daily Sum", daily_sums, mean(daily_sums),
                          my_mode(daily_sums_rounded_means), pstdev(daily_sums_means), daily_sums_rounded_means)

    mean_daily_cnt_mean = mean(daily_count_means)
    stdev_daily_cnt_mean = pstdev(daily_count_means)
    median_daily_cnt_mean = median(daily_count_means)
    daily_count_means_rounded = [*map(lambda x: round(x, 2), daily_count_means)]
    mode_daily_cnt_mean_rounded = my_mode(daily_count_means_rounded)
    if nonverbose == False:
        print_stats_list("Numbers Count Mean", daily_count_means, mean_daily_cnt_mean,
                          mode_daily_cnt_mean_rounded, stdev_daily_cnt_mean, daily_count_means_rounded)

    mean_daily_cnt_stdev = mean(daily_count_stdevs)
    stdev_daily_cnt_stdev = pstdev(daily_count_stdevs)
    median_daily_cnt_stdev = median(daily_count_stdevs)
    daily_count_stdevs_rounded = [*map(lambda x: round(x, 2), daily_count_stdevs)]
    mode_daily_cnt_stdev_rounded = my_mode(daily_count_stdevs_rounded)
    if nonverbose == False:
        print_stats_list("Numbers Count Stdev.", daily_count_stdevs, mean_daily_cnt_stdev,
                          mode_daily_cnt_stdev_rounded, stdev_daily_cnt_stdev, daily_count_stdevs_rounded)

    if nonverbose == False:
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
    if nonverbose == False:
        print("\nLast Winning Numbers Day Sum        : {}".format(current_num_sum))
        print("Last Winning Numbers Day Mean       : {:.3f}".format(current_num_mean))
        print("Last Winning Numbers Day Stdev.     : {:.3f}".format(current_num_stdev))
        print("Last Winning Numbers Day Count Mean.: {:.3f}".format(current_num_cnt_mean))

    if GENERATE_NUMS == True:
        print("Enter your 5 numbers")
        while True:
            user_in = input("Skip > ")
            if user_in == "quit":
                return
            to_skip = [*map(int, re.findall(r"\d+", user_in))]

            user_in = input("Use > ")
            if user_in == "quit":
                return
            to_use = [*map(int, re.findall(r"\d+", user_in))]

            if any(i in to_skip for i in to_use):
                print("Invalid, duplicates")
                continue
            # nums = [*map(int, re.findall(r"\d+", user_in))]
            # if len(nums) != 5 or all(num > 0 and num < 40 for num in nums) == False:
                # print("Invalid input, need 5 numbers, 1 to 39")
                # continue
            if all(num > 0 and num < 40 for num in to_skip) == False:
                print("Invalid, must be 1 to 39")
                continue
            print("Generating...")
            while True:
                nums = random.sample([x for x in range(1,40) if x not in to_skip], 5)
                if all(use in nums for use in to_use) == False:
                    continue
                stdev_nums = pstdev(nums)
                mean_nums = mean(nums)
                freqs_nums = [*map(lambda x: histogram_dict[x], [*map(str, nums)])]
                mean_freq_nums = mean(freqs_nums)
                stdev_freq_nums = pstdev(freqs_nums)

                sd = stdev_daily_stdevs * F5_STDEV
                if (stdev_nums < mean_daily_stdevs + sd and\
                   stdev_nums > mean_daily_stdevs - sd) == False:
                    continue
                sd = stdev_daily_means * F5_STDEV
                if (mean_nums < mean_daily_means + sd and\
                   mean_nums > mean_daily_means - sd) == False:
                    continue
                sd = stdev_daily_cnt_mean * F5_STDEV
                if (mean_freq_nums < mean_daily_cnt_mean + sd and\
                   mean_freq_nums > mean_daily_cnt_mean - sd) == False:
                    continue
                sd = stdev_daily_cnt_stdev * F5_STDEV
                if (stdev_freq_nums < mean_daily_cnt_stdev + sd and\
                   stdev_freq_nums > mean_daily_cnt_stdev - sd) == False:
                    continue

                print(nums)
                break
            # print("1: {}\n2: {}\n3: {}\n4: {}".format(t_1, t_2, t_3, t_4))

    # Figure 0
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

    # Figure 1
    plot_histogram("Daily Winning Numbers Stdevs.", "Daily Stdev.", "Stdev.", daily_stdevs, mean_daily_stdevs,
                    stdev_daily_stdevs, my_mode(daily_stdevs_rounded), current_numbers, current_num_stdev)
    # Figure 2
    plot_histogram("Daily Winning Numbers Means", "Daily Mean", "Mean", daily_means, mean_daily_means,
                    stdev_daily_means, mode_daily_means_rounded, current_numbers, current_num_mean)
    # Figure 3
    plot_histogram("Daily Winning Numbers Frequencies Means", "Daily Mean Frequency", "Mean Freq.",
                    daily_count_means, mean_daily_cnt_mean, stdev_daily_cnt_mean,
                    mode_daily_cnt_mean_rounded, current_numbers, current_num_cnt_mean)
    # Figure 4
    plot_histogram("Daily Winning Frequencies Stdevs.", "Daily Frequency Stdev.", "Mean Freq.",
                    daily_count_stdevs, mean_daily_cnt_stdev, stdev_daily_cnt_stdev,
                    mode_daily_cnt_stdev_rounded, current_numbers, current_num_cnt_stdev)

    print("Loading...")
    # Figure 5
    plt.figure(5)
    in_stdev = [0 for i in range(16)]
    for line in all_lines:
        stdev_line = pstdev(line)
        mean_line = mean(line)
        freqs_line = [*map(lambda x: histogram_dict[x], [*map(str, line)])]
        mean_freq_line = mean(freqs_line)
        stdev_freq_line = pstdev(freqs_line)

        sd = stdev_daily_stdevs * F5_STDEV
        t_1 = int(stdev_line < mean_daily_stdevs + sd and stdev_line > mean_daily_stdevs - sd)
        sd = stdev_daily_means * F5_STDEV
        t_2 = int(mean_line < mean_daily_means + sd and mean_line > mean_daily_means - sd)
        sd = stdev_daily_cnt_mean * F5_STDEV
        t_3 = int(mean_freq_line < mean_daily_cnt_mean + sd and mean_freq_line > mean_daily_cnt_mean - sd)
        sd = stdev_daily_cnt_stdev * F5_STDEV
        t_4 = int(stdev_freq_line < mean_daily_cnt_stdev + sd and stdev_freq_line > mean_daily_cnt_stdev - sd)

        index = t_1 | (t_2 << 1) | (t_3 << 2) | (t_4 << 3)
        in_stdev[index] += 1

    plt.suptitle("Daily Winning Numbers Within +/-{} Stdev. of Mean".format(F5_STDEV))
    plt.title(CURRENT_DATE+": ["+(",".join(current_numbers))+"]")
    plt.xlabel("Conditions")
    plt.ylabel("Total")
    plt.plot([], [], " ", label="1: Daily SD within +/-{} SD of Mean SD".format(F5_STDEV))
    plt.plot([], [], " ", label="2: Daily Mean within +/-{} SD of Mean Mean".format(F5_STDEV))
    plt.plot([], [], " ", label="3: Daily Freq. within +/-{} SD of Mean Freq.".format(F5_STDEV))
    plt.plot([], [], " ", label="4: Daily Freq. SD within +/-{} SD of Mean Freq. SD".format(F5_STDEV))
    plt.plot([], [], " ", label="0: None")
    plt.legend(loc=0, handlelength=0, handletextpad=0, fontsize="small")
    plt.bar(["0","1","2","1,2","3","1,3","2,3","1,2,3","4","1,4","2,4","1,2,4","3,4","1,3,4","2,3,4","1,2,3,4"],
            in_stdev, edgecolor="black")
    print('\033[A\033[K', end='')
    print("Showing plots...")

    plt.show()

#### MAIN ####
def main():
    args = get_args()

    print("--------------------------\n{:^26}\n--------------------------".format("Fantasy 5 | " + CURRENT_DATE))

    if args.uselocal == False:
        print("Fetching...")
        # Get txt file
        lotto_file = get_fantasy5_file()
        if args.savefile == True:
            with open('fantasy5results.txt', 'wb') as out:
                out.write(lotto_file.encode())
        print('\033[A\033[K', end='')
    else:
        with open('fantasy5results.txt', 'r') as local_lotto_file:
            lotto_file = local_lotto_file.read()
    lines = lotto_file.split('\n')

    print("Parsing...")
    # Extract numbers from txt file to build histogram & save raw_numbers file
    if args.nosave == False:
        raw_numbers = open('f5raw_numbers.txt', 'w')
    histogram = build_histogram_and_write_to_file(lines[5:], raw_numbers)
    print('\033[A\033[K', end='')
    if args.nosave == False:
        raw_numbers.close()
        print("Saved: {}".format('f5raw_numbers.txt'))

    # Get computed values
    tot_sum = histogram.pop("sum", None)
    daily_sums = histogram.pop("line_sums", None)
    daily_means = histogram.pop("line_means", None)
    daily_stdevs = histogram.pop("line_stdevs", None)
    daily_count_means = histogram.pop("line_count_means", None)
    daily_count_stdevs = histogram.pop("line_count_stdevs", None)
    all_lines = histogram.pop("all_lines", None)

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

    print("Loading output...")
    print_stats(sorted_hist, histogram, hist_ascend, tot, tot_sum, daily_sums, daily_means, daily_stdevs,
                daily_count_means, daily_count_stdevs, [*map(str, all_lines[0])], all_lines, args.nonverbose)
    print('\033[A\033[K', end='')

if __name__ == "__main__":
    main()
