import io
import html
import datetime
from typing import Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from app.database.models import InvestigationModel

def _esc(text: Any) -> str:
    """Safely escape text for ReportLab XML/HTML Paragraph markup."""
    if text is None:
        return ""
    return html.escape(str(text))

def build_investigation_pdf(inv: InvestigationModel) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#18181B'),
        spaceAfter=6
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#18181B'),
        spaceBefore=9,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#3F3F46')
    )

    mono_style = ParagraphStyle(
        'Mono',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#27272A')
    )

    story = []

    # Header / Meta
    story.append(Paragraph("EARTHSAGE AI — SCIENTIFIC RESEARCH & GEOSPATIAL AUDIT REPORT", ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#71717A'))))
    story.append(Paragraph(_esc(inv.title), title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E4E4E7'), spaceAfter=8))

    # Dynamic Hemisphere & Coordinate Formatting
    lat = inv.latitude if inv.latitude is not None else 0.0
    lon = inv.longitude if inv.longitude is not None else 0.0
    lat_dir = 'N' if lat >= 0 else 'S'
    lon_dir = 'E' if lon >= 0 else 'W'
    coord_str = f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir} (WGS84)"

    # Dynamic Observation Count & Completeness
    obs_summary_str = "Monthly Continuous"
    if inv.statistical_metrics:
        for _, p_stats in inv.statistical_metrics.items():
            comp = p_stats.get("completeness", {})
            tr = p_stats.get("trend", {})
            tot = comp.get("total_records") or tr.get("sample_size_months")
            valid = comp.get("valid_records")
            pct = comp.get("completeness_percentage")
            if tot is not None:
                if valid is not None and pct is not None:
                    obs_summary_str = f"{tot} months ({pct:.1f}% valid, {valid} valid)"
                else:
                    obs_summary_str = f"{tot} months"
                break

    # Dynamic Provider & Source Metadata
    raw_meta = inv.raw_data_summary or {}
    provider_name = raw_meta.get("provider", "NASA Langley Research Center")
    source_name = raw_meta.get("source", "NASA POWER / MERRA-2 Reanalysis")

    # Investigation Metadata Table
    meta_data = [
        [Paragraph("<b>Investigation ID:</b>", body_style), Paragraph(_esc(inv.id), mono_style),
         Paragraph("<b>Date Compiled:</b>", body_style), Paragraph(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'), body_style)],
        [Paragraph("<b>Grid Cell Location:</b>", body_style), Paragraph(_esc(f"{inv.location_name}, {inv.country}"), body_style),
         Paragraph("<b>Coordinates:</b>", body_style), Paragraph(coord_str, mono_style)],
        [Paragraph("<b>Temporal Window:</b>", body_style), Paragraph(_esc(f"{inv.start_year}–{inv.end_year}"), body_style),
         Paragraph("<b>Observations:</b>", body_style), Paragraph(_esc(obs_summary_str), body_style)],
        [Paragraph("<b>Primary Provider:</b>", body_style), Paragraph(_esc(provider_name), body_style),
         Paragraph("<b>Data Source:</b>", body_style), Paragraph(_esc(source_name), body_style)],
    ]

    t_meta = Table(meta_data, colWidths=[95, 175, 95, 175])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FAFAFA')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E4E4E7')),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#E4E4E7')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # Research Question & Hypothesis
    story.append(Paragraph("1. Scientific Inquiry & Formal Question", section_heading))
    story.append(Paragraph(f"<b>Research Question:</b> {_esc(inv.research_question)}", body_style))
    if inv.hypothesis:
        story.append(Spacer(1, 3))
        story.append(Paragraph(f"<b>Working Hypothesis:</b> {_esc(inv.hypothesis)}", body_style))

    story.append(Spacer(1, 8))

    # Analytical Methodology
    story.append(Paragraph("2. Analytical Methodology & Non-Parametric Framework", section_heading))
    method_text = (
        "• <b>Annual Aggregation:</b> Annual series are derived using day-weighted monthly means, with exact month durations "
        "and leap years (366 days) strictly respected. Each year is verified for complete 12-month coverage (months 1–12); "
        "incomplete years are systematically excluded from annual trend analysis.<br/>"
        "• <b>Seasonal Mann-Kendall Test:</b> Evaluates monotonic trend across years within each of the 12 calendar months "
        "(Hirsch & Slack 1984). Sen's slope represents the median annual rate of change across seasonal months. "
        "This test does NOT evaluate intra-annual redistribution or seasonal shifts.<br/>"
        "• <b>Serial Autocorrelation Audit:</b> Evaluated across multiple lags using the multi-lag Ljung-Box test "
        "(statsmodels acorr_ljungbox). For series with serial dependence, the Hamed-Rao (1998) variance correction is applied "
        "to prevent anti-conservative p-values.<br/>"
        "• <b>Magnitude Estimation:</b> Trend magnitudes are estimated via non-parametric Sen's Slope (expressed per year) "
        "and compared with parametric Ordinary Least Squares (OLS) regression parameters."
    )
    story.append(Paragraph(method_text, body_style))

    story.append(Spacer(1, 8))

    # Empirical Findings & Measurements Table
    story.append(Paragraph("3. Validated Empirical Findings & Statistical Output", section_heading))
    
    findings_rows = [
        [Paragraph("<b>Parameter</b>", body_style), 
         Paragraph("<b>Classification</b>", body_style), 
         Paragraph("<b>Annual Sen's Slope</b>", body_style),
         Paragraph("<b>Annual MK p-val</b>", body_style),
         Paragraph("<b>Seasonal MK p-val</b>", body_style)]
    ]

    for f in inv.findings:
        m_slope = next((m['value'] + " " + m.get('unit', '') for m in f.get('measurements', []) if 'Slope' in m['label']), "N/A")
        m_ann_p = next((m['uncertainty'] for m in f.get('measurements', []) if 'Slope' in m['label']), "N/A")
        m_seas_p = next((m['value'] for m in f.get('measurements', []) if 'Seasonal' in m['label']), "N/A")

        param_header = f['title'].split(':')[0]
        findings_rows.append([
            Paragraph(_esc(param_header), body_style),
            Paragraph(_esc(f['classification'].upper()), mono_style),
            Paragraph(_esc(str(m_slope)), mono_style),
            Paragraph(_esc(str(m_ann_p)), mono_style),
            Paragraph(_esc(str(m_seas_p)), mono_style),
        ])

    t_findings = Table(findings_rows, colWidths=[150, 90, 110, 95, 95])
    t_findings.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F4F4F5')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E4E4E7')),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#E4E4E7')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_findings)

    story.append(Spacer(1, 6))

    # Detailed Findings Summaries
    for f in inv.findings:
        story.append(Paragraph(f"<b>• {_esc(f['title'])}:</b> {_esc(f['summary'])}", body_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 8))

    # Autocorrelation Audit Section
    story.append(Paragraph("4. Serial Autocorrelation & Variance Adjustment Audit", section_heading))
    has_audit = False
    if hasattr(inv, 'statistical_metrics') and inv.statistical_metrics:
        for param_key, param_stats in inv.statistical_metrics.items():
            trend_data = param_stats.get("trend", {})
            ac = trend_data.get("autocorrelation_audit", {})
            ann_section = trend_data.get("annual_mann_kendall", {})
            hr = ann_section.get("hamed_rao_modified", {})
            orig = ann_section.get("uncorrected_mann_kendall", {})

            if ac and ac.get("status") == "success":
                has_audit = True
                lags_str = ", ".join([f"Lag-{r['lag']}: r={r['autocorrelation_r']}, p={r['p_value']:.4f}" for r in ac.get("lags_detail", [])])
                var_factor = hr.get("variance_correction_factor", 1.0)
                corr_status = "Active" if hr.get("correction_active", False) else "Not triggered (V*/V = 1.0000)"
                
                ac_paragraph = (
                    f"<b>{_esc(param_key)} (Annual Series, N={ac.get('sample_size', 0)}):</b><br/>"
                    f"• Ljung-Box Test (tested lags 1..{len(ac.get('tested_lags', []))}): {lags_str}<br/>"
                    f"• Standard MK: p = {orig.get('p_value', 'N/A')}, Tau = {orig.get('kendall_tau', 'N/A')}, Var(S) = {orig.get('variance_s', 'N/A')}<br/>"
                    f"• Hamed-Rao Modified MK: p = {hr.get('p_value', 'N/A')}, Modified Var(S) = {hr.get('modified_variance_s', 'N/A')}, Variance Factor (V*/V) = {var_factor}<br/>"
                    f"• Correction Status: {corr_status}. {_esc(ac.get('small_sample_limitation', ''))}"
                )
                story.append(Paragraph(ac_paragraph, body_style))
                story.append(Spacer(1, 4))

    if not has_audit:
        story.append(Paragraph("Autocorrelation audit results are documented in the investigation statistical metrics.", body_style))

    story.append(Spacer(1, 8))

    # Limitations & Provenance
    story.append(Paragraph("5. Observational Scope, Limitations & Provenance", section_heading))
    lim_text = (
        f"• <b>Spatial Attribution:</b> This analysis represents a single geographic grid-cell estimate ({_esc(inv.location_name)}: {coord_str}) "
        "derived from the MERRA-2 assimilation grid (0.5° x 0.625° resolution). It does NOT represent a regional or national spatial average.<br/>"
        "• <b>Source Type:</b> Data are model-assimilated reanalysis estimates (NASA POWER / MERRA-2), not direct ground station observations.<br/>"
        "• <b>Citation & DOI:</b> NASA Prediction of Worldwide Energy Resources (POWER) Project, NASA Langley Research Center. DOI: 10.5067/POWER/MERRA2_MONTHLY.<br/>"
        f"• <b>Reproducibility:</b> Query URL and parameters preserved in EarthSage AI PostgreSQL database under investigation key: {_esc(inv.id)}"
    )
    story.append(Paragraph(lim_text, body_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
