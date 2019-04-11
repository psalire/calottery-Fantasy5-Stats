import re
import requests
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--ascending', action='store_true', default=False, help='Print stats in ascending order by frequency.')
    parser.add_argument('-d', '--descending', action='store_true', default=False, help='Print stats in descending order by frequency.')
    parser.add_argument('--nosave', action='store_true', default=False, help='Don\'t save a raw numbers file.')
    parser.add_argument('--filename', nargs=1, default='raw_numbers.txt', help='Filename to save raw numbers file as. Default: \'raw_numbers.txt\'')
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

    for line in lines:
        numbers = re.findall(r'\d+', line)
        for i, word in enumerate(numbers[3:]):
            histogram[word] += 1
            if out_file is not None:
                out_file.write(word)
                if i < 4:
                    out_file.write(' ')
                else:
                    out_file.write('\r\n')
    return histogram

def print_stats(histogram_items, histogram_dict, tot, max_val, min_val, current_numbers):
    for val in histogram_items:
        print("{}: {} ({:.3f}%)".format(val[0], val[1], (val[1] / tot)*100))
    print("")
    print("Total Numbers: {}".format(tot))
    print("Max Frequency: {}: {} ({:.3f}%)".format(max_val[0], max_val[1], (max_val[1] / tot)*100))
    print("Min. Frequency: {}: {} ({:.3f}%)\n".format(min_val[0], min_val[1], (min_val[1] / tot)*100))
    print("Current Winning Numbers: {}".format(" ".join(current_numbers)))
    for num in current_numbers:
        print("{}: {} ({:.3f}%)".format(num, histogram_dict[num], (histogram_dict[num] / tot)*100))

#### MAIN ####
def main():
    args = get_args()
    
    print("----------\nFantasy 5\n----------")

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

    # Sort histogram
    hist_ascend = sorted(histogram.items(), key=lambda x: x[1])
    min_val = hist_ascend[0]
    max_val = hist_ascend[-1]
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

    print_stats(sorted_hist, histogram, tot, max_val, min_val, re.findall(r'\d+', lines[5])[3:])

if __name__ == "__main__":
    main()
