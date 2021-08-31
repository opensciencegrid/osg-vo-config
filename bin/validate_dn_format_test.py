#!/usr/bin/env python

import unittest
from unittest.mock import patch, mock_open
import validate_dn_format as validateDNFormat

class TestValidate(unittest.TestCase):

    def setUp(self):
        validateDNFormat.errorLog.clear()

    @patch('validate_dn_format.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/DC=org/ST=Wisconsin/CN=bad-name.org\n' +
        '/DC=org/ST=Wisconsin/CN=Test Company\n'
    ))
    def testNotMatchingSubjectCN(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root/folders', (), ('test.org.lsc',)),
        ]
        expectedError = [
            'Error in \"root/folders/test.org.lsc\" at /DC=org/ST=Wisconsin/CN=bad-name.org',
        ]
        validateDNFormat.validate('.')
        self.assertEqual(validateDNFormat.errorLog, expectedError)
    
    @patch('validate_dn_format.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/DC=org/ST=Wisconsin/CN=test.org\n' +
        '/DC=org/ST=Wisconsin\n'
    ))
    def testLastField(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root/folders', (), ('test.org.lsc',)),
        ]
        expectedError = [
            'Error in \"root/folders/test.org.lsc\" at /DC=org/ST=Wisconsin',
        ]
        validateDNFormat.validate('.')
        self.assertEqual(validateDNFormat.errorLog, expectedError)

    @patch('validate_dn_format.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/C=/ST=Wisconsin/L=Madison/CN=test.org\n' +
        '/C=US/ST=Wisconsin/L=Madison/CN=Test Company\n'
    ))
    def testBadKeyValuePair(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root/folders', (), ('test.org.lsc',)),
        ]
        expectedError = [
            'Error in \"root/folders/test.org.lsc\" at /C=/ST=Wisconsin/L=Madison/CN=test.org',
        ]
        validateDNFormat.validate('.')
        self.assertEqual(validateDNFormat.errorLog, expectedError)

    @patch('validate_dn_format.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/DC/=org/ST=Wisconsin/CN=test.org\n' +
        '/DC=orgST=Wisconsin/CN=Test Company\n'
    ))
    def testBadDelimiter(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root/folders', (), ('test.org.lsc',)),
        ]
        expectedError = [
            'Error in \"root/folders/test.org.lsc\" at /DC/=org/ST=Wisconsin/CN=test.org',
            'Error in \"root/folders/test.org.lsc\" at /DC=orgST=Wisconsin/CN=Test Company',
        ]
        validateDNFormat.validate('.')
        self.assertEqual(validateDNFormat.errorLog, expectedError)

    @patch('validate_dn_format.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/DC=org/ST=Wisconsin/CN=test.org\n' +
        '/DC=org/ST=Wisconsin/CN=Test Company\n' +
        '/DC=org/ST=Wisconsin/CN=Third DN\n'
    ))
    def testNumberOfDN(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root/folders', (), ('test.org.lsc',)),
        ]
        expectedError = [
            'Error in \"root/folders/test.org.lsc\" .lsc file should contain exactly 2 DNs'
        ]
        validateDNFormat.validate('.')
        self.assertEqual(validateDNFormat.errorLog, expectedError)

if __name__ == '__main__':
    unittest.main()
