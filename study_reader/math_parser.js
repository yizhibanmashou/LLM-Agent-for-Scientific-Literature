(function attachStudyMath(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.StudyMath = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function createStudyMath() {
  "use strict";

  function isEscaped(value, index) {
    let slashes = 0;
    for (let cursor = index - 1; cursor >= 0 && value[cursor] === "\\"; cursor -= 1) slashes += 1;
    return slashes % 2 === 1;
  }

  function appendText(tokens, value) {
    if (!value) return;
    const previous = tokens[tokens.length - 1];
    if (previous?.kind === "text") previous.value += value;
    else tokens.push({ kind: "text", value });
  }

  function closingBackticks(value, start, width) {
    const marker = "`".repeat(width);
    return value.indexOf(marker, start + width);
  }

  function closingDisplay(value, start) {
    for (let cursor = start + 2; cursor < value.length - 1; cursor += 1) {
      if (value[cursor] === "$" && value[cursor + 1] === "$" && !isEscaped(value, cursor)) return cursor;
    }
    return -1;
  }

  function closingInline(value, start) {
    for (let cursor = start + 1; cursor < value.length; cursor += 1) {
      if (value[cursor] === "\n") return -1;
      if (
        value[cursor] === "$" &&
        !isEscaped(value, cursor) &&
        value[cursor - 1] !== "$" &&
        value[cursor + 1] !== "$"
      ) return cursor;
    }
    return -1;
  }

  function tokenizeMath(rawValue) {
    const value = String(rawValue || "");
    const tokens = [];
    const diagnostics = [];
    let cursor = 0;
    let textStart = 0;

    const flushText = (end) => {
      appendText(tokens, value.slice(textStart, end));
    };

    while (cursor < value.length) {
      if (value[cursor] === "`") {
        let width = 1;
        while (value[cursor + width] === "`") width += 1;
        const end = closingBackticks(value, cursor, width);
        if (end >= 0) {
          cursor = end + width;
          continue;
        }
      }

      if (value[cursor] !== "$" || isEscaped(value, cursor)) {
        cursor += 1;
        continue;
      }

      const display = value[cursor + 1] === "$";
      const end = display ? closingDisplay(value, cursor) : closingInline(value, cursor);
      if (end < 0) {
        diagnostics.push({ code: display ? "unclosed-display-math" : "unclosed-inline-math", position: cursor });
        cursor += display ? 2 : 1;
        continue;
      }

      const width = display ? 2 : 1;
      const body = value.slice(cursor + width, end).trim();
      const nestedDollar = /(^|[^\\])\$/.test(body);
      if (!body || nestedDollar) {
        diagnostics.push({ code: !body ? "empty-math" : "nested-dollar-in-math", position: cursor });
        cursor = end + width;
        continue;
      }

      flushText(cursor);
      tokens.push({ kind: display ? "display" : "inline", value: body });
      cursor = end + width;
      textStart = cursor;
    }

    flushText(value.length);
    return { tokens, diagnostics };
  }

  function mathTokens(rawValue) {
    return tokenizeMath(rawValue).tokens;
  }

  return { tokenizeMath, mathTokens };
});
