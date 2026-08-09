#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const katex = require("katex");
const { tokenizeMath } = require("../study_reader/math_parser.js");

const ROOT = path.resolve(__dirname, "..");

function parseBooks(argv) {
  const index = argv.indexOf("--books");
  const raw = index >= 0 ? argv[index + 1] : argv.find((item) => item.startsWith("--books="))?.slice(8);
  if (raw) return raw.split(",").map((item) => item.trim()).filter(Boolean);
  const config = JSON.parse(fs.readFileSync(path.join(ROOT, "study_reader", "source_config.json"), "utf8"));
  return Array.isArray(config.strict_math_books) ? config.strict_math_books : [];
}

function json(pathname) {
  return JSON.parse(fs.readFileSync(pathname, "utf8"));
}

function filesMatching(directory, predicate) {
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory).filter(predicate).map((name) => path.join(directory, name));
}

function canonicalDisplayErrors(markdown, location) {
  const errors = [];
  markdown.split(/\r?\n/).forEach((line, index) => {
    if (!line.includes("$$")) return;
    const withoutQuote = line.trim().replace(/^>\s?/, "").trim();
    if (withoutQuote !== "$$") errors.push(`${location}:${index + 1}: display delimiter must occupy its own line`);
  });
  return errors;
}

function validateTeX(tex, location, errors, seen) {
  const value = String(tex || "").trim();
  if (!value) {
    errors.push(`${location}: empty TeX`);
    return;
  }
  if (/(^|[^\\])\$/.test(value)) {
    errors.push(`${location}: TeX contains a raw dollar delimiter`);
    return;
  }
  const key = `${location}\0${value}`;
  if (seen.has(key)) return;
  seen.add(key);
  try {
    katex.renderToString(value, { displayMode: true, throwOnError: true, strict: "ignore", trust: true });
  } catch (error) {
    errors.push(`${location}: ${error.message}`);
  }
}

function validateMixedText(text, location, errors, seen, canonical = false) {
  const parsed = tokenizeMath(text);
  parsed.diagnostics.forEach((item) => errors.push(`${location}:${item.position}: ${item.code}`));
  parsed.tokens.filter((item) => item.kind !== "text").forEach((item, index) => {
    validateTeX(item.value, `${location}#${item.kind}-${index + 1}`, errors, seen);
  });
  if (canonical) errors.push(...canonicalDisplayErrors(text, location));
}

function validateBook(book, errors, seen, counts) {
  const textbookDir = path.join(ROOT, "data", "textbook");
  const structuredDir = path.join(ROOT, "data", "structured");
  const generatedDir = path.join(ROOT, "study_reader", "data", "generated", "chapters");

  const markdownFiles = filesMatching(textbookDir, (name) => name.startsWith(`${book}_`) && name.endsWith("_textbook.md"));
  if (!markdownFiles.length) errors.push(`${book}: no textbook Markdown files`);
  markdownFiles.forEach((pathname) => {
    counts.markdown += 1;
    validateMixedText(fs.readFileSync(pathname, "utf8"), path.relative(ROOT, pathname), errors, seen, true);
  });

  filesMatching(structuredDir, (name) => name.startsWith(`${book}_chapter`) && name.endsWith(".json")).forEach((pathname) => {
    const payload = json(pathname);
    (payload.blocks || []).forEach((block, index) => {
      counts.structuredBlocks += 1;
      validateMixedText(String(block.content || ""), `${path.relative(ROOT, pathname)}:blocks[${index}]`, errors, seen);
    });
  });

  const formulaLibrary = path.join(structuredDir, `${book}_formula_library.json`);
  if (!fs.existsSync(formulaLibrary)) errors.push(`${book}: formula library missing`);
  else (json(formulaLibrary).formulas || []).forEach((formula, index) => {
    counts.formulas += 1;
    validateTeX(formula.latex, `${path.relative(ROOT, formulaLibrary)}:formulas[${index}]`, errors, seen);
  });

  filesMatching(generatedDir, (name) => name.startsWith(`${book}_`) && name.endsWith(".json")).forEach((pathname) => {
    const payload = json(pathname);
    (payload.assets || []).filter((asset) => asset.kind === "formula").forEach((asset, index) => {
      counts.generatedFormulas += 1;
      validateTeX(asset.latex_render || asset.latex, `${path.relative(ROOT, pathname)}:formula-assets[${index}]`, errors, seen);
    });
  });
}

function main() {
  const books = parseBooks(process.argv.slice(2));
  if (!books.length) throw new Error("No strict-math books configured or selected");
  const errors = [];
  const seen = new Set();
  const counts = { markdown: 0, structuredBlocks: 0, formulas: 0, generatedFormulas: 0 };
  books.forEach((book) => validateBook(book, errors, seen, counts));
  const result = { valid: errors.length === 0, books, counts, error_count: errors.length, errors };
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  if (errors.length) process.exitCode = 1;
}

main();
