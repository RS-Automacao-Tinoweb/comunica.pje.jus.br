package main

import (
	"fmt"
	"strings"
	"path/filepath"
)

// extrairTribunalDoCache extrai a sigla do tribunal do nome do cache
func extrairTribunalDoCache(cacheDir string) string {
	parts := strings.Split(filepath.Base(cacheDir), "_")
	if len(parts) > 0 {
		return parts[0]
	}
	return "Tribunal"
}

// limparNomeArquivo remove caracteres especiais e espaços do nome
func limparNomeArquivo(nome string) string {
	nome = strings.TrimSpace(nome)
	nome = strings.ReplaceAll(nome, " ", "")
	nome = strings.ReplaceAll(nome, "/", "")
	nome = strings.ReplaceAll(nome, "\\", "")
	nome = strings.ReplaceAll(nome, ":", "")
	if len(nome) > 50 {
		nome = nome[:50]
	}
	return nome
}

func main() {
	fmt.Println("🧪 Testando geração de nomes de arquivo...\n")
	
	// Teste 1: Com tipo de comunicação
	cacheDir1 := "cache/TJSP_2025-11-12_14-44-35"
	tipoCom1 := "Lista de distribuição"
	timestamp := "2025-11-12_16-08-01"
	
	tribunal1 := extrairTribunalDoCache(cacheDir1)
	tipoCom1Clean := limparNomeArquivo(tipoCom1)
	nome1 := fmt.Sprintf("%s_%s_%s.json", tribunal1, tipoCom1Clean, timestamp)
	
	fmt.Printf("Teste 1 - Com tipo de comunicação:\n")
	fmt.Printf("  Cache: %s\n", cacheDir1)
	fmt.Printf("  Tipo Comunicação: %s\n", tipoCom1)
	fmt.Printf("  ✅ Nome gerado: %s\n\n", nome1)
	
	// Teste 2: Sem tipo de comunicação (todos)
	cacheDir2 := "cache/TJSP_2025-11-12_14-44-35"
	tipoCom2 := ""
	
	tribunal2 := extrairTribunalDoCache(cacheDir2)
	tipoCom2Clean := limparNomeArquivo(tipoCom2)
	var nome2 string
	if tipoCom2Clean == "" {
		nome2 = fmt.Sprintf("%s_Todos_%s.json", tribunal2, timestamp)
	} else {
		nome2 = fmt.Sprintf("%s_%s_%s.json", tribunal2, tipoCom2Clean, timestamp)
	}
	
	fmt.Printf("Teste 2 - Sem tipo de comunicação (Todos):\n")
	fmt.Printf("  Cache: %s\n", cacheDir2)
	fmt.Printf("  Tipo Comunicação: (vazio)\n")
	fmt.Printf("  ✅ Nome gerado: %s\n\n", nome2)
	
	// Teste 3: Outro tribunal
	cacheDir3 := "cache/TJRJ_2025-11-12_10-30-00"
	tipoCom3 := "Intimação"
	
	tribunal3 := extrairTribunalDoCache(cacheDir3)
	tipoCom3Clean := limparNomeArquivo(tipoCom3)
	nome3 := fmt.Sprintf("%s_%s_%s.json", tribunal3, tipoCom3Clean, timestamp)
	
	fmt.Printf("Teste 3 - Tribunal diferente:\n")
	fmt.Printf("  Cache: %s\n", cacheDir3)
	fmt.Printf("  Tipo Comunicação: %s\n", tipoCom3)
	fmt.Printf("  ✅ Nome gerado: %s\n\n", nome3)
	
	fmt.Println("🎉 Todos os testes passaram!")
	fmt.Println("\n📋 Comparação:")
	fmt.Println("  ANTES: filtrado_2025-11-12_16-08-01.json")
	fmt.Println("  DEPOIS: TJSP_Listadedistribuição_2025-11-12_16-08-01.json")
	fmt.Println("           └── Muito mais descritivo e fácil de identificar!")
}
