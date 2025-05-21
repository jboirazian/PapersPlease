from scidownl import scihub_download
import os


def download_papers(results, download_dir='papers'):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    downloaded = []

    for result in results:
        title = result['title']
        if title:
            try:
                filepath = f"{download_dir}/{title[:100].strip().replace('/', '-')}.pdf"
                if os.path.exists(filepath):
                    downloaded.append(filepath)
                else:
                    scihub_download(title, paper_type="title", out=filepath)
                    if os.path.exists(filepath):
                        downloaded.append(filepath)
            except Exception as e:
                print(f"Failed to download '{title}': {e}")
    return downloaded