"""
Test suite for the ``metadata`` package.

"""

from django.db import models
from django.test import TestCase
from django.utils import timezone

from metadata.mixins import MetadataSubjectMixin
from metadata.models import TextMetadata, ImageMetadata


class MetadataSubjectTest(models.Model,
                          MetadataSubjectMixin):
    """
    Test metadata subject model.

    """
    test = models.TextField()

    def range_start(self):
        return timezone.now().replace(year=2008)

    def metadata_strands(self):
        return {
            'text': self.metadatasubjecttesttextmetadata_set,
            'image': self.testimagemetadata_set,
        }

    class Meta(object):
        app_label = 'metadata'


MetadataSubjectTestTextMetadata = TextMetadata.make_model(
    MetadataSubjectTest,
    'metadata',
)


# See if overriding as much as possible works
TestImageMetadata = ImageMetadata.make_model(
    MetadataSubjectTest,
    'metadata',
    model_name='TestImageMetadata',
    table='frobnik',
    id_column='foobles',
    fkey_column='badnik',
    help_text="It's the best.  Everyone will want it."
)


class SingleMetadataDictTest(TestCase):
    """
    Tests to see if the dictionary access method for metadata is
    functional on single-entry metadata.

    """
    fixtures = ['test_people', 'metadata_test']

    def test_text_in(self):
        """
        Tests whether the metadata view supports 'in'.

        """
        subject = MetadataSubjectTest.objects.get(pk=1)
        self.assertTrue('text' in subject.metadata)
        self.assertTrue('single' in subject.metadata['text'])

    def test_text_get(self):
        """
        Tests whether getting textual metadata works.

        """
        subject = MetadataSubjectTest.objects.get(pk=1)
        # Should return the latest active piece of metadata
        # relative to range_start, i.e. pk 1
        self.assertEqual(
            subject.metadata['text']['single'],
            'moof!'
        )
        # Should raise KeyError for a nonexistent key...
        with self.assertRaises(KeyError):
            subject.metadata['text']['notakey']
        # Should raise KeyError for a nonexistent value...
        with self.assertRaises(KeyError):
            subject.metadata['text']['nothere']

        # Since text is the default strand for our test model,
        # this shorthand should work:
        self.assertEqual(
            subject.single,
            'moof!'
        )

    def test_image_get(self):
        """
        Tests whether getting image metadata works.

        """
        subject = MetadataSubjectTest.objects.get(pk=1)
        self.assertEqual(
            subject.metadata['image']['single'],
            'nothere.png'
        )
        # Should raise KeyError for a nonexistent key...
        with self.assertRaises(KeyError):
            subject.metadata['image']['nothere']

    def test_effective_range(self):
        """
        Tests whether the single metadata getting system correctly
        respects the *effective_from* and *effective_to* bounds.

        """
        subject = MetadataSubjectTest.objects.get(pk=1)
        meta_far_past, meta_past, meta_future, meta_far_future = (
            subject.metadata_at(subject.range_start().replace(year=x))
            for x in (1970, 2006, 2020, 2422)
        )

        # meta_far_past is before any metadatum's effective_from,
        # so attempting to get metadata during it should raise
        # KeyError
        with self.assertRaises(KeyError):
            meta_far_past['text']['single']

        # During the time period of meta_past, only the 'zillyhoo'
        # value of 'single' is active, and thus it isn't overridden
        # by 'moof!', thus this should check out.
        self.assertEqual(
            meta_past['text']['single'],
            'zillyhoo'
        )

        # At 2020, the active value of 'single' should be 'bank' as
        # it is effective later than anything else, but doesn't
        # expire until 2030.
        self.assertEqual(
            meta_future['text']['single'],
            'bank'
        )

        # And in the far future, the latest value of 'single' should
        # be 'wello'; 'bank' has expired.
        self.assertEqual(
            meta_far_future['text']['single'],
            'wello'
        )


class MultipleMetadataDictTest(TestCase):
    """
    Tests to see if the dictionary access method for metadata is
    functional on multiple-entry metadata.

    """
    fixtures = ['test_people', 'metadata_test']

    def test_text_in(self):
        """
        Tests whether the metadata view supports 'in'.

        """
        subject = MetadataSubjectTest.objects.get(pk=1)
        self.assertTrue('text' in subject.metadata)
        self.assertTrue('multiple' in subject.metadata['text'])

    def test_text_get(self):
        """
        Tests whether getting textual metadata works.

        """
        subject = MetadataSubjectTest.objects.get(pk=1)
        # Should return all active metadata at the
        # relative to range_start, in newest-first order.
        # This means that elementB comes before elementA,
        # as its effective_from is later!
        self.assertEqual(
            subject.metadata['text']['multiple'],
            [u'elementB', u'elementA']
        )
        # Should raise KeyError for a nonexistent key...
        with self.assertRaises(KeyError):
            subject.metadata['text']['notakey']
        # ...but should return the empty list for a valid empty key.
        self.assertEqual(
            subject.metadata['text']['notheremul'],
            []
        )

        # Since text is the default strand for our test model,
        # this shorthand should work:
        self.assertEqual(
            subject.multiple,
            [u'elementB', u'elementA']
        )

    def test_image_get(self):
        """
        Tests whether getting image metadata works.

        """
        subject = MetadataSubjectTest.objects.get(pk=1)
        md = subject.metadata['image']['multiple']

        self.assertIsInstance(md, list)
        self.assertTrue(len(md) == 1)

        self.assertIn(
            u'singleton.jpg',
            subject.metadata['image']['multiple']
        )
        # Should raise KeyError for a nonexistent key...
        self.assertEqual(
            subject.metadata['image']['notheremul'],
            []
        )
