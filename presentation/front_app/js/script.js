// presentation/front_app/js/script.js

document.addEventListener("DOMContentLoaded", function () {
    const chatInput = document.getElementById('chatInput');
    const resultDiv = document.getElementById('result');
    const llmDropdown = document.getElementById('llmDropdown');
    let currentLlm = 'llm_studio';   // valor por defecto

    document.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', e => {
            e.preventDefault();
            currentLlm = item.dataset.llm;
            llmDropdown.textContent = item.textContent;
        });
    });

    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') sendPrompt();
    });

    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            chatInput.value = this.dataset.prompt;
            sendPrompt();
        });
    });

    let sending = false;

    function sendPrompt() {
        if (sending) return;
        const prompt = chatInput.value.trim();
        if (!prompt) return;

        sending = true;
        chatInput.disabled = true;
        resultDiv.innerHTML = '<em>Procesando…</em>';

        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt, llm_type: currentLlm })
        })
            .then(resp => resp.json())
            .then(data => {
                sending = false;
                chatInput.disabled = false;
                // Añade aquí:
                console.log("Respuesta recibida del backend:", data);
                // --- EXITO ---
                if (data.status === "success" && data.data && data.data.status === "SUCCESS" && Array.isArray(data.data.products)) {
                    renderProductsTable(data.data.products, data.data.message || "Operación realizada correctamente.");
                }
                // --- ERROR DEVUELTO POR BACKEND ---
                else if (data.status === "success" && data.data && data.data.status === "ERROR") {
                    renderError(data.data.message || "Error de procesamiento.");
                }
                // --- ERROR HTTP ---
                else if (data.status === "error") {
                    renderError(data.message || "Error de comunicación con el servidor");
                }
                // --- CUALQUIER OTRO CASO ---
                else {
                    renderError("Error de comunicación con el servidor");
                }
            })
            .catch(err => {
                sending = false;
                chatInput.disabled = false;
                renderError("Error de comunicación con el servidor");
            });
    }

    function renderProductsTable(products, successMsg) {
        // Cabecera
        let html = `
        <div class="excel-table-container mt-3">
        

        <table id="tablaProductos" class="tech-table">
            <thead>
                <tr>
                    <th>Datos scrapeados</th>
                </tr>
                <tr>
                    <th>Descripción</th>
                    <th>Precio</th>
                    <th>SKU</th>
                </tr>
            </thead>
            <tbody>
        `;
        // Filas editables
        products.forEach((p, idx) => {
            html += `
                <tr>
                    <td contenteditable="true" spellcheck="false">${escapeHtml(p.description)}</td>
                    <td contenteditable="true" spellcheck="false">${escapeHtml(p.price)}</td>
                    <td contenteditable="true" spellcheck="false">${escapeHtml(p.sku)}</td>
                </tr>
            `;
        });
        html += `
            </tbody>
        </table>
            <div class="tech-table-buttons">
                <button class="tech-btn" id="copyTableBtn">Copiar tabla</button>
                <button class="tech-btn" id="downloadCsvBtn">Descargar CSV</button>
            </div>
        </div>
        `;
        resultDiv.innerHTML = html;

        document.getElementById("copyTableBtn").onclick = function () {
            copyTableToClipboard();
        };
        document.getElementById("downloadCsvBtn").onclick = function () {
            downloadTableAsCsv();
        };
    }

    function renderError(msg) {
        resultDiv.innerHTML = `<div class="alert alert-danger"><b>Error:</b> ${escapeHtml(msg)}</div>`;
    }

    function escapeHtml(text) {
        if (typeof text !== "string") return "";
        return text.replace(/[&<>"'`]/g, function (chr) {
            return ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;',
                '`': '&#96;'
            })[chr];
        });
    }

    function copyTableToClipboard() {
        const table = resultDiv.querySelector("table");
        if (!table) return;
        let text = "";
        // Header
        text += Array.from(table.querySelectorAll("thead th")).map(th => th.textContent.trim()).join("\t") + "\n";
        // Body
        table.querySelectorAll("tbody tr").forEach(tr => {
            text += Array.from(tr.querySelectorAll("td")).map(td => td.textContent.trim()).join("\t") + "\n";
        });

        navigator.clipboard.writeText(text).then(function () {
            showTempAlert("Tabla copiada al portapapeles", "success");
        }, function () {
            showTempAlert("No se pudo copiar la tabla", "danger");
        });
    }

    function downloadTableAsCsv() {
        const table = resultDiv.querySelector("table");
        if (!table) return;
        let csv = "";
        // Header
        csv += Array.from(table.querySelectorAll("thead th")).map(th => `"${th.textContent.trim().replace(/"/g, '""')}"`).join(",") + "\n";
        // Body
        table.querySelectorAll("tbody tr").forEach(tr => {
            csv += Array.from(tr.querySelectorAll("td")).map(td => `"${td.textContent.trim().replace(/"/g, '""')}"`).join(",") + "\n";
        });
        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "productos.csv";
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    }

    function showTempAlert(message, type = "info") {
        let alert = document.createElement("div");
        alert.className = `alert alert-${type} mt-2`;
        alert.textContent = message;
        resultDiv.appendChild(alert);
        setTimeout(() => {
            if (alert.parentNode) alert.parentNode.removeChild(alert);
        }, 2000);
    }

    // Modal de información
    document.getElementById('openInfoModal').onclick = function () {
        document.getElementById('modalOverlay').style.display = 'flex';
    };
    document.getElementById('closeInfoModal').onclick = function () {
        document.getElementById('modalOverlay').style.display = 'none';
    };
    document.getElementById('modalOverlay').onclick = function (e) {
        if (e.target === this) this.style.display = 'none';
    };

    // Modal de instrucciones
    document.getElementById('openInstructionsModal').onclick = function () {
        document.getElementById('instructionsModalOverlay').style.display = 'flex';
    };
    document.getElementById('closeInstructionsModal').onclick = function () {
        document.getElementById('instructionsModalOverlay').style.display = 'none';
    };
    document.getElementById('instructionsModalOverlay').onclick = function (e) {
        if (e.target === this) this.style.display = 'none';
    };

    // Modal README/Arquitectura
    document.getElementById('openReadmeModal').onclick = function () {
        const modal = document.getElementById('readmeModalOverlay');
        const contentDiv = document.getElementById('readmeContent');
        contentDiv.innerHTML = '<em>Cargando README...</em>';
        modal.style.display = 'flex';

        fetch('/readme')
            .then(resp => resp.json())
            .then(data => {
                if (data.status === "success" && data.content) {
                    contentDiv.innerHTML = renderMarkdownToHtml(data.content);
                } else {
                    contentDiv.innerHTML = '<div class="alert alert-danger">No se pudo cargar el README.md</div>';
                }
            })
            .catch(() => {
                contentDiv.innerHTML = '<div class="alert alert-danger">No se pudo cargar el README.md</div>';
            });
    };
    document.getElementById('closeReadmeModal').onclick = function () {
        document.getElementById('readmeModalOverlay').style.display = 'none';
    };
    document.getElementById('readmeModalOverlay').onclick = function (e) {
        if (e.target === this) this.style.display = 'none';
    };

    /**
     * Renderiza markdown a HTML básico compatible con estilos .readme-style
     */
    function renderMarkdownToHtml(md) {
        // Transforma cabeceras
        md = md.replace(/^### (.*)$/gm, '<h3>$1</h3>')
            .replace(/^## (.*)$/gm, '<h2>$1</h2>')
            .replace(/^# (.*)$/gm, '<h1>$1</h1>');
        // Bold, italics, code y blockquotes básicos
        md = md.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
            .replace(/\*(.*?)\*/g, '<i>$1</i>')
            .replace(/`([^`\n]+)`/g, '<code>$1</code>')
            .replace(/^> (.*)$/gm, '<blockquote>$1</blockquote>');
        // Lists
        md = md.replace(/^\s*[-*+] (.*)$/gm, '<li>$1</li>');
        // Ordered lists
        md = md.replace(/^\s*\d+\. (.*)$/gm, '<li>$1</li>');
        // Tables (simplificada)
        md = md.replace(/^\|(.+)\|\n\|([-:\s|]+)\|\n((?:\|.*\|\n)+)/gm, function (_, head, sep, rows) {
            var ths = head.split('|').map(e => '<th>' + e.trim() + '</th>').join('');
            var trs = rows.trim().split('\n').map(r => {
                var tds = r.replace(/^\|/, '').replace(/\|$/, '').split('|').map(e => '<td>' + e.trim() + '</td>').join('');
                return '<tr>' + tds + '</tr>';
            }).join('');
            return `<table class="readme-table"><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table>`;
        });
        // Paragraphs
        md = md.replace(/\n{2,}/g, '</p><p>');
        md = `<p>${md}</p>`;
        // Unordered/ordered lists cleanup
        md = md.replace(/(<\/li>\s*)+(?!<li>)/g, '</li></ul>')
            .replace(/(<li>)/g, '<ul>$1')
            .replace(/(<ul><ul>)/g, '<ul>')
            .replace(/<\/ul><\/ul>/g, '</ul>');
        // Clean up double <ul>s
        return md;
    }

    // Modal de retos y aprendizaje
    document.getElementById('openChallengesModal').onclick = function () {
        document.getElementById('challengesModalOverlay').style.display = 'flex';
    };
    document.getElementById('closeChallengesModal').onclick = function () {
        document.getElementById('challengesModalOverlay').style.display = 'none';
    };
    document.getElementById('challengesModalOverlay').onclick = function (e) {
        if (e.target === this) this.style.display = 'none';
    };

});
