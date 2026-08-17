"""
Generate a 1-page PDF field guide for manual annotation in DMS-Eval using ReportLab.
"""

import pathlib
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

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
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#718096"))
        self.drawString(36, 18, "DMS-Eval Benchmark · Manual Annotation Protocol · http://127.0.0.1:8080")
        self.drawRightString(letter[0] - 36, 18, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf(target_path: str):
    doc = SimpleDocTemplate(
        target_path,
        pagesize=letter,
        leftMargin=28,
        rightMargin=28,
        topMargin=20,
        bottomMargin=26
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        textColor=colors.HexColor("#1A202C")
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#4A5568")
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#2B6CB0"),
        spaceAfter=2
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#1A202C")
    )
    body_text = ParagraphStyle(
        'BodyText',
        fontName='Helvetica',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#2D3748")
    )
    body_code = ParagraphStyle(
        'BodyCode',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#805AD5")
    )
    table_header = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8.5,
        textColor=colors.white
    )

    story = []

    # Title & Header
    header_data = [
        [
            Paragraph("📋 <b>DMS-Eval Manual Annotation Field Guide</b>", title_style),
            Paragraph("<b>Single-Page Quick Reference</b><br/>Project: <code>DMS-Eval</code> · 15,723 Frames", subtitle_style)
        ]
    ]
    t_head = Table(header_data, colWidths=[340, 216])
    t_head.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_head)
    story.append(Spacer(1, 3))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceBefore=1, spaceAfter=3))

    # SECTION 1: Hotkeys & Interface Controls
    story.append(Paragraph("<b>⚡ 1. Label Studio Shortcuts & Navigation</b>", section_heading))
    
    hotkey_data = [
        [
            Paragraph("<b>Key</b>", table_header),
            Paragraph("<b>Label / Action</b>", table_header),
            Paragraph("<b>Bounding Box Extent</b>", table_header),
            Paragraph("<b>Control</b>", table_header),
            Paragraph("<b>Function</b>", table_header)
        ],
        [
            Paragraph("<font color='#DD6B20'><b>1</b></font>", body_bold),
            Paragraph("<code>yawning</code>", body_code),
            Paragraph("<b>Mouth region only</b>", body_bold),
            Paragraph("<b>Ctrl + Enter</b>", body_bold),
            Paragraph("Submit & Next Frame", body_text)
        ],
        [
            Paragraph("<font color='#805AD5'><b>2</b></font>", body_bold),
            Paragraph("<code>hand_over_mouth</code>", body_code),
            Paragraph("<b>Full head / face</b>", body_bold),
            Paragraph("<b>Mouse Wheel</b>", body_bold),
            Paragraph("Zoom Canvas In / Out", body_text)
        ],
        [
            Paragraph("<font color='#3182CE'><b>3</b></font>", body_bold),
            Paragraph("<code>drinking</code>", body_code),
            Paragraph("<b>Face + bottle together</b>", body_bold),
            Paragraph("<b>Ctrl + Drag</b>", body_bold),
            Paragraph("Pan Canvas while Zoomed", body_text)
        ],
        [
            Paragraph("<font color='#D53F8C'><b>4</b></font>", body_bold),
            Paragraph("<code>phone_use</code>", body_code),
            Paragraph("<b>Hand + phone at ear</b>", body_bold),
            Paragraph("<b>Delete / Bksp</b>", body_bold),
            Paragraph("Delete Selected Box", body_text)
        ],
        [
            Paragraph("<font color='#319795'><b>5</b></font>", body_bold),
            Paragraph("<code>head_turned_away</code>", body_code),
            Paragraph("<b>Full head / face</b>", body_bold),
            Paragraph("<b>Ctrl + Z</b>", body_bold),
            Paragraph("Undo Last Edit", body_text)
        ],
        [
            Paragraph("<b>—</b>", body_bold),
            Paragraph("<i>Negative Frame</i>", body_bold),
            Paragraph("<b>0 Boxes (Alert Forward)</b>", body_bold),
            Paragraph("<b>0 Boxes</b>", body_bold),
            Paragraph("<b>Ctrl+Enter</b> (Negative Baseline)", body_text)
        ]
    ]

    t_hotkeys = Table(hotkey_data, colWidths=[22, 90, 145, 90, 209])
    t_hotkeys.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_hotkeys)
    story.append(Spacer(1, 5))

    # SECTION 2: Target Warning Cues (Core Rules)
    story.append(Paragraph("<b>🎯 2. Target Warning Cues & Bounding Box Rules</b>", section_heading))

    cues_data = [
        [
            Paragraph("<b>Cue & Key</b>", table_header),
            Paragraph("<b>Visual Definition</b>", table_header),
            Paragraph("<b>Bounding Box Extent</b>", table_header),
            Paragraph("<b>Strict Exclusions (DO NOT ANNOTATE)</b>", table_header)
        ],
        [
            Paragraph("<font color='#DD6B20'><b>[1] yawning</b></font>", body_bold),
            Paragraph("Visibly active yawn distension / deep inhalation posture.", body_text),
            Paragraph("<b>Mouth region only</b>.<br/>Tight rectangle around lips/mouth.", body_bold),
            Paragraph("• <b>Talking/singing</b> open mouth is NOT yawning.<br/>• Do NOT enclose the entire face/head.", body_text)
        ],
        [
            Paragraph("<font color='#6B46C1'><b>[2] hand_over_mouth</b></font>", body_bold),
            Paragraph("Hand/fingers visibly touch, cover, or occlude mouth.", body_text),
            Paragraph("<b>Full head and face</b>.<br/>Enclose entire head + occluding hand.", body_bold),
            Paragraph("• Hand resting on chin without covering mouth aperture is NOT hand over mouth.<br/>• Hand on wheel is NOT hand over mouth.", body_text)
        ],
        [
            Paragraph("<font color='#2B6CB0'><b>[3] drinking</b></font>", body_bold),
            Paragraph("Active drinking with bottle, cup, or can at mouth/face.", body_text),
            Paragraph("<b>Face + bottle together</b>.<br/>Enclose face and beverage container.", body_bold),
            Paragraph("• Passive bottles in cup holders are NOT drinking.<br/>• Must depict active consumption posture.", body_text)
        ],
        [
            Paragraph("<font color='#D53F8C'><b>[4] phone_use</b></font>", body_bold),
            Paragraph("Active handheld phone call (holding phone to ear/head).", body_text),
            Paragraph("<b>Hand + phone at ear</b>.<br/>Enclose phone, hand, and adjacent ear.", body_bold),
            Paragraph("• <b>Texting / lap browsing is EXCLUDED</b>.<br/>• Hands-free voice calls are NOT phone use.<br/>• Mounted phones are NOT phone use.", body_text)
        ],
        [
            Paragraph("<font color='#285E61'><b>[5] head_turned_away</b></font>", body_bold),
            Paragraph("<b>Driver not focused on road forward</b>.<br/>Includes lateral turn (left/right) and downward head slump.", body_text),
            Paragraph("<b>Full head and face</b>.<br/>Enclose entire visible head profile.", body_bold),
            Paragraph("• Minor standard mirror glances (5°–15°) are NOT turned away.<br/>• <code>head_down</code> is <b>merged</b> into this class.", body_text)
        ]
    ]

    t_cues = Table(cues_data, colWidths=[90, 144, 140, 182])
    t_cues.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_cues)
    story.append(Spacer(1, 5))

    # SECTION 3: Decision Matrix & Protocol Enforcements
    story.append(Paragraph("<b>🔍 3. Protocol Rules & Edge Case Decision Matrix</b>", section_heading))

    rules_data = [
        [
            Paragraph("<b>Scenario / Ambiguity</b>", table_header),
            Paragraph("<b>Correct Action</b>", table_header),
            Paragraph("<b>Authoritative Benchmark Rationale</b>", table_header)
        ],
        [
            Paragraph("Driver head slumped downward or rotated away from forward roadway", body_bold),
            Paragraph("<font color='#285E61'><b>head_turned_away</b></font>", body_bold),
            Paragraph("Annotate full head/face under <code>head_turned_away</code> (subsumes all non-forward gaze/head postures including head down).", body_text)
        ],
        [
            Paragraph("Driver yawning while hand visibly covers mouth", body_bold),
            Paragraph("<font color='#2B6CB0'><b>Both Boxes</b></font>", body_bold),
            Paragraph("Annotate <code>hand_over_mouth</code> (Full Head) AND <code>yawning</code> (Mouth). Overlapping boxes expected.", body_text)
        ],
        [
            Paragraph("Driver holding phone to ear during call", body_bold),
            Paragraph("<font color='#D53F8C'><b>phone_use</b></font>", body_bold),
            Paragraph("Annotate <code>phone_use</code> around hand + phone at ear (calling sense only; texting excluded).", body_text)
        ],
        [
            Paragraph("Driver drinking water/beverage from bottle at lips", body_bold),
            Paragraph("<font color='#2B6CB0'><b>drinking</b></font>", body_bold),
            Paragraph("Annotate <code>drinking</code> around face + bottle together (active consumption).", body_text)
        ],
        [
            Paragraph("Closed eyes / blinking during normal driving", body_bold),
            Paragraph("<font color='#C53030'><b>0 Boxes (Negative)</b></font>", body_bold),
            Paragraph("<code>eyes_closed</code> is removed entirely from the single-frame benchmark ontology.", body_text)
        ],
        [
            Paragraph("Single Static Frame Isolation Principle", body_bold),
            Paragraph("<b>Current Frame Only</b>", body_bold),
            Paragraph("Judge strictly by visible pixels in the current image. Do not infer blinks/motion from video memory.", body_text)
        ]
    ]

    t_rules = Table(rules_data, colWidths=[180, 110, 266])
    t_rules.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#F7FAFC"), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t_rules)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF at {target_path}")

if __name__ == "__main__":
    pdf_out = pathlib.Path(__file__).resolve().parents[2] / "docs" / "manual-annotation-guide.pdf"
    build_pdf(str(pdf_out))
