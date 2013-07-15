import re
import unicodedata
from werkzeug.exceptions import NotFound

# utils
def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)


def get_object_or_404(klass, **query):
    instance = klass.query.filter_by(**query).first()
    if not instance:
        raise NotFound()
    return instance


def get_or_create(klass, **kwargs):
    try:
        return get_object_or_404(klass, **kwargs), False
    except NotFound:
        instance = klass(**kwargs)
        instance.save()
        return instance, True
