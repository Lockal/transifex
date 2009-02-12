from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from projects.models import Component
from repowatch import WatchException

# Create your models here.

class WatchManager(models.Manager):
    def add_watch(self, user, component, path=None):
        """
        Adds a file or repo to the watched list

        user: django.contrib.auth.models.User requesting the watch
        component: projects.models.Component to watch
        path: Path for file to watch, or None for a repo change
        """
        watch, found = self.get_or_create(path=path, component=component,
            user=user)
        if not found:
            try:
                rev = component.get_rev(path)
            except ValueError:
                raise WatchException('Unable to add watch for path %r' % 
                    path)
            watch.rev = rev
            watch.save()
        return watch

    def remove_watch(self, user, component, path=None):
        """
        Removes a file or repo from the watched list
        Returns Watch.DoesNotExist if the watch doesn't exist

        user: django.contrib.auth.models.User requesting the watch
        component: projects.models.Component to watch
        path: Path for file to watch, or None for a repo change
        """
        watch = self.get(user=user, component=component, path=path)
        watch.delete()

    def get_watches(self, user, component):
        """
        Gets the current watches on a component by a user

        user: django.contrib.auth.models.User owning the watches
        component: projects.models.Component being watched
        """
        return self.filter(user=user, component=component)

    def update_watch(self, user, component, path=None):
        """
        Updates a watch without notifying the user

        user: django.contrib.auth.models.User owning the watch
        component: projects.models.Component to watch
        path: Path for file to watch, or None for a repo change
        """
        try:
            watch = self.get(user=user, component=component, path=path)
            try:
                rev = component.get_rev(path)
            except ValueError:
                pass
            watch.rev = rev
            watch.save()
        except Watch.DoesNotExist:
            pass

class Watch(models.Model):
    path = models.CharField(max_length=128, null=True, default=None,
        help_text='Path to the file within the repo, or NULL for the '
        'whole repo')
    rev = models.CommaSeparatedIntegerField(max_length=64,
        help_text='Latest revision seen')
    component = models.ForeignKey(Component,
        help_text='Component containing the repo to watch')
    user = models.ManyToManyField(User,
        help_text='User to notify upon detecting a change')
    
    objects = WatchManager()

    def __unicode__(self):
        if self.path is None:
            return u'repo of %s' % (self.component,)
        return u'%s in %s' % (self.path, self.component)

    class Meta:
        verbose_name = _('watch')
        verbose_name_plural = _('watches')
