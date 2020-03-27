import os
import re

tag = 'v1.0.1'
cdn_url = 'https://cdn.jsdelivr.net/gh/apylers/apylers.github.io@'


exclude_file_list = [r'.gitignore', r'change_link_address.py', r'CNAME', r'favicon.png']
exclude_dir_list = [r'.git', r'.idea', r'background', r'cover', r'icon', r'img', r'search']

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


g = os.walk(r".")

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
