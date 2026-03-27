# BibForge - Bibliography Management System

![Flask](https://img.shields.io/badge/Flask-3.0.0-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-3.1.1-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

BibForge is a powerful, web-based bibliography management system built with Flask. It allows researchers, academics, and students to create, manage, and export bibliographic entries in various formats with ease.

## ✨ Features

### Core Features
- **8 Entry Types**: Support for articles, books, inproceedings, incollection, PhD theses, master's theses, tech reports, and unpublished works
- **Smart Forms**: Dynamic fields that change based on the selected entry type
- **DOI Integration**: Auto-fill metadata from DOI using the Crossref API
- **Citation Generation**: Live preview of citations in MLA, APA, and Chicago styles
- **Export Options**: Single entry or batch export to BibTeX format
- **Search Functionality**: Full-text search across titles, authors, citation keys, and DOIs
- **REST API**: Programmatic access to your bibliography data

### Technical Features
- **SQLite Database**: Lightweight, file-based database
- **Form Validation**: Automatic validation with helpful error messages
- **Duplicate Detection**: Prevents duplicate DOI entries
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Error Handling**: Custom 404 and 500 error pages

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/bibforge.git
cd bibforge
