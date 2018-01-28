#!/usr/bin/env python
import unittest
import lib

class TestStrokeIntersection(unittest.TestCase):
    def test_parallel_lines(self):
        #   0     .....  100
        # 0 ----------------
        # 1 ----------------
        a = ((0,0),(100,0))
        b = ((0,1),(100,1))
        does_it_intersect =  lib.stroke.intersection(a,b)
        self.assertFalse(does_it_intersect)

    def test_intersecting_lines_within_coords(self):
        #   0     .....  100
        # 0 ---___
        # 1 ------x---------
        # 2        ----------
        a = ((0,0),(100,2))
        b = ((0,1),(100,1))
        does_it_intersect =  lib.stroke.intersection(a,b)
        self.assertTrue(does_it_intersect)

    def test_intersecting_lines_outside_coords(self):
        #  4    |
        #  2    |
        #
        #  0 ----------
        #  0           10
        a = ((0,0),(10,0))
        b = ((2,10),(2,2))
        does_it_intersect =  lib.stroke.intersection(a,b)
        self.assertFalse(does_it_intersect)
