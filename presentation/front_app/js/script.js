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
        let html = `<em>${successMsg}</em>
        <div class="excel-table-container mt-3">
        <div>Datos scrappeados</div>

        <table id="tablaProductos" class="tech-table">
            <thead>
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
    document.getElementById('openInfoModal').onclick = function() {
        document.getElementById('modalOverlay').style.display = 'flex';
    };
    document.getElementById('closeInfoModal').onclick = function() {
        document.getElementById('modalOverlay').style.display = 'none';
    };
    document.getElementById('modalOverlay').onclick = function(e) {
        if(e.target === this) this.style.display = 'none';
    };

    // Modal de instrucciones
    document.getElementById('openInstructionsModal').onclick = function() {
        document.getElementById('instructionsModalOverlay').style.display = 'flex';
    };
    document.getElementById('closeInstructionsModal').onclick = function() {
        document.getElementById('instructionsModalOverlay').style.display = 'none';
    };
    document.getElementById('instructionsModalOverlay').onclick = function(e) {
        if(e.target === this) this.style.display = 'none';
    };


});
