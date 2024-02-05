'''
BeautifulSoup - library for parsing (rozebirani) HTML and XML, SSL Certificate Verification, Work with Sessions,
transforms a complex HTML document into a complex tree of Python objects.
You can use BeautifulSoup with various parsers (html.parser, lxml, html5lib)
Uses methods and attributes such as .find(), .find_all(), .children, .parent, etc.
Find elements by tag name, attribute values, CSS class, string content, or using functions with more complex logic.
Modify the parse tree - add, remove, or alter tags, attributes, and strings. This useful for cleaning up HTML or
extracting and transforming data.
Format the modified document in a nicely formatted string. With its prettify().

------------------------------------------------------------------------------------------------------------------------
requests:
- library, HTTP client to send HTTP requests easily, Send HTTP Requests, Handle Redirects, Error Handling
  Handle JSON Data, Pass URL Parameters, Send Headers and Cookies
- how it works:
    Opening a Socket -  establish a connection (TCP/IP), uses the http.client module.
                        It starts by resolving the domain name of the URL to an IP address (DNS lookup) 
                        and then opens a TCP socket to the server on the standard HTTP (80) or HTTPS (443) port. 
                        For HTTPS connections, requests also handles the SSL/TLS handshake to secure the connection
    Sending HTTP Request - requests prepares the HTTP headers, body, URL, data, files ..., via urllib3 (HTTP client) 
                           it establishes a connection. Request data (if any) is encoded as needed. 
                           Requests hands off the prepared request to urllib3, which sends the HTTP req. 
                           For HTTPS requests, urllib3 also handles the SSL/TLS handshake to secure the connection.
                           urllib3 waits for resp., reads its headers and body, then passes it back to requests, 
                           which then parses the response and makes it easily accessible to your Python code.
    Server Processes Request
    Receiving HTTP Response
    Closing the Connection
- requests vs scapy: requests is for working with HTTP at a higher level, making web-related tasks simpler 
                     and more intuitive. Scapy is used for deeper network analysis and packet manipulation.

------------------------------------------------------------------------------------------------------------------------

WEP PAGES FOR PRACTISE:
- Respect the robots.txt file of websites.
HTTrack Website Copier - Not a website to scrape, tool to download a website to local disk. 
                         Useful for practicing scraping locally without sending requests to actual website.
HTTPBin - For testing requests, parsing responses.
JSONPlaceholder- fake online REST API for testing. Great for practicing parsing JSON data.
Books to Scrape - fake bookstore website for scraping practice.For practice scraping data like titles, prices, ratings..
Quotes to Scrape - same, for scraping practice
HackerRank, LeetCode - not for web scraping, challenges that involve parsing and processing data.

------------------------------------------------------------------------------------------------------------------------

requests.get(url):
    - it returns Response object: status_code, text, content. json(), headers, url of server, cookies, ...

classes:
- Dynamic Attributes - u can add it anytime, less organized
- Using __init__ - recommended to declare attributes within the __init__ method (or in the class body for class attributes shared by all instances)
- If use different name then __init__-not recognize it as constructor, not called automatically when new class instance.
- __slots__ = [], when define slots, user cant add new attributes in project.
- self - to access attributes that belong to a specific instance of the class, to call other methods from within the same class,
       - first parameter, when you call a method, you don't need to pass self, python does it for you.
'''
# app for scraping book name, price and rating
import requests, re, logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from logging.handlers import RotatingFileHandler

base_url = 'http://books.toscrape.com/'

text_to_num = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}


class Book:
    # Class attribute - same value for all instances
    type = "book"
    __slots__ = ['title', 'price', 'category', 'rating', 'availability']

    def __init__(self, title, price, rating, category=None, availability=None):
        self.title = title
        self.price = price
        self.rating = rating
        self.category = category
        self.availability = availability


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # RotatingFileHandler - for dealing with log limit
    file_handler = RotatingFileHandler('books_log.log', maxBytes=1024 * 1024 * 500, backupCount=5)
    console_handler = logging.StreamHandler()

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def format_text(unformulated_text):
    formatted_text = unformulated_text.strip().replace('\n', ' ').replace('\r', '')
    return formatted_text


def get_html(url):
    response = requests.get(url)
    unformulated_html = response.content
    formatted_html = BeautifulSoup(unformulated_html, 'html.parser')
    return formatted_html


def get_books(logger):
    books = []
    page_number = 1
    try:
        while True:
            url = urljoin(base_url, f'/catalogue/page-{page_number}.html')
            try:
                page = get_html(url)
            except Exception as e:
                logger.error(f'Error: {e}')
                print(f'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA konec asi {page_number}')

                break

            for bookEl in page.find_all('article', class_='product_pod'):
                title = format_text(bookEl.find('h3').find('a').get('title'))

                price_in_text = bookEl.find(class_='price_color').text
                price = float(price_in_text.replace('£', ''))

                rating_in_text = bookEl.select_one("[class^='star-rating']").get('class')[1]
                # "Unknown rating" is default value, if in dict ist the word
                rating = text_to_num.get(rating_in_text, "Unknown rating")

                book = Book(title=title, price=price, rating=rating)

                try:
                    detail_page_html = get_html(urljoin(base_url, urljoin('catalogue/', bookEl.find('a').get('href'))))
                    breadcrumbs = detail_page_html.find(class_="breadcrumb").find_all('li')
                    book.category = breadcrumbs[len(breadcrumbs) - 2].text.strip().replace('\n', '').replace('\r', '')

                    def find_availability_tr(element):
                        return element.name == 'tr' and 'Availability' in element.text

                    # costume filter function for finding elements
                    availability_in_text = detail_page_html.find(find_availability_tr).find('td').text
                    book.availability = int((re.findall(r'\d+', availability_in_text))[0])
                except Exception as e:
                    logger.error(f'Error: {e}')
                    books.append(book)
                    logger.info(f'Added book:\nTitle: {book.title}\nPrice: {book.price}\nRating: {book.rating}\n')
                else:
                    books.append(book)
                    logger.info(
                        f'Added book:\nTitle: {book.title}\nPrice: {book.price}\nRating: {book.rating}\nCategory: {book.category}\nAvailability: {book.availability}\n')
            page_number += 1
    except KeyboardInterrupt:
        return books
    return books


def main():
    logger = setup_logging()
    logger.info('*** WEB SCRAPING APP ***')

    books = get_books(logger)

    logger.info(f'Books scraped: {len(books)}.\nEnding scraping.')


if __name__ == "__main__":
    main()
