# coding: utf-8
from unittest import TestCase

from smart_qq_plugins.satoru import satoru


class TestSatoru(TestCase):

    def test_is_learn(self):
        result = satoru.is_learn("!learn {1}{2}")
        self.assertEqual(result, ("1", "2"))

    def test_is_remove(self):
        self.assertEqual(
            satoru.is_remove("!remove hello"), "hello"
        )