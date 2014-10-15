import imdb
import re
import csv
import json
import numbers_scrape
import boxofficemojo_scrape
import random
import time
import string

"""
    Data Acquisition Project: Movie Success Predictor
    Team: Jeff Baker, Patrick Howell, David Reilly
    Code Author: David Reilly
    Code Focus: IMDb API and Data Aggregation


    Code Summary: This code accesses the IMDb API in order to obtain information about a movie
    given the name and year of release. After populating a dictionary, the movie
    information is written to a csv file for review.
"""


def imdb_grab(movie_list):
    """
        This function accesses the IMDb API and obtains relevant information
        for each movie in the movie_list
        inputs: list of movie names
        outputs: dictionary populated with title, genre, rating, runtime, country,
        language, producers, writers, directors, and costume designers of each movie
    """
    dictionary = {}
    incorrectMatches = {}

    # Iterate through each movie
    for i in range(0, len(movie_list)):

        # Repeat IMDb initialization to avoid timing out
        while True:
            try:
                ia = imdb.IMDb()
                break
            except:
                pass

        movie = movie_list[i]

        # Repeat search_movie call to avoid timing out
        while True:
            try:
                movieMatches = ia.search_movie(movie)
                break
            except:
                pass

        # Iterate through list of search results
        # Check for case-insensitive title match
        # Resort to first element of list if no matches found
        try:
            for k in range(len(movieMatches)):
                if movie[5:].lower() == str(movieMatches[k]['title']).lower():
                    first_match = movieMatches[k]
                    break
                else:
                    if k == len(movieMatches) - 1:
                        incorrectMatches[movie] = 1.0
                        first_match = movieMatches[0]
                    else:
                        pass
        except:
            continue

        # Repeat update call to avoid timing out
        while True:
            try:
                ia.update(first_match)
                break
            except:
                pass

        # Grab rating
        try:
            rating = str(first_match['rating'])
        except:
            rating = 0.0


        # Grab genre
        genre = ''
        try:
            for a in range(len(first_match['genre'])):
                if a > 0:
                    genre += ' and ' + str(first_match['genre'][a])
                else:
                    genre += str(first_match['genre'][a])
        except:
            genre = 0.0

        # Grab country
        country = ''
        try:
            for b in range(len(first_match['country'])):
                if b > 0:
                    country += ' and ' + str(first_match['country'][b])
                else:
                    country += str(first_match['country'][b])
        except:
            country = 0.0

        # Grab language
        language = ''
        try:
            for c in range(len(first_match['language'])):
                if c > 0:
                    language += ' and ' + str(first_match['language'][c])
                else:
                    language += str(first_match['language'][c])
        except:
            language = 0.0

        # Grab runtime
        try:
            runtime = str(first_match['runtimes'][0])
        except:
            runtime = 0.0

        # Grab costume designers
        costume_designers = ""
        try:
            for j in range(len(first_match['costume designer'])):
                if j > 0:
                    costume_designers += ' and ' + str(first_match['costume designer'][j])
                else:
                    costume_designers += str(first_match['costume designer'][j])
        except:
            costume_designers = 0.0

        # Grab producers
        producers = ""
        try:
            for k in range(len(first_match['producer'])):
                if k > 0:
                    producers += ' and ' + str(first_match['producer'][k])
                else:
                    producers += str(first_match['producer'][k])
        except:
            producers = 0.0

        # Grab writers
        writers = ""
        try:
            for l in range(len(first_match['writer'])):
                if l > 0:
                    writers += ' and ' + str(first_match['writer'][l])
                else:
                    writers += str(first_match['writer'][l])
        except:
            writers = 0.0

        # Grab directors
        directors = ""
        try:
            for m in range(len(first_match['director'])):
                if m > 0:
                    directors += ' and ' + str(first_match['director'][m])
                else:
                    directors += str(first_match['director'][m])
        except:
            directors = 0.0

        # Populate dictionary
        dictionary[movie_list[i]] = {"Genre" : str(genre),
                             "Rating" : str(rating), "Runtime" : str(runtime),
                             "Country" : str(country), "Language" : str(language),
                             "Producers" : str(producers), "Writers" : str(writers),
                             "Directors" : str(directors), "Costume designers" : str(costume_designers)}

        wait_time = round(max(0, 1 + random.gauss(0, 0.5)), 2)
        time.sleep(wait_time)

    return dictionary

def make_json(dictionary, fileName):
    with open(fileName, 'wb') as out_file:
        m = re.search(r'(?:\.)(\w+)',fileName)
        if m is not None:
            ext = m.groups()[0]
            if re.match(ext,'JSON',re.IGNORECASE) is not None:
                json.dump(dictionary, out_file, encoding='latin-1')

def getNumbers():
    return numbers_scrape.create_numbers_dict()

def getBom():
    return boxofficemojo_scrape.create_bom_dict()

def getTotalList(dictionary):
    list_of_movies = []
    for letter in string.uppercase():
        for key in dictionary[letter].keys():
            list_of_movies.append(key)


def populateCSVA(list1, list2):
    """
        Populate CSV file for all movies beginning with the letter 'A'
        Input: Two lists of movie titles, one from The-Numbers.com and one from BoxOfficeMojo.com
        Output: TotalMovie.csv file
    """

    # Initialize IMDb, The-Numbers, and BoxOfficeMojo dictionaries
    imdb_dict = imdb_grab(list1)
    numbers_dict = getNumbers()
    bom_dict = getBom()

    # Update BoxOfficeMojo dictionary with movies from The-Numbers.com
    for i in range(len(list1)):
        try:
            bom_dict['A'][list1[i]].update(imdb_dict[list1[i]])
        except:
            pass
        try:
            bom_dict['A'][list1[i]].update(numbers_dict['A'][list1[i]])
        except:
            pass

    # Initialize IMDb dictionary with second list of movies
    imdb_dict_2 = imdb_grab(list2)

    imdb_dict_2.update(imdb_dict)

    # Update BOM dictionary with IMDb information
    for i in range(len(list1)):
        try:
            bom_dict['A'][list1[i]].update(imdb_dict_2[list1[i]])
        except:
            pass
        try:
            bom_dict['A'][list1[i]].update(numbers_dict['A'][list1[i]])
        except:
            pass

    for j in range(len(list2)):
        try:
            bom_dict['A'][list2[j]].update(imdb_dict_2[list2[j]])
        except:
            pass


    # Write each row of BOM dictionary to a CSV
    with open('TotalMovie.csv', 'wb') as f:
        writer = csv.writer(f)
        header = ["Title", "TotalGross", "OpeningGross", "Rating", \
                    "Country", "TotalTheaters", "DomesticBO", "Directors", \
                    "Studio", "OpeningTheaters", "OpeningDate", "Genre", "Budget", "Runtime"]
        writer.writerow(header)

        # Populate each row
        # If no information is available, append 0
        for key in bom_dict['A'].keys():
            row = []
            row.append(bom_dict['A'][key]["Title"])
            try:
                row.append(bom_dict['A'][key]["TotalGross"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["OpeningGross"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["Rating"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["Country"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["TotalTheaters"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["DomesticBO"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["Directors"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["Studio"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["OpeningTheaters"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["OpeningDate"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["Genre"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["Budget"])
            except:
                row.append(0.0)
            try:
                row.append(bom_dict['A'][key]["Runtime"])
            except:
                row.append(0.0)
            writer.writerow(row)


def populateCSVTotal(list1, list2):

    """
        Populate CSV file for all movies
        Input: Two lists of movie titles, one from The-Numbers.com and one from BoxOfficeMojo.com
        Output: TotalMovie.csv file
    """

    # Initialize IMDb, The-Numbers, and BoxOfficeMojo dictionaries for first list of movies
    imdb_dict = imdb_grab(list1)
    imdb_dict_2 = imdb_grab(list2)
    imdb_dict_2.update(imdb_dict)
    numbers_dict = getNumbers()
    bom_dict = getBom()

    # Update BoxOfficeMojo dictionary with movies from The-Numbers.com
    for letter in string.uppercase():
        for i in range(len(list1)):
            try:
                bom_dict[letter][list1[i]].update(imdb_dict[list1[i]])
            except:
                pass
            try:
                bom_dict[letter][list1[i]].update(numbers_dict[letter][list1[i]])
            except:
                pass

        for i in range(len(list1)):
            try:
                bom_dict[letter][list1[i]].update(imdb_dict_2[list1[i]])
            except:
                pass
            try:
                bom_dict[letter][list1[i]].update(numbers_dict[letter][list1[i]])
            except:
                pass

        for j in range(len(list2)):
            try:
                bom_dict[letter][list2[j]].update(imdb_dict_2[list2[j]])
            except:
                pass


    # Write CSV file with information for every movie
    with open('TotalMovie.csv', 'wb') as f:
        writer = csv.writer(f)
        header = ["Title", "TotalGross", "OpeningGross", "Rating", \
                    "Country", "TotalTheaters", "DomesticBO", "Directors", \
                    "Studio", "OpeningTheaters", "OpeningDate", "Genre", "Budget", "Runtime"]
        writer.writerow(header)
        for letter in string.uppercase():
            # Populate each row
            # If no information is available, append 0
            for key in bom_dict[letter].keys():
                row = []
                row.append(bom_dict[letter][key]["Title"])
                try:
                    row.append(bom_dict[letter][key]["TotalGross"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["OpeningGross"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["Rating"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["Country"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["TotalTheaters"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["DomesticBO"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["Directors"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["Studio"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["OpeningTheaters"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["OpeningDate"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["Genre"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["Budget"])
                except:
                    row.append(0.0)
                try:
                    row.append(bom_dict[letter][key]["Runtime"])
                except:
                    row.append(0.0)
                writer.writerow(row)

if __name__ == '__main__':
    # populateCSVA(getNumbers()['A'].keys()[:10], getBom()['A'].keys()[:10])
    # populateCSVTotal(getTotalList(getNumbers()), getTotalList(getBom()))
    pass