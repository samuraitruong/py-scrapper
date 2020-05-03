
from args import args
from lib.http import http
from lib.fs import fs
from lib.parser import HtmlParser
from threading import Lock
from lib.logger import logger
from lib.db import Db
import concurrent.futures
from urllib.parse import urlparse
from worq import get_broker, TaskSpace, get_queue
from worq.pool.thread import WorkerPool
import time

ts = TaskSpace("tasks")
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


@ts.task
def download_resource(url):
    # logger.debug("Downloading :" + url)
    exist_filename = fs.get_exist_file_name(args.output, url)
    if(exist_filename):
        return exist_filename
    content = http.get_blob(url)
    out_path = fs.save_blob(args.output, url, content)
    logger.info('RESOURCE: %s => %s' % (url, out_path))
    Db.add_done_item(url)
    return out_path


@ts.task
def crawl_page(url):
    global visited_links
    global downloaded_links
    global html_queue
    global resource_queue

    html = http.get_html(url)
    html_links = HtmlParser.get_links(args.url, html)
    resource_links = HtmlParser.get_resource_urls(args.url, html)

    lock.acquire()
    unique_links = list(set(html_links) - set(visited_links))
    visited_links = visited_links + unique_links
    for l in unique_links:
        html_queue.tasks.crawl_page(l)
    lock.release()

    lock2.acquire()
    unique_resource_links = list(set(resource_links) - set(downloaded_links))
    downloaded_links = downloaded_links + unique_resource_links
    lock2.release()
    if args.download_resources == True:
        resources = dict([(resource_url, fs.get_filename_from_url(args.output, resource_url))
                          for resource_url in resource_links])
        html = HtmlParser.replace_resource_url(resources, html)
        for resource_link in unique_resource_links:
            resource_queue.tasks.download_resource(resource_link)

    output_path = fs.save_html(args.output, url, html)
    logger.info('HTML : %s -> %s' % (url, output_path))
    Db.add_done_item(url)
    return output_path


def create_worker_pool(queue_url, thread_count, **kw):
    broker = get_broker(queue_url)
    broker.expose(ts)
    pool = WorkerPool(broker, workers=thread_count)
    pool.start(**kw)
    return pool

# crawl_page(args.url)


visited_links = [args.url]
html_queue_url = "memory://html"
html_pool = create_worker_pool(html_queue_url, args.threads, timeout=2)
html_queue = get_queue(html_queue_url)

res_queue_url = "memory://res"
resource_pool = create_worker_pool(
    html_queue_url, args.resource_threads, timeout=2)
resource_queue = get_queue(html_queue_url)

html_queue.tasks.crawl_page(args.url)
while(True):
    time.sleep(10)
    if len(html_queue) == 0 and len(resource_queue) == 0:
        html_pool.stop()
        resource_pool.stop()
        logger.info(' ------> FINISHED <-----')

        exit(0)
