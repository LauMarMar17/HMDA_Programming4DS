"""
This script...
"""
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from bs4 import BeautifulSoup # class for web scraping. It allows you to interact with HTML in a similar way to how you would interact with a web page using developer tools.
import requests

def extract_movie_data(soup):

    movie_data = []
    #find_all busca todos los elementos que coincidan con los criterios de búsqueda y los guarda en una lista
    movie_names = soup.find_all('h3', class_='ipc-title__text')
    movie_cal = soup.find_all('span', class_='ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating')
    movie_reviews = soup.find_all('span', class_='ipc-rating-star--voteCount')
    movie_numbers = soup.find_all('div', class_="sc-b0691f29-7 hrgukm cli-title-metadata")

    # Rest of the code

    for name, cal, reviews, numbers in zip(movie_names[1:], movie_cal, movie_reviews, movie_numbers):
        movie_name = name.text.strip()
        name_index=movie_name.find(" ")

        #Se procesan algunos datos
        if reviews == 0.0:
            movie_reviews = 0.0
        else:
            movie_reviews = reviews.text.strip().replace(')', '').replace('(', '')

        if cal == 0.0:
            movie_cal_str = 0.0
        else:
            movie_cal_str = cal.text.split()[0]

        movie_numbers = numbers.text.strip()
        #print(len(movie_numbers))

        year = movie_numbers[0:4]

        #procesar duracion de la película enfunción de la posicion de m, los minutos
        duration_index = movie_numbers.find("m")
        if duration_index != -1:
            duration = movie_numbers[4:duration_index+1]
            rating = movie_numbers[duration_index+1:].strip()

        #si no hay regsitrados minutos, es decir, si la película dura 1 o 2 horas exactas por ejemplo, no hay m así que
        #se procesa a partir de h y de la posición del "." de la puntuación de la película.
        #Aunque la puntuación de la película sea un numero entero se registra como decimal ("7.0") así que funciona siempre
        else:
            duration_index = movie_numbers.find("h")
            rate_index = movie_numbers.find(".")
            duration = movie_numbers[duration_index-1:rate_index-1]
            rating = movie_numbers[rate_index-1: ]


        try:
            movie_cal = float(movie_cal_str)
            movie_data.append((movie_name[name_index+1:], movie_cal, movie_reviews, year, duration, rating))
        except ValueError:
            print(f"Could not convert rating '{movie_cal_str}' for movie '{movie_name}' to a float.")

    return movie_data

def enter_web():
    url = "https://www.imdb.com/"
    browser = webdriver.Edge("Web_scrapping/msedgedriver.exe")
    browser.maximize_window()
    browser.get(url)
    
    
    try:
        # Accept Cookies
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div/div/div[2]/div/button[2]'))
        ).click()
    except TimeoutException:
        print("Error.Try again.")
        browser.quit()
    return browser
        
def top_250_by_duration(browser):
    try:
        # Menu
        WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="imdbHeader-navDrawerOpen"]/span'))
            ).click()
        # Top 250 movies
        WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="imdbHeader"]/div[2]/aside[1]/div/div[2]/div/div[1]/span/div/div/ul/a[2]/span'))
            ).click()
    except TimeoutException:
        print("Error in finding top 250 movies.")
        pass
    
    
    my_url = browser.current_url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    soup = BeautifulSoup(requests.get(my_url, headers=headers).content, "html.parser")
    data = extract_movie_data(soup)
    df = pd.DataFrame(data, columns=['Movie', 'Calification', 'N.Reviews', 'Year', 'Duration', 'Rating'])
    df.to_csv('Outputs/top_250_by_duration.csv', index=False)
    
def launching_dates(browser):
    try:
        # Menu
        WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="imdbHeader-navDrawerOpen"]/span'))
            ).click()
        # Comming Movies
        WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="imdbHeader"]/div[2]/aside[1]/div/div[2]/div/div[1]/span/div/div/ul/a[1]/span'))
            ).click()
        # Tabla de lanzamientos
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/div/div[3]/section/section'))
        )
    except TimeoutException:
        print("Error in finding launching dates.")
        pass
    
    table_html = element.get_attribute('outerHTML')
    soup = BeautifulSoup(table_html, "html.parser")

    # DataFrame with movie, release date and genre
    df = pd.DataFrame(columns=['Date', 'Title', 'Genre'])

    tables = soup.find_all('article')
    for table in tables:
        date = table.find('h3', class_='ipc-title__text').text
        titles = [title.text for title in table.find_all('a', class_='ipc-metadata-list-summary-item__t')]
        genre = [genre.text for genre in table.find_all('span', class_='ipc-metadata-list-summary-item__li')[0]]
        # Add to dataframe
        for title in titles:
            df.loc[len(df)] = [date, title, genre]
    # Save to csv
    df.to_csv('Outputs/launching_dates.csv', index=False)

def accademy_awards(browser):
    try:
        # Menu
        WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="imdbHeader-navDrawerOpen"]/span'))
            ).click()
        #
        WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="imdbHeader"]/div[2]/aside[1]/div/div[2]/div/div[3]/span/div/div/ul/a[1]/span'))
            ).click()

        WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/main/div/div[3]/div[2]/div/div[2]/ul/a[2]/span '))
            ).click()
        WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="sidebar"]/div[1]/div/div[2]/div[16]/span[6]/a'))
            ).click()
    except TimeoutException:
        print("Error in finding accademy awards.")
        pass
    
    df_awards = pd.DataFrame(columns=['Year', 'Genres'])
    # We are only interested in the best picture category in the last 20 years
    for i in range(2005,2025):
        my_url = browser.current_url
        my_url = my_url[0:37]+str(i)+my_url[41:]
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="center-3-react"]/div/div/div[1]/h3/div[1]'))
        )
        table_html = element.get_attribute('outerHTML')
        soup = BeautifulSoup(table_html, "html.parser")
        refs = []
        for a in soup.find_all('a', href=True):
            refs.append(a['href'])
        refs = list(set( [ref for ref in refs if 'title' in ref]))
        genres_year = []
        for ref in refs:
            new_url = my_url[:21]+ref
            browser.get(new_url)
            tab = WebDriverWait(browser, 100).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]'))
            )
            tab_html = tab.get_attribute('outerHTML')
            soup = BeautifulSoup(tab_html, "html.parser")
            genres = [genre.text for genre in soup.find_all('span', class_='ipc-chip__text')]
            for g in genres:
                genres_year.append(g)
        browser.get(my_url)

        df_awards.loc[len(df_awards)] = [i, genres_year]
    df_awards.to_csv('Outputs/awards.csv', index=False)



def main():
    # Enter the website
    browser = enter_web()
    # Get top 250 movies by duration
    top_250_by_duration(browser)
    # Get launching dates in Spain
    launching_dates(browser)
    # Get accademy awards nominees for best movie in the last 20 years
    accademy_awards(browser)
    print('Done')


if __name__ == "__main__":
    main()