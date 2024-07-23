import requests
from parsel import Selector
import pandas as pd
from urllib.parse import urljoin
import pathlib

def scrape_page(page_number):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 10066.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}
    url = f'https://www.yellowpages.ca/search/si/{page_number}/restaurants/Toronto+ON'
    print('GETTING URL:', url)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch page {page_number}. Status code: {response.status_code}")
        return []

    selector = Selector(response.text)
    cards = selector.css('div[class="listing__content__wrapper"]')

    results = []
    for card in cards:
        data = {
            'Name': card.css('a[class="listing__name--link listing__link jsListingName"]::text').get(),
            'logo': card.css('a[class="listing__logo--link sponsologolink"] img[class^="jsMerchantLogo"]::attr(src)').get() or card.css('a[class="listing__logo--link sponsologolink"] img[class^="jsMerchantLogo"]::attr(data-src)').get(),
            'merchant_status': card.css('div[class="merchant__status tooltip__toggle see-hours"] a::text').get(),
            'full_adress': ','.join(card.css('span[class="listing__address--full"] span::text').getall()),
            'streetAdress': card.css('span[itemprop="streetAddress"]::text').get(),
            'adressLocality': card.css('span[itemprop="addressLocality"]::text').get(),
            'adressRegion': card.css('span[itemprop="addressRegion"]::text').get(),
            'postalCode': card.css('span[itemprop="postalCode"]::text').get(),
            'listing_captext': card.css('div[class="listing__captext"]::text').get(),
            'description': ''.join([response.strip() for response in card.css('article[itemprop="description"]::text, article[itemprop="description"] > span.no-js::text').getall()]),
            'review': card.css('span[class="bestReviewText"]::text').get(),
            'phone': card.css('a[class="mlr__item__cta jsMlrMenu"]::attr(data-phone)').get(),
            'direction': urljoin('https://www.yellowpages.ca/', card.css('a[class="mlr__item__cta link jsClickPrevent"]::attr(href)').get()) if card.css('a[class="mlr__item__cta link jsClickPrevent"]::attr(href)').get() else None,
            'website': urljoin('https://www.yellowpages.ca/', card.css('li[class="mlr__item mlr__item--website "] a::attr(href)').get()) if card.css('li[class="mlr__item mlr__item--website "] a::attr(href)').get() else None,
            'reservation': urljoin('https://www.yellowpages.ca/', card.css('a[title="Book now"]::attr(href)').get()) if card.css('a[title="Book now"]::attr(href)').get() else None,
            'orderonline': card.css('li[class="mlr__item mlr__item--orderonline"] a::attr(href)').get(),
            'rating_Stars': card.css('span[class="ypStars jsReviewsChart"]::attr(title)').get(),
            'rating_value': card.css('div[class="listing__rating ratingWarp"] > a[class="listing__ratings__count listing__link"]::text').get('').replace('(', '').replace(')', '').strip(),
            'ratingWrap_partner': card.css('span[class="listing__link listing-quote"]::text').get(),
            'ratingLink': urljoin('https://www.yellowpages.ca/', card.css('div[style="font-weight: 400;padding-bottom: 5px;"] a::attr(href)').get()) if card.css('div[style="font-weight: 400;padding-bottom: 5px;"] a::attr(href)').get() else None
        }
        results.append(data)
    return results

def main():
    final_data = []
    for page_number in range(1, 3):  # Scraping first 2 pages for demonstration
        page_data = scrape_page(page_number)
        final_data.extend(page_data)

    csv_name = 'Mostafa_yellowPage_Scraping'
    df = pd.DataFrame(final_data)
    csvfile = pathlib.Path(f'{csv_name}.csv')
    df.to_csv(csvfile, mode='a', index=False, header=not csvfile.exists())

if __name__ == "__main__":
    main()
