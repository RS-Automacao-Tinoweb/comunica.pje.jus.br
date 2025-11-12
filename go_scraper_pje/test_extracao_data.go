package main

import (
	"encoding/json"
	"fmt"
	"os"
	"regexp"
)

func extrairDataDespacho(texto string) string {
	padroes := []string{
		`DATA\s+DE\s+EXPEDIENTE:\s*(\d{2}/\d{2}/\d{4})`,
		`Data\s+de\s+Expediente:\s*(\d{2}/\d{2}/\d{4})`,
		`DATA\s+DE\s+VINCULA[ÇC][ÃA]O:\s*(\d{2}/\d{2}/\d{4})`,
		`Data\s+de\s+Vincula[çc][ãa]o:\s*(\d{2}/\d{2}/\d{4})`,
		`DATA\s+VINCULA[ÇC][ÃA]O:\s*(\d{2}/\d{2}/\d{4})`,
		`Data\s+Vincula[çc][ãa]o:\s*(\d{2}/\d{2}/\d{4})`,
		`Vincula[çc][ãa]o:\s*(\d{2}/\d{2}/\d{4})`,
		`DATA:\s*(\d{2}/\d{2}/\d{4})`,
		`Data:\s*(\d{2}/\d{2}/\d{4})`,
		`na\s+data\s+de\s+(\d{2}/\d{2}/\d{4})`,
		`\b(\d{2}/\d{2}/\d{4})\b`,
	}

	for _, padrao := range padroes {
		re := regexp.MustCompile(padrao)
		if matches := re.FindStringSubmatch(texto); len(matches) > 1 {
			return matches[1]
		}
	}
	return ""
}

func main() {
	// Ler o arquivo de cache
	cacheFile := `d:\RS - LySA - EMPRESA\go_scraper_pje\cache\TJSP_2025-11-12_14-44-35\433b6f5b7c466b7a8612e74ece7d9836.json`
	
	data, err := os.ReadFile(cacheFile)
	if err != nil {
		fmt.Printf("❌ Erro ao ler arquivo: %v\n", err)
		return
	}

	var response map[string]any
	if err := json.Unmarshal(data, &response); err != nil {
		fmt.Printf("❌ Erro ao decodificar JSON: %v\n", err)
		return
	}

	items, ok := response["items"].([]any)
	if !ok {
		fmt.Println("❌ Não foi possível obter items")
		return
	}

	fmt.Printf("\n🔍 Testando extração de datas em %d processos...\n\n", len(items))
	
	processosTeste := []string{
		"40026060620258260438", // processo 4002606-06
		"40028947320258260269", // processo 4002894-73
	}

	encontrados := 0
	total := 0
	
	for _, item := range items {
		itemMap, ok := item.(map[string]any)
		if !ok {
			continue
		}

		numProcesso, _ := itemMap["numero_processo"].(string)
		texto, _ := itemMap["texto"].(string)
		
		// Verificar processos específicos
		for _, procTeste := range processosTeste {
			if numProcesso == procTeste {
				total++
				dataExtraida := extrairDataDespacho(texto)
				
				if dataExtraida != "" {
					encontrados++
					fmt.Printf("✅ Processo: %s\n", numProcesso)
					fmt.Printf("   Data extraída: %s\n", dataExtraida)
					fmt.Printf("   Texto: %s\n\n", texto[:100]+"...")
				} else {
					fmt.Printf("❌ Processo: %s\n", numProcesso)
					fmt.Printf("   Data extraída: NENHUMA\n")
					fmt.Printf("   Texto: %s\n\n", texto[:100]+"...")
				}
			}
		}
	}

	fmt.Printf("📊 Resultado: %d de %d processos testados tiveram datas extraídas\n", encontrados, total)
	
	if encontrados == total && total > 0 {
		fmt.Println("🎉 SUCESSO! Todas as datas foram extraídas corretamente!")
	} else {
		fmt.Println("⚠️  FALHA! Algumas datas não foram extraídas.")
	}
}
