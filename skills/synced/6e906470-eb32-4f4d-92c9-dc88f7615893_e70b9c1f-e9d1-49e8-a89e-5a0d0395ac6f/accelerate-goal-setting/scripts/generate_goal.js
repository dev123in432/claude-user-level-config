#!/usr/bin/env node
/**
 * Accelerate Tech — FASSD Goal Submission Doc Generator
 * Usage: node generate_goal.js --dept "..." --head "..." ... --output "path.docx"
 */

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, TabStopType, TabStopPosition,
  PageBreak
} = require('docx');
const fs = require('fs');

// ── CLI args ──────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
function arg(flag, fallback = '') {
  const i = args.indexOf(flag);
  return i !== -1 && args[i + 1] ? args[i + 1] : fallback;
}

const dept     = arg('--dept',    'Unknown Department');
const head     = arg('--head',    'Unknown');
const role     = arg('--role',    '');
const quarter  = arg('--quarter', 'Q? FY??');
const dates    = arg('--dates',   '');
const title    = arg('--title',   'Untitled Goal');
const desc     = arg('--desc',    '');
const fRat     = arg('--f',       'no');
const fNote    = arg('--f-note',  '');
const aRat     = arg('--a',       'no');
const aNote    = arg('--a-note',  '');
const s1Rat    = arg('--s1',      'no');
const s1Note   = arg('--s1-note', '');
const s2Rat    = arg('--s2',      'no');
const s2Note   = arg('--s2-note', '');
const dRat     = arg('--d',       'no');
const dNote    = arg('--d-note',  '');
const context  = arg('--context', '');
const score    = parseFloat(arg('--score', '0'));
const output   = arg('--output',  'goal-submission.docx');

// ── Brand ─────────────────────────────────────────────────────────────────
const NAVY   = '19263C', DKNAV  = '243A5E', TEAL   = '6BE1B8';
const ABLUE  = '1D69F3', LGREEN = 'DAFDBA', ALIGHT = 'ABF8FF';
const WHITE  = 'FFFFFF', MUTED  = 'A8B4C2', MGREY  = 'E0E4EA';
const LGREY  = 'F4F5F7', TXTGRY = '4A5568';
const GREEN  = '0F6E56', AMBER  = '854F0B', RED    = '993C1D';

// ── Borders ───────────────────────────────────────────────────────────────
const NB = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBdr = { top: NB, bottom: NB, left: NB, right: NB };
function sb(c = MGREY, sz = 4) { return { style: BorderStyle.SINGLE, size: sz, color: c }; }

// ── Page geometry ──────────────────────────────────────────────────────────
const PAGE_W = 11906, PAGE_H = 16838;
const ML = 1134, MR = 1134, MT = 1440, MB = 1440;
const CW = PAGE_W - ML - MR; // 9638

// ── Rating helpers ────────────────────────────────────────────────────────
function ratingLabel(r) {
  return r === 'yes' ? 'Yes' : r === 'partial' ? 'Partial' : 'No';
}
function ratingScore(r) {
  return r === 'yes' ? 1.0 : r === 'partial' ? 0.5 : 0;
}
function ratingColor(r) {
  return r === 'yes' ? GREEN : r === 'partial' ? AMBER : RED;
}
function ratingBg(r) {
  return r === 'yes' ? 'EAF3DE' : r === 'partial' ? 'FAEEDA' : 'FCEBEB';
}

const calculatedScore =
  ratingScore(fRat) + ratingScore(aRat) + ratingScore(s1Rat) +
  ratingScore(s2Rat) + ratingScore(dRat);

const displayScore = isNaN(score) || score === 0 ? calculatedScore : score;

function readinessLabel(s) {
  if (s >= 4.5) return { label: 'Strong', color: GREEN };
  if (s >= 3.5) return { label: 'Ready',  color: ABLUE  };
  if (s >= 2.5) return { label: 'Review', color: AMBER  };
  return               { label: 'Weak',   color: RED    };
}
const readiness = readinessLabel(displayScore);

// ── Helpers ───────────────────────────────────────────────────────────────
function sp(n = 1) {
  return new Paragraph({ children: [new TextRun('')], spacing: { after: 120 * n } });
}
function body(text, color = TXTGRY, bold = false) {
  return new Paragraph({
    spacing: { after: 140 },
    children: [new TextRun({ text, color, size: 20, font: 'Arial', bold })]
  });
}
function rule() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: TEAL, space: 4 } },
    spacing: { before: 0, after: 0 },
    children: [new TextRun('')]
  });
}

// ── Cover block ───────────────────────────────────────────────────────────
function cover() {
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [CW],
    borders: { top: NB, bottom: NB, left: NB, right: NB, insideH: NB, insideV: NB },
    rows: [
      // Navy header block
      new TableRow({ children: [new TableCell({
        shading: { fill: NAVY, type: ShadingType.CLEAR }, borders: noBdr,
        margins: { top: 400, bottom: 240, left: 440, right: 440 },
        width: { size: CW, type: WidthType.DXA },
        children: [
          new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: 'ACCELERATE TECH', color: TEAL, size: 18, bold: true, font: 'Arial', characterSpacing: 60 })] }),
          new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: 'Quarterly Goal Submission', color: MUTED, size: 18, font: 'Arial' })] }),
          new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: title, color: WHITE, size: 44, bold: true, font: 'Arial' })] }),
          new Paragraph({ spacing: { after: 300 }, children: [new TextRun({ text: quarter + (dates ? '  |  ' + dates : ''), color: ALIGHT, size: 22, font: 'Arial' })] }),
        ]
      })] }),
      // Teal bar
      new TableRow({ children: [new TableCell({
        shading: { fill: TEAL, type: ShadingType.CLEAR }, borders: noBdr,
        width: { size: CW, type: WidthType.DXA },
        children: [new Paragraph({ children: [new TextRun('')], spacing: { before: 50, after: 50 } })]
      })] }),
      // Meta bar: dept | head | score
      new TableRow({ children: [new TableCell({
        shading: { fill: DKNAV, type: ShadingType.CLEAR }, borders: noBdr,
        margins: { top: 140, bottom: 140, left: 440, right: 440 },
        width: { size: CW, type: WidthType.DXA },
        children: [new Paragraph({ children: [
          new TextRun({ text: dept, color: WHITE, size: 17, bold: true, font: 'Arial' }),
          new TextRun({ text: '   \u2014   ', color: DKNAV, size: 17, font: 'Arial' }),
          new TextRun({ text: head + (role ? ', ' + role : ''), color: MUTED, size: 17, font: 'Arial' }),
          new TextRun({ text: '   \u2014   ', color: DKNAV, size: 17, font: 'Arial' }),
          new TextRun({ text: 'FASSD Score: ', color: MUTED, size: 17, font: 'Arial' }),
          new TextRun({ text: displayScore.toFixed(1) + ' / 5.0', color: readiness.color, size: 17, bold: true, font: 'Arial' }),
          new TextRun({ text: '  \u25cf  ' + readiness.label, color: readiness.color, size: 17, bold: true, font: 'Arial' }),
        ]})]
      })] }),
    ]
  });
}

// ── Section label ─────────────────────────────────────────────────────────
function secLabel(n, txt) {
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [340, CW - 340],
    borders: { top: NB, bottom: NB, left: NB, right: NB, insideH: NB, insideV: NB },
    rows: [new TableRow({ children: [
      new TableCell({
        shading: { fill: NAVY, type: ShadingType.CLEAR }, borders: noBdr,
        margins: { top: 60, bottom: 60, left: 80, right: 80 },
        width: { size: 340, type: WidthType.DXA },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
          new TextRun({ text: String(n), color: TEAL, size: 28, bold: true, font: 'Arial' })
        ]})]
      }),
      new TableCell({
        shading: { fill: LGREY, type: ShadingType.CLEAR }, borders: noBdr,
        margins: { top: 60, bottom: 60, left: 160, right: 80 },
        width: { size: CW - 340, type: WidthType.DXA },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({ children: [
          new TextRun({ text: txt.toUpperCase(), color: NAVY, size: 20, bold: true, font: 'Arial', characterSpacing: 40 })
        ]})]
      })
    ]})]
  });
}

// ── Goal description block ────────────────────────────────────────────────
function descBlock() {
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [CW],
    borders: { top: NB, bottom: NB, left: NB, right: NB, insideH: NB, insideV: NB },
    rows: [new TableRow({ children: [new TableCell({
      shading: { fill: LGREY, type: ShadingType.CLEAR },
      borders: { top: NB, bottom: NB, left: sb(TEAL, 12), right: NB },
      margins: { top: 160, bottom: 160, left: 240, right: 200 },
      width: { size: CW, type: WidthType.DXA },
      children: [
        new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: 'OUTCOME DESCRIPTION', color: MUTED, size: 15, bold: true, font: 'Arial', characterSpacing: 30 })] }),
        new Paragraph({ children: [new TextRun({ text: desc || 'No description provided.', color: NAVY, size: 21, font: 'Arial' })] }),
      ]
    })]})],
  });
}

// ── FASSD assessment table ────────────────────────────────────────────────
function fassdBlock() {
  const items = [
    { k: 'F', name: 'Feasible',    q: 'Can it be achieved with available resources?',     rat: fRat,  note: fNote,  fill: NAVY  },
    { k: 'A', name: 'Achievable',  q: 'Is it within your capability and control?',          rat: aRat,  note: aNote,  fill: DKNAV },
    { k: 'S', name: 'Suitable',    q: 'Aligned with Accelerate\'s values and direction?',  rat: s1Rat, note: s1Note, fill: ABLUE },
    { k: 'S', name: 'Sustainable', q: 'Can it be maintained once achieved?',                rat: s2Rat, note: s2Note, fill: GREEN },
    { k: 'D', name: 'Specific',    q: 'Is it clear, measurable, and unambiguous?',          rat: dRat,  note: dNote,  fill: RED   },
  ];

  const lw = 680, rw = CW - lw;

  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [lw, rw],
    borders: { top: NB, bottom: NB, left: NB, right: NB, insideH: NB, insideV: NB },
    rows: items.flatMap((item, i) => [
      new TableRow({ children: [
        // Letter cell
        new TableCell({
          shading: { fill: item.fill, type: ShadingType.CLEAR }, borders: noBdr,
          margins: { top: 140, bottom: 100, left: 120, right: 80 },
          width: { size: lw, type: WidthType.DXA },
          verticalAlign: VerticalAlign.CENTER,
          children: [
            new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 30 }, children: [
              new TextRun({ text: item.k, color: WHITE, size: 56, bold: true, font: 'Arial', characterSpacing: -10 })
            ]}),
            new Paragraph({ alignment: AlignmentType.CENTER, children: [
              new TextRun({ text: item.name, color: TEAL, size: 16, bold: true, font: 'Arial' })
            ]}),
          ]
        }),
        // Content cell
        new TableCell({
          shading: { fill: i % 2 === 0 ? LGREY : WHITE, type: ShadingType.CLEAR },
          borders: { top: NB, bottom: sb(MGREY, 2), left: sb(ratingColor(item.rat), 10), right: NB },
          margins: { top: 140, bottom: 100, left: 220, right: 160 },
          width: { size: rw, type: WidthType.DXA },
          children: [
            // Question + rating badge on same row
            new Paragraph({ spacing: { after: 50 }, children: [
              new TextRun({ text: item.q + '  ', color: NAVY, size: 20, bold: true, font: 'Arial' }),
            ]}),
            // Rating pill row
            new Paragraph({ spacing: { after: 60 }, children: [
              new TextRun({
                text: '  ' + ratingLabel(item.rat).toUpperCase() + '  ',
                color: ratingColor(item.rat),
                size: 16,
                bold: true,
                font: 'Arial',
                shading: { fill: ratingBg(item.rat), type: ShadingType.CLEAR },
              }),
            ]}),
            // Note
            new Paragraph({ children: [
              new TextRun({ text: item.note || 'No justification provided.', color: TXTGRY, size: 19, font: 'Arial', italics: !item.note }),
            ]}),
          ]
        }),
      ]}),
      // Spacer row between criteria
      ...(i < items.length - 1 ? [
        new TableRow({ children: [
          new TableCell({ borders: noBdr, columnSpan: 2, width: { size: CW, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun('')], spacing: { after: 40 } })] })
        ]})
      ] : [])
    ])
  });
}

// ── Score summary block ───────────────────────────────────────────────────
function scoreBlock() {
  const hw = Math.floor(CW / 2), rw = CW - hw;
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [hw, rw],
    borders: { top: NB, bottom: NB, left: NB, right: NB, insideH: NB, insideV: NB },
    rows: [new TableRow({ children: [
      // Score
      new TableCell({
        shading: { fill: NAVY, type: ShadingType.CLEAR }, borders: noBdr,
        margins: { top: 180, bottom: 180, left: 280, right: 160 },
        width: { size: hw, type: WidthType.DXA },
        children: [
          new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: 'FASSD READINESS SCORE', color: TEAL, size: 15, bold: true, font: 'Arial', characterSpacing: 30 })] }),
          new Paragraph({ children: [
            new TextRun({ text: displayScore.toFixed(1), color: WHITE, size: 56, bold: true, font: 'Arial' }),
            new TextRun({ text: ' / 5.0', color: MUTED, size: 28, font: 'Arial' }),
          ]}),
        ]
      }),
      // Readiness label
      new TableCell({
        shading: { fill: DKNAV, type: ShadingType.CLEAR }, borders: noBdr,
        margins: { top: 180, bottom: 180, left: 280, right: 160 },
        width: { size: rw, type: WidthType.DXA },
        verticalAlign: VerticalAlign.CENTER,
        children: [
          new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: 'READINESS', color: MUTED, size: 15, bold: true, font: 'Arial', characterSpacing: 30 })] }),
          new Paragraph({ children: [new TextRun({ text: readiness.label, color: readiness.color, size: 42, bold: true, font: 'Arial' })] }),
        ]
      }),
    ]})]
  });
}

// ── Context block ─────────────────────────────────────────────────────────
function contextBlock() {
  if (!context) return null;
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [CW],
    borders: { top: NB, bottom: NB, left: NB, right: NB, insideH: NB, insideV: NB },
    rows: [new TableRow({ children: [new TableCell({
      shading: { fill: 'FAEEDA', type: ShadingType.CLEAR },
      borders: { top: NB, bottom: NB, left: sb(AMBER, 12), right: NB },
      margins: { top: 140, bottom: 140, left: 240, right: 200 },
      width: { size: CW, type: WidthType.DXA },
      children: [
        new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: 'ADDITIONAL CONTEXT / RISKS / DEPENDENCIES', color: AMBER, size: 15, bold: true, font: 'Arial', characterSpacing: 30 })] }),
        new Paragraph({ children: [new TextRun({ text: context, color: TXTGRY, size: 20, font: 'Arial' })] }),
      ]
    })]})],
  });
}

// ── Signature / approval block ─────────────────────────────────────────────
function approvalBlock() {
  const cw3 = Math.floor(CW / 3), last = CW - cw3 * 2;
  function sigCell(label, w) {
    return new TableCell({
      shading: { fill: LGREY, type: ShadingType.CLEAR },
      borders: { top: NB, bottom: NB, left: sb(MGREY, 4), right: NB },
      margins: { top: 120, bottom: 200, left: 180, right: 120 },
      width: { size: w, type: WidthType.DXA },
      children: [
        new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: label.toUpperCase(), color: MUTED, size: 15, bold: true, font: 'Arial', characterSpacing: 20 })] }),
        new Paragraph({ border: { bottom: sb(MGREY, 6) }, children: [new TextRun({ text: '  ', size: 20 })] }),
      ]
    });
  }
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [cw3, cw3, last],
    borders: { top: NB, bottom: NB, left: NB, right: NB, insideH: NB, insideV: NB },
    rows: [new TableRow({ children: [
      sigCell('Submitted by: ' + head, cw3),
      sigCell('Date submitted', cw3),
      sigCell('CEO approval', last),
    ]})]
  });
}

// ── Build the document ────────────────────────────────────────────────────
const today = new Date().toLocaleDateString('en-AU', { day: 'numeric', month: 'long', year: 'numeric' });

const children = [
  cover(),
  sp(3),

  // Section 1 — Goal
  secLabel(1, 'Goal Overview'),
  sp(),
  descBlock(),
  sp(2),

  // Section 2 — FASSD
  secLabel(2, 'FASSD Assessment'),
  sp(),
  fassdBlock(),
  sp(2),

  // Section 3 — Score
  secLabel(3, 'Readiness Score'),
  sp(),
  scoreBlock(),
  sp(2),
];

// Section 4 — Context (conditional)
const ctx = contextBlock();
if (ctx) {
  children.push(secLabel(4, 'Additional Context'), sp(), ctx, sp(2));
}

// Signature
children.push(rule(), sp());
children.push(approvalBlock());
children.push(sp());
children.push(new Paragraph({ children: [new TextRun({ text: 'Generated: ' + today + '  \u2014  Accelerate Tech Quarterly Planning  \u2014  Internal Use Only', color: MUTED, size: 15, font: 'Arial' })] }));

const doc = new Document({
  styles: { default: { document: { run: { font: 'Arial', size: 20 } } } },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: PAGE_H },
        margin: { top: MT, bottom: MB, left: ML, right: MR }
      }
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: TEAL, space: 4 } },
        spacing: { after: 80 },
        tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
        children: [
          new TextRun({ text: 'Accelerate Tech', color: NAVY, size: 16, bold: true, font: 'Arial' }),
          new TextRun({ text: '  \u2014  FASSD Goal Submission', color: MUTED, size: 16, font: 'Arial' }),
          new TextRun({ text: '\t', font: 'Arial' }),
          new TextRun({ text: quarter + '  |  ' + dept, color: MUTED, size: 16, font: 'Arial' }),
        ]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        border: { top: { style: BorderStyle.SINGLE, size: 4, color: MGREY, space: 4 } },
        spacing: { before: 80 },
        tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
        children: [
          new TextRun({ text: 'Confidential \u2014 Accelerate Tech', color: MUTED, size: 16, font: 'Arial' }),
          new TextRun({ text: '\t', font: 'Arial' }),
          new TextRun({ text: 'Page ', color: MUTED, size: 16, font: 'Arial' }),
          new TextRun({ children: [PageNumber.CURRENT], color: MUTED, size: 16, font: 'Arial' }),
          new TextRun({ text: ' of ', color: MUTED, size: 16, font: 'Arial' }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], color: MUTED, size: 16, font: 'Arial' }),
        ]
      })] })
    },
    children,
  }]
});

Packer.toBuffer(doc)
  .then(buf => {
    fs.writeFileSync(output, buf);
    console.log('Generated: ' + output);
  })
  .catch(err => {
    console.error('Error generating document:', err.message);
    process.exit(1);
  });
