#!/usr/bin/env python

import unittest
from unittest.mock import patch, mock_open
import validate_dn_format

class TestValidate(unittest.TestCase):

    def setUp(self):
        validate_dn_format.error_log.clear()

    @patch('validate_dn_format.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/DC=org/ST=Wisconsin/CN=bad-name.org\n' +
        '/DC=org/ST=Wisconsin/CN=Test Company\n'
    ))
    def test_not_matching_subject_cn(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root/folders', (), ('test.org.lsc',)),
        ]
        expected_error = [
            'Error in \"root/folders/test.org.lsc\" at /DC=org/ST=Wisconsin/CN=bad-name.org',
        ]
        validate_dn_format.validate('.')
        self.assertEqual(validate_dn_format.error_log, expected_error)
    
    @patch('validate_dn_format.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/DC=org/ST=Wisconsin/CN=test.org\n' +
        '/DC=org/ST=Wisconsin\n'
    ))
    def test_last_field(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root/folders', (), ('test.org.lsc',)),
        ]
        expected_error = [
            'Error in \"root/folders/test.org.lsc\" at /DC=org/ST=Wisconsin',
        ]
        validate_dn_format.validate('.')
        self.assertEqual(validate_dn_format.error_log, expected_error)

    @patch('validate_dn_format.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/C=/ST=Wisconsin/L=Madison/CN=test.org\n' +
        '/C=US/ST=Wisconsin/L=Madison/CN=Test Company\n'
    ))
    def test_bad_key_value_pair(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root/folders', (), ('test.org.lsc',)),
        ]
        expected_error = [
            'Error in \"root/folders/test.org.lsc\" at /C=/ST=Wisconsin/L=Madison/CN=test.org',
        ]
        validate_dn_format.validate('.')
        self.assertEqual(validate_dn_format.error_log, expected_error)

    @patch('validate_dn_format.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/DC/=org/ST=Wisconsin/CN=test.org\n' +
        '/DC=orgST=Wisconsin/CN=Test Company\n'
    ))
    def test_bad_delimiter(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root/folders', (), ('test.org.lsc',)),
        ]
        expected_error = [
            'Error in \"root/folders/test.org.lsc\" at /DC/=org/ST=Wisconsin/CN=test.org',
            'Error in \"root/folders/test.org.lsc\" at /DC=orgST=Wisconsin/CN=Test Company',
        ]
        validate_dn_format.validate('.')
        self.assertEqual(validate_dn_format.error_log, expected_error)

    @patch('validate_dn_format.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/DC=org/ST=Wisconsin/CN=test.org\n' +
        '/DC=org/ST=Wisconsin/CN=Test Company\n' +
        '/DC=org/ST=Wisconsin/CN=Third DN\n'
    ))
    def test_number_of_dn(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root/folders', (), ('test.org.lsc',)),
        ]
        expected_error = [
            'Error in \"root/folders/test.org.lsc\" .lsc file should contain exactly 2 DNs'
        ]
        validate_dn_format.validate('.')
        self.assertEqual(validate_dn_format.error_log, expected_error)

if __name__ == '__main__':
    unittest.main()
