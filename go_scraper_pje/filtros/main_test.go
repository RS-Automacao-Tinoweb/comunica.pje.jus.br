package main

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
			name:     "Caso real - processo 4002606-06",
			texto:    "Processo 4002606-06.2025.8.26.0438 distribuido para Vara do Juizado Especial Cível e Criminal da Comarca de Penápolis na data de 10/11/2025.",
			esperado: "10/11/2025",
		},
		{
			name:     "Caso real - processo 4002894-73",
			texto:    "Processo 4002894-73.2025.8.26.0269 distribuido para UPJ da 1ª a 4ª Varas Civeis da Comarca de Itapetininga na data de 10/11/2025.",
			esperado: "10/11/2025",
		},
		{
			name:     "DATA DE EXPEDIENTE",
			texto:    "DATA DE EXPEDIENTE: 05/11/2025 - Processo foo bar",
			esperado: "05/11/2025",
		},
		{
			name:     "Data de Expediente",
			texto:    "Data de Expediente: 15/12/2025 - Processo xyz",
			esperado: "15/12/2025",
		},
		{
			name:     "DATA DE VINCULAÇÃO",
			texto:    "DATA DE VINCULAÇÃO: 20/11/2025",
			esperado: "20/11/2025",
		},
		{
			name:     "Sem data",
			texto:    "Processo sem data no texto",
			esperado: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			resultado := extrairDataDespacho(tt.texto)
			if resultado != tt.esperado {
				t.Errorf("\n❌ FALHOU!\nTexto: %s\nRecebido: %v\nEsperado: %v", tt.texto, resultado, tt.esperado)
			} else {
				t.Logf("✅ OK: %s -> %s", tt.name, resultado)
			}
		})
	}
}
