from datetime import datetime
import re
from django.utils import timezone
from celery.utils.log import get_task_logger
from celery.contrib import rdb

from celery.decorators import task
from crawler.constants import FEED_TYPES
from crawler.celery import app
from celery import chain
# Scrapers 
from .scrapers import twitter, xml, page_metas

logger = get_task_logger(__name__)

is_twitter_feed = lambda url: url.startswith('https://twitter.com/')
is_xml_feed = lambda url: url.endswith('.xml')

def __crawl_feed(feed_id, feed_url):
    detected_urls = list()
    if is_twitter_feed(feed_url):
        detected_urls = twitter.scrape(feed_url)
    elif is_xml_feed(feed_url):
        detected_urls = xml.scrape(feed_url)
    else:
        raise ValueError((
            'Feed located at %s wasn\'t recognised, please inform your '
            'administrator'
        ) % feed_url )
    return list(map(lambda url:[feed_id, url], detected_urls))

def __feeds_urls(feeds):
    all_urls = list()
    for feed in feeds:
        all_urls = all_urls + __crawl_feed(feed.pk, feed.url)
    return all_urls

@task(ignore_results=True)
def crawl_articles(ids, update=False):
    from crawler.core import tasks_utils as utils
    from crawler.archiving.tasks import archive_articles
    from crawler.storing.tasks import crawl_resources
    if len(ids) == 0:
        logger.warning('crawl_articles called without articles ids')

    if update:
        articles = utils.articles(ids)
        utils.reset_articles_states(articles)
        # we delete previously detected of the given articles
        utils.delete_tags_of(articles)
        utils.delete_archived_urls_of(articles)
        utils.delete_resources_of(articles)

    return chain(
        crawl_preservation_tags.s(),
        crawl_resources.s(),
        archive_articles.s()
    ).apply_async([ids])

@task(ignore_results=True)
def crawl_feeds(ids=None):
    """This task must be called with a list of feed ids.
    If none is given then it will lookup for active feeds (see
    `tasks_utils.active_feeds`). It will behave as following:
        for every feed given get latest links. If needed create
        the needed links. For every created article (link), look
        for preservation_tags.
    """
    from crawler.core import tasks_utils as utils
    qs = None
    if not ids:
        qs = utils.active_feeds()
    else:
        qs = utils.feeds(ids)

    articles_urls = __feeds_urls(qs)
    qs.update(last_time_crawled=timezone.now())
    articles = utils.create_articles(articles_urls)
    ids = utils.pickattr(articles, 'pk')
    # crawl created articles
    logger.info('crawl_feed created %s articles\nIDS:%s' % (len(articles), ids))
    return crawl_articles.apply_async([ids])

def article_preservation_tags(article_id, article_url, *args, **kwargs):
    """
    This task's goal is to return the various preservation tags (if they
    are any).
    """
    [ title, metas ] = page_metas.scrape(article_url)
    return [ title , list(map(lambda meta: [article_id, meta], metas)) ]

@task
def crawl_preservation_tags(ids, *args, **kwargs):
    from crawler.core.tasks_utils import articles as get_articles, set_articles_crawled, save_preservation_tags
    tags = list()
    logger.debug('crawl_preservation_tags %s' % ids)
    articles = get_articles(ids)
    for article in articles:
        [ title, article_tags] = article_preservation_tags(article.pk, article.url)
        article.title = title
        article.save()
        tags = tags + article_tags
    tags = save_preservation_tags(tags)
    set_articles_crawled(articles)
    return ids
