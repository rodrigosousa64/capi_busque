document.addEventListener('DOMContentLoaded', function() {
    const perfilForm = document.getElementById('perfil-form');
    if (perfilForm) {
        const checkboxes = perfilForm.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => {
            cb.addEventListener('change', () => {
                perfilForm.submit();
            });
        });
    }

    const inputs = [
        document.getElementById('acertos_mat'),
        document.getElementById('acertos_nat'),
        document.getElementById('acertos_hum'),
        document.getElementById('acertos_lin'),
        document.getElementById('nota_redacao'),
        document.getElementById('bonus_regional')
    ];

    // Lógica TRI (baseada nos dados oficiais do ENEM 2024)
    function calcBase(x, min, max, delta, a, b, c) {
        if (x <= 0) return min;
        let t = x / 45;
        return min + delta * (a * t + b * Math.pow(t, 2) + c * Math.pow(t, 3));
    }

    function calcVariancia(x, maxVar) {
        if (x <= 0 || x >= 45) return 0;
        let t = x / 45;
        return 4 * t * (1 - t) * maxVar;
    }

    function getScores(x, min, max, delta, a, b, c, maxVar) {
        let media = calcBase(x, min, max, delta, a, b, c);
        let v = calcVariancia(x, maxVar);
        return {
            media: media,
            otimista: Math.min(media + v, max),
            pessimista: Math.max(media - v, min)
        };
    }

    function calcMat(x) { return getScores(x, 334.30, 961.90, 627.60, 0.34, 0, 0.66, 120); }
    function calcNat(x) { return getScores(x, 308.10, 867.20, 559.10, 0.61, 0.39, 0, 100); }
    function calcHum(x) { return getScores(x, 283.80, 819.70, 535.90, 0.57, 0.43, 0, 80); }
    function calcLin(x) { return getScores(x, 294.10, 795.80, 501.70, 0.51, 0, 0.49, 70); }

    function atualizarCalculo() {
        let matEl = document.getElementById('acertos_mat');
        if (!matEl) return; // Só roda se a calculadora existir

        let acertos_mat = Math.min(parseInt(matEl.value) || 0, 45);
        let acertos_nat = Math.min(parseInt(document.getElementById('acertos_nat').value) || 0, 45);
        let acertos_hum = Math.min(parseInt(document.getElementById('acertos_hum').value) || 0, 45);
        let acertos_lin = Math.min(parseInt(document.getElementById('acertos_lin').value) || 0, 45);
        let redacao = Math.min(parseFloat(document.getElementById('nota_redacao').value) || 0, 1000);
        let bonus = document.getElementById('bonus_regional').checked;

        let s_mat = calcMat(acertos_mat);
        let s_nat = calcNat(acertos_nat);
        let s_hum = calcHum(acertos_hum);
        let s_lin = calcLin(acertos_lin);

        document.getElementById('nota_mat').innerHTML = `Média: ${s_mat.media.toFixed(1)}<br><span style="font-size: 0.65rem; color: #8b949e;">[Otimista: ${s_mat.otimista.toFixed(0)}]</span>`;
        document.getElementById('nota_nat').innerHTML = `Média: ${s_nat.media.toFixed(1)}<br><span style="font-size: 0.65rem; color: #8b949e;">[Otimista: ${s_nat.otimista.toFixed(0)}]</span>`;
        document.getElementById('nota_hum').innerHTML = `Média: ${s_hum.media.toFixed(1)}<br><span style="font-size: 0.65rem; color: #8b949e;">[Otimista: ${s_hum.otimista.toFixed(0)}]</span>`;
        document.getElementById('nota_lin').innerHTML = `Média: ${s_lin.media.toFixed(1)}<br><span style="font-size: 0.65rem; color: #8b949e;">[Otimista: ${s_lin.otimista.toFixed(0)}]</span>`;
        document.getElementById('nota_red').innerHTML = `Nota: ${redacao.toFixed(1)}`;

        let media_simples = (s_mat.media + s_nat.media + s_hum.media + s_lin.media + redacao) / 5;
        let media_otimista = (s_mat.otimista + s_nat.otimista + s_hum.otimista + s_lin.otimista + redacao) / 5;
        
        let final_media = bonus ? media_simples * 1.10 : media_simples;
        let final_otimista = bonus ? media_otimista * 1.10 : media_otimista;

        document.getElementById('media_final').innerHTML = `
            ${final_media.toFixed(2)}
            <div style="font-size: 0.8rem; color: #8b949e; margin-top: 8px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                <span style="color: #39ff14;">Cenário Otimista: ${final_otimista.toFixed(2)}</span>
            </div>
            <div style="font-size: 0.65rem; color: #8b949e; margin-top: 8px; line-height: 1.3; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: left; padding: 8px; background: rgba(0,0,0,0.3); border-left: 2px solid #58a6ff;">
                <strong>[ Variação TRI ]</strong> A TRI avalia a coerência. O <strong>Cenário Otimista</strong> projeta sua nota caso você não tenha "chutado" as fáceis.
            </div>
        `;
        
        avaliarFavoritos(final_otimista);
    }

    function avaliarFavoritos(media_final) {
        if(media_final <= 0) return;
        
        const cards = document.querySelectorAll('.fav-card');
        cards.forEach(card => {
            let minScore = parseFloat(card.getAttribute('data-min-score'));
            if (!isNaN(minScore) && minScore > 0) {
                if (media_final >= minScore) {
                    card.classList.add('passed');
                    card.classList.remove('failed');
                } else {
                    card.classList.add('failed');
                    card.classList.remove('passed');
                }
            }
        });
    }

    inputs.forEach(input => {
        if (input) {
            input.addEventListener('input', atualizarCalculo);
            input.addEventListener('change', atualizarCalculo);
        }
    });

    if (document.getElementById('acertos_mat')) {
        atualizarCalculo();
    }
});
