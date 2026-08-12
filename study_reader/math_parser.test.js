"use strict";

const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const { tokenizeMath } = require("./math_parser.js");

test("tokenizes inline and display math without swallowing prose", () => {
  const parsed = tokenizeMath("Before $ p+q=1 $. Then $$ x=y $$ after.");
  assert.deepEqual(parsed.diagnostics, []);
  assert.deepEqual(parsed.tokens.map((item) => item.kind), ["text", "inline", "text", "display", "text"]);
  assert.equal(parsed.tokens[3].value, "x=y");
  assert.match(parsed.tokens[4].value, /after/);
});

test("handles adjacent display blocks", () => {
  const parsed = tokenizeMath("$$ a=b $$ $$ c=d $$");
  assert.deepEqual(parsed.diagnostics, []);
  assert.deepEqual(parsed.tokens.filter((item) => item.kind === "display").map((item) => item.value), ["a=b", "c=d"]);
});

test("keeps prose after a display closing delimiter", () => {
  const parsed = tokenizeMath("$$ F=x $$ where $ x=1 $ in the sample.");
  assert.deepEqual(parsed.diagnostics, []);
  assert.equal(parsed.tokens[0].kind, "display");
  assert.equal(parsed.tokens[1].value, " where ");
  assert.equal(parsed.tokens[2].kind, "inline");
});

test("leaves unmatched delimiters as text and reports them", () => {
  const source = "Text $ x=1 without a close";
  const parsed = tokenizeMath(source);
  assert.equal(parsed.tokens.length, 1);
  assert.equal(parsed.tokens[0].value, source);
  assert.equal(parsed.diagnostics[0].code, "unclosed-inline-math");
});

test("ignores escaped dollars and dollars inside code spans", () => {
  const source = String.raw`Price \$5 and code \`$not_math$\`, then $x=1$.`;
  const parsed = tokenizeMath(source);
  assert.deepEqual(parsed.diagnostics, []);
  assert.deepEqual(parsed.tokens.filter((item) => item.kind === "inline").map((item) => item.value), ["x=1"]);
});

test("rejects nested dollars inside display math", () => {
  const parsed = tokenizeMath("$$ x + $ y $ = z $$");
  assert.equal(parsed.tokens.length, 1);
  assert.equal(parsed.diagnostics[0].code, "nested-dollar-in-math");
});

test("tokenizes table-cell inline math with the same rules", () => {
  const parsed = tokenizeMath("Expected $ p^{2}+pqF $ value");
  assert.deepEqual(parsed.diagnostics, []);
  assert.equal(parsed.tokens[1].value, "p^{2}+pqF");
});

test("strict book validation includes structured appendices", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "textbook-math-"));
  fs.mkdirSync(path.join(root, "data", "structured"), { recursive: true });
  fs.mkdirSync(path.join(root, "data", "textbook"), { recursive: true });
  fs.writeFileSync(path.join(root, "data", "textbook", "Book_appendix1_textbook.md"), "Valid prose.\n");
  fs.writeFileSync(
    path.join(root, "data", "structured", "Book_appendix1_001.json"),
    JSON.stringify({ blocks: [{ content: "broken $$ formula" }] }),
  );
  fs.writeFileSync(
    path.join(root, "data", "structured", "Book_formula_library.json"),
    JSON.stringify({ formulas: [] }),
  );
  const result = spawnSync(
    process.execPath,
    [path.join(__dirname, "..", "scripts", "validate_textbook_math.js"), "--root", root, "--books", "Book"],
    { encoding: "utf8" },
  );
  assert.equal(result.status, 1);
  assert.match(result.stdout, /Book_appendix1_001\.json/);
  fs.rmSync(root, { recursive: true, force: true });
});
