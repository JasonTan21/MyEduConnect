from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


OUT = "docs/Phase6_Phase1_Phase2_Draft.docx"
HEADER_BLUE = "1F4E79"
BORDER_BLUE = "B9CBE0"
MAX_TABLE_WIDTH_IN = 6.55


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, start=100, bottom=100, end=100):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in [("top", top), ("start", start), ("bottom", bottom), ("end", end)]:
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def set_cell_borders(cell, color=BORDER_BLUE, size="4"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is not None:
        tc_pr.remove(borders)
    borders = OxmlElement("w:tcBorders")
    tc_pr.append(borders)
    for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), size)
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), color)
        borders.append(tag)


def set_table_borders(table, color="D6DEE8", size="4"):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is not None:
        tbl_pr.remove(borders)
    borders = OxmlElement("w:tblBorders")
    tbl_pr.append(borders)
    for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), size)
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), color)
        borders.append(tag)


def set_table_width(table, width_in=MAX_TABLE_WIDTH_IN):
    width_twips = int(width_in * 1440)
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.first_child_found_in("w:tblW")
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(width_twips))
    tbl_w.set(qn("w:type"), "dxa")

    layout = tbl_pr.first_child_found_in("w:tblLayout")
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")


def normalize_widths(widths):
    if not widths:
        return None
    total = sum(w.inches for w in widths)
    if total <= MAX_TABLE_WIDTH_IN:
        return widths
    scale = MAX_TABLE_WIDTH_IN / total
    return [Inches(w.inches * scale) for w in widths]


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_cell_text(cell, text, bold=False, color=None):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(str(text))
    r.bold = bold
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    r.font.name = "Arial"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    r.font.size = Pt(9.5)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(0)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_cell_margins(cell)


def add_table(doc, headers, rows, widths=None, font_size=9.3):
    widths = normalize_widths(widths)
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table, color=BORDER_BLUE)
    set_table_width(table)
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    for i, header in enumerate(headers):
        set_cell_text(hdr.cells[i], header, bold=True, color="FFFFFF")
        set_cell_shading(hdr.cells[i], HEADER_BLUE)
        set_cell_borders(hdr.cells[i], color=HEADER_BLUE)
        if widths:
            hdr.cells[i].width = widths[i]
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            set_cell_text(cells[i], val)
            set_cell_borders(cells[i], color=BORDER_BLUE)
            if widths:
                cells[i].width = widths[i]
            for p in cells[i].paragraphs:
                for run in p.runs:
                    run.font.size = Pt(font_size)
    doc.add_paragraph()
    return table


def add_kv_table(doc, pairs, label_width=1.75, value_width=5.75):
    total = label_width + value_width
    if total > MAX_TABLE_WIDTH_IN:
        scale = MAX_TABLE_WIDTH_IN / total
        label_width *= scale
        value_width *= scale
    table = doc.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table, color=BORDER_BLUE)
    set_table_width(table)
    for label, value in pairs:
        cells = table.add_row().cells
        cells[0].width = Inches(label_width)
        cells[1].width = Inches(value_width)
        set_cell_text(cells[0], label, bold=True)
        set_cell_shading(cells[0], "EAF1F8")
        set_cell_borders(cells[0], color=BORDER_BLUE)
        set_cell_text(cells[1], value)
        set_cell_borders(cells[1], color=BORDER_BLUE)
    doc.add_paragraph()
    return table


def add_para(doc, text="", style=None, bold_prefix=None):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    if bold_prefix and text.startswith(bold_prefix):
        r1 = p.add_run(bold_prefix)
        r1.bold = True
        r2 = p.add_run(text[len(bold_prefix):])
    else:
        p.add_run(text)
    for run in p.runs:
        run.font.name = "Arial"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    return p


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(item)
        r.font.name = "Arial"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")


def add_finding(doc, number, finding):
    doc.add_heading(f"Finding {number}: {finding['Title']}", level=2)
    pairs = [
        ("Title", finding["Title"]),
        ("Severity", finding["Severity"]),
        ("CVSS v3.1", finding["CVSS"]),
        ("OWASP/CWE", finding["OWASP"]),
        ("Affected component", finding["Affected"]),
        ("Description", finding["Description"]),
        ("Reproduction steps", finding["Steps"]),
        ("Evidence", finding["Evidence"]),
        ("Business impact", finding["Impact"]),
        ("Applied remediation", ""),
        ("Re-test result", ""),
    ]
    add_kv_table(doc, pairs, label_width=1.55, value_width=6.1)


def set_document_defaults(doc):
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.0)
    sec.right_margin = Cm(2.0)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(6)

    for name, size, color in [
        ("Title", 18, "1F4E79"),
        ("Heading 1", 15, "1F4E79"),
        ("Heading 2", 13, "2F5597"),
        ("Heading 3", 11.5, "1F4E79"),
    ]:
        style = styles[name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)
        style.font.bold = True
        style.paragraph_format.line_spacing = 1.15
        style.paragraph_format.space_before = Pt(10)
        style.paragraph_format.space_after = Pt(5)

    for name in ["List Bullet", "List Number"]:
        style = styles[name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
        style.font.size = Pt(11)
        style.paragraph_format.line_spacing = 1.15
        style.paragraph_format.space_after = Pt(2)


def add_cover(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("CCS6324 Ethical Hacking and Penetration Testing")
    r.bold = True
    r.font.name = "Arial"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    r.font.size = Pt(16)
    r.font.color.rgb = RGBColor.from_string("1F4E79")

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(8)
    r = title.add_run("Final Report Draft\nPhase 1 Build Documentation and Phase 2 Findings")
    r.bold = True
    r.font.name = "Arial"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    r.font.size = Pt(18)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.space_after = Pt(18)
    r = sub.add_run("Project: MyEduConnect Vulnerable Learning Platform\nPrepared for Phase 6 final report integration")
    r.font.name = "Arial"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    r.font.size = Pt(11)

    add_kv_table(
        doc,
        [
            ("Target company", "MyEduConnect Sdn Bhd (fictional case study)"),
            ("Repository", "https://github.com/JasonTJIASHENG/MyEduConnect"),
            ("Deployment model", "Local Docker Compose lab"),
            ("Current scope", "Phase 1 build documentation and Phase 2 reconnaissance/enumeration findings"),
            ("Remediation status", "Applied remediation and re-test result fields are intentionally blank pending Phase 5 work."),
        ],
    )

def main():
    doc = Document()
    set_document_defaults(doc)
    add_cover(doc)

    doc.add_heading("Phase 1: Build Documentation", level=1)
    add_para(
        doc,
        "This section documents the vulnerable MyEduConnect lab environment built for the CCS6324 final assignment. The platform is intentionally vulnerable and is intended only for authorized testing inside the local Docker lab.",
    )

    doc.add_heading("1.1 Platform Overview", level=2)
    add_bullets(
        doc,
        [
            "Main web platform: Flask-based learning portal with registration, login, profile, course catalogue/search, enrolment, mock payment, support upload, dashboard, and administrator panel.",
            "Backend database: MySQL 8 container used by the web portal and REST API.",
            "Additional component: separate Flask REST API container consumed by the web portal.",
            "Administration component: Adminer database console exposed for assessment of administrative-service exposure.",
            "Deployment: Docker Compose with reproducible services, port mappings, and seeded demo data.",
        ]
    )

    doc.add_heading("1.2 Architecture and Network Layout", level=2)
    add_para(
        doc,
        "The lab is deployed on the student machine and accessed from Kali or another tester workstation through the Mac host IP. The key lab services are exposed through Docker port mappings.",
    )
    add_table(
        doc,
        ["Host/Container", "Exposed Port", "Internal Port", "Role"],
        [
            ("myeduconnect-web", "8080", "8080", "Main learning portal"),
            ("myeduconnect-web", "2222", "22", "SSH service with weak credentials"),
            ("myeduconnect-api", "5001", "5001", "Separate REST API component"),
            ("myeduconnect-db", "3306", "3306", "MySQL database"),
            ("myeduconnect-adminer", "8081", "8080", "Exposed database administration panel"),
        ],
        [Inches(1.8), Inches(1.15), Inches(1.15), Inches(3.2)],
    )

    doc.add_heading("1.3 Implemented Functional Requirements", level=2)
    add_table(
        doc,
        ["Assignment Requirement", "Implementation"],
        [
            ("Working web platform", "Implemented in Flask with student and admin workflows."),
            ("User registration/login/profile", "Registration, login, logout, profile editing, and dashboard views are available."),
            ("Course browsing/search", "Course catalogue includes 22 seeded courses and a search function."),
            ("Enrolment", "Students can enrol, continue pending payment, cancel enrolment, and enrol again after cancellation."),
            ("Payment workflow", "Mock payment page stores approved payment records with card last-four digits."),
            ("Admin panel", "Admin user can view users/payments and publish announcements."),
            ("Backend server/database", "Python Flask web server and MySQL database containers."),
            ("Additional component", "Separate REST API service on port 5001."),
            ("Redeployment", "Docker Compose and setup guide support instructor redeployment."),
        ],
        [Inches(2.35), Inches(5.15)],
    )

    doc.add_heading("1.4 Deliberate Vulnerability Matrix", level=2)
    add_table(
        doc,
        ["ID", "Requirement", "Category", "Location", "Trigger / Evidence Idea"],
        [
            ("VULN-01", "OWASP Top 10", "A03 Injection / CWE-89", "web/app.py /login", "Login query concatenates email and password hash into SQL."),
            ("VULN-02", "OWASP Top 10", "A03 Injection / CWE-89", "web/app.py /courses?q=", "Course search concatenates user input into SQL."),
            ("VULN-03", "OWASP Top 10", "A03 Injection / CWE-89", "api/api.py /internal/student/<id>", "API path value is concatenated into SQL after static API-key check."),
            ("VULN-04", "OWASP Top 10", "A03 Injection / CWE-79", "dashboard/profile/admin templates", "Stored bio/announcement content is rendered with safe output."),
            ("VULN-05", "OWASP Top 10", "A01 Broken Access Control / CWE-639", "web/app.py /invoice/<payment_id>", "Invoice lookup has no ownership check."),
            ("VULN-06", "OWASP Top 10", "A05 Security Misconfiguration", "web/app.py /support and /uploads", "Upload accepts arbitrary file names/extensions and exposes files."),
            ("VULN-07", "Server/OS", "Weak credentials / CWE-521", "web/Dockerfile, port 2222", "SSH user student:student123 is exposed."),
            ("VULN-08", "Server/OS", "Exposed administrative services", "docker-compose.yml", "MySQL 3306 and Adminer 8081 are exposed."),
            ("VULN-09", "Server/OS", "Weak file permissions", "web/Dockerfile", "Upload and backup directories are world-writable."),
            ("VULN-10", "Cryptographic", "Weak password storage / CWE-916", "web/app.py password_hash()", "Passwords use unsalted MD5 hashes."),
            ("VULN-11", "Cryptographic", "Predictable token / CWE-330", "web/app.py make_session()", "Session token uses user ID and minute timestamp."),
            ("VULN-12", "Network layer", "Cleartext protocol / CWE-319", "web/API communication", "Web service calls API over HTTP with static X-API-Key."),
            ("VULN-13", "Recon evidence", "Information disclosure / CWE-200", "HTTP headers", "Server and X-Powered-By headers disclose stack information."),
        ],
        [Inches(0.75), Inches(1.15), Inches(1.6), Inches(1.7), Inches(2.3)],
        font_size=8.3,
    )

    doc.add_heading("1.5 Setup and Redeployment Summary", level=2)
    add_para(doc, "The instructor can redeploy the lab from the repository with Docker Compose:")
    add_para(doc, 'cd "myeduconnect-lab"', style=None)
    add_para(doc, "docker compose up --build", style=None)
    add_para(
        doc,
        "The application seeds demo accounts, course data, and initial content on first startup. Database state can be reset with docker compose down -v followed by docker compose up --build.",
    )

    doc.add_page_break()
    doc.add_heading("Phase 2: Reconnaissance and Enumeration Findings", level=1)
    add_para(
        doc,
        "Reconnaissance and enumeration were performed from Kali against the locally hosted MyEduConnect lab. The target IP during testing was 192.168.0.92. Since MyEduConnect Sdn Bhd is fictional, public OSINT was simulated against the controlled lab domain and local platform; no real third-party organization was targeted.",
    )

    doc.add_heading("2.1 OSINT and Footprinting Summary", level=2)
    add_table(
        doc,
        ["No.", "Intelligence Finding", "Tool / Source", "Evidence"],
        [
            ("1", "No public WHOIS server/record for myeduconnect.local.", "whois", "evidence/scans/whois/phase2-whois.txt"),
            ("2", "DNS lookup returned NXDOMAIN for myeduconnect.local.", "nslookup", "evidence/scans/dns/phase2-nslookup.txt"),
            ("3", "dig ANY returned no DNS answers and warned that .local is reserved for mDNS.", "dig", "evidence/scans/dns/phase2-dig-any.txt"),
            ("4", "Reverse DNS lookup for 192.168.0.92 returned no useful PTR record.", "dig -x", "evidence/scans/dns/phase2-reverse-dns.txt"),
            ("5", "theHarvester returned no public hosts for myeduconnect.local.", "theHarvester", "evidence/scans/theharvester/phase2-theharvester.json"),
            ("6", "Search-engine reconnaissance found limited/no public footprint for the local domain.", "Browser search", "evidence/scans/search-engine-recon/"),
            ("7", "Main portal reachable on port 8080 and titled MyEduConnect.", "WhatWeb/curl", "evidence/scans/whatweb/phase2-whatweb-web.txt"),
            ("8", "Web stack discloses Werkzeug, Python, and MyEduConnect-Legacy headers.", "WhatWeb/curl", "evidence/scans/http/phase2-web-headers.txt"),
            ("9", "Homepage disclosed demo emails and weak/demo account information.", "WhatWeb/browser", "evidence/scans/whatweb/phase2-whatweb-web.txt"),
            ("10", "REST API health endpoint reachable on port 5001.", "curl/WhatWeb", "evidence/scans/http/phase2-api-headers.txt"),
            ("11", "Adminer database console reachable on port 8081.", "curl/WhatWeb", "evidence/scans/http/phase2-adminer-headers.txt"),
            ("12", "MySQL and SSH services exposed through Docker port mappings.", "Nmap", "evidence/scans/nmap/phase2-tcp-service-scan.txt"),
        ],
        [Inches(0.45), Inches(3.0), Inches(1.35), Inches(2.7)],
        font_size=8.5,
    )

    doc.add_heading("2.2 Services Discovered", level=2)
    add_table(
        doc,
        ["Port", "Protocol", "Service", "Version / Fingerprint", "Component"],
        [
            ("2222", "TCP", "SSH", "OpenSSH 10.0p2 Debian 7+deb13u2", "Web container SSH service"),
            ("3306", "TCP", "MySQL", "MySQL 8.0.46, mysql_native_password", "Database service"),
            ("5001", "TCP", "HTTP", "Werkzeug 3.1.8, Python 3.12.13", "REST API"),
            ("8080", "TCP", "HTTP", "Werkzeug 3.1.8, Python 3.12.13; title MyEduConnect", "Main web portal"),
            ("8081", "TCP", "HTTP", "PHP 8.4.21; title Login - Adminer", "Adminer database console"),
        ],
        [Inches(0.65), Inches(0.85), Inches(1.0), Inches(2.65), Inches(2.35)],
        font_size=8.8,
    )

    findings = [
        {
            "Title": "Technology Stack Disclosure Through HTTP Headers",
            "Severity": "Low",
            "CVSS": "5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)",
            "OWASP": "OWASP A05:2021 Security Misconfiguration; CWE-200 Exposure of Sensitive Information",
            "Affected": "Web portal on port 8080; REST API on port 5001; Adminer on port 8081",
            "Description": "HTTP headers and fingerprinting output disclose framework and runtime details including Werkzeug, Python, PHP, and the custom MyEduConnect-Legacy server header.",
            "Steps": "Run curl -I against ports 8080, 5001, and 8081; run WhatWeb against the same services; review Server and X-Powered-By headers.",
            "Evidence": "evidence/scans/http/phase2-web-headers.txt; evidence/scans/http/phase2-api-headers.txt; evidence/scans/http/phase2-adminer-headers.txt; evidence/scans/whatweb/",
            "Impact": "Attackers can use disclosed stack details to choose framework-specific tests, enumerate likely technologies, and prioritize known weakness research.",
        },
        {
            "Title": "Demo Credentials and User Emails Disclosed on Public Homepage",
            "Severity": "High",
            "CVSS": "8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)",
            "OWASP": "OWASP A07:2021 Identification and Authentication Failures; CWE-798 Use of Hard-coded Credentials; CWE-200 Information Exposure",
            "Affected": "Web portal homepage on port 8080",
            "Description": "The public homepage exposes demo account emails and passwords for admin, student, and SSH access. WhatWeb also captured disclosed email patterns.",
            "Steps": "Access http://192.168.0.92:8080/ without authentication; observe the demo account panel; run WhatWeb against the web portal.",
            "Evidence": "evidence/scans/enumeration/phase2-anonymous-web-home.txt; evidence/scans/whatweb/phase2-whatweb-web.txt; evidence/screenshots/Homepage.png",
            "Impact": "Unauthenticated users can obtain valid credentials and use them to access protected portal or SSH functionality, leading to data exposure and system compromise.",
        },
        {
            "Title": "Weak SSH Credentials on Exposed SSH Service",
            "Severity": "High",
            "CVSS": "8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)",
            "OWASP": "OWASP A07:2021 Identification and Authentication Failures; CWE-521 Weak Password Requirements",
            "Affected": "SSH service on port 2222, myeduconnect-web container",
            "Description": "SSH is exposed to the network on port 2222 and accepts the weak known credential student/student123.",
            "Steps": "Run nmap -sV --script ssh2-enum-algos,ssh-hostkey -p 2222 192.168.0.92; run nc -nv 192.168.0.92 2222; attempt SSH login with student/student123.",
            "Evidence": "evidence/scans/nmap/phase2-ssh-enum.txt; evidence/scans/enumeration/phase2-ssh-banner.txt; evidence/scans/enumeration/phase2-ssh-weak-credential.png",
            "Impact": "An attacker with the weak credential can obtain shell access to the web container, inspect application files, and use the foothold for later exploitation.",
        },
        {
            "Title": "MySQL Service Exposed with Weak Known Credentials",
            "Severity": "Critical",
            "CVSS": "9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)",
            "OWASP": "OWASP A05:2021 Security Misconfiguration; OWASP A07:2021 Identification and Authentication Failures; CWE-521 Weak Password Requirements",
            "Affected": "MySQL database service on port 3306",
            "Description": "MySQL is reachable from the testing network and accepts weak known credentials for root/root and myedu/myedu123. Anonymous access was denied, but credential-based database access was confirmed.",
            "Steps": "Run nmap -sV --script mysql-info -p 3306 192.168.0.92; run timeout 5 nc -nv 192.168.0.92 3306; test mysql --ssl=0 -h 192.168.0.92 -P 3306 -u root -proot -e \"SHOW DATABASES;\" and mysql --ssl=0 -h 192.168.0.92 -P 3306 -u myedu -pmyedu123 -e \"SHOW DATABASES;\".",
            "Evidence": "evidence/scans/nmap/phase2-mysql-enum.txt; evidence/scans/enumeration/phase2-mysql-banner.txt; evidence/scans/enumeration/phase2-mysql-weak-credential.png; evidence/scans/enumeration/phase2-app-db-user-weak-credential.png; evidence/scans/enumeration/phase2-anonymous-mysql.png",
            "Impact": "Database exposure can allow unauthorized viewing or modification of student, guardian, enrolment, payment, and administrative data.",
        },
        {
            "Title": "Exposed Adminer Database Administration Console",
            "Severity": "Critical",
            "CVSS": "9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)",
            "OWASP": "OWASP A05:2021 Security Misconfiguration; CWE-284 Improper Access Control; CWE-798 Use of Hard-coded Credentials",
            "Affected": "Adminer console on port 8081",
            "Description": "Adminer is publicly reachable from the testing network and can be used with weak database credentials to access the MySQL backend.",
            "Steps": "Browse to http://192.168.0.92:8081; review HTTP headers and title; authenticate through Adminer using the weak database credential shown in the evidence.",
            "Evidence": "evidence/scans/http/phase2-adminer-headers.txt; evidence/scans/nmap/phase2-http-enum.txt; evidence/scans/enumeration/phase2-adminer-banner.txt; evidence/scans/enumeration/phase2-adminer-weak-credential.png",
            "Impact": "An exposed database console can provide direct administrative access to sensitive data and can support data tampering, extraction, or destructive actions.",
        },
        {
            "Title": "Unauthenticated API Health Endpoint Discloses Service Information",
            "Severity": "Low",
            "CVSS": "5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)",
            "OWASP": "OWASP A05:2021 Security Misconfiguration; CWE-306 Missing Authentication for Critical Function; CWE-200 Information Exposure",
            "Affected": "REST API health endpoint on port 5001",
            "Description": "The /health endpoint is accessible without authentication and returns the service name and status. The internal stats endpoint correctly rejects anonymous requests, but the health endpoint still confirms the API service and stack.",
            "Steps": "Run curl -i http://192.168.0.92:5001/health and curl -i http://192.168.0.92:5001/internal/stats; compare the unauthenticated 200 response for /health with the 403 response for /internal/stats.",
            "Evidence": "evidence/scans/enumeration/phase2-anonymous-api-health.txt; evidence/scans/enumeration/phase2-anonymous-api-stats.txt; evidence/scans/whatweb/phase2-whatweb-api.txt",
            "Impact": "Attackers can confirm the separate API component and use the information to plan targeted enumeration or later API-specific attacks.",
        },
        {
            "Title": "Public Course Catalogue and Homepage Content Exposed Without Authentication",
            "Severity": "Low",
            "CVSS": "5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)",
            "OWASP": "OWASP A01:2021 Broken Access Control; CWE-200 Information Exposure",
            "Affected": "Web portal homepage and /courses on port 8080",
            "Description": "The homepage and course catalogue are available anonymously. This may be acceptable for public marketing content, but in this lab it also exposes platform functionality, course data, and demo credential hints.",
            "Steps": "Run curl -i http://192.168.0.92:8080/ and curl -i http://192.168.0.92:8080/courses without a session cookie; verify HTTP 200 responses and returned page content.",
            "Evidence": "evidence/scans/enumeration/phase2-anonymous-web-home.txt; evidence/scans/enumeration/phase2-anonymous-web-courses.txt; evidence/scans/enumeration/phase2-anonymous-dashboard.txt",
            "Impact": "Unauthenticated exposure gives attackers workflow context, course catalogue details, and account hints that can support targeted attacks.",
        },
        {
            "Title": "Exposed Host and Lab Services Increase Attack Surface",
            "Severity": "Medium",
            "CVSS": "6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)",
            "OWASP": "OWASP A05:2021 Security Misconfiguration; CWE-200 Information Exposure; CWE-668 Exposure of Resource to Wrong Sphere",
            "Affected": "Target host 192.168.0.92 and Docker-exposed lab services",
            "Description": "Full TCP scanning found multiple open ports. The primary lab services are 2222, 3306, 5001, 8080, and 8081, while additional host-level ports were also visible in the scan output.",
            "Steps": "Run nmap -p- --min-rate 3000 192.168.0.92; compare discovered ports with the Docker Compose platform services.",
            "Evidence": "evidence/scans/nmap/phase2-full-tcp-scan.txt; evidence/scans/nmap/phase2-tcp-service-scan.txt; docs/architecture.md",
            "Impact": "A larger exposed service footprint gives attackers more enumeration paths and makes it harder to distinguish intended application services from host-level services.",
        },
    ]

    doc.add_heading("2.3 Finding Tables", level=2)
    add_para(
        doc,
        "The following finding tables use the assignment-required structure. Applied remediation and re-test result fields are left blank because Phase 5 remediation and re-testing have not yet been completed by the team.",
    )
    for idx, finding in enumerate(findings, 1):
        add_finding(doc, idx, finding)

    doc.add_heading("2.4 Phase 2 Evidence Index", level=2)
    add_table(
        doc,
        ["Evidence Category", "Repository Path"],
        [
            ("OSINT and DNS", "evidence/scans/whois/, evidence/scans/dns/, evidence/scans/theharvester/, evidence/scans/search-engine-recon/"),
            ("Active scanning", "evidence/scans/nmap/"),
            ("HTTP and fingerprinting", "evidence/scans/http/, evidence/scans/whatweb/"),
            ("Service enumeration", "evidence/scans/enumeration/"),
            ("Written Phase 2 notes", "docs/phase2-findings.md and docs/phase2-checklist.md"),
        ],
        [Inches(2.0), Inches(5.5)],
    )

    doc.save(OUT)


if __name__ == "__main__":
    main()
