package models

import "regexp"

// ApiResponse representa a resposta da API do PJE
type ApiResponse struct {
	Status  string           `json:"status"`
	Message string           `json:"message"`
	Count   int              `json:"count"`
	Items   []map[string]any `json:"items"`
}

// Resultado representa um item filtrado da API
type Resultado struct {
	ID                   any    `json:"id"`
	Processo             any    `json:"processo"`
	ProcessoSemMascara   any    `json:"processo_sem_mascara"`
	DataDisponibilizacao any    `json:"data_disponibilizacao"`
	DataDespacho         string `json:"data_despacho,omitempty"`
	Tribunal             any    `json:"tribunal"`
	TipoComunicacao      any    `json:"tipo_comunicacao"`
	CodigoClasse         any    `json:"codigo_classe"`
	NomeClasse           any    `json:"nome_classe"`
	Texto                any    `json:"texto"`
	Meio                 any    `json:"meio,omitempty"`
	TipoDocumento        any    `json:"tipo_documento,omitempty"`
	NomeOrgao            any    `json:"nome_orgao,omitempty"`
}

// TribunalResult armazena o resultado do scraping de um tribunal
type TribunalResult struct {
	Sigla  string
	Result []Resultado
	Erros  int
	Err    error
}

// CriarResultado converte um item da API para Resultado
func CriarResultado(item map[string]any) Resultado {
	// Mapeamento correto dos campos da API
	resultado := Resultado{
		ID:                   item["id"],
		Processo:             item["numeroprocessocommascara"],
		ProcessoSemMascara:   item["numero_processo"],
		DataDisponibilizacao: item["data_disponibilizacao"],
		Tribunal:             item["siglaTribunal"],
		TipoComunicacao:      item["tipoComunicacao"],
		CodigoClasse:         item["codigoClasse"],
		NomeClasse:           item["nomeClasse"],
		Texto:                item["texto"],
		Meio:                 item["meio"],
		TipoDocumento:        item["tipoDocumento"],
		NomeOrgao:            item["nomeOrgao"],
	}

	// Extrai data de despacho do texto se existir
	if texto, ok := item["texto"].(string); ok {
		resultado.DataDespacho = ExtrairDataDespacho(texto)
	}

	return resultado
}

// ExtrairDataDespacho extrai a data de despacho do texto
// Formatos suportados:
// - DATA DE EXPEDIENTE: 05/11/2025
// - Data de Expediente: 05/11/2025
// - DATA: 05/11/2025
// - na data de 05/11/2025
// - distribuido para ... na data de 05/11/2025
func ExtrairDataDespacho(texto string) string {
	// Padrões regex para encontrar datas (ordem de especificidade: mais específico primeiro)
	padroes := []string{
		`DATA\s+DE\s+EXPEDIENTE:\s*(\d{2}/\d{2}/\d{4})`,
		`Data\s+de\s+Expediente:\s*(\d{2}/\d{2}/\d{4})`,
		`DATA:\s*(\d{2}/\d{2}/\d{4})`,
		`na\s+data\s+de\s+(\d{2}/\d{2}/\d{4})`,        // Captura "na data de dd/mm/yyyy"
		`distribuido\s+.*?\s+na\s+data\s+de\s+(\d{2}/\d{2}/\d{4})`, // Captura "distribuido ... na data de dd/mm/yyyy"
		`\b(\d{2}/\d{2}/\d{4})\b`, // Qualquer data isolada no formato dd/mm/yyyy
	}

	for _, padrao := range padroes {
		re := regexp.MustCompile(padrao)
		if matches := re.FindStringSubmatch(texto); len(matches) > 1 {
			return matches[1]
		}
	}

	return ""
}
