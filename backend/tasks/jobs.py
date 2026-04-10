"""
Celery Tasks for HMS:
1. send_daily_reminders  - daily appointment reminders via email
2. send_monthly_reports  - monthly activity report for doctors (HTML + PDF)
3. export_patient_csv_task - async CSV export for patients
"""
import csv
import io
import os
from datetime import date, datetime, timedelta
from tasks.celery_app import celery_app


def get_flask_app():
    """Get Flask app for context tasks"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from server import flask_app
    return flask_app


def _generate_monthly_pdf(doctor_name, specialization, month_name, appointments):
    """Generate a PDF monthly activity report using ReportLab"""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=18, textColor=colors.HexColor('#198754'),
                                  spaceAfter=4)
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'],
                                fontSize=11, textColor=colors.HexColor('#495057'),
                                spaceAfter=12)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                    fontSize=12, textColor=colors.HexColor('#0d6efd'),
                                    spaceBefore=12, spaceAfter=6)

    completed = [a for a in appointments if a.status == 'Completed']
    cancelled = [a for a in appointments if a.status == 'Cancelled']

    story = []

    # Title block
    story.append(Paragraph(f'Monthly Activity Report – {month_name}', title_style))
    story.append(Paragraph(f'Dr. {doctor_name} | {specialization}', sub_style))
    story.append(Spacer(1, 0.1*inch))

    # Summary stats table
    story.append(Paragraph('Summary', heading_style))
    summary_data = [
        ['Metric', 'Count'],
        ['Total Appointments', str(len(appointments))],
        ['Completed', str(len(completed))],
        ['Cancelled', str(len(cancelled))],
        ['Pending / Booked', str(len(appointments) - len(completed) - len(cancelled))],
    ]
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.2*inch))

    # Treatment details table
    story.append(Paragraph('Patient Treatment Details', heading_style))
    detail_headers = ['Patient', 'Date', 'Diagnosis', 'Prescription']
    detail_data = [detail_headers]
    for appt in completed:
        t = appt.treatment
        detail_data.append([
            appt.patient.name[:25],
            appt.date.strftime('%d %b %Y'),
            (t.diagnosis[:35] if t and t.diagnosis else '—'),
            (t.prescription[:35] if t and t.prescription else '—'),
        ])
    if len(detail_data) == 1:
        detail_data.append(['No completed appointments', '', '', ''])

    detail_table = Table(detail_data, colWidths=[1.5*inch, 1.2*inch, 2.5*inch, 2.3*inch])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(detail_table)
    story.append(Spacer(1, 0.3*inch))

    # Footer
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'],
                                   fontSize=8, textColor=colors.HexColor('#6c757d'))
    story.append(Paragraph(
        f'Generated on {date.today().strftime("%d %B %Y")} by HMS – Hospital Management System',
        footer_style
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()


@celery_app.task(name='tasks.jobs.send_daily_reminders')
def send_daily_reminders():
    """Send email reminders to patients with appointments today"""
    flask_app = get_flask_app()
    with flask_app.app_context():
        from extensions import mail
        from models.models import Appointment
        from flask_mail import Message

        today = date.today()
        appointments = Appointment.query.filter_by(date=today, status='Booked').all()

        sent_count = 0
        for appt in appointments:
            try:
                patient_email = appt.patient.user.email
                patient_name = appt.patient.name
                doctor_name = appt.doctor.name
                appt_time = appt.time

                msg = Message(
                    subject=f'[HMS] Appointment Reminder - Today at {appt_time}',
                    recipients=[patient_email],
                    html=f"""
                    <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
                    <div style="background:#0d6efd;color:white;padding:20px;border-radius:8px 8px 0 0">
                        <h2>Appointment Reminder</h2>
                    </div>
                    <div style="background:#f8f9fa;padding:20px;border-radius:0 0 8px 8px">
                        <p>Dear <strong>{patient_name}</strong>,</p>
                        <p>This is a reminder that you have a hospital appointment <strong>TODAY</strong>.</p>
                        <table style="width:100%;border-collapse:collapse;margin:15px 0">
                            <tr><td style="padding:8px;background:#e9ecef;font-weight:bold">Doctor</td>
                                <td style="padding:8px">Dr. {doctor_name}</td></tr>
                            <tr><td style="padding:8px;background:#e9ecef;font-weight:bold">Date</td>
                                <td style="padding:8px">{today.strftime('%d %B %Y')}</td></tr>
                            <tr><td style="padding:8px;background:#e9ecef;font-weight:bold">Time</td>
                                <td style="padding:8px">{appt_time}</td></tr>
                            <tr><td style="padding:8px;background:#e9ecef;font-weight:bold">Reason</td>
                                <td style="padding:8px">{appt.reason or 'General consultation'}</td></tr>
                        </table>
                        <p style="color:#6c757d">Please arrive 15 minutes early. Carry your ID and any previous medical records.</p>
                        <p>Best regards,<br><strong>HMS - Hospital Management System</strong></p>
                    </div></body></html>
                    """
                )
                mail.send(msg)
                sent_count += 1
            except Exception as e:
                print(f"Failed to send reminder to {appt.patient.user.email}: {e}")

        return {'sent': sent_count, 'total': len(appointments), 'date': str(today)}


@celery_app.task(name='tasks.jobs.send_monthly_reports')
def send_monthly_reports():
    """Send monthly activity report to all doctors"""
    flask_app = get_flask_app()
    with flask_app.app_context():
        from extensions import mail
        from models.models import Doctor, Appointment, Treatment
        from flask_mail import Message

        today = date.today()
        first_day = today.replace(day=1) - timedelta(days=1)
        month_start = first_day.replace(day=1)
        month_name = month_start.strftime('%B %Y')

        doctors = Doctor.query.filter_by(is_active=True).all()
        sent_count = 0

        for doctor in doctors:
            try:
                appointments = Appointment.query.filter(
                    Appointment.doctor_id == doctor.id,
                    Appointment.date >= month_start,
                    Appointment.date <= first_day
                ).all()

                completed = [a for a in appointments if a.status == 'Completed']
                cancelled = [a for a in appointments if a.status == 'Cancelled']

                rows = ''
                for appt in completed:
                    t = appt.treatment
                    rows += f"""
                    <tr>
                        <td style="padding:8px;border:1px solid #dee2e6">{appt.patient.name}</td>
                        <td style="padding:8px;border:1px solid #dee2e6">{appt.date.strftime('%d %b')}</td>
                        <td style="padding:8px;border:1px solid #dee2e6">{t.diagnosis[:50] if t and t.diagnosis else 'N/A'}</td>
                        <td style="padding:8px;border:1px solid #dee2e6">{t.prescription[:50] if t and t.prescription else 'N/A'}</td>
                    </tr>"""

                html_content = f"""
                <html><body style="font-family:Arial,sans-serif;max-width:700px;margin:0 auto">
                <div style="background:#198754;color:white;padding:20px;border-radius:8px 8px 0 0">
                    <h2>Monthly Activity Report - {month_name}</h2>
                    <p>Dr. {doctor.name} | {doctor.specialization}</p>
                </div>
                <div style="background:#f8f9fa;padding:20px">
                    <div style="display:flex;gap:20px;margin-bottom:20px">
                        <div style="background:white;padding:15px;border-radius:8px;flex:1;text-align:center">
                            <h3 style="color:#0d6efd;margin:0">{len(appointments)}</h3>
                            <p style="margin:5px 0;color:#6c757d">Total Appointments</p>
                        </div>
                        <div style="background:white;padding:15px;border-radius:8px;flex:1;text-align:center">
                            <h3 style="color:#198754;margin:0">{len(completed)}</h3>
                            <p style="margin:5px 0;color:#6c757d">Completed</p>
                        </div>
                        <div style="background:white;padding:15px;border-radius:8px;flex:1;text-align:center">
                            <h3 style="color:#dc3545;margin:0">{len(cancelled)}</h3>
                            <p style="margin:5px 0;color:#6c757d">Cancelled</p>
                        </div>
                    </div>
                    <h4>Patient Treatment Summary</h4>
                    <table style="width:100%;border-collapse:collapse">
                        <tr style="background:#0d6efd;color:white">
                            <th style="padding:8px;text-align:left">Patient</th>
                            <th style="padding:8px;text-align:left">Date</th>
                            <th style="padding:8px;text-align:left">Diagnosis</th>
                            <th style="padding:8px;text-align:left">Prescription</th>
                        </tr>
                        {rows if rows else '<tr><td colspan="4" style="padding:8px;text-align:center">No completed appointments this month</td></tr>'}
                    </table>
                    <p style="margin-top:20px;color:#6c757d;font-size:12px">
                        Generated on {today.strftime('%d %B %Y')} by HMS
                    </p>
                </div></body></html>
                """

                msg = Message(
                    subject=f'[HMS] Monthly Report - {month_name} - Dr. {doctor.name}',
                    recipients=[doctor.user.email],
                    html=html_content
                )

                # Attach PDF report
                try:
                    pdf_bytes = _generate_monthly_pdf(
                        doctor.name, doctor.specialization, month_name, appointments
                    )
                    safe_name = doctor.name.replace(' ', '_')
                    safe_month = month_name.replace(' ', '_')
                    pdf_filename = f"monthly_report_{safe_name}_{safe_month}.pdf"
                    msg.attach(pdf_filename, 'application/pdf', pdf_bytes)
                except Exception as pdf_err:
                    print(f"PDF generation failed for {doctor.name}: {pdf_err}")

                mail.send(msg)
                sent_count += 1
            except Exception as e:
                print(f"Failed to send report to {doctor.user.email}: {e}")

        return {'sent': sent_count, 'total': len(doctors), 'month': month_name}


@celery_app.task(name='tasks.jobs.export_patient_csv_task')
def export_patient_csv_task(patient_id, patient_email, patient_name):
    """Generate and email CSV export of patient treatment history"""
    flask_app = get_flask_app()
    with flask_app.app_context():
        from extensions import mail
        from models.models import Appointment
        from flask_mail import Message

        appointments = Appointment.query.filter_by(
            patient_id=patient_id, status='Completed'
        ).order_by(Appointment.date.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Patient ID', 'Patient Name', 'Consulting Doctor', 'Specialization',
            'Appointment Date', 'Time', 'Diagnosis', 'Prescription',
            'Doctor Notes', 'Next Visit Suggested'
        ])
        for appt in appointments:
            t = appt.treatment
            writer.writerow([
                patient_id, patient_name,
                appt.doctor.name, appt.doctor.specialization,
                appt.date.strftime('%Y-%m-%d'), appt.time,
                t.diagnosis if t else '',
                t.prescription if t else '',
                t.notes if t else '',
                t.next_visit.strftime('%Y-%m-%d') if t and t.next_visit else ''
            ])

        csv_content = output.getvalue()
        filename = f"treatment_history_{patient_name.replace(' ', '_')}_{date.today()}.csv"

        try:
            msg = Message(
                subject=f'[HMS] Your Treatment History Export - {patient_name}',
                recipients=[patient_email],
                html=f"""
                <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
                <div style="background:#0d6efd;color:white;padding:20px;border-radius:8px 8px 0 0">
                    <h2>Treatment History Export</h2>
                </div>
                <div style="background:#f8f9fa;padding:20px;border-radius:0 0 8px 8px">
                    <p>Dear <strong>{patient_name}</strong>,</p>
                    <p>Your treatment history CSV has been generated successfully.</p>
                    <p>The file <strong>{filename}</strong> contains all your completed
                    appointments and treatment details ({len(appointments)} records).</p>
                    <p>Best regards,<br><strong>HMS - Hospital Management System</strong></p>
                </div></body></html>
                """,
                attachments=[(filename, 'text/csv', csv_content.encode('utf-8'))]
            )
            mail.send(msg)
        except Exception as e:
            print(f"Email failed: {e}")

        return {
            'status': 'completed',
            'patient_id': patient_id,
            'records': len(appointments),
            'filename': filename
        }
