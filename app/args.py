import argparse

parser = argparse.ArgumentParser(description='Website scrapper info.')

parser.add_argument('--url', type=str,  help='Url of website')
parser.add_argument('--output', type=str,  required=False, help='Output folder')

# parser.add_argument('--sum', dest='accumulate', action='store_const',
#                     const=sum, default=max,
#                     help='sum the integers (default: find the max)')

args = parser.parse_args()
