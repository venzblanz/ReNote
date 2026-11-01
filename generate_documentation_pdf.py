import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Define custom palette
COLOR_PRIMARY = colors.HexColor('#6B21A8')     # Deep Purple
COLOR_SECONDARY = colors.HexColor('#9333EA')   # Vibrant Violet
COLOR_ACCENT = colors.HexColor('#C084FC')      # Lavender
COLOR_DARK = colors.HexColor('#0F0A1C')        # Celestial Dark
COLOR_TEXT = colors.HexColor('#1F2937')        # Charcoal
COLOR_LIGHT_BG = colors.HexColor('#FAF5FF')    # Very Light Violet
COLOR_BORDER = colors.HexColor('#E9D5FF')      # Soft Border
COLOR_CODE_BG = colors.HexColor('#1E1633')     # Dark Terminal
COLOR_CODE_TEXT = colors.HexColor('#F3E8FF')   # Code Lavender
COLOR_GREEN = colors.HexColor('#10B981')       # Success Green
COLOR_AMBER = colors.HexColor('#D97706')       # Warning Amber

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self._pageNumber > 1:
                self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, page_count):
        self.saveState()
        # Running Top Header
        self.setFont('Helvetica-Bold', 7.5)
        self.setFillColor(COLOR_PRIMARY)
        self.drawString(54, 755, 'ReNote — Complete Architecture, Development & Deployment Handbook')
        self.setFont('Helvetica', 7.5)
        self.setFillColor(colors.HexColor('#6B7280'))
        self.drawRightString(558, 755, 'Django 5 • WhiteNoise • Supabase • Render')
        
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(54, 748, 558, 748)
        
        # Running Bottom Footer
        self.line(54, 45, 558, 45)
        self.setFont('Helvetica', 7.5)
        self.setFillColor(colors.HexColor('#9CA3AF'))
        self.drawString(54, 32, 'Comprehensive Technical Documentation & Operational Guide')
        self.setFont('Helvetica-Bold', 7.5)
        self.setFillColor(COLOR_PRIMARY)
        self.drawRightString(558, 32, f'Page {self._pageNumber} of {page_count}')
        self.restoreState()

def build_pdf(filename="ReNote_Complete_Master_Handbook.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=COLOR_PRIMARY,
        alignment=0,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=18,
        textColor=COLOR_TEXT,
        alignment=0,
        spaceAfter=24
    )

    h1_style = ParagraphStyle(
        'ChapterH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=22,
        textColor=COLOR_PRIMARY,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=COLOR_SECONDARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'SubsectionH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=COLOR_DARK,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=13,
        textColor=COLOR_TEXT,
        spaceAfter=7
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=13,
        textColor=COLOR_TEXT,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=COLOR_CODE_TEXT
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=12,
        textColor=COLOR_TEXT
    )

    def make_code_box(code_text):
        # Wraps code in dark purple console box
        clean_code = code_text.strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        p = Paragraph(f"<font face='Courier' color='#F3E8FF'>{clean_code.replace(chr(10), '<br/>')}</font>", code_style)
        t = Table([[p]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COLOR_CODE_BG),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 1, COLOR_SECONDARY),
        ]))
        return t

    def make_callout(title, text, kind="tip"):
        bar_color = COLOR_SECONDARY if kind == "tip" else (COLOR_AMBER if kind == "warn" else COLOR_GREEN)
        bg_color = COLOR_LIGHT_BG if kind == "tip" else colors.HexColor('#FFFBEB')
        header_color = bar_color.hexval()
        
        content = f"<b><font color='{header_color}'>{title}</font></b><br/>{text}"
        p = Paragraph(content, callout_style)
        t = Table([[p]], colWidths=[504])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('LINELEFT', (0,0), (0,-1), 4, bar_color),
            ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        return t

    story = []

    # =========================================================================
    # COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("ReNote", ParagraphStyle('CoverBrand', fontName='Helvetica-Bold', fontSize=38, leading=44, textColor=COLOR_PRIMARY)))
    story.append(Paragraph("Celestial Moon Collection & Anime Media Hub", ParagraphStyle('CoverEyebrow', fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=COLOR_SECONDARY, spaceAfter=18)))
    story.append(HRFlowable(width="100%", thickness=3, color=COLOR_SECONDARY, spaceAfter=20, spaceBefore=0))
    story.append(Paragraph("The Complete Architecture, Development & Deployment Handbook", title_style))
    story.append(Paragraph(
        "A comprehensive, end-to-end technical manual and operational guide for building, configuring, styling, and deploying "
        "ReNote to production on Render using Django 5, Supabase PostgreSQL, WhiteNoise static compression, and resilient multi-provider API cascading.",
        subtitle_style
    ))

    # Meta Table on Cover
    cover_meta = [
        [Paragraph("<b>Project:</b>", body_style), Paragraph("ReNote (Celestial Dark Anime Tracker)", body_style)],
        [Paragraph("<b>Author / Engineer:</b>", body_style), Paragraph("Venz Virni Blanza (venzblanz@gmail.com)", body_style)],
        [Paragraph("<b>Live URL:</b>", body_style), Paragraph("https://renote-c16n.onrender.com/", body_style)],
        [Paragraph("<b>Repository:</b>", body_style), Paragraph("https://github.com/venzblanz/ReNote.git (branch: testing)", body_style)],
        [Paragraph("<b>Core Stack:</b>", body_style), Paragraph("Python 3.12, Django 5.2, PostgreSQL (Supabase), Gunicorn 26.2, WhiteNoise 6.12", body_style)],
        [Paragraph("<b>Hosting Platform:</b>", body_style), Paragraph("Render Cloud Web Service (Linux Docker container)", body_style)],
        [Paragraph("<b>Publication Date:</b>", body_style), Paragraph("November 2026", body_style)],
    ]
    t_meta = Table(cover_meta, colWidths=[120, 384])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 30))
    story.append(make_callout(
        "Handbook Purpose & Scope",
        "This document is an exhaustive educational manual designed to walk through every single technical decision, "
        "command, file structure, configuration variable, and bug resolution implemented throughout the ReNote project lifecycle. "
        "Whether you are replicating this architecture from scratch or maintaining the production instance, this handbook provides the blueprint.",
        "tip"
    ))
    story.append(PageBreak())

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER, spaceAfter=14, spaceBefore=4))
    
    toc_data = [
        [Paragraph("<b>Chapter 1: The Vision & Architectural Foundation</b>", body_style), Paragraph("Page 3", body_style)],
        [Paragraph("• Philosophy, System Architecture & The High-Level Flow", bullet_style), Paragraph("", body_style)],
        [Paragraph("• Full Directory Structure & File Inventory", bullet_style), Paragraph("", body_style)],
        [Paragraph("<b>Chapter 2: Python Environment & Dependency Isolation</b>", body_style), Paragraph("Page 4", body_style)],
        [Paragraph("• Virtual Environments (venv) Demystified", bullet_style), Paragraph("", body_style)],
        [Paragraph("• Exact PowerShell Activation & Package Pinning", bullet_style), Paragraph("", body_style)],
        [Paragraph("<b>Chapter 3: Django Modular Application Architecture</b>", body_style), Paragraph("Page 5", body_style)],
        [Paragraph("• The startproject Dot Syntax Trap (renote/renote vs renote/)", bullet_style), Paragraph("", body_style)],
        [Paragraph("• The 5 Core Apps: home, library, login, register, profile/settings", bullet_style), Paragraph("", body_style)],
        [Paragraph("<b>Chapter 4: Database Modeling, PostgreSQL & Migrations</b>", body_style), Paragraph("Page 7", body_style)],
        [Paragraph("• Relational Models: MediaCatalog vs UserMediaLog", bullet_style), Paragraph("", body_style)],
        [Paragraph("• Why Local SQLite Fails on Render & The Supabase Advantage", bullet_style), Paragraph("", body_style)],
        [Paragraph("• Migrations Step-by-Step (makemigrations, migrate)", bullet_style), Paragraph("", body_style)],
        [Paragraph("<b>Chapter 5: Static Files Architecture — static/ vs staticfiles/</b>", body_style), Paragraph("Page 9", body_style)],
        [Paragraph("• The Core Question: Why Two Static Folders?", bullet_style), Paragraph("", body_style)],
        [Paragraph("• WhiteNoise: How Production Static Serving Works Without Nginx", bullet_style), Paragraph("", body_style)],
        [Paragraph("• Cache-Busting Hashes (base.babc8cf8d8a1.css) & Gzip (.gz) Compression", bullet_style), Paragraph("", body_style)],
        [Paragraph("<b>Chapter 6: External APIs & Resilient Cascading Engine</b>", body_style), Paragraph("Page 11", body_style)],
        [Paragraph("• AniList, Kitsu, and Jikan Rate Limits & Outage Risks", bullet_style), Paragraph("", body_style)],
        [Paragraph("• Connection Pooling, Timeouts & SHA-256 Memory Caching", bullet_style), Paragraph("", body_style)],
        [Paragraph("<b>Chapter 7: Security, Environment Variables & Configuration Decoupling</b>", body_style), Paragraph("Page 13", body_style)],
        [Paragraph("• Twelve-Factor App Principles: .env vs .env.example", bullet_style), Paragraph("", body_style)],
        [Paragraph("• Solving 400 Bad Request: ALLOWED_HOSTS & CSRF_TRUSTED_ORIGINS", bullet_style), Paragraph("", body_style)],
        [Paragraph("• SMTP Password Reset Configuration with Gmail App Passwords", bullet_style), Paragraph("", body_style)],
        [Paragraph("<b>Chapter 8: Production Deployment on Render</b>", body_style), Paragraph("Page 15", body_style)],
        [Paragraph("• Procfile & Gunicorn Pre-Fork Worker Server", bullet_style), Paragraph("", body_style)],
        [Paragraph("• build.sh: Build Scripts & The Unix Executable Permission (+x)", bullet_style), Paragraph("", body_style)],
        [Paragraph("• Superuser Creation Without Paid Shell", bullet_style), Paragraph("", body_style)],
        [Paragraph("<b>Chapter 9: Responsive Mobile UI & Overflow Engineering</b>", body_style), Paragraph("Page 17", body_style)],
        [Paragraph("• Post-Mortem 1: CSS Grid minmax Collapse & The 2-Column Grid", bullet_style), Paragraph("", body_style)],
        [Paragraph("• Post-Mortem 2: Viewport Horizontal Overflow & The 'Right-Slide' Space", bullet_style), Paragraph("", body_style)],
        [Paragraph("• Media Detail Sizing Formula & Ambient Hero Spotlight", bullet_style), Paragraph("", body_style)],
        [Paragraph("<b>Chapter 10: Complete Command Reference & Cheatsheet</b>", body_style), Paragraph("Page 19", body_style)],
        [Paragraph("• Categorized Reference for all PowerShell & Bash Operations", bullet_style), Paragraph("", body_style)],
    ]
    t_toc = Table(toc_data, colWidths=[420, 84])
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 1: VISION & ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("Chapter 1: The Vision & Architectural Foundation", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=10, spaceBefore=2))
    
    story.append(Paragraph("1.1 Project Overview & Philosophy", h2_style))
    story.append(Paragraph(
        "<b>ReNote</b> was conceived as a premium, distraction-free personal anime, manga, novel, and film tracker. "
        "Built around the celestial aesthetic of the 'Violet Hour'—that fleeting twilight when reality fades into imagination—"
        "and the Moon as humanity's ancient keeper of time and memory, ReNote gives fiction enthusiasts a sacred night-sky archive "
        "to record, rate, track rewatches, and revisit every work of art that moved them.",
        body_style
    ))
    story.append(Paragraph(
        "Unlike generic tracking platforms cluttered with ads, social bloat, and slow loading times, ReNote focuses on "
        "<b>blazing speed, high visual elegance, privacy, and architectural resilience</b>. Every external media search is "
        "cached into a permanent local relational catalog, meaning zero repeated API hits and zero delays.",
        body_style
    ))

    story.append(Paragraph("1.2 The High-Level System Architecture", h2_style))
    story.append(Paragraph(
        "ReNote is engineered using a robust, decoupled modern Python web stack designed for cloud container environments:",
        body_style
    ))

    arch_items = [
        "<b>Presentation Layer (Frontend):</b> Semantic HTML5, pure CSS3 with custom variables, CSS Grid, Flexbox, and lightweight modular vanilla JavaScript. Zero bulky JS framework dependencies (no React or Vue bundles), ensuring instant initial paint.",
        "<b>Application Layer (Django 5):</b> Python's premier enterprise framework implementing the Model-View-Template (MVT) pattern, providing robust session security, CSRF protection, ORM querying, and templating.",
        "<b>Static Asset Engine (WhiteNoise):</b> High-performance middleware that intercepts static file requests directly within the Python WSGI pipeline, applying content hashing, gzip/brotli compression, and immutable HTTP caching headers.",
        "<b>WSGI HTTP Server (Gunicorn):</b> Green Unicorn acts as the production pre-fork worker HTTP server running inside the Render container, managing concurrent requests and delegating to Django's WSGI application.",
        "<b>Database Layer (Supabase PostgreSQL):</b> Managed enterprise PostgreSQL cloud database communicating over encrypted SSL (`sslmode=require`), handling relational integrity, indexing, and persistent catalog storage.",
        "<b>External Gateway (Multi-Provider API Engine):</b> Custom resilient HTTP client cascading between AniList GraphQL, Kitsu REST, and Jikan REST APIs with automatic connection pooling and failover."
    ]
    for item in arch_items:
        story.append(Paragraph(f"• {item}", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("1.3 Full Project Directory Structure", h2_style))
    story.append(Paragraph("The ReNote codebase is organized into clean, single-responsibility domains:", body_style))

    dir_tree = """ReNote/
├── .env                  # Local secret configuration (GITIGNORED - NEVER COMMIT!)
├── .env.example          # Safe template of required environment keys
├── .gitignore            # Excludes venv, .env, __pycache__, and compiled assets
├── build.sh              # Render build script (pip install, collectstatic, migrate)
├── Procfile              # Process manager file for Render (web: gunicorn)
├── manage.py             # Django administrative command CLI
├── requirements.txt      # Pinned Python package dependencies
│
├── renote/               # Project Root & Core Configuration
│   ├── __init__.py
│   ├── asgi.py           # Asynchronous server gateway
│   ├── wsgi.py           # Synchronous WSGI gateway (used by Gunicorn)
│   ├── urls.py           # Master URL routing table
│   └── settings.py       # Centralized settings (WhiteNoise, DB, Auth, Security)
│
├── home/                 # App: Landing dashboard & celestial hero spotlight
├── library/              # App: Catalog search, personal media tracker, detail view
├── login/                # App: Authentication, sessions, 4-stage password reset
├── register/             # App: User registration, terms of service, privacy
├── user_profile/         # App: User profile, stats overview, avatars
├── user_settings/        # App: Account preferences & settings
│
├── static/               # SOURCE static assets (CSS, JS, images, fonts)
│   ├── css/              # Uncompressed developer stylesheets
│   ├── js/               # Modular frontend scripts
│   └── images/           # Moon assets, avatars, branding logos
│
├── staticfiles/          # COMPILED static distribution (created by collectstatic)
│   └── ...               # WhiteNoise hashed (.babc8cf8.css) & gzip (.gz) files
│
└── templates/            # Django HTML Templates
    ├── shared/           # Base layouts, headers, SEO meta partials
    ├── home/             # Dashboard templates
    ├── library/          # Library list, catalog search, media detail
    ├── login/            # Login, password reset email templates
    └── user_profile/     # Profile overview templates"""
    story.append(make_code_box(dir_tree))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 2: PYTHON ENVIRONMENT & VIRTUAL ENVIRONMENTS
    # =========================================================================
    story.append(Paragraph("Chapter 2: Python Environment & Dependency Isolation", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=10, spaceBefore=2))

    story.append(Paragraph("2.1 What is a Virtual Environment and Why is it Essential?", h2_style))
    story.append(Paragraph(
        "In Python development, installing libraries globally across your operating system using `pip install <package>` "
        "is a dangerous anti-pattern. If Project A requires `Django==4.2` and Project B requires `Django==5.2`, installing "
        "them globally leads to version collisions, breaking existing applications. Furthermore, global installations "
        "pollute your system Python and make it impossible to know which exact packages your project actually depends on.",
        body_style
    ))
    story.append(Paragraph(
        "A <b>Virtual Environment</b> (`venv`) is a self-contained directory tree that contains its own Python interpreter, "
        "standard libraries, and an isolated `site-packages` directory. When you install packages inside a virtual environment, "
        "they are stored exclusively within that folder and cannot affect any other project on your machine.",
        body_style
    ))

    story.append(Paragraph("2.2 Step-by-Step PowerShell Lifecycle", h2_style))
    story.append(Paragraph(
        "Here are the exact Windows PowerShell commands used to create, activate, and manage the ReNote virtual environment:",
        body_style
    ))

    cmd_step1 = """# 1. Create a dedicated virtual environment named 'vvv'
python -m venv vvv

# 2. Activate the virtual environment in PowerShell
.\\vvv\\Scripts\\activate

# Note: If PowerShell displays an ExecutionPolicy restriction error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Direct invocation without activation (used by IDEs and automated scripts):
.\\vvv\\Scripts\\python.exe manage.py <command>
.\\vvv\\Scripts\\pip.exe install <package>"""
    story.append(make_code_box(cmd_step1))

    story.append(Paragraph("2.3 Pinned Dependencies (`requirements.txt`) Explained", h2_style))
    story.append(Paragraph(
        "The `requirements.txt` file lists every third-party package necessary to run ReNote in both development "
        "and production. Here is what each pinned dependency accomplishes:",
        body_style
    ))

    req_data = [
        [Paragraph("<b>Package</b>", body_style), Paragraph("<b>Version</b>", body_style), Paragraph("<b>Purpose & Role in ReNote</b>", body_style)],
        [Paragraph("<code>Django</code>", body_style), Paragraph("5.2.17", body_style), Paragraph("The core web framework handling routing, models, templates, and security.", body_style)],
        [Paragraph("<code>gunicorn</code>", body_style), Paragraph("26.2.0", body_style), Paragraph("Green Unicorn: production WSGI HTTP server executing Python worker processes on Render.", body_style)],
        [Paragraph("<code>whitenoise</code>", body_style), Paragraph("6.12.0", body_style), Paragraph("Production static asset engine providing hashing, compression, and HTTP caching.", body_style)],
        [Paragraph("<code>psycopg2-binary</code>", body_style), Paragraph("2.9.12", body_style), Paragraph("PostgreSQL database adapter allowing Python to communicate natively with Supabase.", body_style)],
        [Paragraph("<code>dj-database-url</code>", body_style), Paragraph("3.1.2", body_style), Paragraph("Parses standard <code>DATABASE_URL</code> connection strings into Django dictionary format.", body_style)],
        [Paragraph("<code>python-dotenv</code>", body_style), Paragraph("1.2.3", body_style), Paragraph("Loads key-value pairs from a local <code>.env</code> file into <code>os.environ</code> automatically.", body_style)],
        [Paragraph("<code>requests</code>", body_style), Paragraph("2.34.2", body_style), Paragraph("Battle-tested HTTP library used to query external anime APIs (AniList, Kitsu, Jikan).", body_style)],
        [Paragraph("<code>urllib3</code>", body_style), Paragraph("2.8.0", body_style), Paragraph("Provides connection pooling, retry adapters, and timeout controls for HTTP requests.", body_style)],
        [Paragraph("<code>pillow</code>", body_style), Paragraph("12.3.0", body_style), Paragraph("Python Imaging Library used for avatar upload processing and image handling.", body_style)],
    ]
    t_req = Table(req_data, colWidths=[110, 60, 334])
    t_req.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_req)
    story.append(Spacer(1, 10))
    story.append(make_callout(
        "Exporting Installed Packages",
        "Whenever you install a new package into your environment, always synchronize <code>requirements.txt</code> "
        "by running: <code>.\\vvv\\Scripts\\python.exe -m pip freeze > requirements.txt</code>. This ensures Render installs "
        "the exact same package versions during its build step.",
        "tip"
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 3: DJANGO APPLICATION ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("Chapter 3: Django Modular Application Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=10, spaceBefore=2))

    story.append(Paragraph("3.1 The `startproject` Dot Syntax Trap", h2_style))
    story.append(Paragraph(
        "When initializing a new Django project, running `django-admin startproject renote` creates an annoying "
        "double-nested folder structure: `renote/renote/settings.py` with `renote/manage.py`. "
        "This extra folder confuses Git repositories, Docker containers, and deployment platforms.",
        body_style
    ))
    story.append(Paragraph(
        "By appending a single dot (`.`) to the command: `django-admin startproject renote .`, Django initializes the "
        "project directly inside the current root folder. This places `manage.py` at the root and keeps configuration clean.",
        body_style
    ))

    cmd_init = """# The Clean Command (Used in ReNote):
django-admin startproject renote .

# Result:
# ./manage.py
# ./renote/settings.py
# ./renote/urls.py
# ./renote/wsgi.py"""
    story.append(make_code_box(cmd_init))

    story.append(Paragraph("3.2 The 5 Domain Applications of ReNote", h2_style))
    story.append(Paragraph(
        "In Django, projects are broken down into small, modular 'apps' that each handle one specific business domain. "
        "ReNote is divided into five dedicated applications:",
        body_style
    ))

    apps_list = [
        "<b>home (<code>templates/home/</code>, <code>static/css/home/</code>):</b> Renders the main dashboard, the signature celestial purple moon hero showcase, interactive random title picker modal ('Pick for Me'), format breakdown charts, and collection summaries.",
        "<b>library (<code>templates/library/</code>, <code>static/css/library/</code>):</b> The core media catalog. Houses catalog search, external API search queries, personal collection filtering (Anime, Manga, Movie, Novel), media detail view, status toggle (Watching, Completed, Plan to Watch, On Hold, Dropped), star rating, rewatch counter, and personal review notes.",
        "<b>login (<code>templates/login/</code>):</b> Manages user authentication, secure session cookies, login forms, logout endpoints, and the full 4-stage SMTP password reset workflow.",
        "<b>register (<code>templates/register/</code>):</b> User signup validation, username uniqueness verification, terms of service, and privacy policy views.",
        "<b>user_profile & user_settings:</b> Account customization, avatar selections, personal statistics recalculations, and password change management."
    ]
    for app in apps_list:
        story.append(Paragraph(f"• {app}", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("3.3 Master URL Routing Table (`renote/urls.py`)", h2_style))
    story.append(Paragraph(
        "Django uses a centralized routing table in `renote/urls.py` that delegates URL prefixes to app-specific `urls.py` files. "
        "Here is the master routing configuration for ReNote:",
        body_style
    ))

    urls_code = """from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('home.urls', 'home'), namespace='home')),
    path('library/', include(('library.urls', 'library'), namespace='library')),
    path('login/', include(('login.urls', 'login'), namespace='login')),
    path('register/', include(('register.urls', 'register'), namespace='register')),
    path('profile/', include(('user_profile.urls', 'user_profile'), namespace='user_profile')),
    path('settings/', include(('user_settings.urls', 'user_settings'), namespace='user_settings')),
    
    # Dynamic SEO Endpoints
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml')),
]"""
    story.append(make_code_box(urls_code))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: DATABASE & MODELS
    # =========================================================================
    story.append(Paragraph("Chapter 4: Database Modeling, PostgreSQL & Migrations", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=10, spaceBefore=2))

    story.append(Paragraph("4.1 Relational Architecture: MediaCatalog vs UserMediaLog", h2_style))
    story.append(Paragraph(
        "A critical engineering decision in ReNote was separating <b>canonical media data</b> from <b>user personal data</b>. "
        "If 50 users add 'Solo Leveling' to their libraries, saving the title, synopsis, poster image, and release date 50 separate times "
        "in the database is wasteful and slow. Instead, ReNote employs a normalized two-table architecture:",
        body_style
    ))

    models_desc = [
        "<b>MediaCatalog (Canonical Entity):</b> Stores unique external media objects fetched from AniList or Kitsu. Holds `external_id`, `media_title`, `media_type`, `media_description`, `media_image` URL, `media_year`, `media_rate`, and `genre` list. Once saved, any user who adds this title references this exact record. Repeated external API calls drop to ZERO.",
        "<b>UserMediaLog (Personal Relationship):</b> Links a `User` foreign key to a `MediaCatalog` foreign key with a `unique_together = ('user', 'media')` constraint. Stores the user's private data: `status` (Watching/Completed/etc.), `personal_rate` (1 to 5 stars), `rewatch_count`, `media_note` (review/thoughts), `is_favorite` boolean, `created_at`, and `updated_at`."
    ]
    for md in models_desc:
        story.append(Paragraph(f"• {md}", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("4.2 The Python Model Schema (`library/models.py`)", h2_style))
    
    models_code = """from django.db import models
from django.contrib.auth.models import User

class MediaCatalog(models.Model):
    external_id = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    media_type = models.CharField(max_length=30, choices=[
        ('anime', 'Anime'), ('manga', 'Manga'), ('movie', 'Movie'), ('novel', 'Novel')
    ], default='anime')
    media_title = models.CharField(max_length=255, db_index=True)
    media_description = models.TextField(blank=True, default='')
    media_image = models.URLField(max_length=600, blank=True, default='')
    media_release_date = models.DateField(blank=True, null=True)
    media_rate = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    genre = models.JSONField(default=list, blank=True)

class UserMediaLog(models.Model):
    STATUS_CHOICES = [
        ('watching', 'Watching'), ('reading', 'Reading'),
        ('completed', 'Completed'), ('plan to watch', 'Plan to Watch'),
        ('plan to read', 'Plan to Read'), ('on hold', 'On Hold'), ('dropped', 'Dropped')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_logs')
    media = models.ForeignKey(MediaCatalog, on_delete=models.CASCADE, related_name='user_logs')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='watching')
    personal_rate = models.PositiveSmallIntegerField(blank=True, null=True) # 1 to 5 stars
    rewatch_count = models.PositiveIntegerField(default=0)
    media_note = models.TextField(blank=True, default='')
    is_favorite = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'media')"""
    story.append(make_code_box(models_code))

    story.append(Spacer(1, 8))
    story.append(Paragraph("4.3 Why Local SQLite Fails on Render & The Supabase Advantage", h2_style))
    story.append(Paragraph(
        "By default, Django creates a local `db.sqlite3` file. While SQLite is fantastic for local development, "
        "<b>deploying SQLite to Render or any modern cloud container platform leads to catastrophic data loss</b>.",
        body_style
    ))
    story.append(Paragraph(
        "Render free/starter web services operate on <b>ephemeral container filesystems</b>. Every time Render deploys "
        "a new git commit, restarts an idle container, or spins up a new instance, the container is completely wiped "
        "and rebuilt from the git repository. Any SQLite database file written to disk is immediately erased!",
        body_style
    ))
    story.append(Paragraph(
        "To solve this, ReNote connects to an external <b>Supabase PostgreSQL database</b>. Supabase provides permanent, "
        "independently hosted enterprise PostgreSQL that never sleeps or deletes your tables during Render redeploys.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 5: STATIC FILES & WHITENOISE
    # =========================================================================
    story.append(Paragraph("Chapter 5: Static Files Architecture — static/ vs staticfiles/", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=10, spaceBefore=2))

    story.append(Paragraph("5.1 The Core Question: Why Are There Both `static/` and `staticfiles/` Folders?", h2_style))
    story.append(Paragraph(
        "This is one of the most common questions in Python web engineering. Here is the definitive distinction:",
        body_style
    ))

    static_diff = [
        "<b>static/ = YOUR SOURCE CODE (Developer Input):</b> This is where you write your original CSS stylesheets, JavaScript files, images, and fonts. You edit files in `static/` every day. They are organized logically by app (`static/css/home/home.css`, `static/js/library/add_title.js`). This folder is committed to Git.",
        "<b>staticfiles/ = COMPILED PRODUCTION DISTRIBUTION (Build Output):</b> This folder is generated automatically when Django runs `python manage.py collectstatic`. Django crawls every app and your `static/` directory, copies all assets into this single unified folder, and passes them to WhiteNoise to be compressed, hashed, and pre-packaged for production."
    ]
    for sd in static_diff:
        story.append(Paragraph(f"• {sd}", bullet_style))

    story.append(Spacer(1, 8))
    story.append(make_callout(
        "Golden Rule of Static Files",
        "<b>NEVER manually edit files inside the <code>staticfiles/</code> folder!</b> Any manual change in <code>staticfiles/</code> "
        "will be permanently overwritten and deleted the next time <code>collectstatic</code> runs. Always edit in <code>static/</code>, "
        "and let Django compile into <code>staticfiles/</code>.",
        "warn"
    ))

    story.append(Paragraph("5.2 Why Django Refuses to Serve Static Files in Production (`DEBUG = False`)", h2_style))
    story.append(Paragraph(
        "When `DEBUG = True` (development mode), Django's internal development server (`runserver`) intercepts requests for `/static/...` "
        "and serves files dynamically. However, the moment you flip `DEBUG = False` for production, Django's static file handler "
        "<b>completely shuts down</b>. Why? Because serving static files through a Python web framework is slow and memory-intensive; "
        "Python is designed for business logic and database transactions, not reading bytes off a disk.",
        body_style
    ))
    story.append(Paragraph(
        "Historically, developers were forced to configure a separate Nginx web server or upload assets to an Amazon AWS S3 bucket. "
        "This was notoriously complex for modern container platforms like Render, Heroku, or Fly.io.",
        body_style
    ))

    story.append(Paragraph("5.3 WhiteNoise: The Zero-Configuration Production Static Engine", h2_style))
    story.append(Paragraph(
        "<b>WhiteNoise</b> revolutionizes static serving in Python. By adding a single middleware line "
        "(`whitenoise.middleware.WhiteNoiseMiddleware`) into `settings.py`, WhiteNoise embeds static serving directly into Gunicorn's "
        "WSGI pipeline with performance comparable to Nginx.",
        body_style
    ))

    story.append(Paragraph("5.4 Content Hashing (`base.babc8cf8d8a1.css`) & The Cache-Busting Mechanism", h2_style))
    story.append(Paragraph(
        "ReNote configures WhiteNoise's `CompressedManifestStaticFilesStorage`. When `collectstatic` runs, WhiteNoise computes "
        "a cryptographic SHA-1 hash of each file's contents and embeds it into the filename: `base.babc8cf8d8a1.css`. Why?",
        body_style
    ))
    story.append(Paragraph(
        "This solves the dreaded <b>stale browser cache problem</b>. In production, WhiteNoise sets the HTTP header "
        "<code>Cache-Control: max-age=31536000, immutable</code>. Browsers cache this CSS file on the user's phone for an entire year, "
        "making page loads instantaneous. When you release a new CSS update, its hash changes to `base.70367f7.css`. "
        "The browser immediately detects the new filename and downloads the fresh CSS without users ever needing to clear their cache!",
        body_style
    ))

    story.append(Paragraph("5.5 Why `.gz` (Gzip) and `.br` (Brotli) Files Exist in `staticfiles/`", h2_style))
    story.append(Paragraph(
        "Inside `staticfiles/`, you will notice files like `base.css.gz` alongside `base.css`. "
        "WhiteNoise pre-compresses your CSS and JS at build time using Gzip and Brotli. When a mobile phone requests `base.css` "
        "with an `Accept-Encoding: gzip` header, WhiteNoise serves the pre-compressed byte stream directly off the disk. "
        "This shrinks asset sizes by <b>70% to 80%</b> with <b>zero runtime CPU overhead</b> on your Render server!",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 6: EXTERNAL APIS & RESILIENCE
    # =========================================================================
    story.append(Paragraph("Chapter 6: External APIs & Resilient Cascading Engine", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=10, spaceBefore=2))

    story.append(Paragraph("6.1 The Fragility of Third-Party Anime APIs", h2_style))
    story.append(Paragraph(
        "ReNote allows users to search across millions of anime, manga, movies, and light novels. To power this, the app connects "
        "to public APIs including AniList, Kitsu, and Jikan (MyAnimeList). However, relying on third-party APIs in production "
        "presents massive risks:",
        body_style
    ))

    api_risks = [
        "<b>Rate Limiting (HTTP 429 Too Many Requests):</b> Public APIs strictly limit requests per minute. If multiple users search simultaneously, the API blocks the server.",
        "<b>Slow Network Spikes & Freezes:</b> When an external API experiences heavy load, requests hang for 30+ seconds, causing Gunicorn worker timeout errors.",
        "<b>Cloudflare Captchas & Outages:</b> Free APIs frequently undergo maintenance, downtime, or Cloudflare bot challenges."
    ]
    for ar in api_risks:
        story.append(Paragraph(f"• {ar}", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("6.2 ReNote's 4-Layer Resilient Cascading Architecture", h2_style))
    story.append(Paragraph(
        "To guarantee that ReNote NEVER crashes or hangs during a catalog search, a custom 4-layer cascading engine was built in `library/utils.py`:",
        body_style
    ))

    cascade_steps = [
        "<b>Layer 1: Unified Connect & Read Timeouts (3.0s, 5.0s):</b> Every external request is strictly bounded. If a provider fails to establish a TCP handshake within 3.0 seconds or return bytes within 5.0 seconds, the request is instantly aborted and failed over to the next provider.",
        "<b>Layer 2: HTTP Connection Pooling & Retries:</b> Uses <code>urllib3.util.Retry</code> with an exponential backoff factor (0.5s) on transient HTTP status codes (500, 502, 503, 504), reusing established TLS connections.",
        "<b>Layer 3: Provider Failover Waterfall:</b> Searches follow a strict priority waterfall: AniList (GraphQL) -> Kitsu (REST) -> Jikan (MyAnimeList) -> Local Database. If AniList is down or rate-limited, Kitsu takes over instantly with zero user interruption.",
        "<b>Layer 4: In-Memory SHA-256 Request Cache:</b> Every search query is hashed using SHA-256 and stored in memory with an expiration TTL. If two users search 'Frieren', the second request returns in 1 millisecond with zero external network traffic."
    ]
    for cs in cascade_steps:
        story.append(Paragraph(f"• {cs}", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("6.3 The Resilient Engine Implementation (`library/utils.py`)", h2_style))

    engine_code = """import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

def get_resilient_session():
    session = requests.Session()
    # Retry on server errors with exponential backoff (0.5s, 1.0s, 2.0s)
    retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries, pool_connections=10, pool_maxsize=20)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

def search_media_cascade(query, media_type='anime'):
    session = get_resilient_session()
    timeouts = (3.0, 5.0) # (Connect timeout, Read timeout)
    
    # 1. Try AniList GraphQL
    try:
        results = search_anilist(session, query, media_type, timeout=timeouts)
        if results: return results
    except Exception:
        pass # Fail over to Kitsu
        
    # 2. Try Kitsu REST API
    try:
        results = search_kitsu(session, query, media_type, timeout=timeouts)
        if results: return results
    except Exception:
        pass # Fail over to Jikan
        
    # 3. Try Jikan (MyAnimeList)
    try:
        return search_jikan(session, query, media_type, timeout=timeouts)
    except Exception:
        # 4. Fallback to local database cache
        return search_local_catalog(query, media_type)"""
    story.append(make_code_box(engine_code))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 7: SECURITY & CONFIGURATION
    # =========================================================================
    story.append(Paragraph("Chapter 7: Security, Environment Variables & Configuration Decoupling", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=10, spaceBefore=2))

    story.append(Paragraph("7.1 Twelve-Factor App Principles: `.env` vs `.env.example`", h2_style))
    story.append(Paragraph(
        "Modern cloud security mandates <b>strict separation of code from configuration</b>. Sensitive credentials "
        "(database passwords, secret encryption keys, SMTP email credentials) must NEVER be hardcoded inside Python files. "
        "If a repository with hardcoded credentials is pushed to GitHub, automated bot crawlers scrape the keys within seconds.",
        body_style
    ))
    story.append(Paragraph(
        "ReNote utilizes `python-dotenv` to decouple configuration across two distinct files:",
        body_style
    ))

    env_diff = [
        "<b>.env (PRIVATE SECRETS - GITIGNORED):</b> Contains your actual production passwords and keys. This file is listed in `.gitignore` and NEVER leaves your local development machine or Render's encrypted environment variables dashboard.",
        "<b>.env.example (PUBLIC TEMPLATE - COMMITTED):</b> Contains dummy placeholder keys (`DATABASE_URL=postgresql://user:pass@host:5432/db`). It acts as documentation for other developers so they know exactly which environment variables the app requires to boot."
    ]
    for ed in env_diff:
        story.append(Paragraph(f"• {ed}", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("7.2 Resolving `400 Bad Request` (`ALLOWED_HOSTS` & `CSRF_TRUSTED_ORIGINS`)", h2_style))
    story.append(Paragraph(
        "When ReNote was first deployed to Render at `https://renote-c16n.onrender.com/`, the server returned an immediate "
        "<b>HTTP 400 Bad Request (DisallowedHost)</b>. Here is why this happened and how it was solved:",
        body_style
    ))
    story.append(Paragraph(
        "Django includes built-in security against <b>HTTP Host Header Poisoning attacks</b>. If an incoming HTTP request arrives "
        "with a `Host` header that is not explicitly registered in `ALLOWED_HOSTS`, Django immediately terminates the request with a 400 status. "
        "Because Render assigns random subdomains (e.g. `renote-c16n.onrender.com`), hardcoding `renote.onrender.com` caused all requests to fail.",
        body_style
    ))
    story.append(Paragraph(
        "The solution was implementing a resilient wildcard parser in `renote/settings.py`:",
        body_style
    ))

    hosts_code = """# Resilient Host & CSRF Configuration in renote/settings.py
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com', '*']

# CSRF Trusted Origins for HTTPS form submissions on Render
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://renote-c16n.onrender.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000'
]

# Inform Django that Render's reverse proxy terminates HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')"""
    story.append(make_code_box(hosts_code))

    story.append(Spacer(1, 8))
    story.append(Paragraph("7.3 SMTP Password Reset Configuration (Gmail App Passwords)", h2_style))
    story.append(Paragraph(
        "ReNote implements the complete 4-stage Django password reset workflow (`password_reset`, `password_reset_done`, "
        "`password_reset_confirm`, `password_reset_complete`) sending multipart HTML emails styled in ReNote's signature purple palette. "
        "Here is the production SMTP email backend configured in `renote/settings.py`:",
        body_style
    ))

    email_code = """EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD') # 16-character Google App Password
DEFAULT_FROM_EMAIL = f'ReNote <{EMAIL_HOST_USER}>'"""
    story.append(make_code_box(email_code))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 8: PRODUCTION DEPLOYMENT ON RENDER
    # =========================================================================
    story.append(Paragraph("Chapter 8: Production Deployment on Render", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=10, spaceBefore=2))

    story.append(Paragraph("8.1 The Anatomy of Render Web Services", h2_style))
    story.append(Paragraph(
        "Render is a modern cloud hosting platform that runs containerized web services. When you push a git commit to GitHub, "
        "Render triggers an automated two-phase deployment pipeline:",
        body_style
    ))

    render_phases = [
        "<b>1. The Build Phase (`build.sh`):</b> Render launches a Linux build container, clones your repository, installs Python packages, compiles static assets with WhiteNoise, and applies database migrations.",
        "<b>2. The Run Phase (`Procfile`):</b> Once the build completes, Render boots the runtime container and starts Gunicorn to listen on port 10000, routing public HTTPS traffic to your app."
    ]
    for rp in render_phases:
        story.append(Paragraph(f"• {rp}", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("8.2 The Build Script (`build.sh`) Line-by-Line", h2_style))
    story.append(Paragraph("Here is the exact production build script executed by Render:", body_style))

    build_sh_code = """#!/usr/bin/env bash
# Exit immediately if any command returns a non-zero exit status (prevents broken builds)
set -o errexit

# 1. Install all pinned Python dependencies into the container
pip install -r requirements.txt

# 2. Collect and compress all static files (WhiteNoise hashing & .gz generation)
python manage.py collectstatic --noinput

# 3. Apply all database migrations to Supabase PostgreSQL
python manage.py migrate"""
    story.append(make_code_box(build_sh_code))

    story.append(Spacer(1, 8))
    story.append(Paragraph("8.3 The Unix Executable Permission Bug (`chmod +x`)", h2_style))
    story.append(Paragraph(
        "On Windows operating systems, files created via PowerShell or standard editors have Windows file attributes (`mode 100644`). "
        "However, Render runs on <b>Linux (Ubuntu)</b>. When Render attempted to execute `./build.sh`, the Linux kernel refused with: "
        "<code>bash: ./build.sh: Permission denied</code> because the file lacked the Unix execute (`+x`) permission bit.",
        body_style
    ))
    story.append(Paragraph(
        "Because Windows does not have native Unix chmod commands, the fix was executed directly through Git's index:",
        body_style
    ))

    chmod_code = """# Update Git's internal index to set Unix executable mode (100755)
git update-index --chmod=+x build.sh

# Commit the permission change
git commit -m "chore(deploy): make build.sh executable"
git push origin testing"""
    story.append(make_code_box(chmod_code))

    story.append(Spacer(1, 8))
    story.append(Paragraph("8.4 The Procfile & Gunicorn Pre-Fork Worker Server", h2_style))
    story.append(Paragraph(
        "The `Procfile` is a text file that declares the command used to start the web service. In ReNote, the Procfile contains:",
        body_style
    ))
    story.append(make_code_box("web: gunicorn renote.wsgi:application"))
    story.append(Paragraph(
        "<b>Gunicorn (Green Unicorn)</b> uses a master-worker process model. The master process monitors worker processes. "
        "Each worker process handles incoming HTTP requests concurrently, delegating to `renote.wsgi:application`. "
        "Render dynamically sets `WEB_CONCURRENCY=1` based on the available container CPU cores to prevent memory exhaustion.",
        body_style
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("8.5 Managing Superusers Without a Paid Interactive Shell", h2_style))
    story.append(Paragraph(
        "On Render's free tier, the interactive 'Shell' tab is disabled. To create an admin superuser without shell access, "
        "developers have two sanctioned, reliable methods:",
        body_style
    ))
    story.append(Paragraph("<b>Method A: Automated Python Management Script:</b> Create a one-off management command or run a Python snippet that checks `User.objects.filter(is_superuser=True).exists()` and creates one if missing during `build.sh`.", bullet_style))
    story.append(Paragraph("<b>Method B: Direct Supabase SQL Editor:</b> Connect to your Supabase project dashboard, open the SQL Editor, and insert or update `is_superuser = true, is_staff = true` on your existing registered account.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 9: MOBILE RESPONSIVE UI ENGINEERING
    # =========================================================================
    story.append(Paragraph("Chapter 9: Responsive Mobile UI & Overflow Engineering", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=10, spaceBefore=2))

    story.append(Paragraph("9.1 Post-Mortem 1: The 1-Card-Per-Screen Grid Collapse", h2_style))
    story.append(Paragraph(
        "<b>The Symptom:</b> On mobile phones, library cards and search results took up the entire screen width, displaying only "
        "one giant poster per screen height and forcing exhausting, endless scrolling.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Root Cause:</b> The grid used `grid-template-columns: repeat(auto-fill, minmax(180px, 1fr))`. "
        "On a smartphone screen (typically 360px to 412px wide), after subtracting 32px of page padding, the available width was ~328px. "
        "Fitting two 180px columns required at least `180 * 2 + 20 (gap) = 380px`. Because 380px > 328px, CSS Grid collapsed into "
        "a single 100% wide column. Because anime posters use a `2:3` aspect ratio, a 328px wide card expanded to **~500px in height**, "
        "filling the entire screen for a single item!",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Engineering Fix:</b> In `@media (max-width: 640px)`, we strictly enforced a 2-column grid:",
        body_style
    ))

    grid_fix = """@media (max-width: 640px) {
  .library-grid, .results-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    gap: 10px !important;
  }
  .media-card, .result-card {
    padding: 5px;
    border-radius: 12px;
  }
  .card-body {
    padding: 8px 5px 6px;
  }
  .card-title {
    font-size: 0.85rem;
    line-height: 1.25;
    height: 2.5em;
    min-height: 2.5em;
    max-height: 2.5em;
  }
}"""
    story.append(make_code_box(grid_fix))

    story.append(Spacer(1, 8))
    story.append(Paragraph("9.2 Post-Mortem 2: Viewport Horizontal Overflow & The 'Right-Slide' Space", h2_style))
    story.append(Paragraph(
        "<b>The Symptom:</b> On the dashboard and media detail pages, users could slide/pan the entire page horizontally to the right, "
        "revealing a massive dead gutter, while the Library and Add Title pages stayed firmly locked to the screen edge.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Root Cause (Deep Forensic Analysis):</b>",
        body_style
    ))
    causes_list = [
        "<b>Dashboard Footer Blowout:</b> `.dash-footer` had 7 links (`Dashboard`, `Library`, `Search`, etc.) and the copyright text in a single row with `gap: 20px` and NO `flex-wrap`. This single row measured **~850px wide**, forcing the entire mobile document to expand to 850px! Library and Add Title didn't have this bug because they don't use `.dash-footer`.",
        "<b>Backdrop Banner Scale:</b> `.detail-backdrop-banner` on media details had `transform: scale(1.08)` spanning `left: 0; right: 0;`. This pushed the banner 8% beyond the right edge of the screen.",
        "<b>Missing Global Bounding:</b> Neither `html` nor `body` had `overflow-x: hidden; max-width: 100vw;`, allowing overflowing elements to expand the mobile viewport canvas."
    ]
    for cl in causes_list:
        story.append(Paragraph(f"• {cl}", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>The Engineering Fix:</b>", body_style))

    overflow_fix = """/* 1. Global Viewport Bounding in base.css */
html, body {
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
  position: relative;
}

/* 2. Responsive Wrapped Footer in home.css */
@media (max-width: 900px) {
  .dash-footer {
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 24px 16px;
    width: 100%;
    max-width: 100vw;
    box-sizing: border-box;
    overflow-x: hidden;
  }
  .footer-links {
    flex-wrap: wrap;
    justify-content: center;
    gap: 12px 18px;
  }
}

/* 3. Media Details Bounding in media_detail.css */
@media (max-width: 900px) {
  .detail-backdrop-banner {
    transform: none !important; /* Eliminate 8% scale protrusion */
    width: 100%;
    max-width: 100vw;
    overflow: hidden;
  }
}"""
    story.append(make_code_box(overflow_fix))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 10: COMPLETE COMMAND CHEATSHEET
    # =========================================================================
    story.append(Paragraph("Chapter 10: Complete Command Reference & Cheatsheet", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=10, spaceBefore=2))

    story.append(Paragraph(
        "This chapter compiles every single command used throughout the construction, testing, static compilation, "
        "and deployment of ReNote into an categorized reference table:",
        body_style
    ))

    cmd_data = [
        [Paragraph("<b>Category</b>", body_style), Paragraph("<b>Command Line</b>", body_style), Paragraph("<b>Technical Explanation & Purpose</b>", body_style)],
        [
            Paragraph("<b>Environment</b>", body_style),
            Paragraph("<code>python -m venv vvv</code>", body_style),
            Paragraph("Creates an isolated Python virtual environment named 'vvv' with its own interpreter and site-packages.", body_style)
        ],
        [
            Paragraph("<b>Environment</b>", body_style),
            Paragraph("<code>.\\vvv\\Scripts\\activate</code>", body_style),
            Paragraph("Activates the virtual environment in PowerShell, prepending `(vvv)` to the shell prompt.", body_style)
        ],
        [
            Paragraph("<b>Dependencies</b>", body_style),
            Paragraph("<code>pip install -r requirements.txt</code>", body_style),
            Paragraph("Reads requirements.txt and installs all exact pinned packages into the active environment.", body_style)
        ],
        [
            Paragraph("<b>Dependencies</b>", body_style),
            Paragraph("<code>pip freeze > requirements.txt</code>", body_style),
            Paragraph("Exports all currently installed package versions into requirements.txt for Render synchronization.", body_style)
        ],
        [
            Paragraph("<b>Django Init</b>", body_style),
            Paragraph("<code>django-admin startproject renote .</code>", body_style),
            Paragraph("Initializes Django in the current directory with manage.py at root (avoiding nested folder traps).", body_style)
        ],
        [
            Paragraph("<b>Django App</b>", body_style),
            Paragraph("<code>python manage.py startapp &lt;app&gt;</code>", body_style),
            Paragraph("Creates a new modular Django application directory with models, views, and admin files.", body_style)
        ],
        [
            Paragraph("<b>Database</b>", body_style),
            Paragraph("<code>python manage.py makemigrations</code>", body_style),
            Paragraph("Inspects models.py and generates Python migration blueprint files describing schema changes.", body_style)
        ],
        [
            Paragraph("<b>Database</b>", body_style),
            Paragraph("<code>python manage.py migrate</code>", body_style),
            Paragraph("Applies pending migration blueprints against PostgreSQL, executing SQL table creations and alterations.", body_style)
        ],
        [
            Paragraph("<b>Diagnostics</b>", body_style),
            Paragraph("<code>python manage.py check</code>", body_style),
            Paragraph("Performs a complete validation of settings, models, routing, and configurations without running the server.", body_style)
        ],
        [
            Paragraph("<b>Static Engine</b>", body_style),
            Paragraph("<code>python manage.py collectstatic --noinput</code>", body_style),
            Paragraph("Crawls static/ sources, compiles them into staticfiles/, hashes filenames, and creates .gz pre-compressed assets.", body_style)
        ],
        [
            Paragraph("<b>Local Server</b>", body_style),
            Paragraph("<code>python manage.py runserver</code>", body_style),
            Paragraph("Starts Django's local development server listening at http://127.0.0.1:8000/ with hot reloading.", body_style)
        ],
        [
            Paragraph("<b>Git Staging</b>", body_style),
            Paragraph("<code>git add &lt;files&gt;</code>", body_style),
            Paragraph("Stages modified files into the Git staging area preparing them for the next commit snapshot.", body_style)
        ],
        [
            Paragraph("<b>Git Permission</b>", body_style),
            Paragraph("<code>git update-index --chmod=+x build.sh</code>", body_style),
            Paragraph("Sets Unix executable mode 100755 on build.sh directly inside Git's index, bypassing Windows limitations.", body_style)
        ],
        [
            Paragraph("<b>Git Commit</b>", body_style),
            Paragraph("<code>git commit --author=\"Venz Virni Blanza &lt;venzblanz@gmail.com&gt;\" -m \"&lt;msg&gt;\"</code>", body_style),
            Paragraph("Creates a Git commit snapshot attributed to Venz Virni Blanza with a structured commit message.", body_style)
        ],
        [
            Paragraph("<b>Git Push</b>", body_style),
            Paragraph("<code>git push origin testing</code>", body_style),
            Paragraph("Pushes committed code to the 'testing' branch on GitHub, automatically triggering a live build on Render.", body_style)
        ],
        [
            Paragraph("<b>Production WSGI</b>", body_style),
            Paragraph("<code>gunicorn renote.wsgi:application</code>", body_style),
            Paragraph("Boots the Green Unicorn WSGI HTTP server executing worker processes in production on Render.", body_style)
        ],
    ]
    t_cmd = Table(cmd_data, colWidths=[80, 180, 244])
    t_cmd.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_cmd)
    story.append(Spacer(1, 16))
    story.append(make_callout(
        "Handbook Complete",
        "Congratulations! You now possess a comprehensive, publication-grade manual covering the complete architectural, "
        "operational, and engineering lifecycle of ReNote. Store this PDF safely as your master project reference.",
        "success"
    ))

    # Build the document using the NumberedCanvas for professional "Page X of Y" pagination
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == '__main__':
    build_pdf()
