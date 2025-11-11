package httpclient

import (
	"context"
	"fmt"
	"io"
	"math"
	"math/rand"
	"net/http"
	"time"

	"go_scraper_pje/internal/ratelimiter"
)

var (
	// DefaultHeaders são os headers padrão para requisições
	DefaultHeaders = map[string]string{
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
		"Accept":     "application/json",
	}
)

// Client encapsula o cliente HTTP com retry e rate limiting
type Client struct {
	httpClient *http.Client
	maxRetries int
	timeoutSec int
}

// New cria um novo cliente HTTP
func New(maxRetries, timeoutSec int) *Client {
	return &Client{
		httpClient: &http.Client{
			Transport: &http.Transport{
				MaxIdleConns:        100,
				MaxIdleConnsPerHost: 10,
				IdleConnTimeout:     90 * time.Second,
			},
		},
		maxRetries: maxRetries,
		timeoutSec: timeoutSec,
	}
}

// DoWithRetry executa uma requisição com retry automático
func (c *Client) DoWithRetry(rl *ratelimiter.AdaptiveRateLimiter, req *http.Request) ([]byte, int, error) {
	var resp *http.Response
	var err error

	for attempt := 0; attempt < c.maxRetries; attempt++ {
		// Aguarda rate limiter
		if rl != nil {
			rl.Acquire()
		}

		// Cria context com timeout
		ctx, cancel := context.WithTimeout(context.Background(), time.Duration(c.timeoutSec)*time.Second)
		reqWithTimeout := req.Clone(ctx)
		
		// Adiciona headers
		for k, v := range DefaultHeaders {
			reqWithTimeout.Header.Set(k, v)
		}

		// Executa requisição
		resp, err = c.httpClient.Do(reqWithTimeout)

		if err != nil {
			cancel()
			wait := c.backoffWithJitter(attempt)
			fmt.Printf("\n  [⚠️] Request error: %v — aguardando %v\n", err, wait)
			time.Sleep(wait)
			continue
		}

		// Lê body completo ANTES de cancelar context
		body, readErr := io.ReadAll(resp.Body)
		resp.Body.Close()
		cancel() // Agora pode cancelar após ler body

		if readErr != nil {
			wait := c.backoffWithJitter(attempt)
			fmt.Printf("\n  [⚠️] Erro ao ler body: %v — aguardando %v\n", readErr, wait)
			time.Sleep(wait)
			continue
		}

		// Tratamento de status HTTP
		switch {
		case resp.StatusCode == http.StatusTooManyRequests:
			if rl != nil {
				rl.On429()
			}
			wait := c.handle429(resp, attempt)
			fmt.Printf("\n  [⚠️] HTTP 429 - aguardando %v (tentativa %d/%d)\n", wait, attempt+1, c.maxRetries)
			time.Sleep(wait)
			continue

		case resp.StatusCode == 502 || resp.StatusCode == 503 || resp.StatusCode == 504:
			wait := c.backoffWithJitter(attempt)
			fmt.Printf("\n  [⚠️] HTTP %d - aguardando %v\n", resp.StatusCode, wait)
			time.Sleep(wait)
			continue

		case resp.StatusCode >= 200 && resp.StatusCode < 300:
			if rl != nil {
				rl.OnSuccess()
			}
			return body, resp.StatusCode, nil

		default:
			fmt.Printf("\n  [⚠️] HTTP %d — %s\n", resp.StatusCode, string(body[:min(200, len(body))]))
			wait := c.backoffWithJitter(attempt)
			time.Sleep(wait)
		}
	}

	return nil, 0, fmt.Errorf("todas as tentativas falharam: %v", err)
}

// backoffWithJitter calcula o tempo de espera com exponential backoff e jitter
func (c *Client) backoffWithJitter(attempt int) time.Duration {
	base := time.Duration(math.Pow(2, float64(attempt))*1000) * time.Millisecond
	jitter := time.Duration(rand.Intn(500)) * time.Millisecond
	return base + jitter
}

// handle429 processa erro 429 e retorna tempo de espera
func (c *Client) handle429(resp *http.Response, attempt int) time.Duration {
	var wait time.Duration

	// Tenta usar Retry-After do header
	if ra := resp.Header.Get("Retry-After"); ra != "" {
		if dur, err := time.ParseDuration(ra + "s"); err == nil {
			wait = dur + time.Duration(100+rand.Intn(400))*time.Millisecond
		}
	}

	// Se não tem Retry-After, usa backoff exponencial
	if wait == 0 {
		base := time.Duration(math.Pow(2, float64(attempt))*1000) * time.Millisecond
		wait = base + time.Duration(200+rand.Intn(600))*time.Millisecond
	}

	return wait
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
