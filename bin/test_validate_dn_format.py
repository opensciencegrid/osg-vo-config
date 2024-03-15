#!/usr/bin/python3

import unittest
import validate_dn_format

class TestValidate(unittest.TestCase):

    def setUp(self):
        validate_dn_format.error_log.clear()

    def test_number_of_dn(self):
        dummy_lines = [
            '/DC=org/ST=Wisconsin/CN=test.org',
            '/DC=org/ST=Wisconsin/CN=Test Company',
            '/DC=org/ST=Wisconsin/CN=Third DN',
        ]
        self.assertFalse(validate_dn_format.check_number_of_dn(dummy_lines))

    def test_not_matching_subject_cn(self):
        dummy_lines = [
            '/DC=org/ST=Wisconsin/CN=bad-name.org',
            '/DC=org/ST=Wisconsin/CN=Test Company',
        ]
        dummy_file_path = 'root/folders/test.org.lsc'
        self.assertFalse(validate_dn_format.check_matching_cn(dummy_lines[0], dummy_file_path))
    
    def test_no_cn(self):
        dummy_line = '/DC=org/ST=Wisconsin'
        self.assertFalse(validate_dn_format.check_format(dummy_line))

    def test_bad_key_value_pair(self):
        dummy_line = '/C=/ST=Wisconsin/L=Madison/CN=test.org'
        self.assertFalse(validate_dn_format.check_format(dummy_line))

    def test_first_delimiter(self):
        dummy_line = 'C=US/ST=Wisconsin/L=Madison/CN=test.org'
        self.assertFalse(validate_dn_format.check_format(dummy_line))
    
    def test_missing_delimiter(self):
        dummy_line = '/C=US/ST=WisconsinL=Madison/CN=test.org'
        self.assertFalse(validate_dn_format.check_format(dummy_line))

if __name__ == '__main__':
    unittest.main()
