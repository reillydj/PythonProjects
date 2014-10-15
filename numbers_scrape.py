from bs4 import BeautifulSoup
import urllib2
import string
import html5lib
import re
import os
import time
import random
import json
import sys
from datetime import datetime

"""
    Data Acquisition Project: Movie Success Predictor
    Team: Jeff Baker, Patrick Howell, David Reilly
    Code Author: Patrick Howell
    Code Focus: Scraping The-Numbers.com


    Code Summary: Creates a two-tiered dictionary of dictionaries, grouped by letter,
    then by movie-key, which contains fields for each column of the movie index tables
    found on the-numbers.com
"""

def create_numbers_dict():
    # Master dictionary that will eventually hold all movies sorted by letter
    master = {}

    # Getting the list of upper case and digits to search
    index = ["("]   # The-Numbers starts with an open parentheses
    for d in string.digits:
        index.append(d)
    for i in string.ascii_uppercase:
        index.append(i)

    for char in index:
        if char == "A":     # NOTE: This should be removed for more than just the A example
            # URL request (this can be hidden if you don't want output to console
            print "Requesting movies starting with %s" % char
            table_url = "http://www.the-numbers.com/movies/letter/" + char
            request = urllib2.Request(table_url)

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
            soup = BeautifulSoup(content, "html5lib")
            #print soup.prettify().encode('UTF-8')
            # Raw table data:
            raw_data = soup.find_all('tr')

            # Parsed out data from beautifulsoup in list of lists format
            full_data = []
            for entry in raw_data:
                row_data = [x.string for x in entry.find_all('td')]  # finding all table data by row
                if len(row_data) > 1:
                    full_data.append(row_data)

            # Making a letter/character specific dictionary to store all movies+information within
            letter = {}
            for movie in full_data:
                try:
                    movie_key = movie[0][-4:]+"-"+movie[1]
                except:
                    print "Error on: ", movie
                #########################################################
                # Don't add movie to dictionary if BO and budget not in data

                # Taking out extra symbols
                try:
                    if movie[4][0] == '$':
                        gross = int(movie[4][1:].replace(",", ""))
                    else:
                        gross = int(movie[4].replace(",", ""))
                except:
                    gross = -1      # Equivalent of missing value, to make logic check easier later
                try:
                    if movie[3][0] == '$':
                        budget = int(movie[3][1:].replace(",", ""))
                    else:
                        budget = int(movie[3].replace(",", ""))
                except:
                    budget = -1

                if budget > 0 and gross > 0:
                    # Create the subdictionary with the 5 fields=values
                    letter[movie_key] = {}
                    letter[movie_key]['Release'] = movie[0].encode("utf-8")
                    letter[movie_key]['Title'] = movie[1].encode("utf-8")
                    letter[movie_key]['Genre'] = movie[2]
                    letter[movie_key]['Budget'] = budget
                    letter[movie_key]['DomesticBO'] = gross

            # Adding the letter dictionary to the master dictionary
            master[char] = letter
    return master

def encode(numbers_dict, fileName):
    with open(fileName, 'wb') as out_file:
        m = re.search(r'(?:\.)(\w+)',fileName)
        if m is not None:
            ext = m.groups()[0]
            if re.match(ext,'JSON',re.IGNORECASE) is not None:
                json.dump(numbers_dict, out_file, encoding='latin-1')


if __name__ == "__main__":
    # Only creates the A JSON file as the test case
    a_dict = create_numbers_dict()
    encode(a_dict, "Numbers_A.JSON")

