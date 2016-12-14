#!/usr/bin/env python
import sys
import unittest

from deploy import generate_versioned_tags, main, split_image_tag


class TestMain(unittest.TestCase):
    def test_main(self):
        main(['python:2.7', '2.7.12', '--dry-run'])
        # NOTE: This requires Python 2.7+ and that the tests are run in
        # buffered mode.
        output = sys.stdout.getvalue().strip().split('\n')
        self.assertEqual(output, [
            'docker tag python:2.7 python:2.7.12',
            'docker tag python:2.7 python:2.7',
            'docker tag python:2.7 python:2',
            'docker push python:2.7.12',
            'docker push python:2.7',
            'docker push python:2',
        ])


class TestSplitImageTag(unittest.TestCase):
    def test_image_tag(self):
        image, tag = split_image_tag('foo:bar')
        self.assertEqual(image, 'foo')
        self.assertEqual(tag, 'bar')

    def test_image(self):
        image, tag = split_image_tag('foo')
        self.assertEqual(image, 'foo')
        self.assertIsNone(tag)


class TestGenerateVersionTag(unittest.TestCase):
    def test_name_tag(self):
        versioned_tags = generate_versioned_tags('foo', '5.4.1')
        self.assertEqual(versioned_tags, ['5.4.1-foo', '5.4-foo', '5-foo'])

    def test_version_and_name_tag(self):
        versioned_tags = generate_versioned_tags('5.4-foo', '5.4.1')
        self.assertEqual(versioned_tags, ['5.4.1-foo', '5.4-foo', '5-foo'])

    def test_other_version_tag(self):
        versioned_tags = generate_versioned_tags('2.7-foo', '5.4.1')
        self.assertEqual(versioned_tags,
                         ['5.4.1-2.7-foo', '5.4-2.7-foo', '5-2.7-foo'])

    def test_version_tag(self):
        versioned_tags = generate_versioned_tags('5.4', '5.4.1')
        self.assertEqual(versioned_tags, ['5.4.1', '5.4', '5'])

    def test_none_tag(self):
        versioned_tags = generate_versioned_tags(None, '5.4.1')
        self.assertEqual(versioned_tags, ['5.4.1', '5.4', '5'])

    def test_no_version_zero(self):
        versioned_tags = generate_versioned_tags('foo', '0.4.1')
        self.assertEqual(versioned_tags, ['0.4.1-foo', '0.4-foo'])

    def test_latest(self):
        versioned_tags = generate_versioned_tags('foo', '5.4.1', latest=True)
        self.assertEqual(versioned_tags,
                         ['5.4.1-foo', '5.4-foo', '5-foo', 'foo'])

    def test_latest_no_tag(self):
        versioned_tags = generate_versioned_tags(None, '5.4.1', latest=True)
        self.assertEqual(versioned_tags, ['5.4.1', '5.4', '5', 'latest'])

    def test_latest_version_tag(self):
        versioned_tags = generate_versioned_tags('5.4', '5.4.1', latest=True)
        self.assertEqual(versioned_tags, ['5.4.1', '5.4', '5', 'latest'])


if __name__ == '__main__':
    unittest.main(buffer=True)
