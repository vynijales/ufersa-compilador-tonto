from difflib import get_close_matches
from typing import Optional

from lexer.lexer import (
    CLASS_STEREOTYPES,
    KEYWORDS,
    META_ATTRIBUTES,
    NATIVE_TYPES,
    RELATION_STEREOTYPES,
)


# Função auxiliar para fuzzy matching
def find_similar_token(token: str, token_type: Optional[str] = None) -> Optional[str]:
    """
    Encontra tokens similares usando fuzzy matching.

    Args:
        token: O token que causou erro
        token_type: Tipo do token esperado (opcional)

    Returns:
        String com sugestão ou None
    """
    token_lower = token.lower()
    suggestions = []

    # Buscar em palavras-chave
    keywords = list(KEYWORDS.keys())
    close_keywords = get_close_matches(token_lower, keywords, n=3, cutoff=0.6)
    if close_keywords:
        suggestions.extend(close_keywords)

    # Buscar em estereótipos de classe
    close_class_stereotypes = get_close_matches(
        token_lower, CLASS_STEREOTYPES, n=3, cutoff=0.6
    )
    if close_class_stereotypes:
        suggestions.extend(close_class_stereotypes)

    # Buscar em estereótipos de relação
    close_relation_stereotypes = get_close_matches(
        token_lower, RELATION_STEREOTYPES, n=3, cutoff=0.6
    )
    if close_relation_stereotypes:
        suggestions.extend(close_relation_stereotypes)

    # Buscar em tipos nativos
    close_native_types = get_close_matches(token_lower, NATIVE_TYPES, n=3, cutoff=0.6)
    if close_native_types:
        suggestions.extend(close_native_types)

    # Buscar em meta-atributos
    close_meta_attrs = get_close_matches(token_lower, META_ATTRIBUTES, n=3, cutoff=0.6)
    if close_meta_attrs:
        suggestions.extend(close_meta_attrs)

    if suggestions:
        # Remover duplicatas mantendo ordem
        unique_suggestions = list(dict.fromkeys(suggestions))
        if len(unique_suggestions) == 1:
            return f"Você quis dizer '{unique_suggestions[0]}'?"
        else:
            return f"Você quis dizer: {', '.join(f"'{s}'" for s in unique_suggestions[:3])}?"

    return None


def generate_smart_suggestion(
    token_value: str, token_type: str, context: str = ""
) -> str:
    """
    Gera sugestão inteligente baseada no token e contexto.

    Args:
        token_value: Valor do token que causou erro
        token_type: Tipo do token
        context: Contexto adicional do erro

    Returns:
        Sugestão de correção
    """
    # Tentar encontrar tokens similares
    similar = find_similar_token(token_value, token_type)

    if similar:
        return similar

    # Sugestões baseadas no tipo de token
    if token_type == "IDENTIFIER":
        return "Verifique se o identificador está correto. Identificadores devem começar com letra ou underscore."
    elif token_type == "NATIVE_TYPE":
        return f"Tipo nativo '{token_value}' em posição inesperada. Esperado ':' antes do tipo."
    elif token_type in ["OPEN_BRACE", "CLOSE_BRACE"]:
        return "Verifique se os blocos estão balanceados. Cada '{{' deve ter um '}}' correspondente."
    elif token_type == "COMMA":
        return "Vírgula inesperada. Verifique a sintaxe da lista de elementos."
    elif token_type == "COLON":
        return "':' inesperado. Verifique se há um identificador antes dos dois-pontos."
    else:
        return "Verifique a sintaxe próxima a este token. Pode estar faltando um delimitador ou palavra-chave."


def suggest_missing_syntax(context: str) -> str:
    """
    Sugere sintaxe que pode estar faltando baseado no contexto.

    Args:
        context: Descrição do contexto do erro

    Returns:
        Sugestão de correção
    """
    suggestions = {
        "attribute": "Atributos devem seguir o formato: 'nome: tipo' ou 'nome: tipo [cardinalidade]'",
        "class": "Classes devem seguir o formato: 'stereotype NomeClasse { ... }'",
        "enum": "Enums devem seguir o formato: 'enum NomeEnum { VALOR1, VALOR2, ... }'",
        "relation": "Relações devem seguir o formato: '@stereotype [card] -- nome -- [card] ClasseDestino'",
        "package": "Declaração de pacote: 'package nome_do_pacote'",
        "import": "Declaração de import: 'import nome_do_pacote'",
    }

    for key, suggestion in suggestions.items():
        if key in context.lower():
            return suggestion

    return "Verifique a sintaxe e estrutura do código."
