package cache

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"go_scraper_pje/internal/models"
)

// Manager gerencia o cache local com diretórios isolados por execução
type Manager struct {
	enabled bool
	baseDir string
}

// New cria um novo gerenciador de cache
func New(enabled bool, baseDir string) *Manager {
	return &Manager{
		enabled: enabled,
		baseDir: baseDir,
	}
}

// GenerateKey gera uma chave única para cache baseada nos parâmetros
func (m *Manager) GenerateKey(sigla string, pagina, itens int, inicio, fim string) string {
	s := fmt.Sprintf("%s_%d_%d_%s_%s", sigla, pagina, itens, inicio, fim)
	h := md5.Sum([]byte(s))
	return hex.EncodeToString(h[:])
}

// GetPath retorna o caminho completo do arquivo de cache
func (m *Manager) GetPath(key string) string {
	return filepath.Join(m.baseDir, key+".json")
}

// Read tenta ler do cache, retorna (data, ok)
func (m *Manager) Read(key string) (*models.ApiResponse, bool) {
	if !m.enabled {
		return nil, false
	}

	path := m.GetPath(key)
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, false
	}

	var ar models.ApiResponse
	if err := json.Unmarshal(data, &ar); err != nil {
		return nil, false
	}

	return &ar, true
}

// Write salva dados no cache
func (m *Manager) Write(key string, data []byte) error {
	if !m.enabled {
		return nil
	}

	// Garante que o diretório existe
	if err := os.MkdirAll(m.baseDir, 0o755); err != nil {
		return err
	}

	path := m.GetPath(key)
	return os.WriteFile(path, data, 0o644)
}

// EnsureDir garante que o diretório de cache existe
func (m *Manager) EnsureDir() error {
	if !m.enabled {
		return nil
	}
	return os.MkdirAll(m.baseDir, 0o755)
}

// GetInfo retorna informações sobre o cache
func (m *Manager) GetInfo() string {
	if !m.enabled {
		return "Cache desabilitado"
	}
	return fmt.Sprintf("Cache: %s", m.baseDir)
}
