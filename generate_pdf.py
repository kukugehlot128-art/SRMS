import markdown
from xhtml2pdf import pisa
import sys
import re

def convert_markdown_to_pdf(markdown_string, output_filename):
    # Process page break tags before markdown so they are safely parsed
    markdown_string = markdown_string.replace('<div class="page-break"></div>', '<!-- PAGE_BREAK -->')
    
    # Strip the header yaml block if present
    markdown_string = re.sub(r'(?s)^---.*?---', '', markdown_string).strip()

    # Convert markdown to HTML string
    html = markdown.markdown(markdown_string, extensions=["tables"])
    
    # Replace the tokens with proper xhtml2pdf page breaks
    html = html.replace('<!-- PAGE_BREAK -->', '<pdf:nextpage />')

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @page {{
            size: a4 portrait;
            @frame header_frame {{           /* Static Frame */
                -pdf-frame-content: header_content;
                left: 50pt; width: 512pt; top: 30pt; height: 30pt;
            }}
            @frame content_frame {{          /* Content Frame */
                left: 50pt; width: 512pt; top: 70pt; height: 700pt;
            }}
            @frame footer_frame {{           /* Another static Frame */
                -pdf-frame-content: footer_content;
                left: 50pt; width: 512pt; top: 800pt; height: 30pt;
            }}
        }}

        body {{
            font-family: Helvetica, Arial, sans-serif;
            font-size: 11pt;
            color: #222;
            line-height: 1.5;
        }}
        h1 {{
            font-size: 20pt;
            color: #2c3e50;
            margin-top: 15px;
            margin-bottom: 5px;
            border-bottom: 2px solid #2c3e50;
        }}
        h2 {{
            font-size: 16pt;
            color: #2c3e50;
            margin-top: 15px;
            margin-bottom: 5px;
            border-bottom: 1px solid #ddd;
        }}
        h3 {{
            font-size: 14pt;
        }}
        table {{
            -pdf-keep-with-next: true;
            width: 100%;
            border: 1px solid #ccc;
        }}
        th, td {{
            padding: 8px;
            border: 1px solid #ccc;
        }}
        th {{
            background-color: #f5f5f5;
            font-weight: bold;
        }}
        .title-page {{
            text-align: center;
        }}
        .title-page h1 {{ border: none; font-size: 28pt; }}
        .title-page h2 {{ border: none; font-size: 18pt; }}
        pre {{
            background-color: #f5f5f5;
            padding: 10px;
            border: 1px dotted #ccc;
            font-size: 9pt;
        }}
        code {{
            font-family: "Courier New", Courier, monospace;
            background-color: #f5f5f5;
        }}
    </style>
    </head>
    <body>
    
    <div id="header_content" style="text-align: right; border-bottom: 1px solid #ddd; color: #555;">
        Student Result Management System - Project Report
    </div>
    
    <div id="footer_content" style="text-align: center; border-top: 1px solid #ddd; color: #555;">
        Page <pdf:pagenumber>
    </div>
    
    {html}
    </body>
    </html>
    """
    
    with open(output_filename, "wb") as result_file:
        pisa_status = pisa.CreatePDF(
            src=html_template,  # the HTML to convert
            dest=result_file    # file handle to receive result
        )
        
    return pisa_status.err

if __name__ == "__main__":
    with open('Student_Result_Management_System_Report.md', 'r', encoding='utf-8') as f:
        md_text = f.read()
    status = convert_markdown_to_pdf(md_text, 'Student_Result_Management_System_Report.pdf')
    if status:
        print("Error generating PDF!")
        sys.exit(1)
    else:
        print("Successfully created PDF.")
