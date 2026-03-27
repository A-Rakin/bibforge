from app.models import BibEntry


def check_duplicate_doi(doi):
    """Check if DOI already exists in database"""
    if doi:
        existing = BibEntry.query.filter_by(doi=doi).first()
        return existing is not None
    return False


def validate_required_fields(data, entry_type):
    """Validate required fields based on entry type"""
    required_fields = {
        'article': ['title', 'author', 'year', 'journal'],
        'book': ['title', 'author', 'year', 'publisher'],
        'inproceedings': ['title', 'author', 'year', 'booktitle'],
        'incollection': ['title', 'author', 'year', 'booktitle'],
        'phdthesis': ['title', 'author', 'year', 'school'],
        'mastersthesis': ['title', 'author', 'year', 'school'],
        'techreport': ['title', 'author', 'year', 'institution'],
        'unpublished': ['title', 'author', 'year', 'note']
    }

    missing = []
    for field in required_fields.get(entry_type, []):
        if not data.get(field):
            missing.append(field)

    return missing