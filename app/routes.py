from flask import render_template, redirect, url_for, flash, request, jsonify, make_response
from app import app, db
from app.models import BibEntry
from app.forms import BibEntryForm
from app.utils.doi_utils import fetch_doi_metadata, validate_doi
from app.utils.validators import check_duplicate_doi, validate_required_fields
from app.utils.citation_generators import generate_mla, generate_apa, generate_chicago
import json
from datetime import datetime


@app.route('/')
def index():
    entries = BibEntry.query.order_by(BibEntry.created_at.desc()).all()
    total_entries = len(entries)

    # Statistics
    stats = {
        'total': total_entries,
        'articles': BibEntry.query.filter_by(entry_type='article').count(),
        'books': BibEntry.query.filter_by(entry_type='book').count(),
        'theses': BibEntry.query.filter(BibEntry.entry_type.in_(['phdthesis', 'mastersthesis'])).count()
    }

    return render_template('index.html', entries=entries, stats=stats)


@app.route('/create', methods=['GET', 'POST'])
def create_entry():
    form = BibEntryForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Check for duplicate DOI
        if form.doi.data and check_duplicate_doi(form.doi.data):
            flash('DOI already exists in database!', 'danger')
            return render_template('entry_form.html', form=form)

        # Validate required fields based on entry type
        data = {
            'title': form.title.data,
            'author': form.author.data,
            'year': form.year.data,
            'journal': form.journal.data,
            'publisher': form.publisher.data,
            'booktitle': form.booktitle.data,
            'school': form.school.data,
            'institution': form.institution.data,
            'note': form.note.data
        }

        missing_fields = validate_required_fields(data, form.entry_type.data)
        if missing_fields:
            flash(f'Missing required fields: {", ".join(missing_fields)}', 'danger')
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

    if not doi:
        return jsonify({'error': 'No DOI provided'}), 400

    if not validate_doi(doi):
        return jsonify({'error': 'Invalid DOI format'}), 400

    if check_duplicate_doi(doi):
        return jsonify({'error': 'DOI already exists in database'}), 400

    metadata = fetch_doi_metadata(doi)

    if metadata:
        return jsonify(metadata)
    else:
        return jsonify({'error': 'Could not fetch DOI metadata. Please check the DOI and try again.'}), 404


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
        # Check for duplicate DOI (excluding current entry)
        if form.doi.data and form.doi.data != entry.doi:
            if check_duplicate_doi(form.doi.data):
                flash('DOI already exists in database!', 'danger')
                return render_template('entry_form.html', form=form, entry=entry)

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
    entries = BibEntry.query.order_by(BibEntry.created_at.desc()).all()
    return render_template('export.html', entries=entries)


@app.route('/export-preview', methods=['POST'])
def export_preview():
    """Generate BibTeX preview for selected entries"""
    data = request.json
    entry_ids = data.get('ids', [])

    if not entry_ids:
        return jsonify({'error': 'No entries selected'}), 400

    entries = BibEntry.query.filter(BibEntry.id.in_(entry_ids)).all()

    if not entries:
        return jsonify({'error': 'No entries found'}), 404

    bibtex_content = ''
    for entry in entries:
        bibtex_content += entry.to_bibtex() + '\n'

    return jsonify({'bibtex': bibtex_content})


@app.route('/download-bib', methods=['GET', 'POST'])
def download_bib():
    if request.method == 'POST':
        entry_ids = request.form.getlist('ids')
    else:
        entry_ids = request.args.getlist('ids')

    if entry_ids and entry_ids[0]:  # Check if there are IDs
        entries = BibEntry.query.filter(BibEntry.id.in_(entry_ids)).all()
    else:
        entries = BibEntry.query.all()

    if not entries:
        flash('No entries to export', 'warning')
        return redirect(url_for('export'))

    bib_content = ''
    for entry in entries:
        bib_content += entry.to_bibtex() + '\n'

    response = make_response(bib_content)
    response.mimetype = 'application/x-bibtex'
    response.headers[
        'Content-Disposition'] = f'attachment; filename=bibliography_{datetime.now().strftime("%Y%m%d_%H%M%S")}.bib'
    return response


@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        entries = BibEntry.query.filter(
            db.or_(
                BibEntry.title.contains(query),
                BibEntry.author.contains(query),
                BibEntry.citation_key.contains(query),
                BibEntry.doi.contains(query)
            )
        ).order_by(BibEntry.created_at.desc()).all()
    else:
        entries = []

    return render_template('search.html', entries=entries, query=query)


@app.route('/api/entries', methods=['GET'])
def api_entries():
    """REST API endpoint to get all entries"""
    entries = BibEntry.query.all()
    return jsonify([{
        'id': e.id,
        'citation_key': e.citation_key,
        'title': e.title,
        'author': e.author,
        'year': e.year,
        'entry_type': e.entry_type,
        'doi': e.doi,
        'bibtex': e.to_bibtex()
    } for e in entries])


@app.route('/api/entry/<int:entry_id>', methods=['GET'])
def api_entry(entry_id):
    """REST API endpoint to get a specific entry"""
    entry = BibEntry.query.get_or_404(entry_id)
    return jsonify({
        'id': entry.id,
        'citation_key': entry.citation_key,
        'title': entry.title,
        'author': entry.author,
        'year': entry.year,
        'entry_type': entry.entry_type,
        'doi': entry.doi,
        'bibtex': entry.to_bibtex()
    })


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500