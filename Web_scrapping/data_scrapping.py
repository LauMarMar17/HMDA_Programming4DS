"""
This script...
"""
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup

def enter_web():
    url = "https://www.imdb.com/"
    browser = webdriver.Edge("msedgedriver.exe")
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
        # Menu:
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="imdbHeader-navDrawerOpen"]/span'))
        ).click()
        # Top 250 movies
        WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="imdbHeader"]/div[2]/aside[1]/div/div[2]/div/div[1]/span/div/div/ul/a[2]/span'))
        ).click()
        # sort by duration
        browser.find_element(By.XPATH, '//*[@id="sort-by-selector"]/option[8]').click()
    except TimeoutException:
        print("Error in finding top 250 movies.")
        pass
    element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/div/div[3]/section/div/div[2]/div/ul'))
    )
    table_html = element.get_attribute('outerHTML')
    
    soup = BeautifulSoup(table_html, "html.parser")
    
    titles = [title.text for title in soup.find_all('h3', class_='ipc-title__text')]
    # Remove numbers from titles
    titles = [title.split('.')[1] for title in titles]
    titles = [title[1:] for title in titles]

    califications = [calification.text for calification in soup.find_all('span', class_='ipc-rating-star ipc-rating-star--base ipc-rating-star--imdb ratingGroup--imdb-rating')]
    # from califications  only whats left of "\xa0"
    califications = [calification.split('\xa0')[0] for calification in califications]

    years = [year.text for year in soup.find_all('span', class_='sc-b0691f29-8 ilsLEX cli-title-metadata-item')]
    # from years only interested in what have 4 digits
    years = [year for year in years if len(year) == 4]

    durations = [duration.text for duration in soup.find_all('span', class_="sc-b0691f29-8 ilsLEX cli-title-metadata-item")]
    # from durations only interested if contains "m"
    durations = [duration for duration in durations if 'm' in duration]
    
    # DataFrame
    df = pd.DataFrame(list(zip(titles, years, durations, califications)), columns=['Title', 'Year', 'Duration', 'Calification'])
    # Save to csv
    df.to_csv('../Outputs/top_250_by_duration.csv', index=False)
    
def launching_dates(browser):
    try:
        # Menu
        WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="imdbHeader-navDrawerOpen"]/span'))
            ).click()
        # Lauching dates
        WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="imdbHeader"]/div[2]/aside[1]/div/div[2]/div/div[1]/span/div/div/ul/a[1]/span'))
            ).click()
    except TimeoutException:
        print("Error in finding launching dates.")
        pass
    element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/div/div[3]/section/section'))
    )
    table_html = element.get_attribute('outerHTML')
    soup = BeautifulSoup(table_html, "html.parser")

    # DataFrame with movie and release date
    df = pd.DataFrame(columns=['Date', 'Title'])

    tables = soup.find_all('article')
    for table in tables:
        date = table.find('h3', class_='ipc-title__text').text
        titles = [title.text for title in table.find_all('a', class_='ipc-metadata-list-summary-item__t')]
        # Add to dataframe
        for title in titles:
            df.loc[len(df)] = [date, title]
    # Save to csv
    df.to_csv('../Outputs/launching_dates.csv', index=False)
    


def main():
    # Enter the website
    browser = enter_web()
    # Get top 250 movies by duration
    top_250_by_duration(browser)
    # Get launching dates in Spain
    launching_dates(browser)
    pass


if __name__ == "__main__":
    pass