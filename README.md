# Python Packages

A collection of reusable Python packages.

## Packages

| Package | Description |
|---------|-------------|
| `dev-pytopia` | Development utilities, logging, and terminal command framework |
| `database-dimension` | MongoDB database utilities and models |
| `artificial-mycelium` | LLM/AI provider abstractions (OpenAI, Google, DeepSeek) |
| `fast-server` | FastAPI server utilities and API operation framework |
| `novelty-engine` | Idea management and tracking |
| `coding-guru` | Code observation and improvement tools |

## Installation

Install a specific package from this repository:

```bash
# Using pip
pip install "package-name @ git+https://github.com/CodeThatCodes/python-packages@main#subdirectory=package-name"

# Using uv
uv pip install "package-name @ git+https://github.com/CodeThatCodes/python-packages@main#subdirectory=package-name"
```

Example:
```bash
pip install "database-dimension @ git+https://github.com/CodeThatCodes/python-packages@main#subdirectory=database-dimension"
```

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/CodeThatCodes/python-packages.git
   cd python-packages
   ```

2. Navigate to a package and install dependencies:
   ```bash
   cd database-dimension
   uv sync
   ```

The packages use `[tool.uv.sources]` to reference each other via local paths during development.

## Dependency Graph

```
dev-pytopia (base)
    ↓
database-dimension → dev-pytopia
artificial-mycelium → database-dimension
fast-server → dev-pytopia
    ↓
novelty-engine → fast-server, database-dimension, dev-pytopia
coding-guru → dev-pytopia, artificial-mycelium, fast-server
```
