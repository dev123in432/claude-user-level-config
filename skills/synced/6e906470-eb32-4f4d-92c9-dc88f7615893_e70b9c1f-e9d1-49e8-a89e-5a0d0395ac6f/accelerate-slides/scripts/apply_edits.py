"""apply_edits.py — JSON-driven editor for unpacked PPTX slide XML.

Usage:
    python apply_edits.py < edits.json

Spec format (stdin JSON):
    {
      "path": "<absolute path to slideN.xml>",
      "edits": [
        {
          "shape_id": 4,
          "xfrm": {                          # optional — set shape position/size
            "off": {"x": "587693", "y": "2448834"},
            "ext": {"cx": "5371102", "cy": "3510643"}
          },
          "paragraphs": [                    # optional — replace text in paragraphs
            {"index": 0, "text": "Heading text", "sz": 2000},
            {"index": 2, "text": "Body text",    "sz": 2000}
          ]
        }
      ]
    }

Notes:
    - shape_id matches the <p:cNvPr id="N"> attribute on the shape.
    - Paragraph index is the 0-based position of <a:p> inside the shape's <p:txBody>.
    - If `index` exceeds the current count, a new paragraph is cloned from the last one.
    - "sz" is optional — when set, forces the new run's <a:rPr sz="N"/> to that value.
      Use this to keep callout body text consistent at 20pt (sz=2000) since the
      template's source slides have inconsistent sz attributes across boxes.

Designed to be invoked by Claude during deck generation, with each slide's edits
in its own JSON spec. Discovers shape ids via the helper at the bottom (run with
the --list-shapes flag for ad-hoc inspection).
"""
import json
import sys
import lxml.etree as ET

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'


def replace_paragraph_text(p, new_text, force_sz=None):
    """Collapse a paragraph's runs into a single run with new_text.
    Preserves the first run's <a:rPr> formatting (font, colour, etc.).
    """
    first_r = p.find(f'{A}r')
    rPr_xml = None
    if first_r is not None:
        rPr = first_r.find(f'{A}rPr')
        if rPr is not None:
            rPr_xml = ET.tostring(rPr)
    epr = p.find(f'{A}endParaRPr')
    for child in list(p):
        if child.tag in (f'{A}r', f'{A}br', f'{A}endParaRPr'):
            p.remove(child)
    new_r = ET.SubElement(p, f'{A}r')
    if rPr_xml:
        new_rPr = ET.fromstring(rPr_xml)
        if force_sz is not None:
            new_rPr.set('sz', str(force_sz))
        new_r.insert(0, new_rPr)
    elif force_sz is not None:
        new_rPr = ET.SubElement(new_r, f'{A}rPr')
        new_rPr.set('lang', 'en-AU')
        new_rPr.set('sz', str(force_sz))
        new_rPr.set('dirty', '0')
    new_t = ET.SubElement(new_r, f'{A}t')
    new_t.text = new_text
    if epr is not None:
        p.append(epr)


def find_shape(root, sid):
    for sp in root.iter(f'{P}sp'):
        cNvPr = sp.find(f'.//{P}cNvPr')
        if cNvPr is not None and cNvPr.get('id') == str(sid):
            return sp
    return None


def list_shapes(slide_path):
    """Print a summary of shapes in a slide for ad-hoc inspection.
    Run with: python apply_edits.py --list-shapes <slide_path>
    """
    tree = ET.parse(slide_path)
    root = tree.getroot()
    for sp in root.iter(f'{P}sp'):
        cNvPr = sp.find(f'.//{P}cNvPr')
        sid = cNvPr.get('id')
        name = cNvPr.get('name')
        # xfrm dims
        xfrm = sp.find(f'.//{P}spPr/{A}xfrm')
        dims = ''
        if xfrm is not None:
            off = xfrm.find(f'{A}off')
            ext = xfrm.find(f'{A}ext')
            if off is not None and ext is not None:
                dims = f' off=({off.get("x")},{off.get("y")}) ext=({ext.get("cx")},{ext.get("cy")})'
        # paragraphs
        txBody = sp.find(f'{P}txBody')
        paras = txBody.findall(f'{A}p') if txBody is not None else []
        bits = [f'  sp{sid} {name}{dims}']
        for i, p_el in enumerate(paras):
            t = ''.join(r.text or '' for r in p_el.iter(f'{A}t'))
            bits.append(f'    [{i}] "{t[:80]}"')
        print('\n'.join(bits))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--list-shapes':
        list_shapes(sys.argv[2])
        return
    spec = json.load(sys.stdin)
    path = spec['path']
    tree = ET.parse(path)
    root = tree.getroot()
    for edit in spec['edits']:
        sid = edit['shape_id']
        sp = find_shape(root, sid)
        if sp is None:
            print(f'WARN: shape id {sid} not found in {path}', file=sys.stderr)
            continue
        if 'xfrm' in edit:
            spPr = sp.find(f'{P}spPr')
            xfrm = spPr.find(f'{A}xfrm')
            if xfrm is None:
                xfrm = ET.SubElement(spPr, f'{A}xfrm')
                spPr.remove(xfrm)
                spPr.insert(0, xfrm)
            x = edit['xfrm']
            for tag in ('off', 'ext'):
                el = xfrm.find(f'{A}{tag}')
                if el is None:
                    el = ET.SubElement(xfrm, f'{A}{tag}')
                if tag in x:
                    for k, v in x[tag].items():
                        el.set(k, str(v))
        if 'paragraphs' in edit:
            txBody = sp.find(f'{P}txBody')
            paras = list(txBody.findall(f'{A}p'))
            for change in edit['paragraphs']:
                idx = change['index']
                if idx >= len(paras):
                    new_p = ET.fromstring(ET.tostring(paras[-1]))
                    txBody.append(new_p)
                    paras.append(new_p)
                replace_paragraph_text(paras[idx], change['text'], force_sz=change.get('sz'))
    tree.write(path, xml_declaration=True, encoding='UTF-8', standalone=True)
    print('OK', path)


if __name__ == '__main__':
    main()
