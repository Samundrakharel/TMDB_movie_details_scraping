"""Template robot with Python."""
import sqlite3
import logging
import re

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files

Browser= Selenium(auto_close=False)
excel_lib= Files()

con = sqlite3.connect("tmdb.db")
cur = con.cursor()

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')


URL = 'https://www.themoviedb.org//'
Excel_file= 'movies.xlsx'

def remove_punctuations(string):
    pattern = r'[\"\',]()'
    return re.sub(pattern, '', string)

import sqlite3

def create_table_movies():
    con = sqlite3.connect("tmdb.db")
    cur = con.cursor()
    create_table_sql ="""
        CREATE TABLE IF NOT EXISTS movies(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_name TEXT ,
            user_score TEXT,
            rating TEXT,
            mpaa TEXT,
            overview TEXT,
            genres TEXT,
            tagline TEXT,
            review_1 TEXT,
            review_2 TEXT,
            review_3 TEXT,
            review_4 TEXT,
            review_5 TEXT,
            status  TEXT
        )
    """
    try:
        cur.execute(create_table_sql)
        con.commit()
        print("Table created successfully")
    except sqlite3.Error as e:
        print("An error occurred:", e)
    finally:
        con.close()



def open_website():
    Browser.open_available_browser(URL)
    Browser.click_button('//*[@id="onetrust-accept-btn-handler"]')

def get_excel_data():
    excel_lib.open_workbook(Excel_file)
    movie_table= excel_lib.read_worksheet_as_table (header=True)
    excel_lib.close_workbook()
   
    for movie in movie_table:
        logging.info(movie['Movie']) 
        if movie["Movie"]== "":
            break
        search_movie(movie['Movie'])
       
  

def search_movie(movie):
    get_movie = movie
    Browser.input_text('//*[@id="inner_search_v4"]', get_movie) 
    try:
        Browser.click_element('//*[@id="inner_search_form"]/input') 
    except:
        pass
    Browser.click_element_if_visible('//*[@id="movie"]')
    try:
        links_and_title = ('//*[@class="white_column"]//*[@class="card v4 tight"]/div/div[2]/div[1]/div/div/a')
        
        links_and_titles = Browser.get_webelements(links_and_title)
        release_dates = Browser.get_webelements("//*[@class='card v4 tight']/div/div[2]/div[1]/div/span")
        movie_data_list = [
            {'title': []},
            {'year': []},
            {'link': []}
        ]   
        for element,date in zip(links_and_titles,release_dates):
            logging.info(Browser.get_text(element))
            logging.info(Browser.get_text(date))
            logging.info(Browser.get_element_attribute(element, 'href'))

            title = Browser.get_text(element)
            title = title.strip()
            get_movie = get_movie.strip()
        
            if title == get_movie:
                year = Browser.get_text(date)
                year=year[-4:]
                href = Browser.get_element_attribute(element, 'href')
                movie_data_list[0]['title'].append(title)
                movie_data_list[1]['year'].append(year)
                movie_data_list[2]['link'].append(href)


    except:
        Browser.click_image("The Movie Database (TMDB)")   
        
    try:       
        if movie_data_list[0]['title']:
    
        # Zip the values into tuples
            zipped_data = zip(movie_data_list[0]['title'], movie_data_list[1]['year'], movie_data_list[2]['link'])

            # Sort based on the 'year' value
            sorted_data = sorted(zipped_data, key=lambda x: x[1], reverse=True)

            # Unzip the sorted data back into separate lists
            sorted_titles, sorted_years, sorted_links = zip(*sorted_data)
        try:
            first_link = sorted_links[0]
            print(first_link)

            Browser.go_to(first_link)
            extract_data(movie)
        except:
                   movie_data = {
            "movie_name": movie,
            "user_score": "N/A",
            "rating": "N/A",
            "mpaa": "N/A",
            "overview": "N/A",
            "genres": "N/A",
            "tagline": "N/A",
            "review_1": "N/A",
            "review_2": "N/A",
            "review_3": "N/A",
            "review_4": "N/A",
            "review_5": "N/A",
            "status": "No exact match found"
        }
        insert_into_table(movie_data)
        Browser.click_image("The Movie Database (TMDB)")
    except:
        Browser.click_image("The Movie Database (TMDB)")
    
    


def extract_data(movie):
    try:
        overview = Browser.get_text('//html/body/div[1]/main/section/div[2]/div/div/section/div[2]/section/div[2]/div/p')   
        overview = remove_punctuations(overview)
    except:
        overview= 'Overview not found'
    try:
        tagline = Browser.get_text('//*[@id="original_header"]/div[2]/section/div[2]/h3[1]')
        tagline = remove_punctuations(tagline)
    except:
        tagline= 'Tagline not found'    
    try:
        mpaa = Browser.get_text('//*[@id="original_header"]/div[2]/section/div[1]/div/span[1]')
    except:
        mpaa = 'mpaa rating not found'
    try:
        genres= Browser.get_text('//*[@id="original_header"]/div[2]/section/div[1]/div/span[3]')
    except:
        genres= 'Genres not found'
    # #rating and score
    try:
        Browser.wait_until_element_is_visible('//div[@class="user_score_chart"]')
        Browser.click_element('//div[@class="user_score_chart"]')
        score = Browser.get_element_attribute('//div[@class="user_score_chart"]', 'data-percent')
    except:
        score= "Score not found"
    try:
        Browser.wait_until_element_is_visible('//*[@id="rating_details_window"]/div/div[1]/div/div[2]/h3')
        rating= Browser.get_text('//*[@id="rating_details_window"]/div/div[1]/div/div[2]/h3')
    except:
        rating= 'Rating not found'

    # Browser.click_element(' //*[@id="rating_details_window"]/div/a/span')
    #reviews
    try:
        Browser.wait_until_element_is_visible('//*[@id="media_v4"]/div/div/div[1]/div/section[2]/section/div[2]/div/div/div/div/p/a')
        Browser.click_element('//*[@id="media_v4"]/div/div/div[1]/div/section[2]/section/div[2]/div/div/div/div/p/a')
       
        try:
            review_1 = Browser.get_text('//*[@id="media_v4"]/div/div/div[2]/div/section/div[1]/div[1]/div/div/div[2]/p[1]')
            review_1 = remove_punctuations(review_1)
        except:
            review_1 = 'No reviews'
        try:
            review_2 = Browser.get_text('//*[@id="media_v4"]/div/div/div[2]/div/section/div[1]/div[2]/div/div/div[2]/p[1]')
            review_2 = remove_punctuations(review_2)
        except:
            review_2 = "No reviews"
      
        try:
            review_3 = Browser.get_text('//*[@id="media_v4"]/div/div/div[2]/div/section/div[1]/div[3]/div/div/div[2]/p[1]')
            review_3 = remove_punctuations(review_3)
        except:
            review_3= 'No reviews'

      
        try:
            review_4 = Browser.get_text('//*[@id="media_v4"]/div/div/div[2]/div/section/div[1]/div[4]/div/div/div[2]/p[1]')
            review_4 = remove_punctuations(review_4)
        except:
            review_4 = "No reviews"
   
        try:
            review_5 = Browser.get_text('//*[@id="media_v4"]/div/div/div[2]/div/section/div[1]/div[5]/div/div/div[2]/p[1]')
            review_5 = remove_punctuations(review_5)
        except:
             review_5=  "No reviews" 
        status = 'Success' 

        
        movie_data = {
        "movie_name": movie,
        "user_score": score,
        "rating": rating,
        "mpaa": mpaa,
        "overview": overview,
        "genres": genres,
        "tagline": tagline,
        "review_1": review_1,
        "review_2": review_2,
        "review_3": review_3,
        "review_4": review_4,
        "review_5": review_5,
        "status": status
        }
        logging.info(movie_data)
        insert_into_table(movie_data)
    except:
        print("No Reviews")
    Browser.click_image('The Movie Database (TMDB)')

# create_table_movies()
def insert_into_table(movie_data):
    insert_sql = """
        INSERT INTO movies(
            movie_name, 
            user_score, 
            rating, 
            mpaa, 
            overview, 
            genres, 
            tagline, 
            review_1, 
            review_2, 
            review_3, 
            review_4, 
            review_5,
            status           
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cur.execute(insert_sql,(
        movie_data["movie_name"], 
        movie_data["user_score"], 
        movie_data["rating"], 
        movie_data["mpaa"], 
        movie_data["overview"], 
        movie_data["genres"], 
        movie_data["tagline"], 
        movie_data["review_1"], 
        movie_data["review_2"], 
        movie_data["review_3"], 
        movie_data["review_4"], 
        movie_data["review_5"], 
        movie_data['status']
    ))
    con.commit()
    data = cur.execute("Select * from movies")
    logging.info(data.fetchall())

def main():
    open_website()
    create_table_movies()
    get_excel_data()
    
    


if __name__ == "__main__":
    main()
