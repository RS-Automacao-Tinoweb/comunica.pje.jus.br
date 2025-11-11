package scraper

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"go_scraper_pje/internal/cache"
	"go_scraper_pje/internal/config"
	"go_scraper_pje/internal/httpclient"
	"go_scraper_pje/internal/models"
	"go_scraper_pje/internal/ratelimiter"
)

// Scraper coordena o scraping de tribunais
type Scraper struct {
	cfg        *config.Config
	httpClient *httpclient.Client
	cache      *cache.Manager
}

// New cria um novo scraper
func New(cfg *config.Config) *Scraper {
	return &Scraper{
		cfg:        cfg,
		httpClient: httpclient.New(cfg.MaxRetries, cfg.RequestTimeoutSec),
	}
}

// ProcessarTribunal scrape todos os dados de um tribunal
func (s *Scraper) ProcessarTribunal(sigla, inicio, fim string) ([]models.Resultado, int, error) {
	// Cria cache isolado para esta execução do tribunal
	cacheDir := s.cfg.GetCacheDirForRun(sigla)
	s.cache = cache.New(s.cfg.CacheEnabled, cacheDir)
	
	if err := s.cache.EnsureDir(); err != nil {
		return nil, 0, fmt.Errorf("erro ao criar diretório de cache: %v", err)
	}

	fmt.Printf("\n%s\n", strings.Repeat("=", 80))
	fmt.Printf("🚀 TRIBUNAL: %s\n", sigla)
	fmt.Printf("%s\n\n", strings.Repeat("=", 80))
	fmt.Printf("  [🔍] Filtros ativos: tipoComunicacao='%s', codigoClasse='%s'\n", s.cfg.TipoComunicacao, s.cfg.CodigoClasse)
	if s.cfg.CacheEnabled {
		fmt.Printf("  [📦] Cache: %s\n", cacheDir)
	}

	// Rate limiter para este tribunal
	rl := ratelimiter.New(s.cfg.RPS)

	// Busca primeira página para descobrir total
	fmt.Printf("  [📊] Descobrindo total de páginas...\n")
	primeira, err := s.fetchPage(rl, sigla, 1, inicio, fim)
	if err != nil {
		return nil, 0, fmt.Errorf("falha primeira página (erro HTTP): %v", err)
	}
	if primeira == nil {
		return nil, 0, fmt.Errorf("falha primeira página: resposta nil")
	}
	if strings.ToLower(primeira.Status) != "success" {
		return nil, 0, fmt.Errorf("falha primeira página: status=%s, message=%s", primeira.Status, primeira.Message)
	}

	count := primeira.Count
	totalPaginas := calcularTotalPaginas(count, s.cfg.ItensPorPagina)
	
	fmt.Printf("  [ℹ️] Total de itens: %d\n", count)
	fmt.Printf("  [ℹ️] Total de páginas: %d\n", totalPaginas)
	fmt.Printf("  [⚡] Iniciando scraping paralelo com %d workers...\n\n", s.cfg.WorkersPaginas)

	if totalPaginas == 0 {
		return []models.Resultado{}, 0, nil
	}

	// Processa páginas em paralelo
	return s.processarPaginas(rl, sigla, inicio, fim, totalPaginas)
}

// processarPaginas processa múltiplas páginas em paralelo
func (s *Scraper) processarPaginas(rl *ratelimiter.AdaptiveRateLimiter, sigla, inicio, fim string, totalPaginas int) ([]models.Resultado, int, error) {
	var (
		wg             sync.WaitGroup
		processedPages int32
		errorPages     int32
	)

	pagesCh := make(chan int, totalPaginas)
	resultsCh := make(chan []models.Resultado, s.cfg.WorkersPaginas)
	errorsCh := make(chan error, totalPaginas)

	// Workers
	for i := 0; i < s.cfg.WorkersPaginas; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for pagina := range pagesCh {
				res, err := s.processPagina(rl, sigla, pagina, inicio, fim)
				if err != nil {
					errorsCh <- err
					atomic.AddInt32(&errorPages, 1)
				} else {
					resultsCh <- res
				}
				atomic.AddInt32(&processedPages, 1)
			}
		}()
	}

	// Enqueue páginas
	go func() {
		for p := 1; p <= totalPaginas; p++ {
			pagesCh <- p
		}
		close(pagesCh)
	}()

	// Progress printer
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	done := make(chan struct{})
	
	go func() {
		defer close(done)
		ticker := time.NewTicker(500 * time.Millisecond)
		defer ticker.Stop()
		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
				pp := atomic.LoadInt32(&processedPages)
				ep := atomic.LoadInt32(&errorPages)
				fmt.Printf("  [⚡] Progresso: %d/%d páginas (%.1f%%) | Erros: %d\r", 
					pp, totalPaginas, float64(pp)/float64(totalPaginas)*100.0, ep)
			}
		}
	}()

	// Collector
	var todos []models.Resultado
	go func() {
		wg.Wait()
		close(resultsCh)
		close(errorsCh)
	}()

	for lot := range resultsCh {
		todos = append(todos, lot...)
	}
	
	cancel()
	<-done
	fmt.Println()
	fmt.Printf("\n  [✅] Coleta finalizada: %d resultados filtrados\n", len(todos))

	return todos, int(atomic.LoadInt32(&errorPages)), nil
}

// processPagina processa uma única página
func (s *Scraper) processPagina(rl *ratelimiter.AdaptiveRateLimiter, sigla string, pagina int, inicio, fim string) ([]models.Resultado, error) {
	data, err := s.fetchPage(rl, sigla, pagina, inicio, fim)
	if err != nil {
		return nil, err
	}

	// Filtra itens no lado do cliente (API retorna todos os dados)
	var resultados []models.Resultado
	for _, item := range data.Items {
		if s.matchesFiltros(item) {
			resultados = append(resultados, models.CriarResultado(item))
		}
	}

	return resultados, nil
}

// fetchPage busca uma página da API (com cache)
func (s *Scraper) fetchPage(rl *ratelimiter.AdaptiveRateLimiter, sigla string, pagina int, inicio, fim string) (*models.ApiResponse, error) {
	// Tenta cache
	key := s.cache.GenerateKey(sigla, pagina, s.cfg.ItensPorPagina, inicio, fim)
	if cached, ok := s.cache.Read(key); ok {
		return cached, nil
	}

	// Faz requisição
	u := s.buildURL(sigla, pagina, inicio, fim)
	req, _ := http.NewRequest("GET", u, nil)
	
	start := time.Now()
	body, statusCode, err := s.httpClient.DoWithRetry(rl, req)
	if err != nil {
		fmt.Printf("  [❌] %s página %d: erro na requisição: %v\n", sigla, pagina, err)
		return nil, err
	}

	if len(body) == 0 {
		fmt.Printf("  [⚠️] %s página %d: resposta vazia\n", sigla, pagina)
		return nil, fmt.Errorf("resposta vazia")
	}

	var ar models.ApiResponse
	if err := json.Unmarshal(body, &ar); err != nil {
		fmt.Printf("  [❌] %s página %d: erro ao parsear JSON: %v\n", sigla, pagina, err)
		return nil, err
	}

	// Salva cache
	s.cache.Write(key, body)

	elapsed := time.Since(start)
	if pagina == 1 {
		fmt.Printf("  [✓] Primeira página OK (%.2fs, HTTP %d, count=%d, items=%d)\n", 
			elapsed.Seconds(), statusCode, ar.Count, len(ar.Items))
	}

	return &ar, nil
}

// buildURL constrói a URL da API com todos os filtros
func (s *Scraper) buildURL(sigla string, pagina int, inicio, fim string) string {
	u, _ := url.Parse(s.cfg.APIBaseURL)
	q := u.Query()
	q.Set("pagina", fmt.Sprintf("%d", pagina))
	q.Set("itensPorPagina", fmt.Sprintf("%d", s.cfg.ItensPorPagina))
	q.Set("siglaTribunal", sigla)
	q.Set("dataDisponibilizacaoInicio", inicio)
	q.Set("dataDisponibilizacaoFim", fim)
	
	// Adiciona filtros
	if s.cfg.TipoComunicacao != "" {
		q.Set("tipoComunicacao", s.cfg.TipoComunicacao)
	}
	if s.cfg.CodigoClasse != "" {
		q.Set("codigoClasse", s.cfg.CodigoClasse)
	}
	
	u.RawQuery = q.Encode()
	return u.String()
}

// matchesFiltros verifica se um item atende aos filtros
func (s *Scraper) matchesFiltros(item map[string]any) bool {
	// API retorna campos em camelCase
	if s.cfg.TipoComunicacao != "" {
		if tc, ok := item["tipoComunicacao"].(string); !ok || tc != s.cfg.TipoComunicacao {
			return false
		}
	}
	if s.cfg.CodigoClasse != "" {
		if cc, ok := item["codigoClasse"]; ok {
			if fmt.Sprintf("%v", cc) != s.cfg.CodigoClasse {
				return false
			}
		} else {
			return false
		}
	}
	return true
}

// calcularTotalPaginas calcula o número total de páginas
func calcularTotalPaginas(totalItens, itensPorPagina int) int {
	if itensPorPagina <= 0 || totalItens <= 0 {
		return 0
	}
	return (totalItens + itensPorPagina - 1) / itensPorPagina
}
