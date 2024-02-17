from funda_scraper import FundaScraper

AREAS = ["delft,30km"]
MAX_PRICE = 450000
WANT_TO="buy"

if __name__ == '__main__':
    with open('README.md', 'w+') as readme:
      for area in AREAS:
        scraper_available = FundaScraper(
          area=area, 
          property_type="house",
          want_to=WANT_TO, 
          n_pages=1,
          max_price=MAX_PRICE
          )
        df = scraper_available.run(raw_data=False).drop(["photo", "descrip"], axis=1)
        readme.write(df.to_markdown())
