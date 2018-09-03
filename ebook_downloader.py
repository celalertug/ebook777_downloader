import requests
from bs4 import BeautifulSoup
import argparse
from pprint import pprint
import os


def download_book(book_page_url, savedir):
    try:
        r = requests.get(book_page_url)
    except requests.RequestException as e:
        print(e)
        return False

    if r.status_code == 200:
        try:
            so = BeautifulSoup(r.text, "html.parser")
            pdf = so.find_all("span", class_="downloadlist.txt-links")[0].find("a").get("href")
            title = so.find_all("div", class_="article-details")[0].find("h1", class_="title").text + ".pdf"

            print(savedir, title, "downloading....")
            r = requests.get(pdf, stream=True)
            with open("%s/%s" % (savedir, title), 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            print("finished")
            return True
        except:
            print("downloadlist.txt error")
            return False


def get_books_links(page_url):
    links = []
    try:
        r = requests.get(page_url)
    except requests.RequestException as e:
        print(e)
        return []

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        a = soup.find_all("a", class_="title")
        links = [i.get("href") for i in a]

    return links


def download_pagelink_on_category(category):
    links = []
    for i in range(200):
        u = "http://www.ebook777.com/%s/page/%d/" % (category, i)
        r = requests.get(u)
        if r.status_code == 404:
            break
        links.append(u)

    return links


def download_all_from_category(category, savedir="books", start_page=0, end_page=-1):
    if not os.path.isdir(savedir):
        os.mkdir(savedir)
    page_urls = download_pagelink_on_category(category)
    if end_page == -1:
        end_page = len(page_urls)
    page_urls = page_urls[start_page:end_page]
    for pu in page_urls:
        li = get_books_links(pu)
        for bookpage in li:
            download_book(bookpage, savedir)


def get_all_category_names():
    u = "http://www.ebook777.com"
    r = requests.get(u)
    so = BeautifulSoup(r.text, "html.parser")
    a = so.find_all("li", class_="cat-item")
    categs = [i.find("a").text for i in a]
    return categs


def read_download_file(pth):
    ret = []
    with open(pth, "r") as fp:
        for i in fp:
            ret.append(i)

    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--cat", help="category to downloadlist.txt")
    parser.add_argument("--list", help="list all categories", action="store_true")  # list categories
    parser.add_argument("--file", help="downloadlist.txt list")
    parser.add_argument("--savedir", help="download directory")
    parser.add_argument("--startpage", default=0)
    parser.add_argument("--endpage", default=-1)
    args = parser.parse_args()

    if args.list:
        pprint(get_all_category_names())

    elif args.cat:
        download_all_from_category(args.cat, savedir=args.savedir, start_page=args.startpage,
                                   end_page=args.endpage)

    elif args.file:
        cats = read_download_file(args.file)
        for cat in cats:
            download_all_from_category(cat, savedir=args.savedir, start_page=args.startpage,
                                       end_page=args.endpage)
