#    Copyright (C) ConSol Software & Solutions GmbH
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from monplugin import Threshold, Range, Status, PerformanceLabel, Check, MonShortnameDeprecated
import unittest
import re


class TestRange(unittest.TestCase):
    def test_non_str(self):
        try:
            r = Range(5)
            str(r)
        except:
            self.fail("Range(int) throwed exception")

    def test_num(self):
        r = Range('5')
        self.assertTrue(isinstance(r, Range))
        self.assertEqual(r.start, 0)
        self.assertEqual(r.end, 5)
        self.assertTrue(r.outside)

        self.assertTrue(r.check(-1))
        self.assertFalse(r.check(0))
        self.assertFalse(r.check(2))
        self.assertFalse(r.check(5))
        self.assertTrue(r.check(5.1))

    def test_no_end(self):
        r = Range('5.0:')
        self.assertTrue(isinstance(r, Range))
        self.assertEqual(r.start, 5)
        self.assertEqual(r.end, float('inf'))
        self.assertTrue(r.outside)

        self.assertTrue(r.check(4))
        self.assertFalse(r.check(5))
        self.assertFalse(r.check(6))

    def test_no_start(self):
        r = Range('~:5.0')
        self.assertTrue(isinstance(r, Range))
        self.assertEqual(r.start, float('-inf'))
        self.assertEqual(r.end, 5)
        self.assertTrue(r.outside)

        self.assertFalse(r.check(4))
        self.assertFalse(r.check(5))
        self.assertTrue(r.check(6))

    def test_inside(self):
        r = Range('@2:4.0')
        self.assertTrue(isinstance(r, Range))
        self.assertEqual(r.start, float('2'))
        self.assertEqual(r.end, float('4'))
        self.assertFalse(r.outside)

        self.assertFalse(r.check(1.99))
        self.assertTrue(r.check(2))
        self.assertTrue(r.check(3.5))
        self.assertTrue(r.check(4))
        self.assertFalse(r.check(4.1))

    def test_invalid(self):
        with self.assertRaises(Exception):
            Range('a')
        with self.assertRaises(Exception):
            Range('a:b')
        with self.assertRaises(Exception):
            Range('~:b')
        with self.assertRaises(Exception):
            Range(':1')
        with self.assertRaises(Exception):
            Range('1:~')
        with self.assertRaises(Exception):
            Range('1,1:1,2')

class TestThreshold(unittest.TestCase):
    def test_a(self):
        t = Threshold(warning="5:9")
        self.assertEqual(t.get_status(4), Status.WARNING)
        self.assertEqual(t.get_status(10), Status.WARNING)
        self.assertEqual(t.get_status(6), Status.OK)
        t = Threshold(critical="5:9")
        self.assertEqual(t.get_status(4), Status.CRITICAL)
        self.assertEqual(t.get_status(10), Status.CRITICAL)
        self.assertEqual(t.get_status(6), Status.OK)
        t = Threshold(critical="0:90", warning="0:80")
        self.assertEqual(t.get_status(91), Status.CRITICAL)
        self.assertEqual(t.get_status(-1), Status.CRITICAL)
        self.assertEqual(t.get_status(10), Status.OK)
        self.assertEqual(t.get_status(90), Status.WARNING)
        self.assertEqual(t.get_status(85), Status.WARNING)
        self.assertEqual(t.get_status(95), Status.CRITICAL)
        t = Threshold(critical="@5:9", warning="@20:25")
        self.assertEqual(t.get_status(5), Status.CRITICAL)
        self.assertEqual(t.get_status(9), Status.CRITICAL)
        self.assertEqual(t.get_status(4), Status.OK)
        self.assertEqual(t.get_status(10), Status.OK)
        self.assertEqual(t.get_status(20), Status.WARNING)
        self.assertEqual(t.get_status(22), Status.WARNING)
        self.assertEqual(t.get_status(25), Status.WARNING)
        self.assertEqual(t.get_status(25.1), Status.OK)
        self.assertEqual(t.get_status(19.9), Status.OK)
        self.assertEqual(t.get_status(4,10,5), Status.CRITICAL)
        t = Threshold()
        self.assertEqual(t.get_status(42), Status.OK)

class TestPerfromanceLabel(unittest.TestCase):
    def test_a(self):
        p = PerformanceLabel(
            label = 'a b',
            value = 9.0,
            uom = 'kB',
            warning = '15',
            critical = '90:',
            min=0,
            max=100,
        )
        self.assertEqual(str(p), "'a b'=9.0kB;15;90:;0;100")
        p = PerformanceLabel(
            label = 'a b',
            value = 9.0,
            uom = 'kB',
        )
        self.assertEqual(str(p), "'a b'=9.0kB;;;;")
        p = PerformanceLabel(
            label = 'a\nb',
            value = 9.0,
            uom = 'kB',
            threshold=Threshold(warning='15', critical='90:')
        )
        self.assertEqual(str(p), "'a b'=9.0kB;15;90:;;")

class TestCheck(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(TypeError):
            Check('x')
        with self.assertWarns(MonShortnameDeprecated):
            Check(shortname="foo")
        Check(threshold=None)

    def test_perfmulti(self):
        c = Check()
        c.add_message('OK')
        c.add_perfmultidata('disk1', None, label='used', value='90')
        c.add_perfmultidata('disk1', None, label='free', value='10')
        c.add_perfmultidata('disk2', None, label='free', value='5')
        c.add_perfmultidata('disk2', None, label='used', value='95')

        rmtime = lambda x: re.sub(r"'monplugin::monplugin::time[^ ]* ", "", x)

        self.assertEqual(
            rmtime(c.get_perfdata()),
                "| 'disk1::unknown::free'=10.0;;;; 'used'=90.0;;;;\n"
                "'disk2::unknown::free'=5.0;;;; 'used'=95.0;;;;\n"
        )

        c = Check()
        c.add_message('OK')
        c.add_perfmultidata('disk1', None, label='used', value='90')
        c.add_perfmultidata('disk1', None, label='free', value='10')
        self.assertEqual(
            rmtime(c.get_perfdata()),
                "| 'disk1::unknown::free'=10.0;;;; 'used'=90.0;;;;\n"
        )

        c = Check()
        c.add_message('OK')
        c.add_perfmultidata('disk1', "a", label='used', value='90')
        c.add_perfmultidata('disk1', "a", label='free', value='10')
        self.assertEqual(
            rmtime(c.get_perfdata()),
                "| 'disk1::a::free'=10.0;;;; 'used'=90.0;;;;\n"
        )

        c = Check()
        c.add_message('OK')
        c.add_perfdata(label='used', value=90)
        self.assertEqual(
            re.sub("\n'monplugin_time.*\n", "", c.get_perfdata()),
            "| 'used'=90.0;;;;"
        )

    def test_message(self):
        c = Check()

        (code, message) = c.check_messages()
        self.assertEqual(code, Status.OK)
        self.assertEqual(message, '')

        (code, message) = c.check_messages(separator_all='; ', allok="ALLOK")
        self.assertEqual(code, Status.OK)
        self.assertEqual(message, 'ALLOK')

        c.add_message(Status.OK, 'ok')
        (code, message) = c.check_messages()
        self.assertEqual(code, Status.OK)
        self.assertEqual(message, 'ok')

        (code, message) = c.check_messages(separator_all='; ', allok="ALLOK")
        self.assertEqual(code, Status.OK)
        self.assertEqual(message, 'ALLOK')

        c.add_message(Status.WARNING, 'warning')
        (code, message) = c.check_messages()
        self.assertEqual(code, Status.WARNING)
        self.assertEqual(message, 'warning')

        c.add_message(Status.CRITICAL, 'critical')
        c.add_message(Status.CRITICAL, 'critical2')
        (code, message) = c.check_messages()
        self.assertEqual(code, Status.CRITICAL)
        self.assertEqual(message, 'critical critical2')

        (code, message) = c.check_messages(separator_all='; ')
        self.assertEqual(code, Status.CRITICAL)
        self.assertEqual(message, 'critical critical2; warning; ok')

        (code, message) = c.check_messages(separator_all='; ', allok="ALLOK")
        self.assertEqual(code, Status.CRITICAL)
        self.assertEqual(message, 'critical critical2; warning')

        c = Check()
        c.add_message(Status.OK, 'ok1')
        c.add_message(Status.OK, 'ok2')
        c.add_message(Status.OK, 'ok3')
        (code, message) = c.check_messages(separator_all='\n', separator='\n')
        self.assertEqual(code, Status.OK)
        self.assertEqual(message, 'ok1\nok2\nok3')
