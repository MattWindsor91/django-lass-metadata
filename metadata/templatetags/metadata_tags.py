"""
Various template tags for metadata.

"""
from django import template


register = template.Library()


@register.inclusion_tag('metadata/image-text.html')
def image_text(element, key):
    """
    Checks ``element`` for the metadata key ``key`` in both its image
    and text strands, and renders the image if it exists or the text
    if it does not.

    """
    return {
        'image': getattr(element.image[key], None),
        'text': element.text[key]
    }
