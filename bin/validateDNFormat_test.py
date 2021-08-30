#!/usr/bin/env python

import unittest
from unittest.mock import patch, mock_open
import validateDNFormat

class TestValidate(unittest.TestCase):

    def setUp(self):
        validateDNFormat.errorLog.clear()

    # def testGoodFormat(self, mock_os):
    #     validateDNFormat.validate('.')
    #     self.assertEqual(validateDNFormat.errorLog, [])

    @patch('validateDNFormat.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/DC=org/ST=Wisconsin/CN=bad-name.org\n' +
        '/DC=org/ST=Wisconsin/CN=Test Company\n'
    ))
    def testNotMatchingSubjectCN(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root\\folders', (), ('test.org.lsc',)),
        ]
        expectedError = [
            'Error in \"root\\folders\\test.org.lsc\" at /DC=org/ST=Wisconsin/CN=bad-name.org',
        ]
        validateDNFormat.validate('.')
        self.assertEqual(validateDNFormat.errorLog, expectedError)
    
    @patch('validateDNFormat.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/DC=org/ST=Wisconsin/CN=test.org\n' +
        '/DC=org/ST=Wisconsin\n'
    ))
    def testLastField(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root\\folders', (), ('test.org.lsc',)),
        ]
        expectedError = [
            'Error in \"root\\folders\\test.org.lsc\" at /DC=org/ST=Wisconsin',
        ]
        validateDNFormat.validate('.')
        self.assertEqual(validateDNFormat.errorLog, expectedError)


    @patch('validateDNFormat.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/C=/ST=Wisconsin/L=Madison/CN=test.org\n' +
        '/C=US/ST=Wisconsin/L=Madison/CN=Test Company\n'
    ))
    def testBadKeyValuePair(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root\\folders', (), ('test.org.lsc',)),
        ]
        expectedError = [
            'Error in \"root\\folders\\test.org.lsc\" at /C=/ST=Wisconsin/L=Madison/CN=test.org',
        ]
        validateDNFormat.validate('.')
        self.assertEqual(validateDNFormat.errorLog, expectedError)
    

    @patch('validateDNFormat.os.walk')
    @patch('builtins.open', mock_open(read_data=
        '/DC/=org/ST=Wisconsin/CN=test.org\n' +
        '/DC=/org/ST=Wisconsin/CN=Test Company\n' +
        'DC=org/ST=Wisconsin/CN=test.org\n' +
        '/DC=orgST=Wisconsin/CN=Test Company\n'
    ))
    def testBadDelimiter(self, mock_walk):
        mock_walk.return_value = [
            ('root', ('folders',), ()),
            ('root\\folders', (), ('test.org.lsc',)),
        ]
        expectedError = [
            'Error in \"root\\folders\\test.org.lsc\" at /DC/=org/ST=Wisconsin/CN=test.org',
            'Error in \"root\\folders\\test.org.lsc\" at /DC=/org/ST=Wisconsin/CN=Test Company',
            'Error in \"root\\folders\\test.org.lsc\" at DC=org/ST=Wisconsin/CN=test.org',
            'Error in \"root\\folders\\test.org.lsc\" at /DC=orgST=Wisconsin/CN=Test Company',
        ]
        validateDNFormat.validate('.')
        self.assertEqual(validateDNFormat.errorLog, expectedError)


if __name__ == '__main__':
    unittest.main()