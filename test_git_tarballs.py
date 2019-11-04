# Copyright 2012 SUSE Linux
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import contextlib
import imp
import io
import unittest

import mock

ghb = imp.load_source('ghb', 'git_tarballs')


CHANGELOG = (
    'commit 921b7c514fb79bd4b8a023f34d22df4efe5406ad\n'
    'Merge: 9ae14c7 518bdb5\n'
    'Author: Jenkins <jenkins@review.openstack.org>\n'
    'Date:   Thu Jan 17 12:14:24 2013 +0000\n'
    '\n'
    '    Merge "Expose a get_spice_console RPC API method"\n'
    '\n'
    'commit 9ae14c7570bb9dfc4bf1ab8f8127cae3c9eb2641\n'
    'Merge: b76c5cf d597993\n'
    'Author: Jenkins <jenkins@review.openstack.org>\n'
    'Date:   Thu Jan 17 11:59:39 2013 +0000\n'
    '\n'
    '    Merge "Add a get_spice_console method to nova.virt API"\n'
    '\n'
    'commit eab051ec68bdc8792dddb63c9231ece11ab06037\n'
    'Author: Foo Barwington <barwing@ton.com>\n'
    'Date:   Thu Jan 3 10:23:50 2013 +0000\n'
    '\n'
    '    Add nova-spicehtml5proxy helper\n'
    '    \n'
    '    Add nova-spicehtml5proxy which provides a websockets proxy,\n'
    '    equivalent to nova-novncproxy\n'
    '    \n'
    '    Blueprint: libvirt-spice\n'
    '    Change-Id: I48be78c97bb7dd6635fd4bba476ef22701418ba1\n'
    '    Signed-off-by: Foo Barwington <barwing@ton.com>\n'
    '\n'
    ' bin/nova-spicehtml5proxy                |   93 +++++++++++++++++++++++\n'
    ' doc/source/conf.py                      |    2 +\n'
    ' doc/source/man/nova-spicehtml5proxy.rst |   48 ++++++++++++++++\n'
    ' setup.py                                |    1 +\n'
    ' 4 files changed, 144 insertions(+)\n'
    '\n'
    'commit bd8399bd2f51f1dcaa5194cb035415c634383917\n'
    'Merge: 2cdc27b e71e8c2\n'
    'Author: Jenkins <jenkins@review.openstack.org>\n'
    'Date:   Thu Jan 17 11:59:12 2013 +0000\n'
    '\n'
    '    Merge "Pull NovaWebSocketProxy class out of nova-novncproxy binary"'
    '\n')


class TestGitTarballs(unittest.TestCase):
    def test_version_parse(self):
        with mock_open(u"\nVersion: 2012.2.3+git.1355917214.0c8c2a3\n"):
            self.assertEqual('0c8c2a3',
                             ghb.get_commit_from_spec('example_pkg'))

    def test_version_parse_comment(self):
        with mock_open(
                u"\nVersion: 2012.2.3+git.1355917214.0c8c2a3 # oi comment\n"):
            self.assertEqual('0c8c2a3',
                             ghb.get_commit_from_spec('example_pkg'))

    def test_version_parse_plain(self):
        with mock_open(u"\n%setup -q -n nova-2013.1.a110.g975c5ac\n"):
            self.assertEqual('975c5ac',
                             ghb.get_commit_from_spec('example_pkg',
                                                      plain_version=True))

    def test_version_parse_plain_from_custom(self):
        with mock_open(
                u"\n%setup -q -n "
                "nova-2013.1.a110.g975c5ac+git.1363479139.975c5ac\n"):
            self.assertEqual('975c5ac',
                             ghb.get_commit_from_spec('example_pkg',
                                                      plain_version=True))

    def test_parent_dir(self):
        self.assertEqual("keystone-2013.2.b1.140.g636",
                         ghb.get_parent_dir("fixtures/tarball.tar.gz"))

    def test_parse_version_from_parent_dir(self):
        self.assertEqual(
            "2013",
            ghb.parse_version_from_parent_dir("keystone-2013.2.b1.140.g636",
                                              r"\w+\-(\d+)"))

    def test_parse_version_from_parent_dir_error(self):
        self.assertRaises(SystemExit,
                          ghb.parse_version_from_parent_dir, "", r"\w+")

    def test_get_upstream_commit(self):
        self.assertEqual('921b7c514fb79bd4b8a023f34d22df4efe5406ad',
                         ghb.get_upstream_commit(CHANGELOG))

    def test_parse_changelog(self):
        self.assertEqual(
            [('921b7c514fb79bd4b8a023f34d22df4efe5406ad',
              '518bdb5',
              'Jenkins <jenkins@review.openstack.org>',
              'Thu Jan 17 12:14:24 2013 +0000',
              'Merge "Expose a get_spice_console RPC API method"'),
             ('9ae14c7570bb9dfc4bf1ab8f8127cae3c9eb2641',
              'd597993',
              'Jenkins <jenkins@review.openstack.org>',
              'Thu Jan 17 11:59:39 2013 +0000',
              'Merge "Add a get_spice_console method to nova.virt API"'),
             ('eab051ec68bdc8792dddb63c9231ece11ab06037',
              None,
              'Foo Barwington <barwing@ton.com>',
              'Thu Jan 3 10:23:50 2013 +0000',
              'Add nova-spicehtml5proxy helper'),
             ('bd8399bd2f51f1dcaa5194cb035415c634383917',
              'e71e8c2',
              'Jenkins <jenkins@review.openstack.org>',
              'Thu Jan 17 11:59:12 2013 +0000',
              'Merge "Pull NovaWebSocketProxy class out of '
              'nova-novncproxy binary"')],
            [c.groups() for c in ghb.parse_changelog(CHANGELOG)])

    def test_parse_changelog_empty(self):
        self.assertEqual([],
                         list(ghb.parse_changelog("bogus")))


class TestGitParseUpdateSpec(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(
            "\nVersion: 14.0\n%setup -n bar\nSource: bar-14.0.tar.gz\n",
            ghb.parse_update_spec_file(
                "\nVersion: 13.14\n%setup -n foo\nSource: foo-13.14.tar.gz\n",
                "14.0", "bar", "bar-14.0.tar.gz"))

    def test_no_update(self):
        self.assertEqual(
            "\nVersion: 13.14\n%setup -n bar\nSource: bar-14.0.tar.gz\n",
            ghb.parse_update_spec_file(
                "\nVersion: 13.14\n%setup -n foo\nSource: foo-13.14.tar.gz\n",
                None, "bar", "bar-14.0.tar.gz"))

    def test_source_zero(self):
        self.assertEqual(
            "\nVersion: 14.0\n%setup -n bar\nSource: bar-14.0.tar.gz\n",
            ghb.parse_update_spec_file(
                "\nVersion: 13.14\n%setup -n foo\nSource: foo-13.14.tar.gz\n",
                "14.0", "bar", "bar-14.0.tar.gz"))

    def test_tabs(self):
        self.assertEqual(
            "\nVersion:\t14.0\n%setup\t-n bar\nSource:\tbar-14.0.tar.gz\n",
            ghb.parse_update_spec_file(
                "\nVersion:\t13.14\n%setup\t-n foo\n"
                "Source:\tfoo-13.14.tar.gz\n",
                "14.0", "bar", "bar-14.0.tar.gz"))

    def test_other_options_in_setup(self):
        self.assertEqual(
            "\nVersion:\t14.0\n"
            "%setup -q -a0 -n bar -f 33\nSource:\tbar-14.0.tar.gz\n",
            ghb.parse_update_spec_file(
                "\nVersion:\t13.14\n"
                "%setup -q -a0 -n foo -f 33\nSource:\tfoo-13.14.tar.gz\n",
                "14.0", "bar", "bar-14.0.tar.gz"))

    def test_no_n_option_in_setup(self):
        self.assertEqual(
            "\nVersion: 14.0\n%setup -q\nSource: bar-14.0.tar.gz\n",
            ghb.parse_update_spec_file(
                "\nVersion: 13.14\n%setup -q\nSource: foo-13.14.tar.gz\n",
                "14.0", "bar", "bar-14.0.tar.gz"))


@contextlib.contextmanager
def mock_open(contents):
    with mock.patch("__builtin__.open", return_value=io.StringIO(contents)):
        yield
