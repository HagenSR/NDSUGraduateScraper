import bs4 as bs
import urllib.request
import re
import sqlite3
import time


def good_input(b):
    if b and (not b.isspace()):
        return True
    return False

def good_input_row(row):
    return good_input(row[0].text) and not (good_input(row[1].text) or good_input(row[2].text) or good_input(row[3].text) )


def fix_input(b):
    """
    Removes unwanted Characters, Replaces Abbreviation of State with Full name
    :param b: A string to be cleaned
    :return: A cleaned string
    """
    b = re.sub("Dean's List", "", b)
    b = re.sub("Dean's", "", b)
    b = re.sub("List", "", b)
    b = re.sub("'", " ", b)
    b = re.sub("  *", " ", b)
    b = re.sub("\xa0$", "", b)
    b = re.sub("[.]", "", b)
    b = re.sub("^ Minn$", "Minnesota", b)
    b = re.sub("^ ND$", "North Dakota", b)
    b = re.sub("^ SD$", "South Dakota", b)
    b = re.sub("^ Wis$", "Wisconsin", b)
    b = re.sub("^ Mont$", "Montana", b)
    return b.strip()



def sql_handler(table_rows, year, conn):
    '''
    pulls information out of each row, throwing it away if it doesn't have enough entries to be valid
    (name, degree, major, city, state, country, honors, semester )
    
    :param table_rows: a collection of rows containing graduation information
    :param year: a year and semester for a given table
    :param file: a database to write to
    :return: nothing, this method writes directly to a sqlite file
    '''
    city = ""
    state = ""
    #Assume America because the page never specifies When it is America
    country = "USA"
    
    #Skip the header row
    skip = False
    cursor = conn.cursor()
    for tr in table_rows:
        try:
            td = tr.find_all('td')
            # add information from the row/variables to a list
            student_list = []
            if skip:
                if good_input_row(td) and 'Hometown' not in td[0].string:
                    country = td[0].text
                else:
                    # If the first column of the row isn't empty get the information. If the word 'Continued' is in the column keep the last city/state
                    if good_input(td[0].text) and 'continued' not in td[0].text:
                        try:
                            city = fix_input(td[0].text.split(",")[0])
                            state = fix_input(td[0].text.split(",")[1])
                            td.pop(0)
                            #NDSU switches from (city, state) to just (city state) so this gets both. Remove the column after 
                        except:
                            city = fix_input(td[0].text.split(" ")[0])
                            state = fix_input(td[0].text.split(" ")[1])
                            td.pop(0)
                    else:
                        td.pop(0)
                        
                    honors = False
                    goodCount = 0
                    # Slightly clunky, but the HTML table ocassionally contains padding collumns which varys between years. This will find the information collumns
                    # which are name, degree, major
                    for index in range(len(td)):
                        if good_input(td[index].text):
                            if goodCount == 0:
                                name = td[index].text
                                if '*' in name:
                                    # * delineates graduating with honors, put it into the DB! then remove it from their name
                                    honors = True
                                    name = name.replace("*", "")
                                name = fix_input(name)
                                student_list.append(name)
                                goodCount += 1
                            else:
                                student_list.append(fix_input(td[index].text))
                                goodCount += 1
                    student_list.append(fix_input(str(city)))
                    student_list.append(fix_input(str(state)))
                    student_list.append(fix_input(str(country)))
                    student_list.append(fix_input(str(honors)))
                    student_list.append(fix_input(str(year)))

                    # Checks to see if row is valid
                    if (student_list.__len__() != 8) or (student_list[0].startswith("Hometown")):
                        print("problem with row " + str(student_list))
                    else:
                        # move information from list to string:
                        try:
                            st = str.format("INSERT INTO student(name, degree, major, city, state, country, honors, semester ) VALUES ('{0}','{1}','{2}', '{3}', '{4}', '{5}', {6}, '{7}' )", *tuple(student_list))
                            cursor.execute(st)
                            conn.commit()
                        except Exception as e:
                            print(e)
            else:
                skip = True
        except Exception as e:
            print(e)

def rows_finder(link):
    """
    takes a link, then finds the table rows and table information needed for that page
    :param link: a link to a specific states graduation list
    :return: a string representing year and a list of all the table row elements from the graduation list table
    """    
    # collect information from the title of each link
    words = link.text.split(" ")
    if "" in words:
        words.remove("")
    year = words[-2] + " " + words[-1]
    # build a link for each state, then navigate and create a bs object for it
    text_string = "https://www.ndsu.edu/" + link.get('href')
    url2 = urllib.request.urlopen(text_string)
    soup = bs.BeautifulSoup(url2, 'html.parser')
    # finds all the tables in the file and returns the last one,
    # which (for the NDSU page) is the table that holds the information we want
    table = soup.find_all('table')[-1]
    # checks to see if there is a table within a table
    table_rows = table.find_all('tr')
    rows_info = [year, table_rows]
    return rows_info


def createTable(conn):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "CREATE TABLE student(name varchar(100),city varchar(60),state varchar(60), country varchar(60), major varchar(100), degree varchar(100), honors boolean, semester varchar(20));")
        cursor.execute(
            "CREATE TABLE seen(URL varchar(100));")
    except Exception as e:
        print(e)
    cursor.close()
    conn.commit()
    
def insertLinkIntoSeen(url, conn):
    try:
        cursor = conn.cursor()
        st = str.format("INSERT INTO seen VALUES ('{0}')", url)
        cursor.execute(st)
        conn.commit()
    except:
        print("Error inserting into seen")
    
def getUnseen(list, conn):
    try:
        cursor = conn.cursor()
        strn = str.format("SELECT * FROM seen")
        cursor.execute(strn)
        res = cursor.fetchall()
        listSeen = []
        for url in res:
            listSeen.append(url[0])
        listNotSeen = []
        for link in list:
            if link not in listSeen:
                listNotSeen.append(link)
        return listNotSeen
    except Exception as e:
        print("Error with getting unseen, {}".format(e))
            
