def generate_mla(entry):
    """Generate MLA citation"""
    authors = entry.author.split(' and ')
    if len(authors) == 1:
        author_str = authors[0]
    elif len(authors) == 2:
        author_str = f"{authors[0]} and {authors[1]}"
    else:
        author_str = f"{authors[0]} et al."

    citation = f"{author_str}. \"{entry.title}.\" "

    if entry.entry_type == 'article':
        citation += f"*{entry.journal}*, vol. {entry.volume}, no. {entry.number}, {entry.year}, pp. {entry.pages}."
    elif entry.entry_type == 'book':
        citation += f"*{entry.title}*, {entry.edition} ed., {entry.publisher}, {entry.year}."
    elif entry.entry_type == 'inproceedings':
        citation += f"*{entry.booktitle}*, edited by {entry.editor}, {entry.publisher}, {entry.year}, pp. {entry.pages}."
    else:
        citation += f"{entry.publisher}, {entry.year}."

    if entry.doi:
        citation += f" doi:{entry.doi}."

    return citation


def generate_apa(entry):
    """Generate APA citation"""
    authors = entry.author.split(' and ')
    if len(authors) == 1:
        author_str = authors[0]
    else:
        author_str = f"{authors[0]} et al."

    citation = f"{author_str} ({entry.year}). "

    if entry.entry_type == 'article':
        citation += f"{entry.title}. *{entry.journal}*, *{entry.volume}*({entry.number}), {entry.pages}."
    elif entry.entry_type == 'book':
        citation += f"{entry.title}. {entry.publisher}."
    elif entry.entry_type == 'inproceedings':
        citation += f"{entry.title}. In {entry.editor} (Ed.), *{entry.booktitle}* (pp. {entry.pages}). {entry.publisher}."
    else:
        citation += f"{entry.title}. {entry.publisher}."

    if entry.doi:
        citation += f" https://doi.org/{entry.doi}"

    return citation


def generate_chicago(entry):
    """Generate Chicago citation"""
    authors = entry.author.split(' and ')
    if len(authors) == 1:
        author_str = authors[0]
    else:
        author_str = f"{authors[0]} et al."

    citation = f"{author_str}. {entry.year}. "

    if entry.entry_type == 'article':
        citation += f"\"{entry.title}.\" *{entry.journal}* {entry.volume}, no. {entry.number}: {entry.pages}."
    elif entry.entry_type == 'book':
        citation += f"*{entry.title}*. {entry.publisher}."
    elif entry.entry_type == 'inproceedings':
        citation += f"\"{entry.title}.\" In *{entry.booktitle}*, edited by {entry.editor}, {entry.pages}. {entry.publisher}."
    elif entry.entry_type == 'incollection':
        citation += f"\"{entry.title}.\" In *{entry.booktitle}*, edited by {entry.editor}, {entry.pages}. {entry.publisher}."
    elif entry.entry_type in ['phdthesis', 'mastersthesis']:
        citation += f"\"{entry.title}.\" {entry.entry_type.replace('thesis', ' thesis').title()}, {entry.school}."
    elif entry.entry_type == 'techreport':
        citation += f"\"{entry.title}.\" Technical report, {entry.institution}."
    else:
        citation += f"\"{entry.title}.\""

    if entry.doi:
        citation += f" doi:{entry.doi}."

    return citation