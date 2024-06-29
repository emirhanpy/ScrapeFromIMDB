from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import time

class ScrapeFromIMDB:

    def __init__(self):
        links, titles, years, ratings, run_times, genres, certificates, directors, stars, votes, grosses =\
            [], [], [], [], [], [], [], [], [], [], []

        for i in range(1, 9):
            URL = f"https://www.imdb.com/list/ls000634294/?sort=list_order,asc&st_dt=&mode=detail&page={i}"
            print("Scraping from: ",URL)
            r = self.get_data(URL)
            self.check_response(r)
            html_page = r.text
            time.sleep(10)
            self.soup = BeautifulSoup(html_page, "html.parser")

            links.extend(self.movie_link())
            titles.extend(self.movie_titles())
            years.extend(self.movie_years())
            ratings.extend(self.movie_rating())

            run_time, genre, certificate = self.movie_details()
            run_times.extend(run_time)
            genres.extend(genre)
            certificates.extend(certificate)

            directors.extend(self.movie_directors())
            stars.extend(self.movie_stars())

            vote, gross = self.movie_votes_grosses()
            votes.extend(vote)
            grosses.extend(gross)


        self.df = self.lists_to_df(links, titles, years, ratings, run_times, genres, certificates, directors, stars,
                                  votes, grosses)
        print(self.df)

    def iter_page_count(self):
        movie_links = self.soup.find_all("a")
    def lists_to_df(self, links, titles, years, ratings, run_times, genres, certificates, directors, stars, votes, grosses):
        movie_data = {
            'LINK': links,
            'TITLE': titles,
            'YEAR_OF_RELEASE': years,
            'RATING': ratings,
            'RUN_TIME': run_times,
            'GENRE': genres,
            'CERTIFICATE': certificates,
            'DIRECTOR': directors,
            'STARS': stars,
            'VOTES': votes,
            'GROSS': grosses
        }

        df = pd.DataFrame(movie_data)

        return df
    def get_data(self,URL):

        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0'}
        r_headers = header
        r = requests.get(URL, headers=r_headers)

        return r

    def check_response(self,r):

        if r.status_code == 200:
            response = "Your response is successfully return."
        else:
            response = f"There is an error.: {r.status_code}"

        return print(response)

    def movie_link(self):

        movie_links = self.soup.find_all("a")
        link = "https://www.imdb.com"
        links = [link + movie_link.get('href') for movie_link in movie_links if '?ref_=ttls_li_tt'
                     in movie_link.get('href')]

        return links

    def movie_titles(self):

        movie_titles = self.soup.find_all('h3', class_='lister-item-header')
        titles = [movie_title.find('a').text.strip() for movie_title in movie_titles]

        return titles

    def movie_years(self):

        movie_years = self.soup.find_all('h3', class_='lister-item-header')

        years = []
        for movie_year in movie_years:
            year = movie_year.find('span', class_='lister-item-year text-muted unbold').text
            match = re.search(r'(\d{4})', year)
            if match:
                years.append(match.group(1))

        return years

    def movie_rating(self):

        movie_ratings = self.soup.find_all('div', class_='ipl-rating-widget')

        ratings = [movie_rating.find('span', class_='ipl-rating-star__rating').text.strip() for movie_rating in
                   movie_ratings]

        return ratings

    def movie_details(self):

        movie_details = self.soup.find_all("div", class_="lister-item-content")

        run_times = []
        genres = []
        certificates = []
        for movie_detail in movie_details:

            run_time = movie_detail.find('span', class_='runtime')
            if run_time:
                run_times.append(run_time.text.strip())
            else:
                run_times.append("NA")

            genre = movie_detail.find('span', class_='genre')
            if genre:
                genres.append(genre.text.strip())
            else:
                genres.append("NA")

            certificate = movie_detail.find('span', class_="certificate")
            if certificate:
                certificates.append(certificate.text.strip())
            else:
                certificates.append("NA")

        return run_times, genres, certificates

    def movie_directors(self):

        movie_details = self.soup.find_all("p", class_="text-muted text-small")

        directors = []
        for movie_detail in movie_details:
            director_link = movie_detail.find("a", href=lambda href: href and "?ref_=ttls_li_dr_" in href)
            star_link = movie_detail.find("a", href=lambda href: href and "?ref_=ttls_li_st_" in href)
            if director_link:
                director = director_link.text.strip()
                directors.append(director)
            elif star_link:
                directors.append("NA")

        return directors

    def movie_stars(self):

        stars = []
        movie_details = self.soup.find_all("p", class_="text-muted text-small")
        for movie_detail in movie_details:
            star_links = movie_detail.find_all("a", href=lambda href: href and "?ref_=ttls_li_st_" in href)
            director_link = movie_detail.find("a", href=lambda href: href and "?ref_=ttls_li_dr_" in href)

            if star_links:
                star_list = []
                for star_link in star_links:
                    star = star_link.text.strip()
                    star_list.append(star)
                stars.append(star_list)
            elif director_link:
                stars.append("NA")

        return stars

    def movie_votes_grosses(self):
        movies_votes_gross = self.soup.find_all("div", class_="lister-item-content")

        grosses = []
        votes = []
        votes_grosses = {}
        for mvg in movies_votes_gross:
            vote = mvg.find("span", string="Votes:").find_next_sibling("span").text
            gross = mvg.find('span', string='Gross:').find_next('span').text if mvg.find('span', string='Gross:') else "NA"
            votes_grosses[vote] = gross

        for v, g in votes_grosses.items():
            grosses.append(g)
            votes.append(v)

        return votes, grosses

ScrapeFromIMDB()

