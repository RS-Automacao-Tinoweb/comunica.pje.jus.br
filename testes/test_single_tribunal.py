#!/usr/bin/env python3
"""
Teste rápido com um único tribunal
Use para testar antes de rodar todos os tribunais
"""

import json
from main_multi_tribunal import setup_driver, scrape_tribunal

# Tribunal para testar
TRIBUNAL_TESTE = {
    "sigla": "TRF1",
    "nome": "Tribunal Regional Federal da 1ª Região"
}

def main():
    print("="*60)
    print("TESTE - TRIBUNAL ÚNICO")
    print("="*60)
    print(f"\nTestando: {TRIBUNAL_TESTE['sigla']} - {TRIBUNAL_TESTE['nome']}\n")
    
    driver = setup_driver()
    
    try:
        resultados = scrape_tribunal(driver, TRIBUNAL_TESTE)
        
        print("\n" + "="*60)
        print("RESULTADO DO TESTE")
        print("="*60)
        print(f"Total de registros: {len(resultados)}")
        
        if resultados:
            # Salva resultado
            output_file = f"teste_{TRIBUNAL_TESTE['sigla']}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            print(f"Salvo em: {output_file}")
            
            # Mostra primeiro registro
            print("\nPrimeiro registro:")
            print(json.dumps(resultados[0], ensure_ascii=False, indent=2))
        else:
            print("Nenhum resultado encontrado")
        
    finally:
        driver.quit()
        print("\n" + "="*60)
        print("TESTE CONCLUÍDO!")
        print("="*60)

if __name__ == "__main__":
    main()
