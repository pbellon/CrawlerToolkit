from django.urls import reverse
from celery.decorators import task
from celery.utils import log
from crawler import utils
from crawler.archiving.models import ArchivedArticle
from .scrapers import detect_notfound, archive

logger = log.get_task_logger(__name__)

def notify_archived(articles):
    articles_archived.send(articles)

def archive_article(article):
    from crawler.constants import STATES
    service_name = ''
    archived_url = ''
    # First case: we have no preservation, thus in case of
    # preservation:priority meta tag.
    article_url = article.url

    # Second case: every article that has preservation needs thus other meta
    # tags
    if article.preservation_state != STATES.PRESERVATION.NO_PRESERVE:
        article_path = reverse('store:serve_article', kwargs={
            'feed_slug':article.feed.slug,
            'article_slug':article.slug
        })
        article_url = utils.absurl(article_path)

    try:
        for service in archive.services(article_url):
            service_name = service.name()
            prev_archive = ArchivedArticle.objects.filter(
                service=service_name,
                article=article
            )
            if not prev_archive.exists():
                archived_url = service.start()
                ArchivedArticle.objects.create(
                    service=service_name,
                    url=archived_url,
                    article=article)

        article.archiving_state = STATES.ARCHIVE.ARCHIVED
    except Exception as e:
        article.archiving_state = STATES.ARCHIVE.ERROR
        logger.error("An error occured when archiving article", e)
        logger.info("Article absolute url: %s" % article_url)
        logger.info("Archived url (%s): %s" %  (service_name, archived_url))

    article.save()
    return article.pk

@task(ignore_results=True)
def archive_articles(ids=None, skip_filter=False):
    """
    Archive the given articles by id. If not set, it will filter the articles
    by archive status (based on preservation tags information, see
    `core.managers.ArticleManager`.

    Params:
        - ids, list of articles ids
    """
    from crawler.constants import STATES
    from crawler.core import tasks_utils

    if not ids:
        articles = Articles.objects.all()
    else:
        articles = tasks_utils.articles(ids)

    if not skip_filter:
        articles = articles.should_be_archived()

    articles.update(archiving_state=STATES.ARCHIVE.ARCHIVING)
    return list(map(archive_article, articles))

@task(ignore_results=True)
def check_articles_to_archive():
    from crawler.core import tasks_utils
    articles = Articles.objects.filter_not_needed()

    archive_articles = detect_notfound(
        articles.not_found_only_tagged()
    ).union(
        articles.release_date_tagged()
    ).union(
        articles.priority_tagged()
    )

    archive_articles.apply_async(
        ids=list(set(archive_articles.values_list('pk'))),
        skip_filter=True
    )

