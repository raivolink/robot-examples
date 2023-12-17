from robocorp.tasks import task
import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict


@dataclass
class Book:
    title: str
    price: str
    availability: str
    rating: str


@task
def scrape_sf_book():
    """
    Simple webscraper that gets info from page
    parses it to dataclass and prints result
    """
    r = httpx.get(
        "http://books.toscrape.com/catalogue/category/books/science-fiction_16/index.html"
    )

    tree = HTMLParser(r.content)

    books = tree.css(".product_pod")

    for book in books:
        book_info = Book(
            title=book.css_first(".product_pod h3 a").attributes["title"],
            price=book.css_first(".product_price .price_color").text(strip=True),
            availability=book.css_first(".product_price .instock.availability").text(
                strip=True
            ),
            rating=book.css_first(".star-rating").attributes["class"][12:],
        )

        print(book_info.price)
        print(asdict(book_info))
