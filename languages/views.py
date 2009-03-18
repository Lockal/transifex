import os
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import list_detail
from django.utils.translation import ugettext_lazy as _
from django.contrib.syndication.views import feed
from django.template import RequestContext

from translations.models import POFile
from models import Language
from txcollections.models import (Collection, CollectionRelease as Release)

def slug_feed(request, slug=None, param='', feed_dict=None):
    """
    Override default feed, using custom (including inexistent) slug.
    
    Provides the functionality needed to decouple the Feed's slug from
    the urlconf, so a feed mounted at "^/feed" can exist.
    
    See also http://code.djangoproject.com/ticket/6969.
    """
    if slug:
        url = "%s/%s" % (slug, param)
    else:
        url = param
    return feed(request, url, feed_dict)


def language_release_feed(request,
                          language_slug, collection_slug, release_slug,
                          slug=None, param='', feed_dict=None,):
    param = '%s/%s/%s' % (language_slug, collection_slug, release_slug)
    if slug:
        url = "%s/%s" % (slug, param)
    else:
        url = param
    return feed(request, url, feed_dict)


def language_detail(request, slug, *args, **kwargs):
    language = get_object_or_404(Language, code__iexact=slug)
    pofile_list = POFile.objects.by_language(language)
    return list_detail.object_detail(
        request,
        object_id=language.id,
        extra_context = {'pofile_list': pofile_list,
                         'collection_list': Collection.objects.all()},
        *args, **kwargs
    )


def language_release(request, slug, collection_slug, release_slug):

    language = get_object_or_404(Language, code__iexact=slug)
    collection = get_object_or_404(Collection, 
                                   slug__exact=collection_slug)
    release = get_object_or_404(Release, slug__exact=release_slug,
                                collection=collection)

    pofile_list = POFile.objects.by_language_and_release(language, 
                                                         release)

    return render_to_response('languages/language_release.html', {
        'pofile_list': pofile_list,
        'release': release,
        'language': language,
    }, context_instance=RequestContext(request))

