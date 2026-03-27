from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, URL, NumberRange, Regexp


class BibEntryForm(FlaskForm):
    entry_type = SelectField('Entry Type', choices=[
        ('article', 'Article'),
        ('book', 'Book'),
        ('inproceedings', 'Inproceedings'),
        ('incollection', 'Incollection'),
        ('phdthesis', 'PhD Thesis'),
        ('mastersthesis', 'Master\'s Thesis'),
        ('techreport', 'Tech Report'),
        ('unpublished', 'Unpublished')
    ], validators=[DataRequired()])

    citation_key = StringField('Citation Key', validators=[
        DataRequired(),
        Regexp(r'^[a-zA-Z0-9_:]+$', message='Only letters, numbers, colon, and underscore allowed')
    ])
    doi = StringField('DOI', validators=[Optional()])
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author(s)', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1000, max=2100)])

    # Article fields
    journal = StringField('Journal', validators=[Optional()])
    volume = StringField('Volume', validators=[Optional()])
    number = StringField('Number', validators=[Optional()])
    pages = StringField('Pages', validators=[Optional()])

    # Book fields
    publisher = StringField('Publisher', validators=[Optional()])
    address = StringField('Address', validators=[Optional()])
    edition = StringField('Edition', validators=[Optional()])

    # Inproceedings/Incollection fields
    booktitle = StringField('Book Title', validators=[Optional()])
    editor = StringField('Editor(s)', validators=[Optional()])

    # Thesis fields
    school = StringField('School', validators=[Optional()])

    # Techreport fields
    institution = StringField('Institution', validators=[Optional()])
    report_type = StringField('Report Type', validators=[Optional()])

    # Common fields
    month = StringField('Month', validators=[Optional()])
    note = TextAreaField('Note', validators=[Optional()])
    url = StringField('URL', validators=[Optional(), URL()])

    submit = SubmitField('Generate Entry')