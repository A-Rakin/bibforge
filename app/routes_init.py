# This file will hold all route definitions
from flask import render_template, redirect, url_for, flash, request, jsonify, make_response
from app import db
from app.models import BibEntry
from app.forms import BibEntryForm
from app.utils.doi_utils import fetch_doi_metadata, validate_doi
from app.utils.validators import check_duplicate_doi
from app.utils.citation_generators import generate_mla, generate_apa, generate_chicago
from datetime import datetime
import re


def init_routes(app):
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

        if request.method == 'POST':
            # Debug: Print all form data
            print("=" * 50)
            print("Form Data Received:")
            for key, value in request.form.items():
                print(f"{key}: {value}")
            print("=" * 50)

            # Manually set form data from request
            form.entry_type.data = request.form.get('entry_type')
            form.citation_key.data = request.form.get('citation_key')
            form.doi.data = request.form.get('doi')
            form.title.data = request.form.get('title')
            form.author.data = request.form.get('author')
            form.year.data = request.form.get('year')
            form.journal.data = request.form.get('journal')
            form.volume.data = request.form.get('volume')
            form.number.data = request.form.get('number')
            form.pages.data = request.form.get('pages')
            form.publisher.data = request.form.get('publisher')
            form.address.data = request.form.get('address')
            form.edition.data = request.form.get('edition')
            form.booktitle.data = request.form.get('booktitle')
            form.editor.data = request.form.get('editor')
            form.school.data = request.form.get('school')
            form.institution.data = request.form.get('institution')
            form.report_type.data = request.form.get('report_type')
            form.month.data = request.form.get('month')
            form.note.data = request.form.get('note')
            form.url.data = request.form.get('url')

            # Validate required fields manually
            if not form.citation_key.data:
                flash('Citation Key is required', 'danger')
                return render_template('entry_form.html', form=form)

            if not form.title.data:
                flash('Title is required', 'danger')
                return render_template('entry_form.html', form=form)

            if not form.author.data:
                flash('Author is required', 'danger')
                return render_template('entry_form.html', form=form)

            if not form.year.data:
                flash('Year is required', 'danger')
                return render_template('entry_form.html', form=form)

            # Validate type-specific required fields
            entry_type = form.entry_type.data

            if entry_type == 'article' and not form.journal.data:
                flash('Journal is required for article entries', 'danger')
                return render_template('entry_form.html', form=form)

            if entry_type == 'book' and not form.publisher.data:
                flash('Publisher is required for book entries', 'danger')
                return render_template('entry_form.html', form=form)

            if entry_type in ['inproceedings', 'incollection'] and not form.booktitle.data:
                flash('Book Title is required for inproceedings/incollection entries', 'danger')
                return render_template('entry_form.html', form=form)

            if entry_type in ['phdthesis', 'mastersthesis'] and not form.school.data:
                flash('School is required for thesis entries', 'danger')
                return render_template('entry_form.html', form=form)

            if entry_type == 'techreport' and not form.institution.data:
                flash('Institution is required for tech report entries', 'danger')
                return render_template('entry_form.html', form=form)

            if entry_type == 'unpublished' and not form.note.data:
                flash('Note is required for unpublished entries', 'danger')
                return render_template('entry_form.html', form=form)

            # Check for duplicate DOI
            if form.doi.data and check_duplicate_doi(form.doi.data):
                flash('DOI already exists in database!', 'danger')
                return render_template('entry_form.html', form=form)

            # Create new entry
            try:
                entry = BibEntry(
                    entry_type=form.entry_type.data,
                    citation_key=form.citation_key.data,
                    doi=form.doi.data,
                    title=form.title.data,
                    author=form.author.data,
                    year=int(form.year.data) if form.year.data else None,
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

            except Exception as e:
                db.session.rollback()
                flash(f'Error creating entry: {str(e)}', 'danger')
                return render_template('entry_form.html', form=form)

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

        if request.method == 'POST':
            # Manually update form data
            form.entry_type.data = request.form.get('entry_type')
            form.citation_key.data = request.form.get('citation_key')
            form.doi.data = request.form.get('doi')
            form.title.data = request.form.get('title')
            form.author.data = request.form.get('author')
            form.year.data = request.form.get('year')
            form.journal.data = request.form.get('journal')
            form.volume.data = request.form.get('volume')
            form.number.data = request.form.get('number')
            form.pages.data = request.form.get('pages')
            form.publisher.data = request.form.get('publisher')
            form.address.data = request.form.get('address')
            form.edition.data = request.form.get('edition')
            form.booktitle.data = request.form.get('booktitle')
            form.editor.data = request.form.get('editor')
            form.school.data = request.form.get('school')
            form.institution.data = request.form.get('institution')
            form.report_type.data = request.form.get('report_type')
            form.month.data = request.form.get('month')
            form.note.data = request.form.get('note')
            form.url.data = request.form.get('url')

            # Validate required fields
            if not form.citation_key.data:
                flash('Citation Key is required', 'danger')
                return render_template('entry_form.html', form=form, entry=entry)

            if not form.title.data:
                flash('Title is required', 'danger')
                return render_template('entry_form.html', form=form, entry=entry)

            if not form.author.data:
                flash('Author is required', 'danger')
                return render_template('entry_form.html', form=form, entry=entry)

            if not form.year.data:
                flash('Year is required', 'danger')
                return render_template('entry_form.html', form=form, entry=entry)

            # Check for duplicate DOI (excluding current entry)
            if form.doi.data and form.doi.data != entry.doi:
                if check_duplicate_doi(form.doi.data):
                    flash('DOI already exists in database!', 'danger')
                    return render_template('entry_form.html', form=form, entry=entry)

            # Update entry
            try:
                entry.entry_type = form.entry_type.data
                entry.citation_key = form.citation_key.data
                entry.doi = form.doi.data
                entry.title = form.title.data
                entry.author = form.author.data
                entry.year = int(form.year.data) if form.year.data else None
                entry.journal = form.journal.data
                entry.volume = form.volume.data
                entry.number = form.number.data
                entry.pages = form.pages.data
                entry.publisher = form.publisher.data
                entry.address = form.address.data
                entry.edition = form.edition.data
                entry.booktitle = form.booktitle.data
                entry.editor = form.editor.data
                entry.school = form.school.data
                entry.institution = form.institution.data
                entry.report_type = form.report_type.data
                entry.month = form.month.data
                entry.note = form.note.data
                entry.url = form.url.data

                db.session.commit()
                flash('Entry updated successfully!', 'success')
                return redirect(url_for('view_entry', entry_id=entry.id))

            except Exception as e:
                db.session.rollback()
                flash(f'Error updating entry: {str(e)}', 'danger')
                return render_template('entry_form.html', form=form, entry=entry)

        return render_template('entry_form.html', form=form, entry=entry)

    @app.route('/entry/<int:entry_id>/delete', methods=['POST'])
    def delete_entry(entry_id):
        entry = BibEntry.query.get_or_404(entry_id)
        try:
            db.session.delete(entry)
            db.session.commit()
            flash('Entry deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting entry: {str(e)}', 'danger')
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