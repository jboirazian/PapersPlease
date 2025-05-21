from bs4 import BeautifulSoup
import requests



def search_google_scholar(query, pages=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    all_results = []

    for page in range(pages):
        start = page * 10
        url = f"https://scholar.google.com/scholar?start={start}&q={query}&hl=en&as_sdt=0,5"

        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            for item in soup.select('.gs_ri'):
                title_elem = item.select_one('.gs_rt')
                title = title_elem.text
                link = title_elem.a['href'] if title_elem.a else None

                doi = None
                if link and 'doi.org' in link:
                    doi = link.split('doi.org/')[-1]
                elif item.select_one('.gs_fl a[href*="doi"]'):
                    doi_link = item.select_one('.gs_fl a[href*="doi"]')['href']
                    doi = doi_link.split('doi.org/')[-1]

                snippet = item.select_one(
                    '.gs_rs').text if item.select_one('.gs_rs') else ''
                cited_by = item.select_one('.gs_fl a[href*="cites"]')
                cited_by = cited_by.text.split()[2] if cited_by else '0'

                all_results.append({
                    'title': title,
                    'link': link,
                    'doi': doi,
                    'snippet': snippet,
                    'cited_by': cited_by,
                    'page': page + 1
                })

        except Exception as e:
            print(f"Error: {e}")
            break

    return all_results