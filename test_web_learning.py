"""
Script para testar o aprendizado da web do CodeMarIA com diferentes contextos e idiomas
"""

from code_maria.learning import LearningEngine
import json
from pprint import pprint
from typing import Dict, Any
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns
import pandas as pd

def plot_distribution(data: Dict[str, float], title: str, filename: str):
    """
    Plota e salva um gráfico de distribuição usando seaborn.
    """
    plt.figure(figsize=(12, 6))
    df = pd.DataFrame(list(data.items()), columns=['Categoria', 'Valor'])
    sns.barplot(data=df, x='Categoria', y='Valor')
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_language_distribution(data: Dict[str, int], filename: str):
    """
    Plota a distribuição de idiomas detectados.
    """
    plt.figure(figsize=(8, 8))
    plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
    plt.title('Distribuição de Idiomas')
    plt.savefig(filename)
    plt.close()

def format_metrics(metrics: Dict[str, Any], indent: int = 2) -> str:
    """
    Formata métricas para exibição.
    """
    prefix = " " * indent
    return "\n".join(f"{prefix}{k}: {v:.2f}" if isinstance(v, float) else f"{prefix}{k}: {v}"
                    for k, v in metrics.items())

def main():
    """
    Função principal para testar o aprendizado da web com diferentes contextos
    """
    print("🤖 Iniciando teste de aprendizado da web com contextos e idiomas diversos...\n")
    
    # Inicializa o motor de aprendizado
    engine = LearningEngine()
    
    # URLs para teste (contextos e idiomas diversos)
    urls = {
        "Arte e Cultura": [
            "https://www.itaucultural.org.br/secoes/teatro",
            "https://www.cinemateca.org.br/",
            "https://www.sp.senac.br/cursos-livres/artes/decoracao-de-interiores"
        ],
        "Educação": [
            "https://www5.usp.br/",
            "https://www.prefeitura.sp.gov.br/cidade/secretarias/cultura/bibliotecas/",
            "https://www.sap.com/brazil/index.html"
        ],
        "História e Cultura": [
            "https://www.culturajaponesa.com.br/samurais/",
            "https://www.japanhouse.jp/saopaulo/"
        ],
        "Tecnologia": [
            "https://www.python.org/doc/essays/blurb/",
            "https://docs.python.org/3/tutorial/introduction.html"
        ]
    }
    
    # Resultados do aprendizado
    results = []
    total_chars = 0
    language_counter = Counter()
    context_counter = Counter()
    all_keywords = Counter()
    all_tech_patterns = {
        "code_references": [],
        "urls": [],
        "file_paths": [],
        "variables": [],
        "functions": [],
        "numbers": []
    }
    
    # Processa cada categoria e URL
    for category, category_urls in urls.items():
        print(f"\n📚 Processando categoria: {category}")
        
        for url in category_urls:
            print(f"\n🔍 Analisando: {url}")
            try:
                result = engine.learn_from_web(url)
                results.append(result)
                total_chars += result["content_length"]
                
                # Contagem de idiomas e contextos
                language_counter[result["context_analysis"]["language"]] += 1
                context_counter[result["context"]] += 1
                
                print(f"✅ Análise concluída!")
                print(f"📝 Título: {result['title']}")
                
                # Análise do texto
                print("\n📊 Análise do Texto:")
                stats = result["text_stats"]
                print(format_metrics(stats))
                
                # Análise de contexto
                print("\n🎯 Análise de Contexto:")
                context_analysis = result["context_analysis"]
                print(f"  - Idioma detectado: {context_analysis['language']}")
                print(f"  - Contexto: {context_analysis['context']}")
                print(f"  - Sentenças relevantes: {len(context_analysis['relevant_sentences'])}")
                print(f"  - Termos relevantes: {len(context_analysis['relevant_terms'])}")
                
                # Palavras-chave
                print("\n🔑 Palavras-chave principais:")
                for kw in stats["keywords"][:5]:
                    print(f"  - {kw['word']}:")
                    print(f"    • Frequência: {kw['frequency']}")
                    print(f"    • TF-IDF: {kw['tf_idf']:.2f}")
                    all_keywords[kw['word']] += kw['frequency']
                
                # Padrões técnicos
                if result.get("code_snippets"):
                    print("\n⚙️ Snippets de Código encontrados:")
                    print(f"  - Total: {len(result['code_snippets'])}")
                
                print("\n" + "="*50 + "\n")
                
            except Exception as e:
                print(f"❌ Erro ao processar {url}: {str(e)}\n")
    
    # Análise global
    print("\n📋 Análise Global:")
    print(f"Total de fontes processadas: {len(results)}")
    print(f"Total de conteúdo processado: {total_chars:,} caracteres")
    
    # Distribuição de idiomas
    print("\n🌍 Distribuição de Idiomas:")
    for lang, count in language_counter.items():
        print(f"  - {lang}: {count} fontes ({count/len(results)*100:.1f}%)")
    
    # Distribuição de contextos
    print("\n📊 Distribuição de Contextos:")
    for ctx, count in context_counter.items():
        print(f"  - {ctx}: {count} fontes ({count/len(results)*100:.1f}%)")
    
    # Palavras-chave mais comuns
    print("\n🔑 Top 10 Palavras-chave Globais:")
    for word, freq in all_keywords.most_common(10):
        print(f"  - {word}: {freq} ocorrências")
    
    # Gera visualizações
    try:
        # Distribuição de idiomas
        plot_language_distribution(dict(language_counter), "language_distribution.png")
        print("\n📈 Gráfico de distribuição de idiomas salvo em 'language_distribution.png'")
        
        # Distribuição de contextos
        plot_distribution(dict(context_counter), "Distribuição de Contextos", "context_distribution.png")
        print("📈 Gráfico de distribuição de contextos salvo em 'context_distribution.png'")
        
        # Distribuição de tipos de conteúdo
        sentiment_dist = Counter(r["sentiment"]["label"] for r in results)
        plot_distribution(dict(sentiment_dist), "Distribuição de Tipos de Conteúdo", "content_types.png")
        print("📈 Gráfico de tipos de conteúdo salvo em 'content_types.png'")
    except Exception as e:
        print(f"⚠️ Erro ao gerar visualizações: {str(e)}")
    
    # Análise por categoria
    print("\n📋 Análise por Categoria:")
    for category, category_urls in urls.items():
        category_results = [r for r in results if r["url"] in category_urls]
        if category_results:
            print(f"\n🔍 {category}:")
            print(f"  - Total de fontes: {len(category_results)}")
            
            # Idiomas na categoria
            cat_langs = Counter(r["context_analysis"]["language"] for r in category_results)
            print("  - Idiomas detectados:")
            for lang, count in cat_langs.items():
                print(f"    • {lang}: {count} fontes")
            
            # Palavras-chave da categoria
            cat_keywords = Counter()
            for result in category_results:
                for kw in result["text_stats"]["keywords"]:
                    cat_keywords[kw["word"]] += kw["frequency"]
            
            print("  - Top 5 palavras-chave:")
            for word, freq in cat_keywords.most_common(5):
                print(f"    • {word}: {freq} ocorrências")
    
    # Salva resultados detalhados
    output = {
        "summary": {
            "total_sources": len(results),
            "total_content": total_chars,
            "language_distribution": dict(language_counter),
            "context_distribution": dict(context_counter),
            "top_keywords": dict(all_keywords.most_common(20)),
            "category_analysis": {
                category: {
                    "urls": category_urls,
                    "languages": dict(Counter(r["context_analysis"]["language"] 
                                           for r in results if r["url"] in category_urls)),
                    "keywords": dict(Counter(kw["word"] 
                                          for r in results if r["url"] in category_urls 
                                          for kw in r["text_stats"]["keywords"][:10]))
                } for category, category_urls in urls.items()
            }
        },
        "detailed_results": results
    }
    
    with open("learning_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n💾 Resultados detalhados salvos em 'learning_results.json'")

if __name__ == "__main__":
    main() 