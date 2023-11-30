import os

try:
    # python2.6
    import unittest2 as unittest
except ImportError:
    import unittest

import polib

from autotranslate.management.commands.translate_messages import convert_text, restore_text, Command


class ConvertTestCase(unittest.TestCase):
    def test_named_placeholders(self):
        self.assertEqual('foo <span translate="no">%(item)s</span> bar', convert_text('foo %(item)s bar'))
        self.assertEqual('foo <span translate="no">%(item_name)s</span> bar', convert_text('foo %(item_name)s bar'))

        self.assertEqual('foo % (item)s bar', convert_text('foo % (item)s bar'))

    def test_positional_placeholders(self):
        self.assertEqual('foo <span translate="no">%s</span> bar',
                         convert_text('foo %s bar'))
        self.assertEqual('foo <span translate="no">%d</span> bar',
                         convert_text('foo %d bar'))
        self.assertEqual('foo <span translate="no">%s</span> bar <span translate="no">%s</span>',
                         convert_text('foo %s bar %s'))
        self.assertEqual('foo <span translate="no">%s</span><span translate="no">%s</span>',
                         convert_text('foo %s%s'))

    def test_newline(self):
        self.assertEqual('foo<br translate="no">bar',
                         convert_text('foo\nbar'))
        self.assertEqual('foo<br translate="no"><br translate="no">bar',
                         convert_text('foo\n\nbar'))
        self.assertEqual('foo<br translate="no"><br>bar',
                         convert_text('foo\n<br>bar'))


class RestoreTestCase(unittest.TestCase):
    def test_restore_placeholders(self):
        # should not be translated to over
        # self.assertEqual('baz %(item)s zilot',
        #                  restore_text('baz <span translate="no">over</span> zilot'))
        self.assertEqual('baz %(item_name)s zilot',
                         restore_text('baz <span translate="no">%(item_name)s</span> zilot'))
        self.assertEqual('baz %s zilot',
                         restore_text('baz <span translate="no">%s</span> zilot'))
        self.assertEqual('baz %s%s zilot',
                         restore_text('baz <span translate="no">%s</span><span translate="no">%s</span> zilot'))


class POFileTestCase(unittest.TestCase):
    def setUp(self):
        cmd = Command()
        cmd.set_options(**dict(
                locale='ia',
                set_fuzzy=False,
                skip_translated=False,
                source_language='en',
        ))
        self.cmd = cmd
        self.po = polib.pofile(os.path.join(os.path.dirname(__file__), 'data/django.po'))

    def test_should_read_single(self):
        strings = self.cmd.get_strings_to_translate(self.po)
        self.assertIn('Location', strings)

    def test_should_update_single(self):
        translations = ['XXXX']
        entry = self.po[0]
        self.cmd.update_translations([entry], translations)
        self.assertEqual('XXXX', entry.msgstr)
        self.assertTrue(entry.translated())

    def test_should_read_plural(self):
        strings = self.cmd.get_strings_to_translate(self.po)
        self.assertIn('City', strings)
        self.assertIn('Cities', strings)

    def test_should_update_plural(self):
        translations = ['SINGULAR', 'PLURAL']
        entry = self.po[1]
        self.cmd.update_translations([entry], translations)
        self.assertEqual('', entry.msgstr)
        self.assertEqual('SINGULAR', entry.msgstr_plural[0])
        self.assertEqual(['PLURAL'] * (len(entry.msgstr_plural) - 1),
                         [v for k, v in entry.msgstr_plural.items() if k != 0])
        self.assertTrue(entry.translated())
