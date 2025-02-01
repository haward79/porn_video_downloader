
from typing import List
import inspect
from pathlib import Path
from bs4 import BeautifulSoup

from Main import BashColor


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


def extract_url_from_html_demo():
    print(f'Call function {BashColor.GREEN}extract_url_from_html', inspect.signature(extract_url_from_html), BashColor.CLEAR)

    param_values = []

    for param in inspect.signature(extract_url_from_html).parameters:
        param_values.append(input(f'Parameter {BashColor.GREEN}{param}{BashColor.CLEAR}: '))

    extract_url_from_html(*param_values)


if __name__ == '__main__':
    extract_url_from_html_demo()
