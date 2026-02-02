document.addEventListener('DOMContentLoaded', () => {
    const amountInput = document.getElementById('amount');
    const fromSelect = document.getElementById('from-currency');
    const toSelect = document.getElementById('to-currency');
    const resultValue = document.getElementById('result-value');
    const rateInfo = document.getElementById('rate-info');
    const lastUpdated = document.getElementById('last-updated');
    const swapBtn = document.getElementById('swap-btn');
    const copyBtn = document.getElementById('copy-result-btn');
    const saveHistoryBtn = document.getElementById('save-history-btn');
    const historySection = document.getElementById('history-section');
    const historyList = document.getElementById('history-list');
    const clearHistoryBtn = document.getElementById('clear-history-btn');

    // Variabilă globală pentru datele cursului
    let exchangeData = null;
    let conversionHistory = JSON.parse(localStorage.getItem('currencyHistory')) || [];

    async function loadRates() {
        try {
            // Încărcăm fișierul local
            const response = await fetch('rates.json?v=' + new Date().getTime());
            if (!response.ok) throw new Error('Nu am putut încărca ratele');
            
            exchangeData = await response.json();
            
            if (exchangeData.date) {
                lastUpdated.textContent = `Curs oficial BNM din data: ${exchangeData.date}`;
            }

            calculate();
            renderHistory();

        } catch (error) {
            console.error('Eroare la încărcarea cursurilor:', error);
            resultValue.textContent = "Eroare";
            rateInfo.textContent = "Se încarcă cursurile..."; 
        }
    }

    function calculate() {
        if (!exchangeData || !exchangeData.rates) return;

        const amount = parseFloat(amountInput.value);
        const from = fromSelect.value;
        const to = toSelect.value;

        if (isNaN(amount)) {
            resultValue.textContent = "0.00";
            return;
        }

        const rateFrom = exchangeData.rates[from]; 
        const rateTo = exchangeData.rates[to];

        if (!rateFrom || !rateTo) {
            resultValue.textContent = "---";
            return;
        }

        const amountInMDL = amount * rateFrom;
        const result = amountInMDL / rateTo;

        resultValue.style.opacity = '1';
        
        // Use toFixed(2) to ensure dot separator, not comma
        const formattedResult = result.toFixed(2);
        resultValue.textContent = `${formattedResult} ${to.toUpperCase()}`;

        const exchangeRate = rateFrom / rateTo;

        rateInfo.textContent = `1 ${from.toUpperCase()} = ${exchangeRate.toFixed(4)} ${to.toUpperCase()}`;
    }

    // --- History Functions ---

    function renderHistory() {
        if (conversionHistory.length === 0) {
            historySection.style.display = 'none';
            return;
        }
        
        historySection.style.display = 'block';
        historyList.innerHTML = '';

        conversionHistory.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'history-item';
            
            li.innerHTML = `
                <div class="history-details">
                    <strong>${item.amount} ${item.from}</strong> ➔ <strong>${item.result} ${item.to}</strong>
                    <br><small style="color:#999">${item.date}</small>
                </div>
                <div class="history-actions">
                    <button class="history-copy-btn" title="Copiază valoarea" data-text="${item.result}">
                         📋
                    </button>
                    <button class="history-del-btn" title="Șterge" data-index="${index}">
                         ✕
                    </button>
                </div>
            `;
            historyList.appendChild(li);
        });

        // Add event listeners for dynamic buttons
        document.querySelectorAll('.history-copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const text = e.target.closest('button').dataset.text;
                copyToClipboard(text);
            });
        });

        document.querySelectorAll('.history-del-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.closest('button').dataset.index);
                deleteHistoryItem(index);
            });
        });
    }

    function addToHistory() {
        if (!exchangeData) return;
        
        const amount = amountInput.value;
        const from = fromSelect.value.toUpperCase();
        const to = toSelect.value.toUpperCase();
        
        // Extract plain number code for calculator compatibility
        const resultText = resultValue.textContent.split(' ')[0];

        // Evităm duplicatele consecutive
        if (conversionHistory.length > 0) {
            const last = conversionHistory[0];
            if (last.amount === amount && last.from === from && last.to === to) return;
        }

        const newItem = {
            amount: amount,
            from: from,
            to: to,
            result: resultText,
            date: new Date().toLocaleTimeString('ro-MD', { hour: '2-digit', minute: '2-digit' })
        };

        conversionHistory.unshift(newItem); // Adăugăm la început
        if (conversionHistory.length > 10) conversionHistory.pop(); // Păstrăm doar ultimele 10

        localStorage.setItem('currencyHistory', JSON.stringify(conversionHistory));
        renderHistory();
    }

    function deleteHistoryItem(index) {
        conversionHistory.splice(index, 1);
        localStorage.setItem('currencyHistory', JSON.stringify(conversionHistory));
        renderHistory();
    }

    async function copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            // Optional: Visual feedback
            const originalText = copyBtn.innerHTML;
            /* Simple feedback on main copy button logic could be improved, 
               but essentially the browser handles copy permissions. */
        } catch (err) {
            console.error('Failed to copy: ', err);
        }
    }

    // --- Event Listeners ---

    amountInput.addEventListener('input', calculate);
    fromSelect.addEventListener('change', calculate);
    toSelect.addEventListener('change', calculate);

    swapBtn.addEventListener('click', () => {
        const temp = fromSelect.value;
        fromSelect.value = toSelect.value;
        toSelect.value = temp;
        calculate();
    });

    copyBtn.addEventListener('click', () => {
        // Copiază doar numărul (fără valută)
        const textToCopy = resultValue.textContent.split(' ')[0];
        copyToClipboard(textToCopy);
        
        // Mic feedback vizual
        const originalHTML = copyBtn.innerHTML;

        copyBtn.innerHTML = '<span style="color:green">✓</span>';
        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
        }, 1000);
    });

    saveHistoryBtn.addEventListener('click', () => {
        addToHistory();
    });

    clearHistoryBtn.addEventListener('click', () => {
        conversionHistory = [];
        localStorage.removeItem('currencyHistory');
        renderHistory();
    });

    // Pornire
    loadRates();
});
