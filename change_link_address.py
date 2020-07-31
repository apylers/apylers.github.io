import os
import re
from bs4 import BeautifulSoup as bs
import json
import requests
from fontTools.subset import main as subset
import sys

tag = "v1.0.7"

cdn_url = "https://cdn.jsdelivr.net/gh/apylers/apylers.github.io@"
fontawesome_url = "https://fontawesome.com/cheatsheet/free/"

exclude_file_list = [".gitignore", "change_link_address.py", "CNAME", "favicon.png"]
exclude_dir_list = [
    ".git",
    ".idea",
    "background",
    "cover",
    "icon",
    "img",
    "search",
    "fonts",
]

original_font_dir = "../fonts/"
generate_font_dir = "fonts/"


def replace_with_jsdelivr(file_path):
    with open(file_path, "r", encoding="UTF-8") as f:
        content = f.read()
        new_content = re.sub(
            r"([:(=])((?:'|\"|))(https://cyh\.me)?/((?:background|cover|icon|img|search|css|js))",
            lambda x: x.group(1) + x.group(2) + cdn_url + tag + "/" + x.group(4),
            content,
        )
    with open(file_path, "w", newline="\n", encoding="UTF-8") as f:
        f.write(new_content)


def get_text_and_icon(file_path):
    soup = bs(open(file_path, encoding="UTF-8"), "lxml")
    content = set(soup.text)

    code = soup.find_all("code")
    figure_highlight = soup.find_all("figure", attrs={"class": "highlight"})
    _codeblock = soup.find_all(attrs={"class": "codeblock"})
    _gist = soup.find_all(attrs={"class": "gist"})

    code_family = code + figure_highlight + _codeblock + _gist
    code_content = set()
    if code_family:
        for code_sample in code_family:
            code_content |= set(code_sample.text)

    fas = soup.find_all(attrs={"class": "fas"})
    fas_icons = set()
    for fas_sample in fas:
        fas_icon_class = fas_sample.attrs["class"]
        for item in fas_icon_class:
            if "fa-" in item:
                fas_icons.add(item[3:])

    fab = soup.find_all(attrs={"class": "fab"})
    fab_icons = set()
    for fab_sample in fab:
        fab_icon_class = fab_sample.attrs["class"]
        for item in fab_icon_class:
            if "fa-" in item:
                fab_icons.add(item[3:])

    return content, code_content, fas_icons, fab_icons


def get_icon_unicode(all_icons):
    content = requests.get(fontawesome_url).text

    fontawesome_json = re.search(r"inline_data__ =(.*)", content).group(1)
    fontawesome = json.loads(fontawesome_json)

    unicodes = []
    all_icons_sorted = sorted(all_icons)
    i = 0
    for data in fontawesome[1]["data"]:
        if i >= len(all_icons_sorted):
            break
        if data["id"] == all_icons_sorted[i]:
            unicodes.append(data["attributes"]["unicode"])
            i += 1

    return unicodes


def subset_font(
    orginal_font_path,
    output_font_path,
    text="",
    unicodes="",
    flavor="",
    no_subset_tables="",
):
    argv = [None, orginal_font_path]
    if text:
        argv.append("--text=" + text)
    if unicodes:
        argv.append("--unicodes=" + unicodes)
    if flavor:
        argv.append("--flavor=" + flavor)
    if no_subset_tables:
        argv.append("--no-subset-tables" + no_subset_tables)
    argv.append("--output-file=" + output_font_path)

    sys.argv = argv
    subset()


g = os.walk(".")

all_code = set()
all_content = set()
all_fas = set()
all_fab = set()
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

            if os.path.splitext(file_path)[1] == ".html":
                content, code_content, fas_icons, fab_icons = get_text_and_icon(
                    file_path
                )
                all_content |= content
                all_code |= code_content
                all_fas |= fas_icons
                all_fab |= fab_icons

subset_font(
    original_font_dir + "SourceHanMonoSC-Regular.otf",
    generate_font_dir + "SourceHanMonoSC-Regular.woff2",
    text="".join(sorted(all_code)),
    flavor="woff2",
)
subset_font(
    original_font_dir + "SourceHanMonoSC-Bold.otf",
    generate_font_dir + "SourceHanMonoSC-Bold.woff2",
    text="".join(sorted(all_code)),
    flavor="woff2",
)

subset_font(
    original_font_dir + "SourceHanSerifSC-Regular.otf",
    generate_font_dir + "SourceHanSerifSC-Regular.woff2",
    text="".join(sorted(all_content)),
    flavor="woff2",
)
subset_font(
    original_font_dir + "SourceHanSerifSC-Bold.otf",
    generate_font_dir + "SourceHanSerifSC-Bold.woff2",
    text="".join(sorted(all_content)),
    flavor="woff2",
)

subset_font(
    original_font_dir + "Font-Awesome-solid.woff2",
    generate_font_dir + "Font-Awesome-solid.woff2",
    unicodes=",".join(get_icon_unicode(all_fas)),
    flavor="woff2",
    no_subset_tables="+=FFTM",
)
subset_font(
    original_font_dir + "Font-Awesome-brands.woff2",
    generate_font_dir + "Font-Awesome-brands.woff2",
    unicodes=",".join(get_icon_unicode(all_fab)),
    flavor="woff2",
    no_subset_tables="+=FFTM",
)
