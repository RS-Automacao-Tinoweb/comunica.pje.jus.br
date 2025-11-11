package config

import (
	"flag"
	"fmt"
	"strings"
	"time"
)

// Config armazena todas as configurações do scraper
type Config struct {
	// API
	APIBaseURL      string
	DataInicio      string
	DataFim         string
	ItensPorPagina  int
	TipoComunicacao string
	CodigoClasse    string

	// Concorrência
	WorkersTribunais int
	WorkersPaginas   int
	RPS              int

	// Retry e timeout
	MaxRetries        int
	RequestTimeoutSec int

	// Cache e output
	CacheEnabled bool
	CacheBaseDir string
	OutputDir    string

	// Tribunais
	Tribunais []string
}

// ParseFlags lê os argumentos da linha de comando e retorna a configuração
func ParseFlags() *Config {
	cfg := &Config{}

	var tribunaisStr string
	flag.StringVar(&tribunaisStr, "tribunais", "TJAM", "Siglas dos tribunais separadas por vírgula (ex: TJSP,TJAM)")
	flag.StringVar(&cfg.DataInicio, "inicio", "2025-11-06", "Data inicial (YYYY-MM-DD)")
	flag.StringVar(&cfg.DataFim, "fim", "2025-11-10", "Data final (YYYY-MM-DD)")
	flag.IntVar(&cfg.ItensPorPagina, "itens", 100, "Itens por página (máximo 100)")
	flag.IntVar(&cfg.WorkersPaginas, "wp", 3, "Workers de páginas (goroutines simultâneas)")
	flag.IntVar(&cfg.WorkersTribunais, "wt", 1, "Workers de tribunais")
	flag.IntVar(&cfg.RPS, "rps", 3, "Taxa inicial de requisições por segundo")
	flag.IntVar(&cfg.MaxRetries, "retries", 3, "Número de tentativas por requisição")
	flag.IntVar(&cfg.RequestTimeoutSec, "timeout", 30, "Timeout por requisição em segundos")
	flag.BoolVar(&cfg.CacheEnabled, "cache", true, "Habilitar cache local")
	flag.StringVar(&cfg.OutputDir, "out", "resultados_go", "Diretório de saída")
	flag.StringVar(&cfg.CacheBaseDir, "cache-dir", "cache", "Diretório base de cache")
	flag.StringVar(&cfg.TipoComunicacao, "tipo", "Lista de distribuição", "Filtro tipoComunicacao")
	flag.StringVar(&cfg.CodigoClasse, "classe", "12154", "Filtro codigoClasse")

	flag.Parse()

	// Parse tribunais
	tribunaisStr = strings.TrimSpace(tribunaisStr)
	if tribunaisStr != "" {
		parts := strings.Split(tribunaisStr, ",")
		for _, p := range parts {
			if t := strings.TrimSpace(p); t != "" {
				cfg.Tribunais = append(cfg.Tribunais, strings.ToUpper(t))
			}
		}
	}

	cfg.APIBaseURL = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"

	return cfg
}

// GetCacheDirForRun retorna o diretório de cache isolado para esta execução
// Padrão: cache/TJSP_2025-11-11_17-45-30/
func (c *Config) GetCacheDirForRun(tribunal string) string {
	if !c.CacheEnabled {
		return ""
	}

	// Formato: TRIBUNAL_YYYY-MM-DD_HH-MM-SS
	timestamp := time.Now().Format("2006-01-02_15-04-05")
	runID := fmt.Sprintf("%s_%s", tribunal, timestamp)
	
	return fmt.Sprintf("%s/%s", c.CacheBaseDir, runID)
}

// PrintConfig exibe a configuração atual
func (c *Config) PrintConfig() {
	fmt.Println("\n" + strings.Repeat("=", 80))
	fmt.Println("🚀 SCRAPER PJE (Go) - VERSÃO MODULAR")
	fmt.Println(strings.Repeat("=", 80))
	fmt.Println()
	fmt.Println("[⚙️] CONFIGURAÇÕES:")
	fmt.Printf("    Período: %s a %s\n", c.DataInicio, c.DataFim)
	fmt.Printf("    Tipo Comunicação: %s\n", c.TipoComunicacao)
	fmt.Printf("    Código Classe: %s\n", c.CodigoClasse)
	fmt.Printf("    Itens por página: %d\n", c.ItensPorPagina)
	fmt.Printf("    Workers páginas: %d | RPS inicial: %d\n", c.WorkersPaginas, c.RPS)
	fmt.Printf("    Cache: %v (base: %s)\n", c.CacheEnabled, c.CacheBaseDir)
	fmt.Printf("    Tribunais: %v\n", c.Tribunais)
	fmt.Println()
}
