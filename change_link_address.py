import os
import re
from bs4 import BeautifulSoup as bs

tag = 'v1.0.2'
cdn_url = 'https://cdn.jsdelivr.net/gh/apylers/apylers.github.io@'

exclude_file_list = ['.gitignore', 'change_link_address.py', 'CNAME', 'favicon.png', 'code.txt', 'content.txt']
exclude_dir_list = ['.git', '.idea', 'background', 'cover', 'icon', 'img', 'search', 'fonts']


def replace_with_jsdelivr(file_path):
    with open(file_path, "r") as f:
        content = f.read()
        new_content = re.sub(r"https://cyh.me/((?:background|cover|icon|img|search|css|js))",
                             lambda x: cdn_url + tag + "/" + x.group(1),
                             content)
        new_content = re.sub(r"((?:'|\"))/((?:background|cover|icon|img|search|css|js))",
                             lambda x: x.group(1) + cdn_url + tag + "/" + x.group(2),
                             new_content)
    with open(file_path, "w", newline='\n') as f:
        f.write(new_content)


g = os.walk(".")

all_code = set()
all_content = set()
for path, dir_list, file_list in g:
    for exclude_dir in exclude_dir_list:
        if exclude_dir in path:
            break
    else:
        for file_name in file_list:
            if file_name in exclude_file_list:
                continue
            file_path = os.path.join(path, file_name)
            print(file_path)
            replace_with_jsdelivr(file_path)

            if os.path.splitext(file_path)[1] == '.html':
                soup = bs(open(file_path), 'lxml')
                all_content |= set(soup.text)

                code = soup.find_all('code')
                figure_highlight = soup.find_all('figure', attrs={'class': 'highlight'})
                _codeblock = soup.find_all(attrs={'class': 'codeblock'})
                _gist = soup.find_all(attrs={'class': 'gist'})

                code_family = code + figure_highlight + _codeblock + _gist
                if code_family:
                    for code in code_family:
                        all_code |= set(code.text)

with open("code.txt", "w", newline="\n") as f:
    f.write(''.join(sorted(all_code)))

with open("content.txt", "w", newline="\n") as f:
    f.write(''.join(sorted(all_content)))
