package main

import (
	"html/template"
	"net/http"
)

// handleDashboard renderiza a página do dashboard
func handleDashboard(w http.ResponseWriter, r *http.Request) {
	tmpl := `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - PJE Scraper</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        header { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); margin-bottom: 30px; }
        h1 { color: #1f2937; font-size: 2.5em; margin-bottom: 10px; }
        .nav { display: flex; gap: 15px; margin-top: 20px; }
        .nav a { padding: 10px 20px; background: #2563eb; color: white; border-radius: 8px; text-decoration: none; transition: all 0.3s; }
        .nav a:hover { background: #1d4ed8; transform: translateY(-2px); }
        .nav a.active { background: #10b981; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .stat-value { font-size: 2.5em; font-weight: bold; color: #2563eb; margin: 10px 0; }
        .stat-label { color: #6b7280; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
        .stat-icon { font-size: 3em; margin-bottom: 10px; }
        .section { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .section-title { color: #1f2937; font-size: 1.8em; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #2563eb; }
        .loading { text-align: center; padding: 40px; color: #6b7280; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>Dashboard - PJE Scraper</h1>
        <div class="nav">
            <a href="/" >Filtrar Dados</a>
            <a href="/visualizar">Visualizar Resultados</a>
            <a href="/gerenciar-cache">Gerenciar Cache</a>
            <a href="/dashboard" class="active">Dashboard</a>
        </div>
    </header>

    <div class="stats-grid" id="statsGrid">
        <div class="loading">Carregando estatísticas...</div>
    </div>

    <div class="section">
        <h2 class="section-title">Visão Geral do Sistema</h2>
        <div id="visaoGeral" class="loading">Carregando...</div>
    </div>
</div>

<script>
async function carregarEstatisticas() {
    try {
        const response = await fetch('/api/estatisticas');
        const stats = await response.json();
        
        document.getElementById('statsGrid').innerHTML = ` +
		"`" + `
            <div class="stat-card">
                <div class="stat-icon">📦</div>
                <div class="stat-label">Total de Caches</div>
                <div class="stat-value">${stats.total_caches}</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-label">Arquivos Filtrados</div>
                <div class="stat-value">${stats.total_filtrados}</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📄</div>
                <div class="stat-label">Registros Filtrados</div>
                <div class="stat-value">${stats.total_registros_filtrados.toLocaleString('pt-BR')}</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">💰</div>
                <div class="stat-label">Valor Potencial</div>
                <div class="stat-value">R$ ${stats.valor_potencial.toFixed(2)}</div>
            </div>
        ` + "`" + `;
        
        const metaMensal = 400000;
        const percentualMeta = (stats.total_registros_filtrados / metaMensal * 100).toFixed(1);
        
        document.getElementById('visaoGeral').innerHTML = ` + "`" + `
            <div style="padding: 20px;">
                <h3 style="margin-bottom: 15px;">Meta Mensal: 400.000 extrações</h3>
                <div style="background: #f3f4f6; border-radius: 10px; height: 40px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #2563eb, #10b981); height: 100%; width: ${Math.min(percentualMeta, 100)}%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; transition: width 1s;">
                        ${percentualMeta}%
                    </div>
                </div>
                <p style="margin-top: 15px; color: #6b7280;">
                    ${stats.total_registros_filtrados.toLocaleString('pt-BR')} de 400.000 extrações realizadas
                </p>
                <p style="margin-top: 10px; color: ${percentualMeta >= 100 ? '#10b981' : '#f59e0b'}; font-weight: bold;">
                    ${percentualMeta >= 100 ? '✅ Meta atingida!' : '⏳ Em andamento...'}
                </p>
            </div>
        ` + "`" + `;
    } catch (err) {
        document.getElementById('statsGrid').innerHTML = '<div class="loading">Erro ao carregar estatísticas</div>';
    }
}

carregarEstatisticas();
</script>
</body>
</html>
	`

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	tmpl_parsed, _ := template.New("dashboard").Parse(tmpl)
	tmpl_parsed.Execute(w, nil)
}

// handleVisualizarDados renderiza a página de visualização de dados filtrados
func handleVisualizarDados(w http.ResponseWriter, r *http.Request) {
	tmpl := `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualizar Dados - PJE Scraper</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        header { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); margin-bottom: 30px; }
        h1 { color: #1f2937; font-size: 2.5em; margin-bottom: 10px; }
        .nav { display: flex; gap: 15px; margin-top: 20px; }
        .nav a { padding: 10px 20px; background: #2563eb; color: white; border-radius: 8px; text-decoration: none; transition: all 0.3s; }
        .nav a:hover { background: #1d4ed8; transform: translateY(-2px); }
        .nav a.active { background: #10b981; }
        .section { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .section-title { color: #1f2937; font-size: 1.8em; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #2563eb; }
        select { padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1em; width: 100%; max-width: 500px; }
        .btn { background: #2563eb; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-size: 1em; cursor: pointer; transition: all 0.3s; margin-right: 10px; }
        .btn:hover { background: #1d4ed8; }
        .btn-success { background: #10b981; }
        .btn-success:hover { background: #059669; }
        .btn-danger { background: #ef4444; }
        .btn-danger:hover { background: #dc2626; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
        th { background: #f9fafb; font-weight: 600; color: #1f2937; }
        th.data-destaque { background: #fef3c7; color: #92400e; font-weight: 700; }
        td.data-destaque { background: #fffbeb; font-weight: 700; color: #b45309; font-size: 1.1em; }
        .data-alerta { background: #fee2e2 !important; color: #991b1b !important; font-weight: bold; }
        tr:hover { background: #f9fafb; }
        .loading { text-align: center; padding: 40px; color: #6b7280; }
        .info-box { background: #dbeafe; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb; }
        .pagination { display: flex; gap: 10px; justify-content: center; margin-top: 20px; }
        .pagination button { padding: 8px 16px; border: 1px solid #e5e7eb; background: white; border-radius: 5px; cursor: pointer; }
        .pagination button.active { background: #2563eb; color: white; border-color: #2563eb; }
        .search-box { display: flex; gap: 10px; margin: 20px 0; }
        .search-box input { flex: 1; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>Visualizar Dados Filtrados</h1>
        <div class="nav">
            <a href="/">Filtrar Dados</a>
            <a href="/visualizar" class="active">Visualizar Resultados</a>
            <a href="/gerenciar-cache">Gerenciar Cache</a>
            <a href="/dashboard">Dashboard</a>
        </div>
    </header>

    <div class="section">
        <h2 class="section-title">Selecionar Arquivo Filtrado</h2>
        <select id="arquivoSelect" onchange="carregarDados()">
            <option value="">Carregando...</option>
        </select>
        
        <div id="acoes" style="margin-top: 20px; display: none;">
            <button class="btn btn-success" onclick="exportarCSV()">📥 Exportar CSV</button>
            <button class="btn" onclick="baixarJSON()">📄 Baixar JSON</button>
            <button class="btn btn-danger" onclick="confirmarDeletar()">🗑️ Deletar Arquivo</button>
        </div>
    </div>

    <div class="section" id="dadosSection" style="display: none;">
        <h2 class="section-title">Dados Filtrados</h2>
        
        <div class="info-box" id="infoBox"></div>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Buscar por processo, tribunal, classe..." onkeyup="filtrarTabela()">
        </div>
        
        <div style="overflow-x: auto;">
            <table id="tabelaDados">
                <thead>
                    <tr>
                        <th>Processo</th>
                        <th>Tribunal</th>
                        <th class="data-destaque">⚠️ DATA DESPACHO (PRAZO)</th>
                        <th>Data Disponibilização</th>
                        <th>Tipo Comunicação</th>
                        <th>Classe</th>
                        <th>Órgão</th>
                    </tr>
                </thead>
                <tbody id="tabelaBody">
                </tbody>
            </table>
        </div>
        
        <div class="pagination" id="pagination"></div>
    </div>
</div>

<script>
let dadosAtuais = [];
let arquivoAtual = '';
const itensPorPagina = 50;
let paginaAtual = 1;

async function listarArquivos() {
    const response = await fetch('/api/listar-filtrados');
    const arquivos = await response.json();
    
    const select = document.getElementById('arquivoSelect');
    if (arquivos.length === 0) {
        select.innerHTML = '<option value="">Nenhum arquivo filtrado encontrado</option>';
        return;
    }
    
    select.innerHTML = '<option value="">Selecione um arquivo...</option>';
    arquivos.forEach(arq => {
        const option = document.createElement('option');
        option.value = arq.nome;
        option.textContent = arq.nome + ' (' + (arq.tamanho / 1024).toFixed(2) + ' KB)';
        select.appendChild(option);
    });
}

async function carregarDados() {
    const select = document.getElementById('arquivoSelect');
    arquivoAtual = select.value;
    
    if (!arquivoAtual) {
        document.getElementById('dadosSection').style.display = 'none';
        document.getElementById('acoes').style.display = 'none';
        return;
    }
    
    const response = await fetch('/api/ler-filtrado?arquivo=' + encodeURIComponent(arquivoAtual));
    dadosAtuais = await response.json();
    
    document.getElementById('acoes').style.display = 'block';
    document.getElementById('dadosSection').style.display = 'block';
    
    // Contar registros sem data e com prazo vencido
    let semData = 0;
    let prazoVencido = 0;
    dadosAtuais.forEach(item => {
        if (!item.data_despacho) {
            semData++;
        } else {
            const partesData = item.data_despacho.split('/');
            if (partesData.length === 3) {
                const dataDespacho = new Date(partesData[2], partesData[1] - 1, partesData[0]);
                const hoje = new Date();
                const diffTime = hoje - dataDespacho;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                if (diffDays > 15) prazoVencido++;
            }
        }
    });
    
    document.getElementById('infoBox').innerHTML = ` + "`" + `
        <div style="margin-bottom: 15px; padding: 10px; background: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 5px;">
            <strong style="color: #92400e;">⚠️ ATENÇÃO - PRAZOS:</strong><br>
            <span style="color: #78350f;">A coluna <strong>DATA DESPACHO</strong> é CRÍTICA para decisões sobre prazos legais!</span><br>
            <span style="color: #78350f;">🔴 Processos com mais de 15 dias aparecem em <strong style="color: #991b1b;">VERMELHO</strong></span>
        </div>
        <strong>Total de registros:</strong> ${dadosAtuais.length} <br>
        <strong>Valor potencial:</strong> R$ ${(dadosAtuais.length * 0.03).toFixed(2)} <br>
        ${prazoVencido > 0 ? '<strong style="color: #991b1b;">⚠️ Processos com prazo crítico (>15 dias):</strong> ' + prazoVencido + ' <br>' : ''}
        ${semData > 0 ? '<strong style="color: #991b1b;">⚠️ Processos SEM DATA:</strong> ' + semData : ''}
    ` + "`" + `;
    
    paginaAtual = 1;
    renderizarTabela();
}

function renderizarTabela() {
    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;
    const dadosPagina = dadosAtuais.slice(inicio, fim);
    
    const tbody = document.getElementById('tabelaBody');
    tbody.innerHTML = dadosPagina.map(item => {
        // Calcular dias desde o despacho
        let classeData = 'data-destaque';
        let textoData = item.data_despacho || 'SEM DATA';
        let diasInfo = '';
        
        if (item.data_despacho) {
            const partesData = item.data_despacho.split('/');
            if (partesData.length === 3) {
                const dataDespacho = new Date(partesData[2], partesData[1] - 1, partesData[0]);
                const hoje = new Date();
                const diffTime = hoje - dataDespacho;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                
                if (diffDays > 15) {
                    classeData += ' data-alerta';
                    diasInfo = ' (' + diffDays + ' dias!)';
                } else if (diffDays >= 0) {
                    diasInfo = ' (' + diffDays + ' dias)';
                }
                textoData = item.data_despacho + diasInfo;
            }
        } else {
            classeData += ' data-alerta';
            textoData = '⚠️ SEM DATA';
        }
        
        return ` + "`" + `
        <tr>
            <td>${item.processo || '-'}</td>
            <td>${item.tribunal || '-'}</td>
            <td class="${classeData}">${textoData}</td>
            <td>${item.data_disponibilizacao || '-'}</td>
            <td>${item.tipo_comunicacao || '-'}</td>
            <td>${item.nome_classe || '-'}</td>
            <td>${item.nome_orgao || '-'}</td>
        </tr>
        ` + "`" + `;
    }).join('');
    
    renderizarPaginacao();
}

function renderizarPaginacao() {
    const totalPaginas = Math.ceil(dadosAtuais.length / itensPorPagina);
    const pagination = document.getElementById('pagination');
    
    let html = '';
    for (let i = 1; i <= totalPaginas; i++) {
        html += ` + "`<button class=\"${i === paginaAtual ? 'active' : ''}\" onclick=\"irParaPagina(${i})\">${i}</button>`" + `;
    }
    pagination.innerHTML = html;
}

function irParaPagina(pagina) {
    paginaAtual = pagina;
    renderizarTabela();
}

function filtrarTabela() {
    const termo = document.getElementById('searchInput').value.toLowerCase();
    if (!termo) {
        renderizarTabela();
        return;
    }
    
    const dadosFiltrados = dadosAtuais.filter(item => 
        (item.processo && item.processo.toString().toLowerCase().includes(termo)) ||
        (item.tribunal && item.tribunal.toString().toLowerCase().includes(termo)) ||
        (item.nome_classe && item.nome_classe.toString().toLowerCase().includes(termo))
    );
    
    const tbody = document.getElementById('tabelaBody');
    tbody.innerHTML = dadosFiltrados.map(item => {
        // Calcular dias desde o despacho
        let classeData = 'data-destaque';
        let textoData = item.data_despacho || 'SEM DATA';
        let diasInfo = '';
        
        if (item.data_despacho) {
            const partesData = item.data_despacho.split('/');
            if (partesData.length === 3) {
                const dataDespacho = new Date(partesData[2], partesData[1] - 1, partesData[0]);
                const hoje = new Date();
                const diffTime = hoje - dataDespacho;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                
                if (diffDays > 15) {
                    classeData += ' data-alerta';
                    diasInfo = ' (' + diffDays + ' dias!)';
                } else if (diffDays >= 0) {
                    diasInfo = ' (' + diffDays + ' dias)';
                }
                textoData = item.data_despacho + diasInfo;
            }
        } else {
            classeData += ' data-alerta';
            textoData = '⚠️ SEM DATA';
        }
        
        return ` + "`" + `
        <tr>
            <td>${item.processo || '-'}</td>
            <td>${item.tribunal || '-'}</td>
            <td class="${classeData}">${textoData}</td>
            <td>${item.data_disponibilizacao || '-'}</td>
            <td>${item.tipo_comunicacao || '-'}</td>
            <td>${item.nome_classe || '-'}</td>
            <td>${item.nome_orgao || '-'}</td>
        </tr>
        ` + "`" + `;
    }).join('');
}

function exportarCSV() {
    window.location.href = '/api/exportar-csv?arquivo=' + encodeURIComponent(arquivoAtual);
}

function baixarJSON() {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(dadosAtuais, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", arquivoAtual);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
}

function confirmarDeletar() {
    if (!arquivoAtual) {
        alert('Nenhum arquivo selecionado');
        return;
    }
    
    if (confirm('Tem certeza que deseja deletar o arquivo "' + arquivoAtual + '"?\n\nEsta ação não pode ser desfeita!')) {
        deletarArquivo();
    }
}

async function deletarArquivo() {
    try {
        const response = await fetch('/api/deletar-filtrado', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ arquivo: arquivoAtual })
        });
        
        const data = await response.json();
        
        if (data.sucesso) {
            alert('Arquivo deletado com sucesso!');
            window.location.reload();
        } else {
            alert('Erro ao deletar: ' + (data.erro || 'Erro desconhecido'));
        }
    } catch (err) {
        alert('Erro ao deletar arquivo: ' + err.message);
    }
}

listarArquivos();
</script>
</body>
</html>
	`

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	tmpl_parsed, _ := template.New("visualizar").Parse(tmpl)
	tmpl_parsed.Execute(w, nil)
}

// handleGerenciarCache renderiza a página de gerenciamento de cache
func handleGerenciarCache(w http.ResponseWriter, r *http.Request) {
	tmpl := `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerenciar Cache - PJE Scraper</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        header { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); margin-bottom: 30px; }
        h1 { color: #1f2937; font-size: 2.5em; margin-bottom: 10px; }
        .nav { display: flex; gap: 15px; margin-top: 20px; }
        .nav a { padding: 10px 20px; background: #2563eb; color: white; border-radius: 8px; text-decoration: none; transition: all 0.3s; }
        .nav a:hover { background: #1d4ed8; transform: translateY(-2px); }
        .nav a.active { background: #10b981; }
        .section { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .section-title { color: #1f2937; font-size: 1.8em; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #2563eb; }
        .cache-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .cache-card { background: #f9fafb; padding: 20px; border-radius: 10px; border: 2px solid #e5e7eb; transition: all 0.3s; }
        .cache-card:hover { border-color: #2563eb; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2); }
        .cache-name { font-weight: bold; color: #1f2937; margin-bottom: 10px; font-size: 1.1em; }
        .cache-info { color: #6b7280; font-size: 0.9em; margin: 5px 0; }
        .btn { background: #2563eb; color: white; padding: 10px 20px; border: none; border-radius: 8px; font-size: 0.9em; cursor: pointer; transition: all 0.3s; margin-top: 15px; width: 100%; }
        .btn:hover { background: #1d4ed8; }
        .btn-danger { background: #ef4444; }
        .btn-danger:hover { background: #dc2626; }
        .loading { text-align: center; padding: 40px; color: #6b7280; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; }
        .modal-content { background: white; margin: 15% auto; padding: 30px; border-radius: 15px; max-width: 500px; }
        .modal-buttons { display: flex; gap: 10px; margin-top: 20px; }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>Gerenciar Cache</h1>
        <div class="nav">
            <a href="/">Filtrar Dados</a>
            <a href="/visualizar">Visualizar Resultados</a>
            <a href="/gerenciar-cache" class="active">Gerenciar Cache</a>
            <a href="/dashboard">Dashboard</a>
        </div>
    </header>

    <div class="section">
        <h2 class="section-title">Caches Disponíveis</h2>
        <div class="cache-grid" id="cacheGrid">
            <div class="loading">Carregando caches...</div>
        </div>
    </div>
</div>

<div class="modal" id="deleteModal">
    <div class="modal-content">
        <h2 style="margin-bottom: 15px;">Confirmar Exclusão</h2>
        <p>Tem certeza que deseja deletar este cache?</p>
        <p style="color: #ef4444; margin-top: 10px;"><strong id="cacheName"></strong></p>
        <div class="modal-buttons">
            <button class="btn" onclick="fecharModal()">Cancelar</button>
            <button class="btn btn-danger" onclick="confirmarDelete()">Deletar</button>
        </div>
    </div>
</div>

<script>
let cacheParaDeletar = '';

async function listarCaches() {
    try {
        const response = await fetch('/api/listar-cache');
        const caches = await response.json();
        
        if (caches.length === 0) {
            document.getElementById('cacheGrid').innerHTML = '<div class="loading">Nenhum cache encontrado</div>';
            return;
        }
        
        const grid = document.getElementById('cacheGrid');
        grid.innerHTML = '';
        
        for (const cache of caches) {
            const infoResponse = await fetch('/api/info-cache?cache=' + encodeURIComponent(cache));
            const info = await infoResponse.json();
            
            const card = document.createElement('div');
            card.className = 'cache-card';
            card.innerHTML = ` + "`" + `
                <div class="cache-name">${cache}</div>
                <div class="cache-info">📦 Arquivos: ${info.total_arquivos}</div>
                <div class="cache-info">📄 Itens: ${info.total_itens.toLocaleString('pt-BR')}</div>
                <div class="cache-info">💾 Tamanho: ${info.tamanho_mb.toFixed(2)} MB</div>
                <div class="cache-info">📅 Criado: ${info.data_criacao}</div>
                <button class="btn btn-danger" onclick="abrirModalDelete('${cache}')">🗑️ Deletar</button>
            ` + "`" + `;
            
            grid.appendChild(card);
        }
    } catch (err) {
        document.getElementById('cacheGrid').innerHTML = '<div class="loading">Erro ao carregar caches</div>';
    }
}

function abrirModalDelete(cache) {
    cacheParaDeletar = cache;
    document.getElementById('cacheName').textContent = cache;
    document.getElementById('deleteModal').style.display = 'block';
}

function fecharModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

async function confirmarDelete() {
    try {
        const response = await fetch('/api/deletar-cache', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cache: cacheParaDeletar })
        });
        
        if (response.ok) {
            alert('Cache deletado com sucesso!');
            fecharModal();
            listarCaches();
        } else {
            const data = await response.json();
            alert('Erro ao deletar: ' + data.erro);
        }
    } catch (err) {
        alert('Erro ao deletar cache');
    }
}

listarCaches();
</script>
</body>
</html>
	`

	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	tmpl_parsed, _ := template.New("gerenciar").Parse(tmpl)
	tmpl_parsed.Execute(w, nil)
}
