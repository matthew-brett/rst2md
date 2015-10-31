# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test writer conversions

Test running writer over example files and chosen snippets
"""
from __future__ import division, print_function, absolute_import

from os.path import (dirname, join as pjoin, abspath)
from glob import glob
import difflib

from docutils.core import publish_string
from docutils.writers.pseudoxml import Writer as PXMLWriter

from ..markdown import Writer

from nose.tools import (assert_true, assert_false, assert_not_equal,
                        assert_equal)

DATA_PATH = abspath(pjoin(dirname(__file__), 'rst_md_files'))

def _fcontents(fname):
    with open(fname, 'rb') as fobj:
        contents = fobj.read()
    return contents


def _diff_strs(first, second):
    # Replicate some of the standard string comparison error message.
    # This is from unittest.TestCase.assertMultiLineEqual
    firstlines = first.splitlines(True)
    secondlines = second.splitlines(True)
    if len(firstlines) == 1 and first.strip('\r\n') == first:
        firstlines = [first + '\n']
        secondlines = [second + '\n']
    return ''.join(difflib.ndiff(firstlines, secondlines))


def assert_conv_equal(rst_str, md_expected):
    md_actual = publish_string(rst_str, writer=Writer())
    if (md_actual == md_expected):
        assert_equal(md_actual, md_expected)
        return
    # Make some useful debugging output
    msg = 'actual, expected not equal:\n' + _diff_strs(md_actual, md_expected)
    pxml = publish_string(rst_str, writer=PXMLWriter())
    msg += '\nwith doctree\n' + pxml
    assert_equal(md_actual, md_expected, msg=msg)


def test_example_files():
    # test rst2md script over all .rst files checking against .md files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        rst_contents = _fcontents(rst_fname)
        md_fname = rst_fname[:-3] + 'md'
        md_contents = _fcontents(md_fname)
        assert_conv_equal(rst_contents, md_contents)


def test_snippets():
    assert_conv_equal("Some text", "\nSome text\n")
    assert_conv_equal("With *emphasis*", "\nWith *emphasis*\n")
    assert_conv_equal("That's **strong**", "\nThat's **strong**\n")
