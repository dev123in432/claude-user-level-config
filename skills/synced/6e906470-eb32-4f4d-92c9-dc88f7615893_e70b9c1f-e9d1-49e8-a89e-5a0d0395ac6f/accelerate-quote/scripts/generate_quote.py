#!/usr/bin/env python3
"""
Accelerate Tech One-Page Quote Generator

Takes a JSON config and the branded template docx, produces a completed quote.
Uses unpack → XML edit → repack approach to preserve all template formatting.

Usage:
    python generate_quote.py --config quote_data.json --template template.docx --output quote.docx
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from copy import deepcopy

# Namespace map for OOXML
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}

# Register all namespaces to avoid ns0: prefixes on output
NAMESPACES_FULL = {
    'wpc': 'http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas',
    'cx': 'http://schemas.microsoft.com/office/drawing/2014/chartex',
    'cx1': 'http://schemas.microsoft.com/office/drawing/2015/9/8/chartex',
    'cx2': 'http://schemas.microsoft.com/office/drawing/2015/10/21/chartex',
    'cx3': 'http://schemas.microsoft.com/office/drawing/2016/5/9/chartex',
    'cx4': 'http://schemas.microsoft.com/office/drawing/2016/5/10/chartex',
    'cx5': 'http://schemas.microsoft.com/office/drawing/2016/5/11/chartex',
    'cx6': 'http://schemas.microsoft.com/office/drawing/2016/5/12/chartex',
    'cx7': 'http://schemas.microsoft.com/office/drawing/2016/5/13/chartex',
    'cx8': 'http://schemas.microsoft.com/office/drawing/2016/5/14/chartex',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'aink': 'http://schemas.microsoft.com/office/drawing/2016/ink',
    'am3d': 'http://schemas.microsoft.com/office/drawing/2017/model3d',
    'o': 'urn:schemas-microsoft-com:office:office',
    'oel': 'http://schemas.microsoft.com/office/2019/extlst',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'v': 'urn:schemas-microsoft-com:vml',
    'wp14': 'http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'w10': 'urn:schemas-microsoft-com:office:word',
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
    'w16cex': 'http://schemas.microsoft.com/office/word/2018/wordml/cex',
    'w16cid': 'http://schemas.microsoft.com/office/word/2016/wordml/cid',
    'w16': 'http://schemas.microsoft.com/office/word/2018/wordml',
    'w16du': 'http://schemas.microsoft.com/office/word/2023/wordml/word16du',
    'w16sdtdh': 'http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash',
    'w16sdtfl': 'http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock',
    'w16se': 'http://schemas.microsoft.com/office/word/2015/wordml/symex',
    'wpg': 'http://schemas.microsoft.com/office/word/2010/wordprocessingGroup',
    'wpi': 'http://schemas.microsoft.com/office/word/2010/wordprocessingInk',
    'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
}

for prefix, uri in NAMESPACES_FULL.items():
    ET.register_namespace(prefix, uri)


def find_text_and_replace(xml_path, old_text, new_text):
    """Simple text find-and-replace in XML file content (string-level)."""
    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(old_text, new_text)
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(content)


def format_currency(amount):
    """Format a number as AUD currency string like $5,610.00"""
    return f"${amount:,.2f}"


def build_line_item_row(description, amount_str):
    """Build XML for a charges table line item row."""
    return f'''<w:tr w:rsidR="009B4887" w:rsidRPr="00FE084C" w14:paraId="75205692" w14:textId="77777777" w:rsidTr="351D3A27">
        <w:tc>
          <w:tcPr>
            <w:tcW w:w="6941" w:type="dxa"/>
            <w:gridSpan w:val="3"/>
          </w:tcPr>
          <w:p w14:paraId="2DA96A8B" w14:textId="4F47DF3C" w:rsidR="009B4887" w:rsidRPr="00F62EDF" w:rsidRDefault="00C3799F" w:rsidP="00885F6D">
            <w:pPr>
              <w:spacing w:before="80" w:after="80"/>
            </w:pPr>
            <w:r>
              <w:t>{escape_xml(description)}</w:t>
            </w:r>
          </w:p>
        </w:tc>
        <w:tc>
          <w:tcPr>
            <w:tcW w:w="2687" w:type="dxa"/>
          </w:tcPr>
          <w:p w14:paraId="57691390" w14:textId="585949E7" w:rsidR="009B4887" w:rsidRPr="00FE084C" w:rsidRDefault="00F62EDF" w:rsidP="00885F6D">
            <w:pPr>
              <w:spacing w:before="80" w:after="80"/>
              <w:jc w:val="right"/>
            </w:pPr>
            <w:r>
              <w:t>{escape_xml(amount_str)}</w:t>
            </w:r>
          </w:p>
        </w:tc>
      </w:tr>'''


def build_total_row(total_str):
    """Build XML for the TOTAL row."""
    return f'''<w:tr w:rsidR="009B4887" w:rsidRPr="00FE084C" w14:paraId="35D8AAD5" w14:textId="77777777" w:rsidTr="351D3A27">
        <w:tc>
          <w:tcPr>
            <w:tcW w:w="6941" w:type="dxa"/>
            <w:gridSpan w:val="3"/>
          </w:tcPr>
          <w:p w14:paraId="238F226C" w14:textId="0B9894E1" w:rsidR="009B4887" w:rsidRPr="00F62EDF" w:rsidRDefault="00F62EDF" w:rsidP="00885F6D">
            <w:pPr>
              <w:spacing w:before="80" w:after="80"/>
              <w:jc w:val="right"/>
              <w:rPr>
                <w:rFonts w:ascii="Cerco" w:hAnsi="Cerco"/>
              </w:rPr>
            </w:pPr>
            <w:r>
              <w:rPr>
                <w:rFonts w:ascii="Cerco" w:hAnsi="Cerco"/>
              </w:rPr>
              <w:t>TOTAL ex GST</w:t>
            </w:r>
          </w:p>
        </w:tc>
        <w:tc>
          <w:tcPr>
            <w:tcW w:w="2687" w:type="dxa"/>
          </w:tcPr>
          <w:p w14:paraId="45284B2C" w14:textId="33CD064D" w:rsidR="009B4887" w:rsidRPr="00F62EDF" w:rsidRDefault="0099353C" w:rsidP="798B323D">
            <w:pPr>
              <w:spacing w:before="80" w:after="80"/>
              <w:jc w:val="right"/>
              <w:rPr>
                <w:rFonts w:ascii="Cerco" w:hAnsi="Cerco"/>
              </w:rPr>
            </w:pPr>
            <w:r>
              <w:t>{escape_xml(total_str)}</w:t>
            </w:r>
          </w:p>
        </w:tc>
      </w:tr>'''


def build_assumption_paragraph(text, is_last=False):
    """Build XML for a single assumption bullet point."""
    return f'''<w:p w14:paraId="48160769" w14:textId="419BAE16" w:rsidR="7B3F5169" w:rsidRPr="00017B52" w:rsidRDefault="7B3F5169" w:rsidP="00017B52">
            <w:pPr>
              <w:pStyle w:val="ListBullet"/>
            </w:pPr>
            <w:r>
              <w:t>{escape_xml(text)}</w:t>
            </w:r>
          </w:p>'''


def escape_xml(text):
    """Escape special XML characters."""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text


def generate_quote(config, template_path, output_path):
    """Main generation function."""
    work_dir = Path('/tmp/quote_work')
    unpacked_dir = work_dir / 'unpacked'

    # Clean up any previous run
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    # Find the docx skill scripts
    skill_scripts = Path('/mnt/skills/public/docx/scripts/office')

    # Unpack
    subprocess.run([
        'python', str(skill_scripts / 'unpack.py'),
        str(template_path), str(unpacked_dir)
    ], check=True, capture_output=True)

    doc_xml = unpacked_dir / 'word' / 'document.xml'

    # --- Simple text replacements in the header metadata table ---
    replacements = {
        # Header metadata table
        '>7 May 2025<': f'>{escape_xml(config["quote_date"])}<',
        '>OPP-01136-2025<': f'>{escape_xml(config["quote_number"])}<',
        '>James Diekman<': f'>{escape_xml(config["document_by"])}<',
        '>Inner West Council<': f'>{escape_xml(config["client_name"])}<',
        '>Steven Thompson<': f'>{escape_xml(config["requested_by"])}<',
    }

    # Email replacement (has space prefix and mixed bold/normal in same paragraph)
    replacements['> Steven.Thompson@innerwest.nsw.gov.au<'] = f'> {escape_xml(config["client_email"])}<'

    # Valid until date
    valid_until = config.get('valid_until', '')
    replacements['>             6 June 2025<'] = f'>             {escape_xml(valid_until)}<'

    # Quote request name
    replacements['>Nitro Forms Integration Pilot (Training and Documentation)<'] = f'>{escape_xml(config["quote_request_name"])}<'

    # Date raised (in quote details table)
    date_raised = config.get('date_raised', config['quote_date'])
    # The date appears twice - once in header, once in details. Handle details separately.
    # We already replaced in header. Now replace the second occurrence in the details table.

    # Date required
    replacements['>20 June 2025<'] = f'>{escape_xml(config["date_required"])}<'

    # Order number
    order_no = config.get('order_number', '-')
    replacements['>-</w:t>\n            </w:r>\n          </w:p>\n        </w:tc>\n      </w:tr>\n      <w:tr w:rsidR="007B4B7C" w14:paraId="3FE279EB"'] = f'>{escape_xml(order_no)}</w:t>\n            </w:r>\n          </w:p>\n        </w:tc>\n      </w:tr>\n      <w:tr w:rsidR="007B4B7C" w14:paraId="3FE279EB"'

    # Charges section header - adapt for model type
    charges_model = config.get('charges_model', 'Time & Material')
    replacements['>Charges \u2013 Time &amp; Material<'] = f'>Charges \u2013 {escape_xml(charges_model)}<'

    # Description of proposed consultation
    replacements['>IWC are seeking Accelerate Tech to assist them with integrating Nitro Forms (esignature solution) into TechnologyOne ECM. Microsoft have provided $11,000 co-funding for this engagement with an additional 3 days effort to be funded by IWC for training, documentation and hand over. The solution will leverage the Microsoft Power Platform, specifically Power Automate and AI Builder to receive Nitro forms requires and route them to different workflows and folders in ECM.<'] = f'>{escape_xml(config["description"])}<'

    # Signature block - Accelerate Tech side
    signer_name = config.get('signer_name', 'James Diekman')
    signer_title = config.get('signer_title', 'CEO')
    signer_date = config.get('signer_date', config['quote_date'])

    # Signature name (Lucida Calligraphy italic)
    # This specific pattern: <w:t>James Diekman</w:t> in Lucida Calligraphy run
    replacements['<w:rPr>\n                <w:rFonts w:ascii="Lucida Calligraphy" w:eastAsia="Lucida Calligraphy" w:hAnsi="Lucida Calligraphy" w:cs="Lucida Calligraphy"/>\n                <w:i/>\n                <w:iCs/>\n              </w:rPr>\n              <w:t>James Diekman</w:t>'] = f'<w:rPr>\n                <w:rFonts w:ascii="Lucida Calligraphy" w:eastAsia="Lucida Calligraphy" w:hAnsi="Lucida Calligraphy" w:cs="Lucida Calligraphy"/>\n                <w:i/>\n                <w:iCs/>\n              </w:rPr>\n              <w:t>{escape_xml(signer_name)}</w:t>'

    # Name row in signature table
    replacements['> James Diekman</w:t>'] = f'> {escape_xml(signer_name)}</w:t>'

    # Title row
    replacements['> Director, Sales &amp; Marketing<'] = f'> {escape_xml(signer_title)}<'

    # Date row in signature
    replacements['> 3 December 2024<'] = f'> {escape_xml(signer_date)}<'

    # Client name in signature acceptance table
    # Already handled by the Inner West Council replacement (appears in both places)

    # Apply all simple replacements
    with open(doc_xml, 'r', encoding='utf-8') as f:
        content = f.read()

    for old, new in replacements.items():
        content = content.replace(old, new)

    # --- Dynamic sections: Line items ---
    # Find and replace the existing line item row + total row
    # Strategy: locate the line item row pattern, replace with new rows

    line_items = config.get('line_items', [])
    if line_items:
        # Build new line item rows
        total = sum(item.get('amount', 0) for item in line_items)
        new_rows = []
        for item in line_items:
            amount_str = format_currency(item['amount'])
            new_rows.append(build_line_item_row(item['description'], amount_str))
        new_rows.append(build_total_row(format_currency(total)))

        # Find the existing line item row (between Description/AUD header and TOTAL row)
        # We'll replace from the first data row through the TOTAL row
        # Pattern: the row containing the consultant description through the TOTAL row

        # Find start: after "AUD ex GST" header row
        marker_start = '<w:t>3 day - Senior Consultant [George Demertzis] @ $1,870.00/day (1 day training, 2 days documentation)</w:t>'
        marker_end_total = '<w:t>$5,610.00</w:t>\n            \n            \n          </w:p>\n        </w:tc>\n      </w:tr>'

        # Find the full row containing the line item
        li_row_start = content.find('<w:tr w:rsidR="009B4887" w:rsidRPr="00FE084C" w14:paraId="75205692"')
        total_row_end_marker = 'w14:paraId="35D8AAD5"'
        total_row_start = content.find('<w:tr w:rsidR="009B4887" w:rsidRPr="00FE084C" w14:paraId="35D8AAD5"')

        if li_row_start > 0 and total_row_start > 0:
            # Find end of total row
            total_row_end = content.find('</w:tr>', total_row_start)
            if total_row_end > 0:
                total_row_end += len('</w:tr>')
                old_block = content[li_row_start:total_row_end]
                new_block = '\n      '.join(new_rows)
                content = content.replace(old_block, new_block)

    # --- Dynamic sections: Assumptions ---
    assumptions = config.get('assumptions', [])
    if assumptions:
        # Find the assumptions cell content (all the ListBullet paragraphs)
        # Pattern: paragraphs with pStyle ListBullet inside the assumptions cell
        # Find from first assumption to last

        first_assumption = 'Accelerate Tech will perform this engagement remotely.'
        last_assumption_end = 'This engagement will be conducted in line with the Microsoft funded engagement. </w:t>'

        # Build new assumption paragraphs
        new_assumptions = []
        for i, assumption in enumerate(assumptions):
            new_assumptions.append(build_assumption_paragraph(
                assumption, is_last=(i == len(assumptions) - 1)
            ))

        # Find the block of assumption paragraphs
        first_p_start = content.find('<w:p w14:paraId="48160769"')
        last_p_marker = 'This engagement will be conducted in line with the Microsoft funded engagement.'
        last_p_pos = content.find(last_p_marker)

        if first_p_start > 0 and last_p_pos > 0:
            # Find end of last assumption paragraph
            last_p_end = content.find('</w:p>', last_p_pos)
            if last_p_end > 0:
                last_p_end += len('</w:p>')
                old_assumptions = content[first_p_start:last_p_end]
                new_assumptions_block = '\n          '.join(new_assumptions)
                content = content.replace(old_assumptions, new_assumptions_block)

    # Write modified content
    with open(doc_xml, 'w', encoding='utf-8') as f:
        f.write(content)

    # Repack (skip validation - template has pre-existing external reference)
    result = subprocess.run([
        'python', str(skill_scripts / 'pack.py'),
        str(unpacked_dir), str(output_path),
        '--original', str(template_path),
        '--validate', 'false'
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Pack stdout: {result.stdout}", file=sys.stderr)
        print(f"Pack stderr: {result.stderr}", file=sys.stderr)
        result.check_returncode()

    # Clean up
    shutil.rmtree(work_dir)

    print(f"Quote generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Generate Accelerate Tech one-page quote')
    parser.add_argument('--config', required=True, help='Path to JSON config file')
    parser.add_argument('--template', required=True, help='Path to template .docx')
    parser.add_argument('--output', required=True, help='Output .docx path')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = json.load(f)

    generate_quote(config, args.template, args.output)


if __name__ == '__main__':
    main()
