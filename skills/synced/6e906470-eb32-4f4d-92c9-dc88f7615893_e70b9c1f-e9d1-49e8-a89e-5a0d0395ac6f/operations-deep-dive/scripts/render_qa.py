# -*- coding: utf-8 -*-
"""Render .docx / .pptx files to PNG for visual QA on Windows.

Usage:
    python render_qa.py <out_png_dir> <file1> [file2 ...]

There is no LibreOffice/poppler on this machine, so this uses the installed
Microsoft Office via COM:
  - .pptx -> PNG per slide via PowerPoint Export
  - .docx -> PDF via Word ExportAsFixedFormat, then PNG per page via PyMuPDF

Requires: pywin32 (pip install pywin32), pymupdf (pip install pymupdf), and
Microsoft Office installed. Prints the PNG paths it produced. Read those images
to eyeball the output before delivering. Keep renders OUT of OneDrive-synced
workspace folders - pass a %TEMP% dir as <out_png_dir>.
"""
import sys
import os


def render_pptx(path, outdir):
    import win32com.client as w
    app = w.Dispatch("PowerPoint.Application")
    try:
        pres = app.Presentations.Open(path, ReadOnly=True, WithWindow=False)
        sub = os.path.join(outdir, os.path.splitext(os.path.basename(path))[0])
        os.makedirs(sub, exist_ok=True)
        pres.Export(sub, "PNG", 1280, 720)
        pres.Close()
        return sorted(os.path.join(sub, f) for f in os.listdir(sub) if f.lower().endswith(".png"))
    finally:
        app.Quit()


def render_docx(path, outdir):
    import win32com.client as w
    import fitz
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(path))[0] + ".pdf")
    app = w.gencache.EnsureDispatch("Word.Application")
    app.Visible = False
    try:
        doc = app.Documents.Open(path, ReadOnly=True)
        doc.ExportAsFixedFormat(pdf, 17)  # 17 = wdExportFormatPDF
        doc.Close(False)
    finally:
        app.Quit()
    out = []
    d = fitz.open(pdf)
    base = os.path.splitext(os.path.basename(path))[0]
    for i in range(d.page_count):
        png = os.path.join(outdir, f"{base}_p{i+1}.png")
        d[i].get_pixmap(dpi=100).save(png)
        out.append(png)
    return out


def main():
    if len(sys.argv) < 3:
        print("Usage: python render_qa.py <out_png_dir> <file1> [file2 ...]"); sys.exit(1)
    outdir = os.path.abspath(sys.argv[1])
    os.makedirs(outdir, exist_ok=True)
    for path in sys.argv[2:]:
        # Office COM needs absolute, native (backslash) paths - normalise whatever
        # the caller passed (forward-slash / relative paths otherwise fail to open).
        path = os.path.normpath(os.path.abspath(path))
        ext = os.path.splitext(path)[1].lower()
        try:
            pngs = render_pptx(path, outdir) if ext == ".pptx" else render_docx(path, outdir)
            print(f"\n{path}")
            for p in pngs:
                print("  ", p)
        except Exception as e:
            print(f"\n{path}\n  RENDER FAILED: {e}")


if __name__ == "__main__":
    main()
