"""
Test suite for the ``metadata`` package.

"""

from django.db import models
from django.test import TestCase

from metadata.mixins import MetadataSubjectMixin
from metadata.models import TextMetadata, ImageMetadata


class MetadataSubjectTest(models.Model,
                          MetadataSubjectMixin):
    test = models.TextField()

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
        self.assertEqual(
            subject.metadata['text']['single'],
            'moof!'
        )
        # Should raise KeyError for a nonexistent key...
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
