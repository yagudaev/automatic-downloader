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

'''
Created on 2011-04-19

Description: This script screen scrapes a page provided to it as an argument and then downloads
all the audio files found on the page.

Use: > downloader http://www.example.com/music
'''
import getopt
import sys
import urllib
import re
import threading
import datetime
import os

FILE_EXTENSIONS = [".wav", ".wma", ".mp3"]
downloadListLock = threading.Lock()

class WorkerThread (threading.Thread):
    def __init__(self, downloadList, destination):
        self._downloadList = downloadList
        self._destination = destination
        threading.Thread.__init__ ( self )
    
    def run(self):
        # download the files
        i = 0
        print "started thread #%s" % self.getName()
        
        for download in self._downloadList:
            i += 1
            downloadListLock.acquire(True)
            
            if download['inProgress'] == False:
                print "downloading file %s of %s (%s, thread: %s)" % (i, len(self._downloadList), download['filename'], self.getName())
                download['inProgress'] = True
                downloadListLock.release()

                dst = self._destination + download['filename']
                if not os.path.isfile(dst): # check that file does not exist
                    try:
                        urllib.urlretrieve(download['url'], dst)
                        print "finished writing %s (thread: %s)" % (download['filename'], self.getName())
                    except IOError:
                        if '/' in download['filename']:
                            dir = self._destination + download['filename'][:download['filename'].rfind('/')]
                            os.makedirs(dir)
                            urllib.urlretrieve(download['url'], dst)
                else:
                    print "skipped file " + dst + " because it already exists"
            else:
                downloadListLock.release()

def findUrls(url, html, fileExtensions):
    '''
    extracts the links from an html string and returns absolute addresses to the
    resource and the resource filename. Resources will be filtered based on the 
    fileExtension list provided
    '''
    patternLinks = re.compile(r'<a\s.*?href\s*?=\s*?"(.*?)"', re.DOTALL | re.IGNORECASE)
    iterator = patternLinks.finditer(html)
    downloadList = []
    
    # process individual items
    for match in iterator:
        #    print match.groups()
        fileUrl = match.group(1)
        if any(fileUrl.endswith(extension) for extension in fileExtensions):
            urlType = re.match('^https?://(.*)', fileUrl)
            # absolute URL
            if urlType:
                filename = urlType.group(1)
                downloadUrl = urlType.group(0)
            else: # relative URL
                filename = fileUrl
                
                protocol = 'https://' if url.startswith('https') else 'http://'
                pos = url.replace(protocol, '').rfind('/')
                if pos >= 0:
                    url = url[: pos + len(protocol)]
                    
                downloadUrl = url + '/' + fileUrl 
            downloadList.append({'filename':urllib.unquote(filename), 'url':downloadUrl, 'inProgress':False})
    
    return downloadList


def printStatistics(timeAtStart, downloadList):
    # print summary
    fileCount = len(downloadList)
    totalTime = datetime.datetime.now() - timeAtStart
    print "-" * 50
    print "Statistics"
    print "-" * 50
    print "Total Running Time: %s" % totalTime
    print "Files Found: %d" % fileCount
    if (fileCount > 0):
        print "Average per File Time: %s" % (totalTime / fileCount)

def main():
    #Reading in options from the command line
    optlist, args = getopt.getopt(sys.argv[2:], 't:d:', ['threads=', 'dst='])
    
    timeAtStart = datetime.datetime.now()
    
    if (len(sys.argv) < 2 or sys.argv[1].startswith('-')):
        print """Wrong format!
            downloader <url> [options]
            Options are:
            -t (--threads): number of threads to use when downloading files
            -d (--dst): destination where the donwloaded files will be saved to
            """
        exit()
    
    url = sys.argv[1]
    if url.endswith('/'):
        url = url[:-1]
        
    print "`%s`" % url
    
    # defaults
    numThreads = 5
    destination = '' # current working directory
            
    if optlist:
        #Parsing options specified in command line
        for opt, val in optlist:
            if opt == "-t" or opt == "--threads":
                numThreads = int(val)
            elif opt == "-d" or opt == "--dst":
                destination = val if re.search('/$', val) != None else val + '/'
    
    # start reading the URL
    connection = urllib.urlopen(url)
    html = connection.read()
    
    print 'destination=' + destination
    
    downloadList = findUrls(url, html, FILE_EXTENSIONS)
    
    threads = []
    
    # create threads
    for i in range(0, numThreads):
        threads.append(WorkerThread(downloadList, destination))
        threads[i].setName(i)
        threads[i].start()
    
    # wait for all threads to finish
    for t in threads:
        t.join()
        
    printStatistics(timeAtStart, downloadList)
                  
if __name__ == "__main__":
    main()