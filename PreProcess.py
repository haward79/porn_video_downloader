
from typing import List
from pathlib import Path
from bs4 import BeautifulSoup


def extract_url_from_html(html_filepath: str, url_filepath: str) -> bool:
    if Path(html_filepath).is_file():
        if Path(url_filepath).exists():
            is_overwrite = input(f'Output filepath "{url_filepath}" does exist. Overwrite? [y/N] ')

            if is_overwrite.lower() != 'y':
                print(f'Output filepath "{url_filepath}" does exist. To prevent from overwrite, aborted.')
                return False

        with open(html_filepath, 'r') as fin:
            source_code = fin.read()

        bs = BeautifulSoup(source_code, "html.parser")
        link_elements = bs.find_all('a')
        links = [element.attrs.get('href') for element in link_elements]

        with open(url_filepath, 'w') as fout:
            fout.write('\n'.join(links))

        return True

    else:
        print(f'Input filepath "{html_filepath}" does NOT exist.')
        return False


def remove_duplicated_url(urls: List[str]) -> List[str]:
    return list(set(urls))


if __name__ == '__main__':
    extract_url_from_html('firefox.html', 'firefox')
    extract_url_from_html('edge.html', 'edge')
