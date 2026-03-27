from flask import render_template, redirect, url_for, flash, request, session, jsonify
from app import app, db
from app.models import BibEntry
from app.forms import BibEntryForm
from app.utils.doi_utils import fetch_doi_metadata, validate_doi
from app.utils.validators import check_duplicate_doi, validate_required_fields
from app.utils.citation_generators import generate_mla, generate_apa, generate_chicago
import json


@app.route('/')
def index():
    entries = BibEntry.query.order_by(BibEntry.created_at.desc()).all()
    return render_template('index.html', entries=entries)


@app.route('/create', methods=['GET', 'POST'])
def create_entry():
    form = BibEntryForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Check for duplicate DOI
        if form.doi.data and check_duplicate_doi(form.doi.data):
            flash('DOI already exists in database!', 'danger')
            return render_template('entry_form.html', form=form)

        # Create new entry
        entry = BibEntry(
            entry_type=form.entry_type.data,
            citation_key=form.citation_key.data,
            doi=form.doi.data,
            title=form.title.data,
            author=form.author.data,
            year=form.year.data,
            journal=form.journal.data,
            volume=form.volume.data,
            number=form.number.data,
            pages=form.pages.data,
            publisher=form.publisher.data,
            address=form.address.data,
            edition=form.edition.data,
            booktitle=form.booktitle.data,
            editor=form.editor.data,
            school=form.school.data,
            institution=form.institution.data,
            report_type=form.report_type.data,
            month=form.month.data,
            note=form.note.data,
            url=form.url.data
        )

        db.session.add(entry)
        db.session.commit()

        flash('Bibliography entry created successfully!', 'success')
        return redirect(url_for('view_entry', entry_id=entry.id))

    return render_template('entry_form.html', form=form)


@app.route('/fetch-doi', methods=['POST'])
def fetch_doi():
    doi = request.json.get('doi')

    if not doi or not validate_doi(doi):
        return jsonify({'error': 'Invalid DOI format'}), 400

    if check_duplicate_doi(doi):
        return jsonify({'error': 'DOI already exists in database'}), 400

    metadata = fetch_doi_metadata(doi)

    if metadata:
        return jsonify(metadata)
    else:
        return jsonify({'error': 'Could not fetch DOI metadata'}), 404


@app.route('/entry/<int:entry_id>')
def view_entry(entry_id):
    entry = BibEntry.query.get_or_404(entry_id)

    citations = {
        'mla': generate_mla(entry),
        'apa': generate_apa(entry),
        'chicago': generate_chicago(entry)
    }

    return render_template('entry_form.html', entry=entry, citations=citations, view_mode=True)


@app.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry = BibEntry.query.get_or_404(entry_id)
    form = BibEntryForm(obj=entry)

    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(entry)
        db.session.commit()
        flash('Entry updated successfully!', 'success')
        return redirect(url_for('view_entry', entry_id=entry.id))

    return render_template('entry_form.html', form=form, entry=entry)


@app.route('/entry/<int:entry_id>/delete', methods=['POST'])
def delete_entry(entry_id):
    entry = BibEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/export')
def export():
    entry_ids = request.args.getlist('ids')
    if entry_ids:
        entries = BibEntry.query.filter(BibEntry.id.in_(entry_ids)).all()
    else:
        entries = BibEntry.query.all()

    return render_template('export.html', entries=entries)


@app.route('/download-bib')
def download_bib():
    entry_ids = request.args.getlist('ids')
    if entry_ids:
        entries = BibEntry.query.filter(BibEntry.id.in_(entry_ids)).all()
    else:
        entries = BibEntry.query.all()

    bib_content = ''
    for entry in entries:
        bib_content += entry.to_bibtex() + '\n'

    response = app.response_class(
        response=bib_content,
        mimetype='application/x-bibtex',
        headers={'Content-Disposition': 'attachment; filename=bibliography.bib'}
    )
    return response