from django.core.urlresolvers import reverse
from django.db.models.loading import get_model
from django.utils import simplejson
from txcommon.tests.base import BaseTestCase


Translation = get_model('resources', 'Translation')

class LotteViewsTests(BaseTestCase):

    DataTable_params = { 'bEscapeRegex':True, 'bEscapeRegex_0':True, 
        'bEscapeRegex_1':True, 'bEscapeRegex_2':True, 'bEscapeRegex_3':True,
        'bEscapeRegex_4':True, 'bEscapeRegex_5':True, 'bSearchable_0':True,
        'bSearchable_1':True, 'bSearchable_2':True, 'bSearchable_3':True,
        'bSearchable_4':True, 'bSearchable_5':True, 'bSortable_0':True,
        'bSortable_1':False, 'bSortable_2':True, 'bSortable_3':False,
        'bSortable_4':False, 'bSortable_5':False, 'iColumns':6, 
        'iDisplayLength':10, 'iDisplayStart':0, 'iSortCol_0':0, 'iSortingCols':1,
        'sSortDir_0':'asc'}

    def setUp(self):
        super(LotteViewsTests, self).setUp()
        self.entity = self.resource.entities[0]

        # Set some custom translation data
        # Source strings
        self.source_string_plural1 = self.source_entity_plural.translations.create(resource=self.resource,
            string="SourceArabicTrans1", language=self.language_en,
            user=self.user["maintainer"], rule=1)
        self.source_string_plural2 = self.source_entity_plural.translations.create(resource=self.resource,
            string="SourceArabicTrans2", language=self.language_en,
            user=self.user["maintainer"], rule=5)
        # Translation strings
        self.source_entity_plural.translations.create(resource=self.resource,
            string="ArabicTrans0", language=self.language_ar,
            user=self.user["maintainer"], rule=0)
        self.source_entity_plural.translations.create(resource=self.resource,
            string="ArabicTrans1", language=self.language_ar,
            user=self.user["maintainer"], rule=1)
        self.source_entity_plural.translations.create(resource=self.resource,
            string="ArabicTrans2", language=self.language_ar,
            user=self.user["maintainer"], rule=2)
        self.source_entity_plural.translations.create(resource=self.resource,
            string="ArabicTrans3", language=self.language_ar,
            user=self.user["maintainer"], rule=3)
        self.source_entity_plural.translations.create(resource=self.resource,
            string="ArabicTrans4", language=self.language_ar,
            user=self.user["maintainer"], rule=4)
        self.source_entity_plural.translations.create(resource=self.resource,
            string="ArabicTrans5", language=self.language_ar,
            user=self.user["maintainer"], rule=5)

        # URLs
        self.snippet_url = reverse('translation_details_snippet',
            args=[self.entity.id, self.language.code])
        self.translate_view_url = reverse('translate_resource',
            args=[self.project.slug, self.resource.slug, self.language.code])
        self.translate_content_arabic_url = reverse('stringset_handling',
            args=[self.project.slug, self.resource.slug, self.language_ar.code])
        self.push_translation = reverse('push_translation',
            args=[self.project.slug, self.language_ar.code])


    def tearDown(self):
        super(LotteViewsTests, self).tearDown()
        self.source_entity_plural.translations.all().delete()

    def test_snippet_entities_data(self):
        """Test the entity details part of the snippet is correct."""
        # Create custom fields in entity
        self.entity.string = "Key1"
        self.entity.context = "Description1"
        self.entity.occurrences = "Occurrences1"
        self.entity.save()
        # Test the response contents
        resp = self.client['team_member'].get(self.snippet_url)
        self.assertContains(resp, self.entity.string, status_code=200)
        self.assertContains(resp, self.entity.context)
        self.assertContains(resp, self.entity.occurrences)
        self.assertTemplateUsed(resp, 'lotte_details_snippet.html')


    def test_snippet_translation_data(self):
        """Test the translation details part of the snippet is correct."""
        # Set some custom data
        self.entity.translations.create(resource=self.resource, string="StringTrans1",
            language=self.language, user=self.user["team_member"])
        # Test the response contents
        resp = self.client['team_member'].get(self.snippet_url)
        self.assertContains(resp, '0 minutes', status_code=200)
#        self.assertContains(resp, 'alt="team_member"')


    def test_translate_view(self):
        """Test the basic response of the main view for lotte."""
        # Check page status
        resp = self.client['maintainer'].get(self.translate_view_url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'translate.html')

    def test_plural_data(self):
        """Test that all plural fields are sent."""

        self.assertEqual(Translation.objects.filter(
            source_entity=self.source_entity_plural,
            language=self.language_en).count(), 2)

        self.assertEqual(Translation.objects.filter(
            source_entity=self.source_entity_plural,
            language=self.language_ar).count(), 6)

        resp = self.client['maintainer'].post(
            self.translate_content_arabic_url, self.DataTable_params)
        self.assertContains(resp, 'ArabicTrans1', status_code=200)
        self.assertContains(resp, 'ArabicTrans2')
        self.assertContains(resp, 'ArabicTrans3')
        self.assertContains(resp, 'ArabicTrans4')

    def test_push_plural_translation(self):
        """Test pushing pluralized translations."""
        data1 = {"strings":[{"id":self.source_string_plural1.id,
                            "translations":{
                                "zero":"Arabic string zero",
                                "one":"Arabic string one",
                                "few":"Arabic string few",
                                "other":"Arabic string other",}
                           },]
               }
        data2 = {"strings":[{"id":self.source_string_plural1.id,
                            "translations":{
                                "zero":"Arabic string zero",
                                "one":"Arabic string one",
                                "two":"Arabic string two",
                                "few":"Arabic string few",
                                "many":"Arabic string many",}
                           },]
               }
        data3 = {"strings":[{"id":self.source_string_plural1.id,
                            "translations":{
                                "zero":"Arabic string zero",
                                "one":"Arabic string one",
                                "two":"Arabic string two",
                                "few":"Arabic string few",
                                "many":"Arabic string many",
                                "other":"Arabic string other",}
                           },]
               }
        data4 = {"strings":[{"id":self.source_string_plural1.id,
                            "translations":{
                                "zero":"",
                                "one":"",
                                "two":"",
                                "few":"",
                                "many":"",
                                "other":"",}
                           },]
               }
        resp1 = self.client['maintainer'].post(self.push_translation, simplejson.dumps(data1), content_type='application/json')
        self.assertContains(resp1, 'All the plural translations must be filled in', status_code=200)

        resp2 = self.client['maintainer'].post(self.push_translation, simplejson.dumps(data2), content_type='application/json')
        self.assertContains(resp2, 'All the plural translations must be filled in', status_code=200)

        resp3 = self.client['maintainer'].post(self.push_translation, simplejson.dumps(data3), content_type='application/json')
        self.assertContains(resp3, 'Translation updated successfully', status_code=200)

        self.assertEqual(Translation.objects.filter(
            source_entity=self.source_entity_plural,
            language=self.language_ar).count(), 6)

        resp4 = self.client['maintainer'].post(self.push_translation, simplejson.dumps(data4), content_type='application/json')
        self.assertContains(resp4, 'Translation updated successfully', status_code=200)

        self.assertEqual(Translation.objects.filter(
            source_entity=self.source_entity_plural,
            language=self.language_ar).count(), 0)