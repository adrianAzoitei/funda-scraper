from funda_scraper import FundaScraper
from sheets import GoogleSheetsClient

AREAS = ["delft,30km"]
MAX_PRICE = 450000
WANT_TO="buy"

sheets_client = GoogleSheetsClient()

if __name__ == '__main__':
    with open('README.md', 'w+') as readme:
      for area in AREAS:
        scraper_available = FundaScraper(
          area=area, 
          property_type="house",
          exterior_space_type="garden",
          garden_orientation="south,west",
          want_to=WANT_TO, 
          n_pages=2,
          max_price=MAX_PRICE
          )
        df = scraper_available.run(raw_data=False)
        df = df[[
          "address",
          "price",
          "energy_label",
          "bedroom",
          "city",
          "house_age"
        ]]
        readme.write(df.to_markdown())
        sheets_client.update(df)
