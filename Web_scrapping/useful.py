"""
This script contains useful functions for the data scrapping process.
"""

from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

def extract_top250movie_data(soup):

    movie_data = []
    # "find_all" looks for all elements that match the search criteria and saves them in a list
    movie_names = soup.find_all("h3", class_="ipc-title__text")
    movie_cal = soup.find_all(
        "span",
        class_="ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating",
    )
    movie_reviews = soup.find_all("span", class_="ipc-rating-star--voteCount")
    movie_numbers = soup.find_all(
        "div", class_="sc-b0691f29-7 hrgukm cli-title-metadata"
    )

    for name, cal, reviews, numbers in zip(
        movie_names[1:], movie_cal, movie_reviews, movie_numbers
    ):
        movie_name = name.text.strip()
        name_index = movie_name.find(" ")

        if reviews == 0.0:
            movie_reviews = 0.0
        else:
            movie_reviews = reviews.text.strip().replace(")", "").replace("(", "")

        if cal == 0.0:
            movie_cal_str = 0.0
        else:
            movie_cal_str = cal.text.split()[0]

        movie_numbers = numbers.text.strip()
        year = movie_numbers[0:4]

        # process the duration of the movie based on the position of m, the minutes
        duration_index = movie_numbers.find("m")
        if duration_index != -1:
            duration = movie_numbers[4 : duration_index + 1]
            rating = movie_numbers[duration_index + 1 :].strip()

        # if there are no registered minutes, that is if the movie lasts 1 or 2 exact hours for example, there is no m so
        # it is processed from h and from the position of the "." of the movie rating.
        # Although the movie rating is an integer it is registered as a decimal ("7.0") so it always works
        else:
            duration_index = movie_numbers.find("h")
            rate_index = movie_numbers.find(".")
            duration = movie_numbers[duration_index - 1 : rate_index - 1]
            rating = movie_numbers[rate_index - 1 :]

        try:
            movie_cal = float(movie_cal_str)
            movie_data.append(
                (
                    movie_name[name_index + 1 :],
                    movie_cal,
                    movie_reviews,
                    year,
                    duration,
                    rating,
                )
            )
        except ValueError:
            print(
                f"Could not convert rating '{movie_cal_str}' for movie '{movie_name}' to a float."
            )

    return movie_data


def extract_newreleases_data(soup):
    df = pd.DataFrame(columns=['Date', 'Title', 'Genres'])

    tables = soup.find_all('article')
    for table in tables:
        movies = table.find_all('li', class_='ipc-metadata-list-summary-item ipc-metadata-list-summary-item--click sc-8c2b7f1f-0 eWVqBf') 
        for movie in movies:
            date = table.find('h3', class_='ipc-title__text').text
            titles = [title.text for title in movie.find_all('a', class_='ipc-metadata-list-summary-item__t')]
            genre = [genre.text for genre in movie.find_all('span', class_='ipc-metadata-list-summary-item__li')]
            # from genres select only those with 1 word
            genre = [g for g in genre if len(g.split()) == 1]
            # if there is no genre then add 'Unknown'
            if len(genre) == 0:
                genre = ['Unknown']
        
            # Add to dataframe
            for title in titles:
                df.loc[len(df)] = [date, title, genre]
    return df


def extract_accademyawards_data(browser):
    df = pd.DataFrame(columns=["Year", "Genres"])
    for i in range(2005, 2025):
        my_url = browser.current_url
        my_url = my_url[0:37] + str(i) + my_url[41:]
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="center-3-react"]/div/div/div[1]/h3/div[1]')
            )
        )
        table_html = element.get_attribute("outerHTML")
        soup = BeautifulSoup(table_html, "html.parser")
        refs = []
        for a in soup.find_all("a", href=True):
            refs.append(a["href"])
        refs = list(set([ref for ref in refs if "title" in ref]))
        genres_year = []
        for ref in refs:
            new_url = my_url[:21] + ref
            browser.get(new_url)
            tab = WebDriverWait(browser, 100).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="__next"]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/section/div[1]/div[2]',
                    )
                )
            )
            tab_html = tab.get_attribute("outerHTML")
            soup = BeautifulSoup(tab_html, "html.parser")
            genres = [
                genre.text for genre in soup.find_all("span", class_="ipc-chip__text")
            ]
            for g in genres:
                genres_year.append(g)
        browser.get(my_url)

        df.loc[len(df)] = [i, genres_year]
    return df

def time_to_mins(duracion):
    duracion = duracion.strip()  # Eliminar espacios en blanco al inicio y al final
    if 'h' in duracion and 'm' in duracion:
        horas, minutos = duracion.split('h ')
        horas = int(horas)
        minutos = int(minutos.replace('m', ''))
        return horas * 60 + minutos
    elif 'h' in duracion:
        horas = int(duracion.split('h')[0])
        return horas * 60
    elif 'm' in duracion:
        minutos = int(duracion.split('m')[0])
        return minutos
    else:
        return 0  # Si no se encuentra 'h' ni 'm', devolvemos 0 minutos

