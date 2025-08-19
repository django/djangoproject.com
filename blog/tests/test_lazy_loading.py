from django.test import SimpleTestCase
from blog.templatetags.blog_extras import add_lazy_loading

class AddLazyLoadingFilterTests(SimpleTestCase):
    def test_adds_attributes_to_img_without_them(self):
        html = '<p>Example <img src="example.jpg"></p>'
        result = add_lazy_loading(html)
        self.assertIn('loading="lazy"', result)
        self.assertIn('decoding="async"', result)

    def test_does_not_override_existing_attributes(self):
        html = '<p><img src="test.jpg" loading="eager" decoding="sync"></p>'
        result = add_lazy_loading(html)
        self.assertIn('loading="eager"', result)
        self.assertIn('decoding="sync"', result)

    def test_handles_multiple_images(self):
        html = '<img src="a.jpg"><img src="b.jpg">'
        result = add_lazy_loading(html)
        self.assertEqual(result.count('loading="lazy"'), 2)
        self.assertEqual(result.count('decoding="async"'), 2)

    def test_non_image_tags_are_untouched(self):
        html = '<p>No images here</p>'
        result = add_lazy_loading(html)
        self.assertEqual(result, html)
