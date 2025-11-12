package models

import (
	"testing"
)

func TestExtrairDataDespacho(t *testing.T) {
	tests := []struct {
		name     string
		texto    string
		esperado string
	}{
		{
			name:     "Texto com 'distribuido para ... na data de'",
			texto:    "Processo 4002606-06.2025.8.26.0438 distribuido para Vara do Juizado Especial Cível e Criminal da Comarca de Penápolis na data de 10/11/2025.",
			esperado: "10/11/2025",
		},
		{
			name:     "Texto com 'distribuido para ... na data de' (outro exemplo)",
			texto:    "Processo 4002894-73.2025.8.26.0269 distribuido para UPJ da 1ª a 4ª Varas Civeis da Comarca de Itapetininga na data de 10/11/2025.",
			esperado: "10/11/2025",
		},
		{
			name:     "DATA DE EXPEDIENTE",
			texto:    "DATA DE EXPEDIENTE: 05/11/2025 - Processo foo bar",
			esperado: "05/11/2025",
		},
		{
			name:     "Data de Expediente (case insensitive)",
			texto:    "Data de Expediente: 15/12/2025 - Processo xyz",
			esperado: "15/12/2025",
		},
		{
			name:     "DATA:",
			texto:    "Intimação com DATA: 20/11/2025",
			esperado: "20/11/2025",
		},
		{
			name:     "Sem data",
			texto:    "Processo sem data no texto",
			esperado: "",
		},
		{
			name:     "Data isolada",
			texto:    "Audiência marcada para 25/12/2025",
			esperado: "25/12/2025",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			resultado := ExtrairDataDespacho(tt.texto)
			if resultado != tt.esperado {
				t.Errorf("ExtrairDataDespacho() = %v, esperado %v\nTexto: %s", resultado, tt.esperado, tt.texto)
			}
		})
	}
}
