from sqlite3.dbapi2 import Cursor
import bs4 as bs
import urllib.request
import Utility
import sqlite3


if __name__ == "__main__":
    
    # NDSU likes to seperate each semester by state, so find the landing page for each semester
    listLandingPage = ['https://www.ndsu.edu/news/studentnews/gradlistfall2012/', 'https://www.ndsu.edu/news/studentnews/gradlistspring2012/', 
                       'https://www.ndsu.edu/news/studentnews/gradlistfall2013/', 'https://www.ndsu.edu/news/studentnews/gradlistspring2013/', 
                       'https://www.ndsu.edu/news/studentnews/gradlistfall2014/', 'https://www.ndsu.edu/news/studentnews/gradlistspring2014/', 'https://www.ndsu.edu/news/studentnews/gradlistsummer2014/',
                       'https://www.ndsu.edu/news/studentnews/gradlistfall2015/', 'https://www.ndsu.edu/news/studentnews/gradlistspring2015/', 'https://www.ndsu.edu/news/studentnews/gradlistsummer2015/',
                       'https://www.ndsu.edu/news/studentnews/gradlistfall2016/', 'https://www.ndsu.edu/news/studentnews/gradlistspring2016/', 'https://www.ndsu.edu/news/studentnews/gradlistsummer2016/',
                       'https://www.ndsu.edu/news/studentnews/gradlistfall2017/', 'https://www.ndsu.edu/news/studentnews/gradlistspring2017/', 'https://www.ndsu.edu/news/studentnews/gradlistsummer2017/',  
                       'https://www.ndsu.edu/news/studentnews/gradlistfall2018/', 'https://www.ndsu.edu/news/studentnews/gradlistspring2018/', 'https://www.ndsu.edu/news/studentnews/gradlistsummer2018/',
                       'https://www.ndsu.edu/news/studentnews/gradlistfall2019/', 'https://www.ndsu.edu/news/studentnews/graduation_list_spring_2019/', 'https://www.ndsu.edu/news/studentnews/graduation_list_summer_2019/', 
                       'https://www.ndsu.edu/news/studentnews/gradlistfall2020/', 'https://www.ndsu.edu/news/studentnews/graduation_list_spring_2020/', 'https://www.ndsu.edu/news/studentnews/graduation_list_summer_2020/' ]
    
    # opens the SQLIte to write to
    conn = sqlite3.connect('graduationList.db')
    Utility.createTable(conn)
    
    #Only check semesters that haven't been added yet
    unseenList = Utility.getUnseen(listLandingPage, conn)
    
    for link in listLandingPage:
        try:
            #Add the link to the seen list
            Utility.insertLinkIntoSeen(link, conn)
            
            # creates a BS object for each Semester's landing page
            url = urllib.request.urlopen(link)
            soup = bs.BeautifulSoup(url, 'html.parser')
            
            # Find all links on the page
            links = soup.find_all('a')
            for x in links:
                try:
                    if 'Graduation' not in x.text:
                        continue
                        #Skip the link if it's text doesn't contain "Graduation"
                        
                    # collects table rows and other information about table
                    rows_info = Utility.rows_finder(x)
                    
                    # collect information from each row in the table, then writes it to a file
                    Utility.sql_handler(rows_info[1], rows_info[0], conn)
                except:
                    # do nothing, throw away bad link
                    print(end="")
        except:
            print("whoops")