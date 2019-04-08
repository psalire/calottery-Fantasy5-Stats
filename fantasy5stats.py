import re
import requests
import argparse

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('--ascending', '-a', action='store_true', default=False, help='Print stats in ascending order by frequency.')
parser.add_argument('--descending', '-d', action='store_true', default=False, help='Print stats in descending order by frequency.')
parser.add_argument('--nosave', action='store_true', default=False, help='Don\'t save a raw numbers file.')
parser.add_argument('--filename', nargs=1, default='raw_numbers.txt', help='Filename to save raw numbers file as. Default: \'raw_numbers.txt\'')
args = parser.parse_args()

# Get txt file
page = requests.get('https://www.calottery.com/sitecore/content/Miscellaneous/download-numbers/?GameName=fantasy-5&Order=No')

# Fix line endings
txt_file = str(page.content).replace(r'\r', '\r')
txt_file = txt_file.replace(r'\n', '\n')
lines = txt_file.split('\n')

# Initialize histogram
histogram = {}
for i in range(39):
    histogram[str(i + 1)] = 0

# Extract numbers from txt file to build histogram & save raw_numbers file
if args.nosave == False:
    raw_numbers = open(args.filename[0], 'w')
for line in lines[5:]:
    numbers = re.findall(r'\d+', line)
    for i, word in enumerate(numbers[3:]):
        histogram[word] += 1
        if args.nosave == False:
            raw_numbers.write(word)
            if i < 4:
                raw_numbers.write(' ')
            else:
                raw_numbers.write('\r\n')
if args.nosave == False:
    raw_numbers.close()

# Sort histogram descending
if args.ascending == True or args.descending == True:
    sorted_hist = sorted(histogram.items(), key=lambda x: x[1])
    if args.ascending == False:
        sorted_hist.reverse() # Ascending order
else:
    sorted_hist = histogram.items()

# Get total numbers
tot = 0
for val in sorted_hist:
    tot += val[1]

print("Total: {}".format(tot))
for val in sorted_hist:
    print("{}: {} ({:.3f}%)".format(val[0], val[1], (val[1] / tot)*100))
