"""
Test suite for the ``metadata`` package.

TODO: Cache tests

"""

from django.db import models
from django.test import TestCase
from django.utils import timezone

from metadata.mixins import MetadataSubjectMixin
from metadata.models import PackageEntry
from metadata.models import TextMetadata, ImageMetadata


class MetadataSubjectTest(models.Model,
                          MetadataSubjectMixin):
    """
    Test metadata subject model.

    """
    test = models.TextField()

    def packages(self):
        return self.metadatasubjecttestpackageentry_set

    def range_start(self):
        return timezone.now().replace(day=1, month=5, year=2008)

    def metadata_strands(self):
        return {
            'text': self.metadatasubjecttesttextmetadata_set,
            'image': self.testimagemetadata_set,
        }

    class Meta(object):
        app_label = 'metadata'

    @classmethod
    def make_foreign_key(cls, nullable=False):
        return models.ForeignKey(
            cls,
            blank=nullable,
            null=nullable,
        )

MetadataSubjectTestTextMetadata = TextMetadata.make_model(
    MetadataSubjectTest,
    'metadata',
    fkey=MetadataSubjectTest.make_foreign_key(nullable=True)
)

MetadataSubjectTestPackageEntry = PackageEntry.make_model(
    MetadataSubjectTest,
    'metadata',
    fkey=MetadataSubjectTest.make_foreign_key(nullable=True)
)

# See if overriding as much as possible works
TestImageMetadata = ImageMetadata.make_model(
    MetadataSubjectTest,
    'metadata',
    model_name='TestImageMetadata',
    table='frobnik',
    id_column='foobles',
    fkey=MetadataSubjectTest.make_foreign_key(nullable=True),
)


class PackageTest(TestCase):
    """
    Tests to see if the metadata packages system is hooked in
    correctly and used as a fallback metadata source.

    """
    fixtures = ['test_people', 'metadata_test', 'package_test']

    def test_text(self):
        """
        Tests whether the package is used to provide default textual
        metadata.
        """
        subject = MetadataSubjectTest.objects.get(pk=1)

        # This should not be overridden by the package metadata,
        # as it exists in the model's own metadata.
        self.assertEqual(
            subject.metadata['text']['single'],
            'moof!'
        )
        # However, this should be provided by the package.
        self.assertEqual(
            subject.metadata['text']['nothere'],
            'yes it is!'
        )
        # TODO: Possibly unregister hook and try again, to see if
        # this causes the above to fail.


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

    def test_default(self):
        """
        Tests whether default metadata works as expected.

        """
        subject = MetadataSubjectTest.objects.get(pk=1)
        self.assertEqual(
            subject.metadata['text']['defaulttest'],
            'defaultWorks'
        )

        self.assertEqual(
            subject.metadata['image']['defaulttest'],
            'thisShouldAppear'
        )

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
        self.assertFalse('single' in meta_far_past['text'])

        # During the time period of meta_past, only the 'zillyhoo'
        # value of 'single' is active, and thus it isn't overridden
        # by 'moof!', thus this should check out.
        self.assertEqual(
            meta_past['text']['single'],
            'zillyhoo'
        )
        self.assertTrue('single' in meta_past['text'])

        # At 2020, the active value of 'single' should be 'bank' as
        # it is effective later than anything else, but doesn't
        # expire until 2030.
        self.assertEqual(
            meta_future['text']['single'],
            'bank'
        )
        self.assertTrue('single' in meta_future['text'])

        # And in the far future, the latest value of 'single' should
        # be 'wello'; 'bank' has expired.
        self.assertEqual(
            meta_far_future['text']['single'],
            'wello'
        )
        self.assertTrue('single' in meta_far_future['text'])


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
        # relative to range_start.
        self.assertEqual(
            subject.metadata['text']['multiple'],
            {u'elementA', u'elementB'}
        )
        # Should raise KeyError for a nonexistent key...
        with self.assertRaises(KeyError):
            subject.metadata['text']['notakey']
        # ...but should return the empty set for a valid empty key.
        self.assertEqual(
            subject.metadata['text']['notheremul'],
            set()
        )

        # Since text is the default strand for our test model,
        # this shorthand should work:
        self.assertItemsEqual(
            subject.multiple,
            [u'elementB', u'elementA']
        )

    def test_image_get(self):
        """
        Tests whether getting image metadata works.

        """
        subject = MetadataSubjectTest.objects.get(pk=1)
        md = subject.metadata['image']['multiple']

        self.assertIsInstance(md, set)
        self.assertTrue(len(md) == 1)

        self.assertIn(
            u'singleton.jpg',
            subject.metadata['image']['multiple']
        )
        # Should give the empty set for a valid but empty key.
        self.assertEqual(
            subject.metadata['image']['notheremul'],
            set()
        )
