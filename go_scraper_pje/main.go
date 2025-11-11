package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"

	"go_scraper_pje/internal/config"
	"go_scraper_pje/internal/models"
	"go_scraper_pje/internal/scraper"
)

func main() {
	start := time.Now()

	// Parse configurações da CLI
	cfg := config.ParseFlags()
	cfg.PrintConfig()

	// Cria diretório de saída
	if err := os.MkdirAll(cfg.OutputDir, 0o755); err != nil {
		fmt.Printf("Erro ao criar diretório de saída: %v\n", err)
		os.Exit(1)
	}

	// Cria scraper
	scr := scraper.New(cfg)

	// Canal para resultados dos tribunais
	resCh := make(chan models.TribunalResult, len(cfg.Tribunais))

	// Processa tribunais em paralelo
	var wg sync.WaitGroup
	tribCh := make(chan string, len(cfg.Tribunais))

	// Workers de tribunais
	for i := 0; i < cfg.WorkersTribunais; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for sigla := range tribCh {
				result, erros, err := scr.ProcessarTribunal(sigla, cfg.DataInicio, cfg.DataFim)
				resCh <- models.TribunalResult{
					Sigla:  sigla,
					Result: result,
					Erros:  erros,
					Err:    err,
				}
			}
		}()
	}

	// Enfileira tribunais
	go func() {
		for _, t := range cfg.Tribunais {
			tribCh <- t
		}
		close(tribCh)
		wg.Wait()
		close(resCh)
	}()

	// Coleta resultados
	totalRegistros := 0
	concluidos := 0

	for r := range resCh {
		concluidos++
		if r.Err != nil {
			fmt.Printf("\n[❌] %s: ERRO - %v\n", r.Sigla, r.Err)
			continue
		}

		// Salva arquivo JSON por tribunal
		tribOut := filepath.Join(cfg.OutputDir, r.Sigla+".json")
		b, _ := json.MarshalIndent(r.Result, "", "  ")
		_ = os.WriteFile(tribOut, b, 0o644)
		
		fmt.Printf("\n[💾] %s: %d registros salvos | Erros de páginas: %d\n", r.Sigla, len(r.Result), r.Erros)
		totalRegistros += len(r.Result)
	}

	// Resumo final
	fmt.Println()
	fmt.Println(strings.Repeat("=", 80))
	fmt.Println("📊 RESUMO FINAL")
	fmt.Println(strings.Repeat("=", 80))
	fmt.Printf("Tribunais processados: %d\n", concluidos)
	fmt.Printf("Total geral de registros: %d\n", totalRegistros)
	fmt.Printf("Tempo total: %.1fs (%.1f min)\n", time.Since(start).Seconds(), time.Since(start).Minutes())
	fmt.Printf("Go version: %s | CPUs: %d\n", runtime.Version(), runtime.NumCPU())
	fmt.Println(strings.Repeat("=", 80))
}
