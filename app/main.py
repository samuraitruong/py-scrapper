
from args import args
from lib.http import http
from lib.fs import fs
from lib.parser import HtmlParser
from threading import Lock
import concurrent.futures

visited_links = []
lock = Lock()

def crawl_page(url):
  global visited_links

  html = http.get_html(url)
  fs.save_html(args.output, url, html)
  l = HtmlParser.get_links(args.url, html)
  lock.acquire()
  unique_links = list(set(l) - set(visited_links))
  visited_links = visited_links + unique_links
  lock.release()
  with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
      # Start the load operations and mark each future with its URL
      future_to_url = {executor.submit(crawl_page, url): url for url in unique_links}
      for future in concurrent.futures.as_completed(future_to_url):
          url = future_to_url[future]
          try:
              data = future.result()
          except Exception as exc:
              print('%r generated an exception: %s' % (url, exc))
          else:
              print('Successful %s' % (url))


crawl_page(args.url)
