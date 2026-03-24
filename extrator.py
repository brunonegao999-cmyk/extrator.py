import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys
import re

def buscar_leads_reais(nicho, data_inicio, cidade):
    print(f"Buscando leads reais para '{nicho}' em '{cidade}' na web...")
    leads = []
    
    # Expressões regulares para achar Celular e CNPJ no meio dos textos da internet
    regex_telefone = r'\(?\d{2}\)?\s?(?:9\d{4}|[2-9]\d{3})[-.\s]?\d{4}'
    regex_cnpj = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
    
    # Disfarça o robô como se fosse um navegador real acessando do computador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # Busca no DuckDuckGo HTML (ótimo para scraping gratuito)
    query = f"{nicho} {cidade} cnpj whatsapp"
    url = f"https://html.duckduckgo.com/html/?q={query}"
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pega todos os resultados da página
        resultados = soup.find_all('div', class_='result__body')
        
        for res in resultados:
            titulo_tag = res.find('a', class_='result__title')
            snippet_tag = res.find('a', class_='result__snippet')
            
            if not titulo_tag:
                continue
                
            titulo = titulo_tag.text
            texto_completo = titulo + " " + (snippet_tag.text if snippet_tag else "")
            
            # O robô vasculha o texto em busca de números
            telefones = re.findall(regex_telefone, texto_completo)
            cnpjs = re.findall(regex_cnpj, texto_completo)
            
            # Se achou um telefone, é um lead válido!
            if telefones:
                # Limpa tudo que não for número (tira traços, parênteses, etc)
                numero_limpo = ''.join(filter(str.isdigit, telefones[0]))
                
                # Garante que tem o código do Brasil (55) para o link do WhatsApp funcionar
                if len(numero_limpo) >= 10:
                    if not numero_limpo.startswith('55'):
                        numero_limpo = '55' + numero_limpo
                        
                    cnpj_encontrado = cnpjs[0] if cnpjs else "Não informado"
                    
                    leads.append({
                        "Empresa": titulo.strip()[:40], # Pega o começo do nome da empresa
                        "WhatsApp": numero_limpo,
                        "CNPJ": cnpj_encontrado
                    })
        
        # Cria a tabela e remove números de WhatsApp repetidos
        if leads:
            df = pd.DataFrame(leads).drop_duplicates(subset=['WhatsApp'])
        else:
            df = pd.DataFrame(columns=["Empresa", "WhatsApp", "CNPJ"])
            
        # Salva o arquivo CSV que o seu site vai ler
        df.to_csv('leads_nuvem.csv', index=False)
        print(f"Sucesso! {len(df)} leads reais extraídos.")
        
    except Exception as e:
        print(f"Erro fatal na extração: {e}")
        pd.DataFrame(columns=["Empresa", "WhatsApp", "CNPJ"]).to_csv('leads_nuvem.csv', index=False)

if __name__ == "__main__":
    # Recebe os parâmetros do seu site
    n = sys.argv[1] if len(sys.argv) > 1 else "Oficina"
    d = sys.argv[2] if len(sys.argv) > 2 else "2026-01-01"
    c = sys.argv[3] if len(sys.argv) > 3 else "Vila Velha"
    
    buscar_leads_reais(n, d, c)