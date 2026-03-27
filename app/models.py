from app import db
from datetime import datetime


class BibEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_type = db.Column(db.String(50), nullable=False)
    citation_key = db.Column(db.String(100), unique=True, nullable=False)
    doi = db.Column(db.String(100), unique=True)
    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    # Article fields
    journal = db.Column(db.String(200))
    volume = db.Column(db.String(50))
    number = db.Column(db.String(50))
    pages = db.Column(db.String(50))

    # Book fields
    publisher = db.Column(db.String(200))
    address = db.Column(db.String(200))
    edition = db.Column(db.String(50))

    # Inproceedings/Incollection fields
    booktitle = db.Column(db.String(200))
    editor = db.Column(db.Text)

    # Thesis fields
    school = db.Column(db.String(200))

    # Techreport fields
    institution = db.Column(db.String(200))
    report_type = db.Column(db.String(100))

    # Common fields
    month = db.Column(db.String(20))
    note = db.Column(db.Text)
    url = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_bibtex(self):
        fields = []

        # Common fields
        if self.author:
            fields.append(f"  author = {{{self.author}}}")
        if self.title:
            fields.append(f"  title = {{{self.title}}}")
        if self.year:
            fields.append(f"  year = {{{self.year}}}")
        if self.month:
            fields.append(f"  month = {{{self.month}}}")
        if self.doi:
            fields.append(f"  doi = {{{self.doi}}}")
        if self.url:
            fields.append(f"  url = {{{self.url}}}")
        if self.note:
            fields.append(f"  note = {{{self.note}}}")

        # Type-specific fields
        if self.entry_type == 'article':
            if self.journal:
                fields.append(f"  journal = {{{self.journal}}}")
            if self.volume:
                fields.append(f"  volume = {{{self.volume}}}")
            if self.number:
                fields.append(f"  number = {{{self.number}}}")
            if self.pages:
                fields.append(f"  pages = {{{self.pages}}}")

        elif self.entry_type == 'book':
            if self.publisher:
                fields.append(f"  publisher = {{{self.publisher}}}")
            if self.address:
                fields.append(f"  address = {{{self.address}}}")
            if self.edition:
                fields.append(f"  edition = {{{self.edition}}}")

        elif self.entry_type == 'inproceedings':
            if self.booktitle:
                fields.append(f"  booktitle = {{{self.booktitle}}}")
            if self.editor:
                fields.append(f"  editor = {{{self.editor}}}")
            if self.pages:
                fields.append(f"  pages = {{{self.pages}}}")
            if self.publisher:
                fields.append(f"  publisher = {{{self.publisher}}}")

        elif self.entry_type == 'incollection':
            if self.booktitle:
                fields.append(f"  booktitle = {{{self.booktitle}}}")
            if self.editor:
                fields.append(f"  editor = {{{self.editor}}}")
            if self.pages:
                fields.append(f"  pages = {{{self.pages}}}")
            if self.publisher:
                fields.append(f"  publisher = {{{self.publisher}}}")

        elif self.entry_type in ['phdthesis', 'mastersthesis']:
            if self.school:
                fields.append(f"  school = {{{self.school}}}")
            if self.address:
                fields.append(f"  address = {{{self.address}}}")

        elif self.entry_type == 'techreport':
            if self.institution:
                fields.append(f"  institution = {{{self.institution}}}")
            if self.report_type:
                fields.append(f"  type = {{{self.report_type}}}")
            if self.address:
                fields.append(f"  address = {{{self.address}}}")

        bibtex = f"@{self.entry_type}{{{self.citation_key},\n"
        bibtex += ",\n".join(fields)
        bibtex += "\n}\n"

        return bibtex