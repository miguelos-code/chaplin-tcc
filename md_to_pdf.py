import markdown
from xhtml2pdf import pisa
import sys

def convert_md_to_pdf(md_file, pdf_file):
    # Read the markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert Markdown to HTML
    # Add extensions to support tables and blockquotes properly
    html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])

    # Wrap the HTML with basic CSS for PDF rendering
    # xhtml2pdf requires a bit of styling for tables
    styled_html = f"""
    <html>
    <head>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: Arial, sans-serif;
            font-size: 12pt;
            line-height: 1.5;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            font-size: 20pt;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 5px;
            margin-top: 25px;
        }}
        h3 {{
            color: #2980b9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #bdc3c7;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #ecf0f1;
            font-weight: bold;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 10px;
            color: #555;
            font-style: italic;
            margin-left: 0;
            background-color: #f9f9f9;
        }}
        .alert {{
            background-color: #fef9e7;
            border-left: 4px solid #f1c40f;
            padding: 10px;
            margin: 10px 0;
        }}
    </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    
    # We will replace github alerts notation with standard divs if needed, 
    # but the blockquote style already covers them decently since they are blockquotes.
    
    # Write PDF
    with open(pdf_file, "wb") as result_file:
        pisa_status = pisa.CreatePDF(styled_html, dest=result_file)

    if pisa_status.err:
        print("Erro na geração do PDF:", pisa_status.err)
    else:
        print(f"PDF gerado com sucesso em: {pdf_file}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python md_to_pdf.py <input.md> <output.pdf>")
    else:
        convert_md_to_pdf(sys.argv[1], sys.argv[2])
