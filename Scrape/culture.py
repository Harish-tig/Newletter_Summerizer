import bs4
from urllib.parse import urljoin
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
import asyncio
import aiohttp
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')





#Global variable
culture_link=[]
def url_join():
    url = "https://bbc.com"
    global culture_link
    culture_link = [urljoin(url, link) if not link.startswith("http") else link for link in culture_link]

async def fetch_page(session,url:str): #used in #used in scrape_element function and summarize_as
    async with session.get(fr"{url}") as response:
        return await response.text()

async def scrape_element(session, url, tag):
    global culture_link
    head = []
    para = []
    image = []
    content = await fetch_page(session=session, url = url)
    soup = bs4.BeautifulSoup(content,"html.parser")
    tags = soup.select(f"{tag}")

    for elements in tags:
        h2 = elements.select("h2")
        p = elements.select("p")
        img = elements.select('img[src]')
        ##check if both tags present extract iff <=> both present
        if h2 and p:
            head.append(h2[0].getText())
            para.append(p[0].getText())
            culture_link.append(elements.get('href'))
            if img:
                image.append(img[1]['src'])
            else:
                image.append("/static/images/noimage.png")

    url_join()

    sum_news =  await summarize(culture_link)

    return zip(head, para, image, sum_news,culture_link)

def foo():
    pass


async def summarize(link_list):
    summaries = []
    async with aiohttp.ClientSession() as session:
        try:
            # Fetch all pages concurrently
            tasks = [fetch_page(session, x) for x in link_list]
            pages = await asyncio.gather(*tasks)

            parser = PlaintextParser  # Moved outside to avoid recreation in each iteration
            summarizer = TextRankSummarizer()

            for idx, page_content in enumerate(pages):
                if not page_content:
                    summaries.append(f"No content returned from {link_list[idx]}.")
                    continue

                # Parse the HTML content
                soup = bs4.BeautifulSoup(page_content, "html.parser")
                article_tag = soup.find('article')

                if article_tag:
                    paragraphs = article_tag.find_all('p')
                    text = " ".join([p.get_text() for p in paragraphs])

                    if text.strip():  # Ensure the text is not empty
                        # Parse and summarize the text
                        parsed_text = parser.from_string(text, Tokenizer("english"))
                        summary = summarizer(parsed_text.document,  min(6, max(1, len(text.split()) // 30)))

                        # Join summarized sentences
                        summary_sentences = " ".join(str(sentence) for sentence in summary)
                        summaries.append(summary_sentences)
                    else:
                        summaries.append("Article content is empty.")
                else:
                    summaries.append("Article tag not found.")
        except Exception as e:
            summaries.append(f"An error occurred: {e}")

    return summaries


async def culture_function():
    url = 'https://bbc.com/culture'
    async with aiohttp.ClientSession() as session:
        news = await scrape_element(session=session,url=url,tag="a")
        context = {
            "culture_news" : news
        }
        return context

