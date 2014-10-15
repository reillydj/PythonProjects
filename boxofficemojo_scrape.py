__author__ = 'jrbaker'

from bs4 import BeautifulSoup
import urllib2
import re
import os
import time
import random
import csv
import sys
import string
import json
import pickle
from datetime import datetime

"""
    Data Acquisition Project: Movie Success Predictor
    Team: Jeff Baker, Patrick Howell, David Reilly
    Code Author: David Reilly
    Code Focus: Box Office Mojo (BOM) page scraping (http://www.boxofficemojo.com)


    Code Summary: This code scrapes BOM for movie data. After populating a dictionary, the movie
    information is written to a JSON file for merging with other data sources (namely www.the-numbers.com).
"""



def genCanonicalName(S):
        S = S.upper()
        S = re.sub('\((.|\s)+\)', '', S)
        S = re.sub(r'\s?&\s?', ' AND ', S)
        S = re.sub(r'\.', '', S)
        S = re.sub(r'\/', '', S)
        S = re.sub(r'\:', '', S)
        S = re.sub(r'\'', '', S)
        S = re.sub(r'[;\s,-]','', S)
        return S

def encode(BOM_dict, fileName):
    with open(fileName, 'wb') as out_file:
        m = re.search(r'(?:\.)(\w+)',fileName)
        if m is not None:
            ext = m.groups()[0]
            if re.match(ext,'JSON',re.IGNORECASE) is not None:
                json.dump(BOM_dict, out_file, indent=4) # encoding='latin-1')

def create_bom_dict():
    full_data = []
    bomMasterDict = {}
    movieCount = 0
    bomMasterDict = {}

    alpha = list(string.uppercase)
    #BOM has a "NUM" page for numbered/special character titles; we add this to the front of the list of letters
    #alpha = ["NUM"] + alpha
    alpha = "A"          # FOR TESTING ONLY

    # stopstring indicates empty page content
    stopstring = "Open</font></td></tr></table><div class=\"alpha-nav-holder\">"

    # initialize the master dictionary with alphabet + NUM as keys
    for letter in alpha:
        bomMasterDict[alpha] = {}


    for letter in alpha:
        bomAlphaDict = {}
        i = 1
        more = True
        while(more):
            # status update print statement
            print("letter %s, page %d" % (letter,i))
            # Open the URL to get the review data
            url = "http://www.boxofficemojo.com/movies/alphabetical.htm?letter="+letter+"&page="+str(i)+"&p=.htm"
            request = urllib2.Request(url)

            try:
                page = urllib2.urlopen(request)
            except urllib2.URLError, e:
                if hasattr(e, 'reason'):
                    print 'Failed to reach url'
                    print 'Reason: ', e.reason
                    sys.exit()
                elif hasattr(e, 'code'):
                    if e.code == 404:
                        print 'Error: ', e.code
                        sys.exit()


            content = page.read()

            # if stopstring is found in source code, there is no content
            # if letter=="NUM", then set more = False to stop after this iteration (only 1 page)
            if (letter=="NUM" or re.findall(stopstring, content)):
                more = False

            soup = BeautifulSoup(content)
            raw_data = soup.find_all('tr')

            for entry in raw_data:
                row_data = [x.string for x in entry.find_all('td')]
                full_data.append(row_data)

            # first four listings in full_data are columns/page header/etc.; ignored since len(listing) !> 1
            # last entry is "[ALPHABETICAL INDEX]" and not used

            for listing in full_data:
                bomTitleEntry = {}
                if (len(listing) > 1):
                    try:
                        # remove any special characters in the figures (theaters, dollar amounts)
                        tgross = listing[2]
                        ogross = listing[4]
                        ttheaters = listing[3]
                        otheaters = listing[5]
                        tgross = re.sub(r'\$','',tgross)
                        tgross = re.sub(r',','',tgross)
                        tgross = re.sub(r'\*','',tgross)
                        ogross = re.sub(r'\$','',ogross)
                        ogross = re.sub(r',','',ogross)
                        ogross = re.sub(r'\*','',ogross)
                        ttheaters = re.sub(r',','',ttheaters)
                        otheaters = re.sub(r',','',otheaters)

                        # pull release year out to create "movieKey"
                        releaseYear = listing[6][-4:]
                        # release year + movie title is the key for the movie's dictionary value
                        movieKey = releaseYear+"-"+listing[0]
                        bomTitleEntry["Title"] = listing[0]
                        bomTitleEntry["Studio"] = listing[1]
                        bomTitleEntry["TotalGross"] = int(tgross)
                        bomTitleEntry["TotalTheaters"] = int(ttheaters)
                        bomTitleEntry["OpeningGross"] = int(ogross)
                        bomTitleEntry["OpeningTheaters"] = int(otheaters)
                        bomTitleEntry["OpeningDate"] = listing[6]
                        bomAlphaDict[movieKey] = bomTitleEntry
                        movieCount += 1
                    except:
                        continue
                else: continue
            i += 1
            wait_time = round(max(0, 1 + random.gauss(0,0.5)), 2)
            time.sleep(wait_time)
        bomMasterDict[alpha].update(bomAlphaDict)
    # print("Movie count: %d" % movieCount)
    # print json.dumps(bomMasterDict, indent = 4)
    return bomMasterDict


if __name__ == '__main__':
    bom_dict = create_bom_dict()
    encode(bom_dict, "BOM_A.JSON")

