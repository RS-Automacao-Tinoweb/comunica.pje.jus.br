package ratelimiter

import (
	"fmt"
	"sync"
	"time"
)

// AdaptiveRateLimiter implementa rate limiting adaptativo com token bucket
type AdaptiveRateLimiter struct {
	mu                sync.Mutex
	rate              float64   // requisições por segundo
	tokens            float64   // tokens disponíveis
	lastRefill        time.Time
	maxTokens         float64
	last429Time       time.Time
	consecutive429    int
	minRate           float64
	maxRate           float64
}

// New cria um novo rate limiter adaptativo
func New(initialRPS int) *AdaptiveRateLimiter {
	rate := float64(initialRPS)
	return &AdaptiveRateLimiter{
		rate:       rate,
		tokens:     rate,
		lastRefill: time.Now(),
		maxTokens:  rate * 2,
		minRate:    0.5,
		maxRate:    float64(initialRPS) * 2,
	}
}

// Acquire aguarda até ter um token disponível
func (rl *AdaptiveRateLimiter) Acquire() {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now()
	elapsed := now.Sub(rl.lastRefill).Seconds()
	
	// Refill tokens baseado no tempo decorrido
	rl.tokens += elapsed * rl.rate
	if rl.tokens > rl.maxTokens {
		rl.tokens = rl.maxTokens
	}
	rl.lastRefill = now

	// Se não tem tokens, aguarda
	if rl.tokens < 1.0 {
		waitTime := time.Duration((1.0-rl.tokens)/rl.rate*1000) * time.Millisecond
		rl.mu.Unlock()
		time.Sleep(waitTime)
		rl.mu.Lock()
		rl.tokens = 1.0
		rl.lastRefill = time.Now()
	}

	rl.tokens -= 1.0
}

// On429 reduz a taxa quando detecta erro 429
func (rl *AdaptiveRateLimiter) On429() {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	rl.last429Time = time.Now()
	rl.consecutive429++
	
	// Reduz taxa em 40%
	oldRate := rl.rate
	rl.rate *= 0.6
	if rl.rate < rl.minRate {
		rl.rate = rl.minRate
	}
	rl.maxTokens = rl.rate * 2

	fmt.Printf("[rate_limiter] 429 detectado: nova taxa %.2f req/s (consec=%d)\n", rl.rate, rl.consecutive429)
	
	if rl.rate != oldRate {
		rl.tokens = rl.rate // Reset tokens
	}
}

// OnSuccess aumenta gradualmente a taxa após período sem 429
func (rl *AdaptiveRateLimiter) OnSuccess() {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	// Se passou 30s sem 429, aumenta gradualmente
	if time.Since(rl.last429Time) > 30*time.Second && rl.consecutive429 > 0 {
		rl.consecutive429 = 0
		oldRate := rl.rate
		rl.rate = min(rl.rate*1.15, rl.maxRate)
		rl.maxTokens = rl.rate * 2
		
		if rl.rate != oldRate {
			fmt.Printf("[rate_limiter] Taxa aumentada para %.2f req/s\n", rl.rate)
		}
	}
}

func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}
