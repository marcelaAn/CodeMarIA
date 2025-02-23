#!/bin/bash

echo "Verificando referências pessoais e caminhos locais..."

# Padrões a serem verificados
PATTERNS=(
    "C:[\\\/]"
    "D:[\\\/]"
    "E:[\\\/]"
    "\/home\/"
    "\\Users\\"
    "DESKTOP-"
    "\\Documents\\"
    "\\AppData\\"
    "marce"
)

# Arquivos a serem ignorados
IGNORED_FILES=(
    ".git/"
    "venv/"
    "node_modules/"
    ".env"
    "*.pyc"
    "__pycache__/"
    ".pytest_cache/"
)

# Constrói o comando grep
IGNORE_PATTERN=$(printf " --exclude-dir=%s" "${IGNORED_FILES[@]}")
SEARCH_PATTERN=$(printf "|%s" "${PATTERNS[@]}")
SEARCH_PATTERN=${SEARCH_PATTERN:1}  # Remove o primeiro |

# Procura por padrões nos arquivos
FOUND=$(grep -r -l -E "$SEARCH_PATTERN" . $IGNORE_PATTERN)

if [ ! -z "$FOUND" ]; then
    echo "ERRO: Encontradas referências pessoais nos seguintes arquivos:"
    echo "$FOUND"
    echo "Por favor, remova estas referências antes de fazer commit."
    exit 1
fi

echo "✅ Nenhuma referência pessoal encontrada."
exit 0 