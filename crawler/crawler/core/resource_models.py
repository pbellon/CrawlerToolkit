""" KEEPING FOR MIGRATION PURPOSE, DO NOT USE """
from uuid import uuid4

def resource_path(instance, filename):
    article = instance.article
    feed = article.feed
    folders = [ feed.slug, article.slug ]

    if instance.use_resource_type_dir:
        folders.append(
            '{}s'.format(getattr(instance._meta, 'resource_type'))
        )

    if instance.use_unique_name:
        ext = filename.split('.')[-1]
        fid = str(uuid4())
        filename = "{}.{}".format(fid, ext)

    return "{path}/{fn}".format(
        path='/'.join(folders),
        fn=filename
    )
