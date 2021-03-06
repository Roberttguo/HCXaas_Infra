import json
import os
import ssl
import sys
import logging
import time
import unittest
import lib.HTMLTestRunner as HTMLTestRunner

TESTDATA_FILENAME = os.path.join(os.path.dirname(__file__), '../testdata/testdata.json')
TESTBED_FILENAME = os.path.join(os.path.dirname(__file__), '../testdata/testbed_info.json')

"""Set up local logger"""
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
logger.addHandler(ch)
"""Set up local logger End"""


class NetworkExtensionsTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_network_extension(self):
        """Dummy test."""
        self.assertEqual(True, True, "Dummy test.")