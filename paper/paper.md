---
title: "SlideJet: A Lightweight Tool for Multilingual Presentation of PowerPoint Slides in Streamlit-Based Educational Apps"
tags:
  - Python
  - Streamlit
  - Education
  - Open Source
  - Presentation
  - Translation
  - Multilingual
authors:
  - name: Thomas Reimann
    orcid: 0000-0000-0000-0000  # <-- Replace with your real ORCID
    affiliation: 1
  - name: Nils Wallenberg
    orcid: 0000-0000-0000-0000  # <-- Replace with your real ORCID
    affiliation: 2
  - name: Markus Giese
    orcid: 0000-0000-0000-0000  # <-- Replace with your real ORCID
    affiliation: 2
  - name: Eileen Poeter
    orcid: 0000-0002-1234-5678  # Replace with actual ORCID
    affiliation: 3
affiliations:
  - name: TU Dresden, Institute for Groundwater Management
    index: 1
  - name: University of Gothenburg, Department of Earth Sciences
    index: 2
  - name: Colorado School of Mines, Department of Geology and Geological Engineering
    index: 3
date: YYYY-MM-DD  # <-- Replace with the final submission date
bibliography: paper.bib
---

# Summary

**SlideJet** is an open-source tool that allows educators and researchers to present PowerPoint slides interactively within a web browser using [Streamlit](https://streamlit.io). It preserves the original slide layout and speaker notes and supports automated translation of notes into more than 20 languages using the Google Translate API. 

SlideJet lowers the barrier for sharing multilingual teaching materials and conference presentations by turning `.pptx` files into web-ready content, with integrated speaker notes, navigation, and PDF export. Its simplicity and accessibility make it ideal for online education, blended learning, and international outreach.

The tool has been used in academic programs, such as the SYMPLE25 school, university courses, and the European Geosciences Union (EGU) 2025 conference. SlideJet promotes open science and inclusive education by providing platform-independent, translatable presentation resources.

# Statement of Need

PowerPoint is still the dominant format for educational presentations, yet it lacks a simple, interactive, and multilingual web interface. Tools such as Reveal.js or Jupyter Slides require technical overhead or don’t support notes and translation out-of-the-box.

SlideJet addresses these gaps by:
- Allowing educators to **present anywhere** using Streamlit
- Making speaker notes **visible and editable**
- Supporting **real-time translation** to help multilingual audiences
- Enabling **platform-independent sharing** without needing PowerPoint installed

It is especially useful for educators working in international programs or open education initiatives (e.g., ERASMUS+ or the Groundwater Project).

# Functionality

SlideJet:
- Converts `.pptx` slides to `.png` images and speaker notes to `.json`
- Organizes outputs for use in GitHub Pages or Streamlit apps
- Integrates translation (via `deep-translator`) with support for 20+ languages
- Allows interactive presentation with navigation controls
- Exports PDF with translated speaker notes using `pypdf`

SlideJet runs on Windows (due to PowerPoint COM interface) and is implemented in Python with minimal dependencies.

# Use Cases

**1. SYMPLE25 School**: Delivered multilingual materials for an online hydrogeology school.

**2. EGU25 Conference**: Enabled streamlined sharing of slides without PDF or PPT download.

**3. University Courses**: Used for semester-long teaching with evolving content and accessible notes.

Over 100 students and educators have used SlideJet, with more than 20 different presentations created and hosted.

# Example

To use SlideJet, the user prepares a `.pptx` file and runs the Streamlit app to generate slides and notes. The slideshow can then be deployed via Streamlit Cloud or GitHub Pages.

```bash
streamlit run slidejet_app.py
