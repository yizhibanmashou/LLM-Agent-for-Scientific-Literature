# Examples

This directory contains example scripts demonstrating how to use paper2latex.

## Basic Usage

### [basic_conversion.py](basic_conversion.py)

Demonstrates basic PDF to LaTeX conversion:

```bash
python examples/basic_conversion.py
```

Features shown:
- Full PDF to LaTeX conversion
- Bibliography-only extraction
- Error handling
- Output inspection

## Prerequisites

Before running examples:

1. **Install paper2latex**:
   ```bash
   pip install -e .
   ```

2. **Start GROBID**:
   ```bash
   docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0
   ```

3. **Update PDF path** in the example scripts to point to your test PDF

## More Examples

### Using the MCP Server

Start the server:
```bash
paper2latex
```

Then use with MCP Inspector or any MCP client:
```bash
npx -y @modelcontextprotocol/inspector
```

### Testing with Claude Desktop

Add to your Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "paper2latex": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Tips

- Check `output/report.md` for conversion quality metrics
- Use `keep_intermediates: true` to debug issues
- Increase `formula_dpi` for better formula image quality
- Check `intermediate/grobid.tei.xml` if structure extraction fails
