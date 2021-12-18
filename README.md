# tokopediawebscraper

is a simple web scraper for tokopedia using modules selenium, beautifulsoup4, Pandas

### Usage

install the required package:

```python
pip install -r requirements.txt
```

change products to be scraped on

```python
scraper = TokopediaScraper("https://www.tokopedia.com/p/handphone-tablet/handphone?od=5")
scraper.doScraping(100)
```

run tokopediaWebscraper.py

```python
python tokopediaWebscraper.py
```
