from firecrawl import FirecrawlApp
import os
import re
from dotenv import load_dotenv
load_dotenv()
from pprint import pprint

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

app = FirecrawlApp(api_key = FIRECRAWL_API_KEY)
results = app.crawl(
    "https://www.inorco.in/",
    limit=100,  #Up to 100 pages
    scrape_options={
        "formats":["markdown"]  # Return the scraped data into markdown format
    }
)
crawl_result = results.model_dump()
os.makedirs("web_data",exist_ok = True)
for page in crawl_result["data"]:
    markdown = page["markdown"]
    metadata = page["metadata"]
    title = metadata.get("title")
    if not title:
        title = metadata.get("url").split("/")[-1].replace(".html","")
    filename = re.sub(r'[\\/*?:"<>|]',"",title)
    with open(f"web_data/{filename}.md",'w',encoding="utf-8") as f:
        f.write(markdown)


# print("Done")