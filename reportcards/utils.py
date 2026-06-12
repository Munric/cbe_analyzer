from django.template.loader import render_to_string
from weasyprint import HTML

def generate_report_card(student, results):
    html_string = render_to_string(
        'reportcards/report.html',
        {
            'student': student,
            'results': results
        }
    )

    html = HTML(string=html_string)
    html.write_pdf(target='report.pdf')