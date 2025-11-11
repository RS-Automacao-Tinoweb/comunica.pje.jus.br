package models

// ApiResponse representa a resposta da API do PJE
type ApiResponse struct {
	Status  string           `json:"status"`
	Message string           `json:"message"`
	Count   int              `json:"count"`
	Items   []map[string]any `json:"items"`
}

// Resultado representa um item filtrado da API
type Resultado struct {
	ID                   any `json:"id"`
	Processo             any `json:"processo"`
	ProcessoSemMascara   any `json:"processo_sem_mascara"`
	DataDisponibilizacao any `json:"data_disponibilizacao"`
	Tribunal             any `json:"tribunal"`
	TipoComunicacao      any `json:"tipo_comunicacao"`
	CodigoClasse         any `json:"codigo_classe"`
	NomeClasse           any `json:"nome_classe"`
	Comunicacao          any `json:"comunicacao"`
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
	return Resultado{
		ID:                   item["id"],
		Processo:             item["processo"],
		ProcessoSemMascara:   item["processo_sem_mascara"],
		DataDisponibilizacao: item["data_disponibilizacao"],
		Tribunal:             item["tribunal"],
		TipoComunicacao:      item["tipo_comunicacao"],
		CodigoClasse:         item["codigo_classe"],
		NomeClasse:           item["nome_classe"],
		Comunicacao:          item["comunicacao"],
	}
}
