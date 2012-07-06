#!/usr/bin/python

###############################################################################
# Yagudaev.com                                                                #
# Copyright (C) 2011                                                          #
#                                                                             #
# Authors:                                                                    #
#    Michael Yagudaev michael@yagudaev.com                                    #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
###############################################################################

import unittest

import code

from code.downloader import findUrls 

class Test(unittest.TestCase):


    def setUp(self):
        self._html5 = '''
        <!doctype html>
        <htm lang="en-US">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        </head>
        <body>
            <span>stuff...</span>
                <a href="doc1.pdf">doc 1</a>
                <a href="folder/doc2.pdf">doc 2</a>
                <a href="http://example.com/doc1.pdf">doc 1</a>
                <a href="dead_flash_back.swf">flash</a>
                <A HREF="doc2.pdf">doc 2</A>
                <a href="https://example.com/doc3.pdf">doc 3</a>
            </span>more stuff...</span>
        </body>
        </html>
        '''


    def tearDown(self):
        pass


    def testFindUrls(self):
        url = "http://google.com"
        expected = [
            {'filename': 'doc1.pdf', 'url': url + '/doc1.pdf'},
            {'filename': 'folder/doc2.pdf', 'url': url + '/folder/doc2.pdf'},
            {'filename': 'example.com/doc1.pdf', 'url': 'http://example.com/doc1.pdf'},
            {'filename': 'doc2.pdf', 'url': url + '/doc2.pdf'},
            {'filename': 'example.com/doc3.pdf', 'url': 'https://example.com/doc3.pdf'},
        ]

        results = findUrls(url, self._html5, ['.pdf'])
        
        self.assertEqual(len(expected), len(results));
        
        for i in range(0, len(results)):
            self.assertEqual(expected[i]['filename'], results[i]['filename'])
            self.assertEqual(expected[i]['url'], results[i]['url'])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
