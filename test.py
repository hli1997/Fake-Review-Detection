from bs4 import BeautifulSoup  
import requests
import time
import urllib.parse
from urllib.parse import urlparse
from urllib.parse import urljoin





def scrape_reviews(url):
    reviews = []
    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + '://' + parsed_url.netloc
    while True:
        # send a request to the URL and get the HTML content
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
        for i in range(3):  # retry the request up to 3 times
            try:
                r = requests.get(url, headers=headers)
                html_content = r.text
                break  # if the request was successful, break the loop
            except requests.exceptions.RequestException:
                time.sleep(1)  # delay for 1 second before retrying
        else:  # if the request was not successful after 3 tries, raise an exception
            raise requests.exceptions.RequestException('Error: the request was not successful')

        # parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        # find all the review elements on the page
        review_elements = soup.find_all(class_='a-size-base review-text review-text-content')
        # extract the text from each review element and append it to the reviews list
        for element in review_elements:
            review = element.get_text()
            reviews.append(review)
        # find the "Next" button element
        next_button = soup.find(class_='a-last')
        # check if the "Next" button element exists
        if next_button is None:
            # if the "Next" button does not exist, we have reached the last page
            print('dddd')
            break
        # if the "Next" button exists, get the URL of the next page
        next_url = next_button.get('href')
        url =  urljoin(base_url , next_url)
        # return soup
    return reviews


print(scrape_reviews('https://www.amazon.com/Nautica-Navtech-Folding-Travel-Umbrella/product-reviews/B0B359H7GS/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'))
reviews = scrape_reviews('https://www.amazon.com/Nautica-Navtech-Folding-Travel-Umbrella/product-reviews/B0B359H7GS/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews')
for review in reviews:
    print(review)

# def test(url):
    
#     parsed_url = urlparse(url)
#     base_url = parsed_url.scheme + '://' + parsed_url.netloc
#     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
#     for i in range(3):  # retry the request up to 3 times
#         try:
#                 r = requests.get(url, headers=headers)
#                 html_content = r.text
#                 break  # if the request was successful, break the loop
#         except requests.exceptions.RequestException:
#                 time.sleep(1)  # delay for 1 second before retrying
#         else:  # if the request was not successful after 3 tries, raise an exception
#             raise requests.exceptions.RequestException('Error: the request was not successful')

#         # parse the HTML content
#     soup = BeautifulSoup(html_content, 'html.parser')
#     next_button = soup.find('a', text='Next page')
#     if next_button is not None:
#         next_url = next_button.get('href')
#         url =  urljoin(base_url , next_url)
#     return url

# print(test('https://www.amazon.com/Nautica-Navtech-Folding-Travel-Umbrella/product-reviews/B0B359H7GS/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'))
