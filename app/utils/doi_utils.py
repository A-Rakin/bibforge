import requests
import re


def fetch_doi_metadata(doi):
    """Fetch metadata from DOI using Crossref API"""
    try:
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            message = data.get('message', {})

            metadata = {
                'title': message.get('title', [''])[0] if message.get('title') else '',
                'author': ' and '.join([f"{author.get('family', '')}, {author.get('given', '')}"
                                        for author in message.get('author', [])]) if message.get('author') else '',
                'year': message.get('issued', {}).get('date-parts', [[None]])[0][0],
                'journal': message.get('container-title', [''])[0] if message.get('container-title') else '',
                'volume': message.get('volume', ''),
                'number': message.get('issue', ''),
                'pages': message.get('page', ''),
                'publisher': message.get('publisher', '')
            }

            return metadata
    except Exception as e:
        print(f"DOI fetch error: {e}")

    return None


def validate_doi(doi):
    """Validate DOI format"""
    pattern = r'^10.\d{4,9}/[-._;()/:A-Z0-9]+$'
    return bool(re.match(pattern, doi, re.IGNORECASE))