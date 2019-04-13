import re
import requests
import argparse
from statistics import mode, median, mean, stdev

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--ascending', action='store_true', default=False, help='Print stats in ascending order by frequency.')
    parser.add_argument('-d', '--descending', action='store_true', default=False, help='Print stats in descending order by frequency.')
    parser.add_argument('--nosave', action='store_true', default=False, help='Don\'t save a raw numbers file.')
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
        line_stdevs.append(stdev(numbers_int))
        for i, word in enumerate(numbers):
            histogram[word] += 1
            if out_file is not None:
                out_file.write(word)
                if i < 4:
                    out_file.write(',')
                else:
                    out_file.write('\r\n')
    histogram["line_sums"] = sorted(line_sums)
    histogram["line_means"] = sorted(line_means)
    histogram["line_stdevs"] = sorted(line_stdevs)
    return histogram

def print_stats(histogram_items, histogram_dict, ascend_hist, tot_cnt, tot_sum, daily_sums, daily_means, daily_stdevs, current_numbers):
    min_val = ascend_hist[0]
    max_val = ascend_hist[-1]
    med_val = (ascend_hist[19][1] + ascend_hist[20][1]) / 2
    print("Number: Count (% of total)")
    for val in histogram_items:
        print("{:^6}: {:^5} ({:^.3f}%)".format(val[0], val[1], (val[1] / tot_cnt)*100))
    print("")
    print("Total Number Count: {}\n".format(tot_cnt))
    print("Count Max   : #{:<7}: {} ({:.3f}%)".format(max_val[0], max_val[1], (max_val[1] / tot_cnt)*100))
    print("Count Min.  : #{:<7}: {} ({:.3f}%)".format(min_val[0], min_val[1], (min_val[1] / tot_cnt)*100))
    print("Count Mean  : {:.3f} ({:.3f}%)".format(tot_cnt / 39, (1 / 39)*100))
    print("Count Median: {:.3f} ({:.3f}%)".format(med_val, (med_val / tot_cnt)*100))
    cnt_mode = mode(histogram_dict.values())
    print("Count Mode  : {}     ({:.3f}%)".format(cnt_mode, (cnt_mode / tot_cnt)*100))
    cnt_stdev = stdev(histogram_dict.values())
    print("Count Stdev.: {:.3f}   ({:.3f}%)\n".format(cnt_stdev, (cnt_stdev / tot_cnt)*100))
    print("Numbers Total Sum     : {}".format(tot_sum))
    print("Numbers Total Sum Mean: {:.3f}\n".format(tot_sum / tot_cnt))
    print("Numbers Daily Mean Max   : {:.3f}".format(daily_means[-1]))
    print("Numbers Daily Mean Min.  : {:.3f}".format(daily_means[0]))
    print("Numbers Daily Mean Mean  : {:.3f}".format(mean(daily_means)))
    print("Numbers Daily Mean Median: {:.3f}".format(median(daily_means)))
    print("Numbers Daily Mean Mode  : {:.3f}".format(mode(daily_means)))
    print("Numbers Daily Mean Stdev.: {:.3f}\n".format(mean(daily_means)))
    print("Numbers Daily Stdev. Max           : {:.3f}".format(daily_stdevs[-1]))
    print("Numbers Daily Stdev. Min.          : {:.3f}".format(daily_stdevs[0]))
    print("Numbers Daily Stdev. Mean          : {:.3f}".format(mean(daily_stdevs)))
    print("Numbers Daily Stdev. Median        : {:.3f}".format(median(daily_stdevs)))
    print("Numbers Daily Stdev. Mode          : {:.3f}".format(mode(daily_stdevs)))
    daily_stdevs_rounded = [*map(round, daily_stdevs)]
    print("Numbers Daily Stdev. Rounded Mode  : {:.3f}".format(mode(daily_stdevs_rounded)))
    print("Numbers Daily Stdev. Stdev.        : {:.3f}".format(stdev(daily_stdevs)))
    print("Numbers Daily Stdev. Rounded Stdev.: {:.3f}\n".format(stdev(daily_stdevs_rounded)))
    print("Numbers Daily Sum Max                : {}".format(daily_sums[-1]))
    print("Numbers Daily Sum Min.               : {}".format(daily_sums[0]))
    print("Numbers Daily Sum Median             : {:.3f}".format(median(daily_sums)))
    print("Numbers Daily Sum Mean               : {:.3f}".format(mean(daily_sums)))
    print("Numbers Daily Sum Mode               : {}".format(mode(daily_sums)))
    print("Numbers Daily Sum Stdev.             : {:.3f}".format(stdev(daily_sums)))
    line_sums_means = [*map(lambda x: (x/5), daily_sums)]
    line_sums_rounded_means = [*map(round, line_sums_means)]
    print("Numbers Daily Sum Mean Mode          : {}".format(mode(line_sums_means)))
    print("Numbers Daily Sum Rounded Mean Mode  : {}".format(mode(line_sums_rounded_means)))
    print("Numbers Daily Sum Mean Stdev.        : {:.3f}".format(stdev(line_sums_means)))
    print("Numbers Daily Sum Rounded Mean Stdev.: {:.3f}\n".format(stdev(line_sums_rounded_means)))

    print("Last Winning Numbers: {}".format(" ".join(current_numbers)))
    for num in current_numbers:
        print("{:>2}: {} ({:.3f}%)".format(num, histogram_dict[num], (histogram_dict[num] / tot_cnt)*100))
    current_numbers_int = [*map(int, current_numbers)]
    num_sum = sum(current_numbers_int)
    cnt_sum = sum([*map(lambda x: histogram_dict[x], current_numbers)])
    print("\nLast Winning Numbers Day Sum   : {}".format(num_sum))
    print("Last Winning Numbers Day Mean  : {:.3f}".format(num_sum / 5))
    print("Last Winning Numbers Day Stdev.: {:.3f}".format(stdev(current_numbers_int)))

#### MAIN ####
def main():
    args = get_args()

    print("--------------------------\n{:^26}\n--------------------------".format("Fantasy 5"))

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

    sum = histogram.pop("sum", None)
    line_sums = histogram.pop("line_sums", None)
    line_means = histogram.pop("line_means", None)
    line_stdevs = histogram.pop("line_stdevs", None)
    # Sort histogram, ascending
    hist_ascend = sorted(histogram.items(), key=lambda x: x[1])
    if args.ascending == True or args.descending == True:
        sorted_hist = hist_ascend
        if args.descending == True:
            sorted_hist.reverse() # Descending order
    else:
        sorted_hist = histogram.items()

    # Get total numbers
    tot = 0
    for val in sorted_hist:
        tot += val[1]

    print_stats(sorted_hist, histogram, hist_ascend, tot, sum, line_sums, line_means, line_stdevs, re.findall(r'\d+', lines[5])[3:])

if __name__ == "__main__":
    main()
