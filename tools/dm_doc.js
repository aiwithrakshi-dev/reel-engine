// DM document renderer (lead magnet sent when someone comments the keyword).
// node tools/dm_doc.js <spec.json> <watermark.png> <out.docx>
// spec: { title, subtitle, checked, brand, handle, intro, sections: [ {heading, paragraphs:[], checklist:[], bullets:[],
//         table:{header:[], rows:[[...]], widths:[dxa...]}, note } ], sources:[{title,url}], disclaimer }
// Every page carries the "AI with Rakshith" watermark (floating image behind the text in the header), a brand header and
// a page-numbered footer.
const fs = require('fs');
const d = require('docx');
const [specPath, wmPath, out] = process.argv.slice(2);
const S = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const RED = 'E3121B', INK = '1A1A1F', GREY = '6B6B73', FONT = 'Arial';
const W = 11906, H = 16838, M = 1134;          // A4, 2 cm margins
const CW = W - 2 * M;

const run = (text, o = {}) => new d.TextRun({ text, font: FONT, ...o });
const para = (children, o = {}) => new d.Paragraph({ children: Array.isArray(children) ? children : [children], ...o });

function richText(s, base = {}) {             // **bold** spans inside a line
  return s.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map(p =>
    p.startsWith('**') ? run(p.slice(2, -2), { ...base, bold: true }) : run(p, base));
}

const wm = fs.readFileSync(wmPath);
const header = new d.Header({ children: [
  para([
    new d.ImageRun({ type: 'png', data: wm, transformation: { width: 560, height: 560 },
      floating: { horizontalPosition: { relative: d.HorizontalPositionRelativeFrom.PAGE, align: d.HorizontalPositionAlign.CENTER },
                  verticalPosition: { relative: d.VerticalPositionRelativeFrom.PAGE, align: d.VerticalPositionAlign.CENTER },
                  behindDocument: true, allowOverlap: true } }),
    run(S.brand || 'AI with Rakshith', { bold: true, color: RED, size: 18 }),
    run('   ' + (S.handle || ''), { color: GREY, size: 18 }),
  ], { border: { bottom: { style: d.BorderStyle.SINGLE, size: 6, color: RED, space: 4 } } }),
] });
const footer = new d.Footer({ children: [
  para([run('Free resource from ' + (S.brand || 'AI with Rakshith') + ' · please do not resell · page ', { color: GREY, size: 16 }),
        new d.TextRun({ children: [d.PageNumber.CURRENT], font: FONT, color: GREY, size: 16 })], { alignment: d.AlignmentType.CENTER }),
] });

const body = [];
body.push(para(run(S.title, { bold: true, size: 44, color: INK }), { heading: d.HeadingLevel.TITLE }));
if (S.subtitle) body.push(para(run(S.subtitle, { size: 26, color: RED, bold: true }), { spacing: { after: 80 } }));
if (S.checked) body.push(para(run(S.checked, { size: 18, color: GREY, italics: true }), { spacing: { after: 240 } }));
if (S.intro) for (const p of [].concat(S.intro)) body.push(para(richText(p, { size: 22 }), { spacing: { after: 160 } }));

const cell = (text, w, o = {}) => new d.TableCell({
  width: { size: w, type: d.WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 },
  shading: o.fill ? { type: d.ShadingType.CLEAR, color: 'auto', fill: o.fill } : undefined,
  children: [para(richText(String(text), { size: 20, bold: !!o.bold, color: o.color || INK }))] });

let n = 0;
for (const s of S.sections || []) {
  body.push(para(run(s.heading, { bold: true, size: 30, color: INK }), { heading: d.HeadingLevel.HEADING_1 }));
  for (const p of s.paragraphs || []) body.push(para(richText(p, { size: 22 }), { spacing: { after: 140 } }));
  if (s.table) {
    const ws = s.table.widths || s.table.header.map(() => Math.floor(CW / s.table.header.length));
    const tw = ws.reduce((a, b) => a + b, 0);
    body.push(new d.Table({ width: { size: tw, type: d.WidthType.DXA }, columnWidths: ws, rows: [
      new d.TableRow({ tableHeader: true, children: s.table.header.map((h, i) => cell(h, ws[i], { fill: RED, bold: true, color: 'FFFFFF' })) }),
      ...s.table.rows.map((r, k) => new d.TableRow({ children: r.map((c, i) => cell(c, ws[i], { fill: k % 2 ? 'F6F6F8' : 'FFFFFF' })) })),
    ] }));
    body.push(para(run(''), { spacing: { after: 120 } }));
  }
  for (const c of s.checklist || []) {
    n += 1;
    body.push(para([run('☐  ', { size: 24, color: RED, bold: true }), run(n + '. ', { size: 22, bold: true }), ...richText(c, { size: 22 })],
                   { spacing: { after: 120 }, indent: { left: 360, hanging: 360 } }));
  }
  for (const b of s.bullets || []) body.push(para(richText(b, { size: 22 }), { numbering: { reference: 'bul', level: 0 }, spacing: { after: 80 } }));
  if (s.note) body.push(para(richText(s.note, { size: 20, italics: true, color: GREY }), { spacing: { before: 80, after: 160 } }));
}
if ((S.sources || []).length) {
  body.push(para(run('Sources', { bold: true, size: 30, color: INK }), { heading: d.HeadingLevel.HEADING_1 }));
  for (const src of S.sources) body.push(para([new d.ExternalHyperlink({ link: src.url, children: [run(src.title, { size: 18, color: '1155CC', underline: {} })] })],
                                              { numbering: { reference: 'bul', level: 0 }, spacing: { after: 60 } }));
}
if (S.disclaimer) body.push(para(run(S.disclaimer, { size: 16, color: GREY, italics: true }), { spacing: { before: 240 } }));

const doc = new d.Document({
  creator: S.brand || 'AI with Rakshith', title: S.title,
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', run: { font: FONT, size: 44, bold: true }, paragraph: { spacing: { before: 0, after: 80 }, keepNext: true } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', run: { font: FONT, size: 30, bold: true },
        paragraph: { spacing: { before: 280, after: 120 }, keepNext: true, outlineLevel: 0 } },
    ],
  },
  numbering: { config: [{ reference: 'bul', levels: [{ level: 0, format: d.LevelFormat.BULLET, text: '•', alignment: d.AlignmentType.LEFT,
                                                       style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] }] },
  sections: [{ properties: { page: { size: { width: W, height: H }, margin: { top: M, bottom: M, left: M, right: M, header: 567, footer: 567 } } },
               headers: { default: header }, footers: { default: footer }, children: body }],
});
d.Packer.toBuffer(doc).then(b => { fs.writeFileSync(out, b); console.log('docx ->', out); });
