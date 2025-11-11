import json

def contar_itens_json(caminho_arquivo):
    try:
        # Lê o arquivo JSON
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
        
        # Verifica se existe a chave 'items' e conta os itens
        if 'items' in dados and isinstance(dados['items'], list):
            total_itens = len(dados['items'])
            print(f"O arquivo JSON contém {total_itens} itens no array 'items'.")
            return total_itens
        else:
            print("O arquivo JSON não contém um array 'items' válido.")
            return 0
            
    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return -1
    except json.JSONDecodeError:
        print("Erro: O arquivo não está em um formato JSON válido.")
        return -1
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {str(e)}")
        return -1

if __name__ == "__main__":
    caminho = "feaed4b612546b514eab8f104a07e7a3.json"
    contar_itens_json(caminho)
