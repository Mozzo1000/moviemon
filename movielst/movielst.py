
import os
import textwrap
import requests
import json
import argparse
import pkg_resources
import hashlib
import csv
from .config import *
from .omdb import *
from guessit import guessit
from terminaltables import AsciiTable
from urllib.parse import urlencode
from tqdm import tqdm
from colorama import init, Fore

init()

EXT = (".3g2 .3gp .3gp2 .3gpp .60d .ajp .asf .asx .avchd .avi .bik .bix"
       ".box .cam .dat .divx .dmf .dv .dvr-ms .evo .flc .fli .flic .flv"
       ".flx .gvi .gvp .h264 .m1v .m2p .m2ts .m2v .m4e .m4v .mjp .mjpeg"
       ".mjpg .mkv .moov .mov .movhd .movie .movx .mp4 .mpe .mpeg .mpg"
       ".mpv .mpv2 .mxf .nsv .nut .ogg .ogm .omf .ps .qt .ram .rm .rmvb"
       ".swf .ts .vfw .vid .video .viv .vivo .vob .vro .wm .wmv .wmx"
       ".wrap .wvx .wx .x264 .xvid")

EXT = tuple(EXT.split())



def main():

    create_config()

    parser = argparse.ArgumentParser()
    parser.add_argument('PATH', nargs='?', default='')
    parser.add_argument('-v', '--version', help='Show version.', action='version', version='%(prog)s ' + get_version())
    parser.add_argument('-i', '--imdb', help='Sort acc. to IMDB rating.(dec)', action='store_true')
    parser.add_argument('-t', '--tomato', help='Sort acc. to Tomato Rotten rating.(dec)', action='store_true')
    parser.add_argument('-g', '--genre', help='Show movie name with its genre.', action='store_true')
    parser.add_argument('-a', '--awards', help='Show movie name with awards recieved.', action='store_true')
    parser.add_argument('-c', '--cast', help='Show movie name with its cast.', action='store_true')
    parser.add_argument('-d', '--director', help='Show movie name with its director(s).', action='store_true')
    parser.add_argument('-y', '--year', help='Show movie name with its release date.', action='store_true')
    parser.add_argument('-r', '--runtime', help='Show movie name with its runtime.', action='store_true')
    parser.add_argument('-e', '--export', help='Export list to either csv or excel', nargs=2)
    parser.add_argument('-I', '--imdb-rev', help='Sort acc. to IMDB rating.(inc)', action='store_true')
    parser.add_argument('-T', '--tomato-rev', help='Sort acc. to Tomato Rotten rating.(inc)', action='store_true')
    util(parser.parse_args())

def get_version():
    try:
        return pkg_resources.get_distribution("movielst").version
    except pkg_resources.DistributionNotFound:
        return "NOT INSTALLED ON SYSTEM! - SHA: " + hashlib.sha256(open(os.path.realpath(__file__), 'rb').read()).hexdigest()


def util(args):
    if args.PATH:
        if os.path.isdir(args.PATH):

            print("\n\nIndexing all movies inside ",
                  args.PATH + "\n\n")

            dir_json = get_setting('Index', 'location')

            scan_dir(args.PATH, dir_json)

            if movie_name:
                if movie_not_found:
                    print(Fore.RED + "\n\nData for the following movie(s)"
                          " could not be fetched -\n")
                    for val in movie_not_found:
                        print(Fore.RED + val)
                if not_a_movie:
                    print(Fore.RED + "\n\nThe following media in the"
                          " folder is not movie type -\n")
                    for val in not_a_movie:
                        print(Fore.RED + val)
                print(Fore.GREEN + "\n\nRun $movielst\n\n")
            else:
                print(Fore.RED + "\n\nGiven directory does not contain movies."
                      " Pass a directory containing movies\n\n")
        else:
            print(Fore.RED + "\n\nDirectory does not exists."
                  " Please pass a valid directory containing movies.\n\n")

    elif args.imdb:
        table_data = [["TITLE", "IMDB RATING"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"] = clean_table(item["Title"], None, item,
                                        table)
            table_data.append([item["Title"], item["imdbRating"]])
        sort_table(table_data, 1, True)

    elif args.tomato:
        table_data = [["TITLE", "TOMATO RATING"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"] = clean_table(item["Title"], None, item,
                                        table)
            table_data.append([item["Title"], get_rotten_score(item)])
        sort_table(table_data, 1, True)

    elif args.genre:
        table_data = [["TITLE", "GENRE"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"] = clean_table(item["Title"], None,
                                        item, table)
            table_data.append([item["Title"], item["Genre"]])
        sort_table(table_data, 0, False)

    elif args.awards:
        table_data = [["TITLE", "AWARDS"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"], item["Awards"] = clean_table(item["Title"],
                                                        item["Awards"], item,
                                                        table)
            table_data.append([item["Title"], item["Awards"]])
        sort_table(table_data, 0, False)

    elif args.cast:
        table_data = [["TITLE", "CAST"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"], item["Actors"] = clean_table(item["Title"],
                                                        item["Actors"], item,
                                                        table)
            table_data.append([item["Title"], item["Actors"]])
        sort_table(table_data, 0, False)

    elif args.director:
        table_data = [["TITLE", "DIRECTOR(S)"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"], item["Director"] = clean_table(item["Title"],
                                                          item["Director"],
                                                          item, table)
            table_data.append([item["Title"], item["Director"]])
        sort_table(table_data, 0, False)

    elif args.year:
        table_data = [["TITLE", "RELEASED"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"] = clean_table(item["Title"], None, item,
                                        table)
            table_data.append([item["Title"], item["Released"]])
        sort_table(table_data, 0, False)

    elif args.runtime:  # Sort result by handling numeric sort
        table_data = [["TITLE", "RUNTIME"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"] = clean_table(item["Title"], None, item,
                                        table)
            table_data.append([item["Title"], item["Runtime"]])
        print_table(table_data)

    elif args.imdb_rev:
        table_data = [["TITLE", "IMDB RATING"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"] = clean_table(item["Title"], None, item,
                                        table)
            table_data.append([item["Title"], item["imdbRating"]])
        sort_table(table_data, 1, False)

    elif args.tomato_rev:
        table_data = [["TITLE", "TOMATO RATING"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"] = clean_table(item["Title"], None, item,
                                        table)
            table_data.append([item["Title"], get_rotten_score(item)])
        sort_table(table_data, 1, False)
    elif args.export:
        table_data = [
            ["TITLE", "GENRE", "IMDB", "RUNTIME", "TOMATO",
             "YEAR"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"], item["Genre"] = clean_table(item["Title"],
                                                       item["Genre"], item,
                                                       table)
            table_data.append([item["Title"], item["Genre"],
                               item["imdbRating"], item["Runtime"],
                               get_rotten_score(item), item["Year"]])
        sort_table(table_data, 0, False)

        if 'excel' in args.export:
            export_type = args.export.index('excel')
            filename = args.export[:export_type] + args.export[export_type + 1:]
        elif 'csv' in args.export:
            export_type = args.export.index('csv')
            filename = args.export[:export_type] + args.export[export_type + 1:]
            with open(str(filename[0]), 'w', newline='') as outputfile:
                wr = csv.writer(outputfile, quoting=csv.QUOTE_ALL)
                wr.writerows(table_data)
        else:
            print("Unsupported character.")

    else:
        table_data = [
            ["TITLE", "GENRE", "IMDB", "RUNTIME", "TOMATO",
             "YEAR"]]
        data, table = butler(table_data)
        for item in data:
            item["Title"], item["Genre"] = clean_table(item["Title"],
                                                       item["Genre"], item,
                                                       table)
            table_data.append([item["Title"], item["Genre"],
                               item["imdbRating"], item["Runtime"],
                               get_rotten_score(item), item["Year"]])
        sort_table(table_data, 0, False)


def get_rotten_score(item):
    if item['Ratings'][1]['Source'] == "Rotten Tomatoes":
        return item['Ratings'][1]['Value']
    else:
        return "N/A"


def sort_table(table_data, index, reverse):
    table_data = (table_data[:1] + sorted(table_data[1:],
                                          key=lambda i: i[index],
                                          reverse=reverse))
    print_table(table_data)


def clean_table(tag1, tag2, item, table):
    if tag1 and tag2:
        if len(tag1) > table.column_max_width(0):
            tag1 = textwrap.fill(
                tag1, table.column_max_width(0))
            if len(tag2) > table.column_max_width(1):
                tag2 = textwrap.fill(
                    tag2, table.column_max_width(1))
        elif len(tag2) > table.column_max_width(1):
            tag2 = textwrap.fill(
                tag2, table.column_max_width(1))
        return tag1, tag2
    elif tag1:
        if len(tag1) > table.column_max_width(0):
            tag1 = textwrap.fill(
                tag1, table.column_max_width(0))
        return tag1


def butler(table_data):
    try:
        movie_path = get_setting('Index', 'location')
    except IOError:
        print(Fore.RED, "\n\nRun `$movielst PATH` to "
              "index your movies directory.\n\n")
        quit()
    else:
        table = AsciiTable(table_data)
        try:
            with open(movie_path) as inp:
                data = json.load(inp)
            return data, table
        except IOError:
            print(Fore.YELLOW, "\n\nRun `movielst PATH` to "
                  "index your movies directory.\n\n")
            quit()


def print_table(table_data):
    table = AsciiTable(table_data)
    table.inner_row_border = True
    if table_data[:1] in ([['TITLE', 'IMDB RATING']],
                          [['TITLE', 'TOMATO RATING']]):
        table.justify_columns[1] = 'center'
    print("\n")
    print(table.table)


movies = []
movie_name = []
not_a_movie = []
movie_not_found = []


def scan_dir(path, dir_json):
    # Preprocess the total files count
    for root, dirs, files in tqdm(os.walk(path)):
        for name in files:
            path = os.path.join(root, name)
            if os.path.getsize(path) > (25*1024*1024):
                ext = os.path.splitext(name)[1]
                if ext in EXT:
                    movie_name.append(name)

    with tqdm(total=len(movie_name), leave=True, unit='B',
              unit_scale=True) as pbar:
        for name in movie_name:
            data = get_movie_info(name)
            pbar.update()
            if data is not None and data['Response'] == 'True':
                for key, val in data.items():
                    if val == "N/A":
                        data[key] = "-"  # Should N/A be replaced with `-`?
                movies.append(data)
            else:
                if data is not None:
                    movie_not_found.append(name)
        with open(dir_json, "w") as out:
            json.dump(movies, out, indent=2)


def get_movie_info(name):
    """Find movie information"""
    movie_info = guessit(name)
    if movie_info['type'] == "movie":
        if 'year' in movie_info:
            return get_omdb_movie(movie_info['title'], movie_info['year'])
        else:
            return get_omdb_movie(movie_info['title'], None)
    else:
        not_a_movie.append(name)


if __name__ == '__main__':
    main()
