package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

// FiltroConfig representa os filtros configurados pelo usuário
type FiltroConfig struct {
	Tribunal            string `json:"tribunal"`
	TipoComunicacao     string `json:"tipo_comunicacao"`
	CodigoClasse        string `json:"codigo_classe"`
	NomeClasse          string `json:"nome_classe"`
	TipoDocumento       string `json:"tipo_documento"`
	DataInicio          string `json:"data_inicio"`
	DataFim             string `json:"data_fim"`
	DataDespachoInicio  string `json:"data_despacho_inicio"`
	DataDespachoFim     string `json:"data_despacho_fim"`
	TextoContains       string `json:"texto_contains"`
	DiretorioCache      string `json:"diretorio_cache"`
	DiretorioSaida      string `json:"diretorio_saida"`
}

// ResultadoProcessado representa um item processado
type ResultadoProcessado struct {
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

var (
	basePath = "D:\\RS - LySA - EMPRESA\\go_scraper_pje"
)

func main() {
	// Páginas
	http.HandleFunc("/", handleIndex)
	http.HandleFunc("/visualizar", handleVisualizarDados)
	http.HandleFunc("/gerenciar-cache", handleGerenciarCache)
	http.HandleFunc("/dashboard", handleDashboard)
	
	// API
	http.HandleFunc("/api/listar-cache", handleListarCache)
	http.HandleFunc("/api/processar", handleProcessar)
	http.HandleFunc("/api/listar-filtrados", handleListarFiltrados)
	http.HandleFunc("/api/ler-filtrado", handleLerFiltrado)
	http.HandleFunc("/api/exportar-csv", handleExportarCSV)
	http.HandleFunc("/api/deletar-cache", handleDeletarCache)
	http.HandleFunc("/api/deletar-filtrado", handleDeletarFiltrado)
	http.HandleFunc("/api/info-cache", handleInfoCache)
	http.HandleFunc("/api/estatisticas", handleEstatisticas)
	
	http.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))

	fmt.Println("╔════════════════════════════════════════════════════╗")
	fmt.Println("║   🔍 Interface de Filtros PJE Scraper 🔍          ║")
	fmt.Println("╚════════════════════════════════════════════════════╝")
	fmt.Println("")
	fmt.Println("🌐 Servidor iniciado em: http://localhost:8080")
	fmt.Println("📁 Diretório base:", basePath)
	fmt.Println("")
	fmt.Println("✅ Abra o navegador e acesse: http://localhost:8080")
	fmt.Println("")

	log.Fatal(http.ListenAndServe(":8080", nil))
}

func handleIndex(w http.ResponseWriter, r *http.Request) {
	tmpl := `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 Interface de Filtros PJE</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: center; }
        h1 { color: #1f2937; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { color: #6b7280; font-size: 1.1em; }
        .section { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .section-title { color: #1f2937; font-size: 1.8em; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #2563eb; }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .form-group { display: flex; flex-direction: column; }
        label { color: #374151; font-weight: 600; margin-bottom: 8px; font-size: 0.95em; }
        input, select { padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1em; transition: all 0.3s; }
        input:focus, select:focus { outline: none; border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }
        textarea { padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1em; min-height: 80px; font-family: inherit; }
        .btn { background: #2563eb; color: white; padding: 15px 30px; border: none; border-radius: 10px; font-size: 1.1em; font-weight: 600; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); }
        .btn:hover { background: #1d4ed8; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4); }
        .btn:disabled { background: #9ca3af; cursor: not-allowed; transform: none; }
        .result-box { background: #f9fafb; padding: 20px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #10b981; }
        .success { color: #10b981; font-weight: bold; }
        .error { color: #ef4444; font-weight: bold; }
        .loading { display: none; text-align: center; padding: 20px; }
        .loading.active { display: block; }
        .spinner { border: 4px solid #f3f4f6; border-top: 4px solid #2563eb; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .info-box { background: #dbeafe; border-left: 4px solid #2563eb; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .cache-list { max-height: 200px; overflow-y: auto; background: #f9fafb; padding: 15px; border-radius: 8px; margin-top: 10px; }
        .cache-item { padding: 8px; margin: 5px 0; background: white; border-radius: 5px; cursor: pointer; transition: all 0.2s; }
        .cache-item:hover { background: #e5e7eb; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>🔍 Interface de Filtros PJE Scraper</h1>
        <p class="subtitle">Processe e filtre dados extraídos do cache</p>
        <div style="display: flex; gap: 15px; margin-top: 20px;">
            <a href="/" style="padding: 10px 20px; background: #10b981; color: white; border-radius: 8px; text-decoration: none;">Filtrar Dados</a>
            <a href="/visualizar" style="padding: 10px 20px; background: #2563eb; color: white; border-radius: 8px; text-decoration: none;">Visualizar Resultados</a>
            <a href="/gerenciar-cache" style="padding: 10px 20px; background: #2563eb; color: white; border-radius: 8px; text-decoration: none;">Gerenciar Cache</a>
            <a href="/dashboard" style="padding: 10px 20px; background: #2563eb; color: white; border-radius: 8px; text-decoration: none;">Dashboard</a>
        </div>
    </header>

    <div class="section">
        <h2 class="section-title">⚙️ Configurar Filtros</h2>
        
        <form id="filtroForm">
            <div class="form-grid">
                <div class="form-group">
                    <label>📁 Diretório de Cache</label>
                    <input type="text" id="diretorioCache" placeholder="cache/TJSP_2025-11-11_18-07-56" required>
                    <button type="button" onclick="listarCache()" style="margin-top: 10px; padding: 8px; background: #6b7280; color: white; border: none; border-radius: 5px; cursor: pointer;">📂 Listar Caches</button>
                    <div id="cacheList" class="cache-list" style="display: none;"></div>
                </div>

                <div class="form-group">
                    <label>💾 Diretório de Saída</label>
                    <input type="text" id="diretorioSaida" value="dados_filtrados" required>
                </div>

                <div class="form-group">
                    <label>🏛️ Tribunal (sigla)</label>
                    <input type="text" id="tribunal" placeholder="TJSP, TJAM, etc" title="Deixe vazio para todos">
                </div>

                <div class="form-group">
                    <label>📋 Tipo de Comunicação</label>
                    <select id="tipoComunicacao">
                        <option value="">Todos</option>
                        <option value="Lista de distribuição">Lista de distribuição</option>
                        <option value="Intimação">Intimação</option>
                        <option value="Citação">Citação</option>
                        <option value="Edital">Edital</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>⚖️ Código da Classe</label>
                    <input type="text" id="codigoClasse" placeholder="12154">
                </div>

                <div class="form-group">
                    <label>📄 Nome da Classe</label>
                    <input type="text" id="nomeClasse" placeholder="Procedimento Comum">
                </div>

                <div class="form-group">
                    <label>📝 Tipo de Documento</label>
                    <input type="text" id="tipoDocumento" placeholder="Decisão, Sentença, etc">
                </div>

                <div class="form-group">
                    <label>📅 Data Disponibilização (Início)</label>
                    <input type="date" id="dataInicio">
                </div>

                <div class="form-group">
                    <label>📅 Data Disponibilização (Fim)</label>
                    <input type="date" id="dataFim">
                </div>

                <div class="form-group">
                    <label>📆 Data Despacho (Início)</label>
                    <input type="date" id="dataDespachoInicio">
                </div>

                <div class="form-group">
                    <label>📆 Data Despacho (Fim)</label>
                    <input type="date" id="dataDespachoFim">
                </div>

                <div class="form-group" style="grid-column: 1 / -1;">
                    <label>🔍 Texto Contém (palavras-chave)</label>
                    <textarea id="textoContains" placeholder="Digite palavras ou frases separadas por vírgula"></textarea>
                    <small style="color: #6b7280; margin-top: 5px;">Ex: edital, intimação, sentença</small>
                </div>
            </div>

            <div class="info-box">
                <strong>💡 Dica:</strong> Deixe os campos vazios para não aplicar aquele filtro específico. Todos os filtros são opcionais!
            </div>

            <button type="submit" class="btn" id="btnProcessar">🚀 Processar e Filtrar Dados</button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 15px; color: #6b7280;">Processando dados do cache...</p>
        </div>

        <div id="resultado" style="display: none;"></div>
    </div>
</div>

<script>
async function listarCache() {
    const list = document.getElementById('cacheList');
    list.innerHTML = '<p style="text-align: center; color: #6b7280;">Carregando...</p>';
    list.style.display = 'block';
    
    try {
        const response = await fetch('/api/listar-cache');
        const caches = await response.json();
        
        if (caches.length === 0) {
            list.innerHTML = '<p style="color: #ef4444;">Nenhum cache encontrado</p>';
            return;
        }
        
        list.innerHTML = caches.map(cache => 
            '<div class="cache-item" onclick="selecionarCache(\''+cache+'\')">' + cache + '</div>'
        ).join('');
    } catch (err) {
        list.innerHTML = '<p style="color: #ef4444;">Erro ao listar caches</p>';
    }
}

function selecionarCache(cache) {
    document.getElementById('diretorioCache').value = 'cache/' + cache;
    document.getElementById('cacheList').style.display = 'none';
}

document.getElementById('filtroForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btn = document.getElementById('btnProcessar');
    const loading = document.getElementById('loading');
    const resultado = document.getElementById('resultado');
    
    btn.disabled = true;
    loading.classList.add('active');
    resultado.style.display = 'none';
    
    const filtro = {
        diretorio_cache: document.getElementById('diretorioCache').value,
        diretorio_saida: document.getElementById('diretorioSaida').value,
        tribunal: document.getElementById('tribunal').value,
        tipo_comunicacao: document.getElementById('tipoComunicacao').value,
        codigo_classe: document.getElementById('codigoClasse').value,
        nome_classe: document.getElementById('nomeClasse').value,
        tipo_documento: document.getElementById('tipoDocumento').value,
        data_inicio: document.getElementById('dataInicio').value,
        data_fim: document.getElementById('dataFim').value,
        data_despacho_inicio: document.getElementById('dataDespachoInicio').value,
        data_despacho_fim: document.getElementById('dataDespachoFim').value,
        texto_contains: document.getElementById('textoContains').value
    };
    
    try {
        const response = await fetch('/api/processar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(filtro)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultado.innerHTML = '<div class="result-box">' +
                '<h3 class="success">✅ Processamento Concluído!</h3>' +
                '<p style="margin: 15px 0;"><strong>Total de registros processados:</strong> ' + data.total_processados + '</p>' +
                '<p style="margin: 15px 0;"><strong>Total de registros filtrados:</strong> ' + data.total_filtrados + '</p>' +
                '<p style="margin: 15px 0;"><strong>Arquivo de saída:</strong> ' + data.arquivo_saida + '</p>' +
                '<p style="margin: 15px 0; color: #10b981;"><strong>💰 Valor potencial:</strong> R$ ' + (data.total_filtrados * 0.03).toFixed(2) + '</p>' +
                '<p style="margin-top: 15px; padding: 15px; background: #dbeafe; border-radius: 8px;">' +
                '<strong>📊 Taxa de filtro:</strong> ' + ((data.total_filtrados / data.total_processados) * 100).toFixed(1) + '%' +
                '</p>' +
                '</div>';
        } else {
            resultado.innerHTML = '<div class="result-box" style="border-left-color: #ef4444;">' +
                '<h3 class="error">❌ Erro no Processamento</h3>' +
                '<p style="margin-top: 10px;">' + data.erro + '</p>' +
                '</div>';
        }
    } catch (err) {
        resultado.innerHTML = '<div class="result-box" style="border-left-color: #ef4444;">' +
            '<h3 class="error">❌ Erro de Conexão</h3>' +
            '<p style="margin-top: 10px;">' + err.message + '</p>' +
            '</div>';
    } finally {
        btn.disabled = false;
        loading.classList.remove('active');
        resultado.style.display = 'block';
    }
});
</script>
</body>
</html>
	`

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	tmpl_parsed, _ := template.New("index").Parse(tmpl)
	tmpl_parsed.Execute(w, nil)
}

func handleListarCache(w http.ResponseWriter, r *http.Request) {
	cacheDir := filepath.Join(basePath, "cache")
	
	entries, err := os.ReadDir(cacheDir)
	if err != nil {
		http.Error(w, "Erro ao ler diretório de cache", http.StatusInternalServerError)
		return
	}

	var caches []string
	for _, entry := range entries {
		if entry.IsDir() {
			caches = append(caches, entry.Name())
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(caches)
}

func handleProcessar(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Método não permitido", http.StatusMethodNotAllowed)
		return
	}

	var filtro FiltroConfig
	if err := json.NewDecoder(r.Body).Decode(&filtro); err != nil {
		http.Error(w, "Erro ao decodificar JSON", http.StatusBadRequest)
		return
	}

	// Processa cache
	resultados, err := processarCache(filtro)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]any{
			"erro": err.Error(),
		})
		return
	}

	// Salva resultado com nome descritivo
	timestamp := time.Now().Format("2006-01-02_15-04-05")
	outputDir := filepath.Join(basePath, filtro.DiretorioSaida)
	os.MkdirAll(outputDir, 0755)
	
	// Gera nome descritivo: Tribunal_TipoComunicacao_Data.json
	tribunal := extrairTribunalDoCache(filtro.DiretorioCache)
	tipoComunicacao := limparNomeArquivo(filtro.TipoComunicacao)
	nomeArquivo := fmt.Sprintf("%s_%s_%s.json", tribunal, tipoComunicacao, timestamp)
	if tipoComunicacao == "" {
		nomeArquivo = fmt.Sprintf("%s_Todos_%s.json", tribunal, timestamp)
	}
	outputFile := filepath.Join(outputDir, nomeArquivo)
	
	file, err := os.Create(outputFile)
	if err != nil {
		http.Error(w, "Erro ao criar arquivo de saída", http.StatusInternalServerError)
		return
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	encoder.Encode(resultados)

	// Retorna resultado
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]any{
		"total_processados": len(resultados) + contarFiltrados(filtro),
		"total_filtrados":   len(resultados),
		"arquivo_saida":     outputFile,
	})
}

func processarCache(filtro FiltroConfig) ([]ResultadoProcessado, error) {
	cacheDir := filepath.Join(basePath, filtro.DiretorioCache)
	
	files, err := filepath.Glob(filepath.Join(cacheDir, "*.json"))
	if err != nil {
		return nil, err
	}

	var todosResultados []ResultadoProcessado

	for _, filePath := range files {
		data, err := os.ReadFile(filePath)
		if err != nil {
			continue
		}

		var apiResponse map[string]any
		if err := json.Unmarshal(data, &apiResponse); err != nil {
			continue
		}

		items, ok := apiResponse["items"].([]any)
		if !ok {
			continue
		}

		for _, item := range items {
			itemMap, ok := item.(map[string]any)
			if !ok {
				continue
			}

			resultado := converterParaResultado(itemMap)
			
			if aplicarFiltros(resultado, filtro) {
				todosResultados = append(todosResultados, resultado)
			}
		}
	}

	return todosResultados, nil
}

func converterParaResultado(item map[string]any) ResultadoProcessado {
	resultado := ResultadoProcessado{
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

	// Extrai data de despacho
	if texto, ok := item["texto"].(string); ok {
		resultado.DataDespacho = extrairDataDespacho(texto)
	}

	return resultado
}

func extrairDataDespacho(texto string) string {
	// Ordem dos padrões importa - mais específicos primeiro
	padroes := []string{
		`DATA\s+DE\s+EXPEDIENTE:\s*(\d{2}/\d{2}/\d{4})`,
		`Data\s+de\s+Expediente:\s*(\d{2}/\d{2}/\d{4})`,
		`DATA\s+DE\s+VINCULA[ÇC][ÃA]O:\s*(\d{2}/\d{2}/\d{4})`,
		`Data\s+de\s+Vincula[çc][ãa]o:\s*(\d{2}/\d{2}/\d{4})`,
		`DATA\s+VINCULA[ÇC][ÃA]O:\s*(\d{2}/\d{2}/\d{4})`,
		`Data\s+Vincula[çc][ãa]o:\s*(\d{2}/\d{2}/\d{4})`,
		`Vincula[çc][ãa]o:\s*(\d{2}/\d{2}/\d{4})`,
		`DATA:\s*(\d{2}/\d{2}/\d{4})`,
		`Data:\s*(\d{2}/\d{2}/\d{4})`,
		// CRÍTICO: Padrão para "distribuido para ... na data de DD/MM/YYYY"
		`na\s+data\s+de\s+(\d{2}/\d{2}/\d{4})`,
		`\b(\d{2}/\d{2}/\d{4})\b`, // Qualquer data isolada como fallback
	}

	for _, padrao := range padroes {
		re := regexp.MustCompile(padrao)
		if matches := re.FindStringSubmatch(texto); len(matches) > 1 {
			return matches[1]
		}
	}

	return ""
}

// parseDataISO converte data no formato ISO (YYYY-MM-DD) para time.Time
func parseDataISO(dataStr string) (time.Time, error) {
	return time.Parse("2006-01-02", dataStr)
}

// parseDataBR converte data no formato brasileiro (DD/MM/YYYY) para time.Time
func parseDataBR(dataStr string) (time.Time, error) {
	return time.Parse("02/01/2006", dataStr)
}

func aplicarFiltros(resultado ResultadoProcessado, filtro FiltroConfig) bool {
	// Tribunal
	if filtro.Tribunal != "" {
		if trib, ok := resultado.Tribunal.(string); ok {
			if trib != filtro.Tribunal {
				return false
			}
		}
	}

	// Tipo Comunicação
	if filtro.TipoComunicacao != "" {
		if tc, ok := resultado.TipoComunicacao.(string); ok {
			if tc != filtro.TipoComunicacao {
				return false
			}
		}
	}

	// Código Classe
	if filtro.CodigoClasse != "" {
		if cc, ok := resultado.CodigoClasse.(string); ok {
			if cc != filtro.CodigoClasse {
				return false
			}
		}
	}

	// Nome Classe
	if filtro.NomeClasse != "" {
		if nc, ok := resultado.NomeClasse.(string); ok {
			if !strings.Contains(strings.ToLower(nc), strings.ToLower(filtro.NomeClasse)) {
				return false
			}
		}
	}

	// Tipo Documento
	if filtro.TipoDocumento != "" {
		if td, ok := resultado.TipoDocumento.(string); ok {
			if !strings.Contains(strings.ToLower(td), strings.ToLower(filtro.TipoDocumento)) {
				return false
			}
		}
	}

	// Texto contém
	if filtro.TextoContains != "" {
		if texto, ok := resultado.Texto.(string); ok {
			palavras := strings.Split(filtro.TextoContains, ",")
			encontrou := false
			for _, palavra := range palavras {
				palavra = strings.TrimSpace(palavra)
				if strings.Contains(strings.ToLower(texto), strings.ToLower(palavra)) {
					encontrou = true
					break
				}
			}
			if !encontrou {
				return false
			}
		}
	}

	// Data Disponibilização
	if filtro.DataInicio != "" || filtro.DataFim != "" {
		if dataDisp, ok := resultado.DataDisponibilizacao.(string); ok && dataDisp != "" {
			dataDisponibilizacao, err := parseDataISO(dataDisp)
			if err == nil {
				if filtro.DataInicio != "" {
					dataInicio, err := parseDataISO(filtro.DataInicio)
					if err == nil && dataDisponibilizacao.Before(dataInicio) {
						return false
					}
				}
				if filtro.DataFim != "" {
					dataFim, err := parseDataISO(filtro.DataFim)
					if err == nil && dataDisponibilizacao.After(dataFim) {
						return false
					}
				}
			}
		}
	}

	// Data Despacho (extraída do texto)
	if filtro.DataDespachoInicio != "" || filtro.DataDespachoFim != "" {
		if resultado.DataDespacho != "" {
			dataDespacho, err := parseDataBR(resultado.DataDespacho)
			if err == nil {
				if filtro.DataDespachoInicio != "" {
					dataInicio, err := parseDataISO(filtro.DataDespachoInicio)
					if err == nil && dataDespacho.Before(dataInicio) {
						return false
					}
				}
				if filtro.DataDespachoFim != "" {
					dataFim, err := parseDataISO(filtro.DataDespachoFim)
					if err == nil && dataDespacho.After(dataFim) {
						return false
					}
				}
			}
		} else {
			// Se filtro de data despacho está ativo mas registro não tem data, filtrar
			return false
		}
	}

	return true
}

func contarFiltrados(filtro FiltroConfig) int {
	// Placeholder - conta total de itens no cache
	return 0
}

// ========== NOVOS HANDLERS ==========

// handleListarFiltrados lista todos os arquivos filtrados
func handleListarFiltrados(w http.ResponseWriter, r *http.Request) {
	filtradosDir := filepath.Join(basePath, "dados_filtrados")
	
	files, err := os.ReadDir(filtradosDir)
	if err != nil {
		http.Error(w, "Erro ao ler diretório de filtrados", http.StatusInternalServerError)
		return
	}

	type ArquivoFiltrado struct {
		Nome          string `json:"nome"`
		Tamanho       int64  `json:"tamanho"`
		DataCriacao   string `json:"data_criacao"`
		CaminhoRelativo string `json:"caminho_relativo"`
	}

	var arquivos []ArquivoFiltrado
	for _, file := range files {
		if !file.IsDir() && filepath.Ext(file.Name()) == ".json" {
			info, _ := file.Info()
			arquivos = append(arquivos, ArquivoFiltrado{
				Nome:            file.Name(),
				Tamanho:         info.Size(),
				DataCriacao:     info.ModTime().Format("2006-01-02 15:04:05"),
				CaminhoRelativo: "dados_filtrados/" + file.Name(),
			})
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(arquivos)
}

// handleLerFiltrado lê o conteúdo de um arquivo filtrado
func handleLerFiltrado(w http.ResponseWriter, r *http.Request) {
	arquivo := r.URL.Query().Get("arquivo")
	if arquivo == "" {
		http.Error(w, "Parâmetro 'arquivo' obrigatório", http.StatusBadRequest)
		return
	}

	filePath := filepath.Join(basePath, "dados_filtrados", filepath.Base(arquivo))
	
	data, err := os.ReadFile(filePath)
	if err != nil {
		http.Error(w, "Erro ao ler arquivo", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(data)
}

// handleExportarCSV exporta dados filtrados para CSV
func handleExportarCSV(w http.ResponseWriter, r *http.Request) {
	arquivo := r.URL.Query().Get("arquivo")
	if arquivo == "" {
		http.Error(w, "Parâmetro 'arquivo' obrigatório", http.StatusBadRequest)
		return
	}

	filePath := filepath.Join(basePath, "dados_filtrados", filepath.Base(arquivo))
	
	data, err := os.ReadFile(filePath)
	if err != nil {
		http.Error(w, "Erro ao ler arquivo", http.StatusInternalServerError)
		return
	}

	var resultados []ResultadoProcessado
	if err := json.Unmarshal(data, &resultados); err != nil {
		http.Error(w, "Erro ao decodificar JSON", http.StatusInternalServerError)
		return
	}

	// Gera CSV
	w.Header().Set("Content-Type", "text/csv; charset=utf-8")
	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=%s.csv", strings.TrimSuffix(filepath.Base(arquivo), ".json")))
	
	// BOM para Excel reconhecer UTF-8
	w.Write([]byte{0xEF, 0xBB, 0xBF})
	
	// Cabeçalho - DATA DESPACHO em destaque (primeira coluna de data)
	fmt.Fprintln(w, "ID,Processo,Processo Sem Mascara,**DATA DESPACHO (PRAZO)**,Data Disponibilizacao,Tribunal,Tipo Comunicacao,Codigo Classe,Nome Classe,Tipo Documento,Nome Orgao")
	
	// Dados
	for _, r := range resultados {
		dataDespacho := r.DataDespacho
		if dataDespacho == "" {
			dataDespacho = "SEM DATA - VERIFICAR"
		}
		
		fmt.Fprintf(w, "%v,%v,%v,%v,%v,%v,%v,%v,%v,%v,%v\n",
			r.ID, r.Processo, r.ProcessoSemMascara, dataDespacho,
			r.DataDisponibilizacao, r.Tribunal, r.TipoComunicacao, r.CodigoClasse,
			r.NomeClasse, r.TipoDocumento, r.NomeOrgao)
	}
}

// handleDeletarCache deleta um diretório de cache
func handleDeletarCache(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Método não permitido", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Cache string `json:"cache"`
	}
	
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Erro ao decodificar JSON", http.StatusBadRequest)
		return
	}

	cacheDir := filepath.Join(basePath, "cache", filepath.Base(req.Cache))
	
	if err := os.RemoveAll(cacheDir); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{
			"erro": "Erro ao deletar cache: " + err.Error(),
		})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"mensagem": "Cache deletado com sucesso",
	})
}

// handleInfoCache retorna informações sobre um cache
func handleInfoCache(w http.ResponseWriter, r *http.Request) {
	cache := r.URL.Query().Get("cache")
	if cache == "" {
		http.Error(w, "Parâmetro 'cache' obrigatório", http.StatusBadRequest)
		return
	}

	cacheDir := filepath.Join(basePath, "cache", filepath.Base(cache))
	
	files, err := filepath.Glob(filepath.Join(cacheDir, "*.json"))
	if err != nil {
		http.Error(w, "Erro ao ler cache", http.StatusInternalServerError)
		return
	}

	totalItens := 0
	var tamanhoTotal int64
	
	for _, file := range files {
		info, _ := os.Stat(file)
		tamanhoTotal += info.Size()
		
		data, _ := os.ReadFile(file)
		var apiResponse map[string]any
		if json.Unmarshal(data, &apiResponse) == nil {
			if items, ok := apiResponse["items"].([]any); ok {
				totalItens += len(items)
			}
		}
	}

	dirInfo, _ := os.Stat(cacheDir)
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]any{
		"total_arquivos": len(files),
		"total_itens":    totalItens,
		"tamanho_mb":     float64(tamanhoTotal) / 1024 / 1024,
		"data_criacao":   dirInfo.ModTime().Format("2006-01-02 15:04:05"),
	})
}

// handleEstatisticas retorna estatísticas gerais
func handleEstatisticas(w http.ResponseWriter, r *http.Request) {
	// Conta caches
	cacheDir := filepath.Join(basePath, "cache")
	caches, _ := os.ReadDir(cacheDir)
	totalCaches := 0
	for _, c := range caches {
		if c.IsDir() {
			totalCaches++
		}
	}

	// Conta filtrados
	filtradosDir := filepath.Join(basePath, "dados_filtrados")
	filtrados, _ := os.ReadDir(filtradosDir)
	totalFiltrados := 0
	totalRegistrosFiltrados := 0
	
	for _, f := range filtrados {
		if !f.IsDir() && filepath.Ext(f.Name()) == ".json" {
			totalFiltrados++
			
			filePath := filepath.Join(filtradosDir, f.Name())
			data, _ := os.ReadFile(filePath)
			var resultados []ResultadoProcessado
			if json.Unmarshal(data, &resultados) == nil {
				totalRegistrosFiltrados += len(resultados)
			}
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]any{
		"total_caches":              totalCaches,
		"total_filtrados":           totalFiltrados,
		"total_registros_filtrados": totalRegistrosFiltrados,
		"valor_potencial":           float64(totalRegistrosFiltrados) * 0.03,
	})
}

// extrairTribunalDoCache extrai a sigla do tribunal do nome do cache
// Ex: "TJSP_2025-11-12_14-44-35" -> "TJSP"
func extrairTribunalDoCache(cacheDir string) string {
	parts := strings.Split(filepath.Base(cacheDir), "_")
	if len(parts) > 0 {
		return parts[0]
	}
	return "Tribunal"
}

// limparNomeArquivo remove caracteres especiais e espaços do nome
func limparNomeArquivo(nome string) string {
	// Remove espaços e caracteres especiais
	nome = strings.TrimSpace(nome)
	nome = strings.ReplaceAll(nome, " ", "")
	nome = strings.ReplaceAll(nome, "/", "")
	nome = strings.ReplaceAll(nome, "\\", "")
	nome = strings.ReplaceAll(nome, ":", "")
	nome = strings.ReplaceAll(nome, "*", "")
	nome = strings.ReplaceAll(nome, "?", "")
	nome = strings.ReplaceAll(nome, "\"", "")
	nome = strings.ReplaceAll(nome, "<", "")
	nome = strings.ReplaceAll(nome, ">", "")
	nome = strings.ReplaceAll(nome, "|", "")
	
	// Limita o tamanho
	if len(nome) > 50 {
		nome = nome[:50]
	}
	
	return nome
}

// handleDeletarFiltrado deleta um arquivo filtrado
func handleDeletarFiltrado(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Método não permitido", http.StatusMethodNotAllowed)
		return
	}

	var req struct {
		Arquivo string `json:"arquivo"`
	}
	
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{
			"erro": "Erro ao decodificar JSON",
		})
		return
	}

	// Valida o nome do arquivo para evitar directory traversal
	if strings.Contains(req.Arquivo, "..") || strings.Contains(req.Arquivo, "/") || strings.Contains(req.Arquivo, "\\") {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{
			"erro": "Nome de arquivo inválido",
		})
		return
	}

	filtradosDir := filepath.Join(basePath, "dados_filtrados")
	filePath := filepath.Join(filtradosDir, req.Arquivo)

	// Verifica se o arquivo existe
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{
			"erro": "Arquivo não encontrado",
		})
		return
	}

	// Deleta o arquivo
	if err := os.Remove(filePath); err != nil {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]string{
			"erro": "Erro ao deletar arquivo: " + err.Error(),
		})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"sucesso": "Arquivo deletado com sucesso",
	})
}
