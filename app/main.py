
from args import args
from lib.http import http
from lib.fs import fs
from lib.parser import HtmlParser
from threading import Lock
from lib.logger import logger
from lib.db import Db
import concurrent.futures
from urllib.parse import urlparse

visited_links = []
downloaded_links = []
lock = Lock()
lock2 = Lock()
parsed = urlparse(args.url)

Db.create_db(parsed.netloc, args.force)


def run_in_threads(data, action, thread_count):
    results = {}
    if not data or len(data) == 0:
        return results

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(action, url): url for url in data}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            result = ''
            try:
                result = future.result()
                results[url] = result.replace(args.output, '')
            except Exception as exc:
                logger.error('%r generated an exception: %s' % (url, exc))
                Db.add_error_link(url, str(exc))
            else:
                logger.info('FECHED: %s => %s' % (url, result))
                Db.add_done_item(url)
    return results


def download_resource(url):
    # logger.debug("Downloading :" + url)
    content = http.get_blob(url)
    out_path = fs.save_blob(args.output, url, content)
    # logger.info('Downloaded: %s' % (url))
    return out_path


def crawl_page(url):
    global visited_links
    global downloaded_links
    html = http.get_html(url)
    html_links = HtmlParser.get_links(args.url, html)
    resource_links = HtmlParser.get_resource_urls(args.url, html)
    lock2.acquire()
    unique_resource_links = list(set(resource_links) - set(downloaded_links))
    downloaded_links = downloaded_links + unique_resource_links
    lock2.release()
    resources = run_in_threads(
        unique_resource_links, download_resource, args.resource_threads)

    html = HtmlParser.replace_resource_url(resources, html)
    output_path = fs.save_html(args.output, url, html)

    lock.acquire()
    unique_links = list(set(html_links) - set(visited_links))
    visited_links = visited_links + unique_links
    lock.release()

    run_in_threads(unique_links, crawl_page, args.threads)
    return output_path


crawl_page(args.url)
