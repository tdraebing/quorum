import unittest
import quorum.consumers as qc


class TwitterConsumersTestCase(unittest.iTestCase):
    def setUp(self):
        twitter = TwitterConsumer()

    def tearDown(self):
        teitter.terminate_driver()

