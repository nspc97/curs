document.addEventListener('DOMContentLoaded', () => {
    const amountInput = document.getElementById('amount');
    const fromSelect = document.getElementById('from-currency');
    const toSelect = document.getElementById('to-currency');
    const resultValue = document.getElementById('result-value');
    const rateInfo = document.getElementById('rate-info');
    const lastUpdated = document.getElementById('last-updated');
    const swapBtn = document.getElementById('swap-btn');

    // Variabilă globală pentru datele cursului
    let exchangeData = null;

    async function loadRates() {
        try {
            // Încărcăm fișierul local generat de scriptul Python
            // Cache busting cu ?v=timestamp pentru a nu primi versiunea veche din cache-ul browserului
            const response = await fetch('rates.json?v=' + new Date().getTime());
            if (!response.ok) throw new Error('Nu am putut încărca ratele');
            
            exchangeData = await response.json();
            
            // Actualizăm data care vine de la BNM
            if (exchangeData.date) {
                lastUpdated.textContent = `Curs oficial BNM din data: ${exchangeData.date}`;
            }

            // Facem primul calcul după ce avem datele
            calculate();

        } catch (error) {
            console.error('Eroare la încărcarea cursurilor:', error);
            resultValue.textContent = "Eroare";
            rateInfo.textContent = "Se încarcă cursurile..."; 
            // Putem încerca din nou sau afișa un mesaj user-friendly
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

        // Obținem ratele față de MDL (Leul Moldovenesc)
        // Exemplu: eur = 19.50 (înseamnă 1 EUR = 19.50 MDL)
        const rateFrom = exchangeData.rates[from]; 
        const rateTo = exchangeData.rates[to];

        if (!rateFrom || !rateTo) {
            resultValue.textContent = "---";
            return;
        }

        // Calculăm
        // 1. Convertim suma "input" în MDL (valoare * cursul_valutei_sursă)
        const amountInMDL = amount * rateFrom;
        
        // 2. Convertim MDL în moneda "output" (valoare_mdl / cursul_valutei_destinație)
        const result = amountInMDL / rateTo;

        // Afișăm rezultatul
        resultValue.style.opacity = '1';
        
        const formatter = new Intl.NumberFormat('ro-MD', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        resultValue.textContent = `${formatter.format(result)} ${to.toUpperCase()}`;

        // Afișăm cursul de schimb unitar (1 X = ? Y)
        const exchangeRate = rateFrom / rateTo;
        rateInfo.textContent = `1 ${from.toUpperCase()} = ${exchangeRate.toFixed(4)} ${to.toUpperCase()}`;
    }

    // Event Listeners
    amountInput.addEventListener('input', calculate);
    fromSelect.addEventListener('change', calculate);
    toSelect.addEventListener('change', calculate);

    swapBtn.addEventListener('click', () => {
        const temp = fromSelect.value;
        fromSelect.value = toSelect.value;
        toSelect.value = temp;
        calculate();
    });

    // Pornire
    loadRates();
});
