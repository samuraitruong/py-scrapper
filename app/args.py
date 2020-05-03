import argparse

parser = argparse.ArgumentParser(description='Website scrapper info.')

parser.add_argument('--url', type=str,  help='Url of website')
parser.add_argument('--output', type=str,
                    required=True, help='Set the target folder to store crawl data (html + others)')
parser.add_argument('--threads', type=int, default=5,  required=False,
                    help='Number of threads to run to fetch html page in concurences')
parser.add_argument('--resource-threads', type=int, default=5,  required=False,
                    help='Number of threads to run to fetch resources just as image, video')

parser.add_argument('--force', type=bool, default=False,  required=False,
                    help='Remove history and download everything again ')

parser.add_argument('--download_resources', type=bool, default=True,  required=False,
                    help='Download images, js, css, and other files ')

args = parser.parse_args()
print(args)
