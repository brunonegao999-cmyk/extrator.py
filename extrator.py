import pandas as pd
import sys
import re
from duckduckgo_search import DDGS

def buscar_leads_reais(nicho, cidade):
    print(f"Buscando contatos reais para '{nicho}' em '{cidade}'...")
    leads = []
    
    # Regra para encontrar números de celular do Brasil no meio do texto
    regex_telefone = r'\(?\d{2}\)?\s?(?:9\d{4}|[2-9]\d{3})[-.\s]?\d{4}'
    
    # Pesquisa exata que o robô vai fazer
    query = f"{nicho} {cidade} whatsapp"
    
    try:
        # Abre a conexão "invisível" com o buscador para driblar bloqueios
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, region='br-tz', max_results=30))
            
            for res in resultados:
                titulo = res.get('title', '')
                corpo = res.get('body', '')
                texto_completo = f"{titulo} {corpo}"
                
                # Procura telefones no texto
                telefones = re.findall(regex_telefone, texto_completo)
                
                if telefones:
                    # Limpa tudo que não for número (tira traços e espaços)
                    numero_limpo = ''.join(filter(str.isdigit, telefones[0]))
                    
                    if len(numero_limpo) >= 10:
                        # Adiciona o 55 (Brasil) se não tiver
                        if not numero_limpo.startswith('55'):
                            numero_limpo = '55' + numero_limpo
                            
                        # Limpa o nome da empresa para ficar mais bonito no seu CRM
                        nome_empresa = titulo.split('-')[0].split('|')[0].replace("WhatsApp", "").strip()[:40]
                        
                        leads.append({
                            "Empresa": nome_empresa,
                            "WhatsApp": numero_limpo,
                            "CNPJ": "Busca via WhatsApp"
                        })
                        
        # Organiza a lista e remove números repetidos
        if leads:
            df = pd.DataFrame(leads).drop_duplicates(subset=['WhatsApp'])
        else:
            df = pd.DataFrame(columns=["Empresa", "WhatsApp", "CNPJ"])
            
        # Salva o arquivo CSV que o seu site vai ler
        df.to_csv('leads_nuvem.csv', index=False)
        print(f"Sucesso! {len(df)} leads salvos na nuvem.")
        
    except Exception as e:
        print(f"Erro na extração: {e}")
        # Cria um arquivo vazio para não travar o site caso dê erro
        df = pd.DataFrame(columns=["Empresa", "WhatsApp", "CNPJ"])
        df.to_csv('leads_nuvem.csv', index=False)

if __name__ == "__main__":
    # Pega os dados que o site envia ao clicar no botão
    nicho_site = sys.argv[1] if len(sys.argv) > 1 else "Oficina"
    # O argv[2] é a data, mas ocultamos da pesquisa para achar mais resultados
    cidade_site = sys.argv[3] if len(sys.argv) > 3 else "Vila Velha"
    
    buscar_leads_reais(nicho_site, cidade_site)