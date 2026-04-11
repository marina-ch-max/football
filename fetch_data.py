<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Футбольные Прогнозы</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #0d1117; --bg2: #161b22; --card: #1c2333; --hover: #242d3d;
            --green: #00e676; --red: #ff5252; --yellow: #ffd740; --blue: #448aff;
            --text: #e6edf3; --text2: #8b949e; --border: #30363d; --radius: 12px;
        }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }
        .container { max-width: 900px; margin: 0 auto; padding: 16px; }
        h1 { font-size: 24px; margin-bottom: 8px; }

        /* Buttons */
        .btn { padding: 10px 20px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; }
        .btn-primary { background: var(--blue); color: #fff; }
        .btn-primary:hover { background: #5c9aff; }
        .btn-green { background: var(--green); color: #000; }
        .btn-green:hover { background: #33eb91; }
        .btn-sm { padding: 6px 14px; font-size: 13px; }

        /* Header */
        .header { display: flex; align-items: center; justify-content: space-between; padding: 16px 0; flex-wrap: wrap; gap: 8px; }
        .header-right { font-size: 12px; color: var(--text2); }

        /* Leagues */
        .leagues { display: flex; gap: 6px; overflow-x: auto; padding: 8px 0 16px; -webkit-overflow-scrolling: touch; }
        .leagues::-webkit-scrollbar { height: 4px; }
        .leagues::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
        .league-btn { padding: 8px 16px; background: var(--bg2); border: 1px solid var(--border); border-radius: 20px; color: var(--text2); cursor: pointer; white-space: nowrap; font-size: 13px; transition: all 0.2s; }
        .league-btn:hover { background: var(--card); color: var(--text); }
        .league-btn.active { background: var(--blue); border-color: var(--blue); color: #fff; }

        /* Matches */
        .matches { display: flex; flex-direction: column; gap: 8px; }
        .match-card { display: flex; align-items: center; gap: 12px; padding: 16px; background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); cursor: pointer; transition: all 0.2s; }
        .match-card:hover { background: var(--card); border-color: var(--blue); }
        .match-date { font-size: 12px; color: var(--text2); min-width: 50px; text-align: center; line-height: 1.3; }
        .match-teams { flex: 1; display: flex; flex-direction: column; gap: 6px; }
        .match-team { display: flex; align-items: center; gap: 8px; font-size: 14px; }
        .match-team img { width: 24px; height: 24px; object-fit: contain; }

        /* Modal */
        .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 100; display: flex; align-items: flex-start; justify-content: center; overflow-y: auto; padding: 20px; }
        .modal { background: var(--bg); border: 1px solid var(--border); border-radius: var(--radius); width: 100%; max-width: 700px; margin: 20px auto; animation: slideUp 0.3s ease; }
        @keyframes slideUp { from { transform: translateY(30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .modal-header { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px; border-bottom: 1px solid var(--border); }
        .modal-header h2 { font-size: 16px; color: var(--text); margin: 0; }
        .modal-close { background: none; border: none; color: var(--text2); font-size: 24px; cursor: pointer; padding: 4px 8px; }
        .modal-close:hover { color: var(--text); }
        .modal-body { padding: 24px; }

        /* Prediction sections */
        .pred-teams { display: flex; align-items: center; justify-content: center; gap: 24px; padding: 20px; margin-bottom: 20px; background: var(--bg2); border-radius: var(--radius); }
        .pred-team { text-align: center; }
        .pred-team img { width: 56px; height: 56px; object-fit: contain; margin-bottom: 8px; }
        .pred-team-name { font-size: 14px; font-weight: 600; }
        .pred-vs { font-size: 20px; font-weight: 700; color: var(--text2); }

        .pred-section { margin-bottom: 20px; }
        .pred-section-title { font-size: 14px; font-weight: 700; color: var(--text2); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }

        .pred-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; }
        .pred-label { font-size: 14px; color: var(--text2); }
        .pred-value { font-size: 14px; font-weight: 600; }

        .prob-bar { display: flex; align-items: center; gap: 8px; margin: 6px 0; }
        .prob-bar-track { flex: 1; height: 8px; background: var(--bg); border-radius: 4px; overflow: hidden; }
        .prob-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
        .prob-bar-label { font-size: 13px; min-width: 45px; text-align: right; font-weight: 600; }
        .prob-high { color: var(--green); }
        .prob-mid { color: var(--yellow); }
        .prob-low { color: var(--red); }

        .form-row { display: flex; gap: 4px; }
        .form-item { width: 28px; height: 28px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; }
        .form-W { background: #1b5e20; color: var(--green); }
        .form-D { background: #4e342e; color: var(--yellow); }
        .form-L { background: #b71c1c; color: var(--red); }

        .h2h-match { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
        .h2h-match:last-child { border-bottom: none; }
        .h2h-score { font-weight: 700; min-width: 40px; text-align: center; }
        .h2h-date { color: var(--text2); min-width: 80px; }
        .h2h-teams { flex: 1; }

        .shots-table { width: 100%; border-collapse: collapse; font-size: 13px; }
        .shots-table th { text-align: left; padding: 8px; color: var(--text2); font-weight: 600; border-bottom: 1px solid var(--border); }
        .shots-table td { padding: 8px; border-bottom: 1px solid var(--border); }
        .shots-table tr:last-child td { border-bottom: none; }

        /* Odds comparison table */
        .odds-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }
        .odds-table th { text-align: center; padding: 8px 4px; color: var(--text2); font-weight: 600; border-bottom: 1px solid var(--border); font-size: 12px; }
        .odds-table th:first-child { text-align: left; }
        .odds-table td { padding: 8px 4px; border-bottom: 1px solid var(--border); text-align: center; }
        .odds-table td:first-child { text-align: left; color: var(--text2); font-size: 12px; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .odds-table tr:last-child td { border-bottom: none; }
        .odds-table tr.odds-best-row td { font-weight: 700; border-top: 2px solid var(--border); }
        .odds-best { color: var(--green); font-weight: 700; }

        /* Arbitrage alert */
        .arb-alert { display: flex; align-items: center; gap: 10px; padding: 14px; background: #1a2e1a; border: 1px solid var(--green); border-radius: 8px; margin-bottom: 12px; }
        .arb-alert-icon { font-size: 22px; }
        .arb-alert-text { flex: 1; }
        .arb-alert-title { font-size: 14px; font-weight: 700; color: var(--green); }
        .arb-alert-detail { font-size: 12px; color: var(--text2); margin-top: 2px; }
        .arb-near { background: #2e2a1a; border-color: var(--yellow); }
        .arb-near .arb-alert-title { color: var(--yellow); }
        .arb-normal { padding: 8px 12px; background: var(--card); border-radius: 8px; font-size: 12px; color: var(--text2); margin-bottom: 12px; }

        /* Value bet */
        .value-bet { background: #1a2e1a; border: 1px solid var(--green); border-radius: 8px; padding: 10px 14px; margin: 6px 0; }
        .value-bet-label { font-size: 11px; color: var(--green); text-transform: uppercase; letter-spacing: 1px; font-weight: 700; }
        .value-bet-text { font-size: 13px; color: var(--text); margin-top: 4px; }
        .value-bet-edge { font-weight: 700; color: var(--green); }

        /* Odds freshness */
        .odds-fresh { font-size: 11px; color: var(--text2); text-align: right; margin-top: 4px; }

        /* Loading */
        .loading { text-align: center; padding: 40px; color: var(--text2); }
        .spinner { display: inline-block; width: 32px; height: 32px; border: 3px solid var(--border); border-top-color: var(--blue); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 12px; }
        @keyframes spin { to { transform: rotate(360deg); } }

        .error-msg { padding: 16px; background: #2d1515; border: 1px solid var(--red); border-radius: 8px; color: var(--red); font-size: 14px; margin: 12px 0; }
        .empty-msg { text-align: center; padding: 40px; color: var(--text2); font-size: 14px; }
        .info-msg { padding: 12px; background: var(--card); border: 1px solid var(--border); border-radius: 8px; color: var(--text2); font-size: 12px; margin: 8px 0; }

        @media (max-width: 600px) {
            .container { padding: 8px; }
            .match-card { flex-wrap: wrap; }
            .pred-teams { gap: 12px; flex-wrap: wrap; }
            .pred-team img { width: 40px; height: 40px; }
            .modal { margin: 8px; }
            .modal-body { padding: 16px; }
            .pred-row { flex-wrap: wrap; gap: 4px; }
        }
    </style>
</head>
<body>
    <div id="app"></div>

    <script>
    // ==================== CONFIG ====================
    const DATA_BASE = './data';
    const LEAGUES = [
        { code: 'RPL', name: '\u0420\u041F\u041B',              flag: '\u{1F1F7}\u{1F1FA}' },
        { code: 'PL',  name: '\u0410\u041F\u041B',              flag: '\u{1F1EC}\u{1F1E7}' },
        { code: 'PD',  name: '\u041B\u0430 \u041B\u0438\u0433\u0430',           flag: '\u{1F1EA}\u{1F1F8}' },
        { code: 'SA',  name: '\u0421\u0435\u0440\u0438\u044F \u0410',            flag: '\u{1F1EE}\u{1F1F9}' },
        { code: 'BL1', name: '\u0411\u0443\u043D\u0434\u0435\u0441\u043B\u0438\u0433\u0430',         flag: '\u{1F1E9}\u{1F1EA}' },
        { code: 'FL1', name: '\u041B\u0438\u0433\u0430 1',             flag: '\u{1F1EB}\u{1F1F7}' },
        { code: 'CL',  name: '\u041B\u0438\u0433\u0430 \u0427\u0435\u043C\u043F\u0438\u043E\u043D\u043E\u0432',     flag: '\u2B50' },
    ];

    // ==================== STATE ====================
    const state = { currentLeague: null, leagueData: {}, oddsData: {} };

    // ==================== DATA LOADING ====================
    async function loadLeague(code) {
        if (state.leagueData[code]) return state.leagueData[code];
        const res = await fetch(`${DATA_BASE}/${code}.json`);
        if (!res.ok) throw new Error(`\u041D\u0435\u0442 \u0434\u0430\u043D\u043D\u044B\u0445 \u0434\u043B\u044F ${code}`);
        const data = await res.json();
        state.leagueData[code] = data;
        return data;
    }

    async function loadOdds(code) {
        if (state.oddsData[code]) return state.oddsData[code];
        try {
            const res = await fetch(`${DATA_BASE}/odds_${code}.json`);
            if (!res.ok) return null;
            const data = await res.json();
            state.oddsData[code] = data;
            return data;
        } catch (e) {
            return null;
        }
    }

    function findOddsForMatch(match, oddsData) {
        if (!oddsData || !oddsData.events) return null;
        const byId = oddsData.events.find(e => e.matchId === match.id);
        if (byId) return byId;
        const matchDate = new Date(match.utcDate).getTime();
        const hName = match.homeTeam.name.toLowerCase();
        const aName = match.awayTeam.name.toLowerCase();
        return oddsData.events.find(e => {
            const oddsDate = new Date(e.commenceTime).getTime();
            if (Math.abs(matchDate - oddsDate) > 86400000) return false;
            const oh = e.homeTeam.toLowerCase();
            const oa = e.awayTeam.toLowerCase();
            return (oh.includes(hName) || hName.includes(oh)) &&
                   (oa.includes(aName) || aName.includes(oa));
        }) || null;
    }

    // ==================== MATH (Dixon-Coles + Elo) ====================
    function factorial(n) { let r = 1; for (let i = 2; i <= n; i++) r *= i; return r; }
    function poisson(lambda, k) {
        if (lambda <= 0) return k === 0 ? 1 : 0;
        return Math.pow(lambda, k) * Math.exp(-lambda) / factorial(k);
    }

    // Dixon-Coles rho correction for low scores (0-0, 0-1, 1-0, 1-1)
    function dixonColesRho(x, y, hLam, aLam, rho) {
        if (x === 0 && y === 0) return 1 - hLam * aLam * rho;
        if (x === 1 && y === 0) return 1 + aLam * rho;
        if (x === 0 && y === 1) return 1 + hLam * rho;
        if (x === 1 && y === 1) return 1 - rho;
        return 1;
    }

    // Dixon-Coles joint probability P(home=x, away=y)
    function dcProb(x, y, hLam, aLam, rho) {
        return poisson(hLam, x) * poisson(aLam, y) * dixonColesRho(x, y, hLam, aLam, rho);
    }

    // Score matrix up to maxGoals
    function scoreMatrix(hLam, aLam, rho, maxGoals) {
        const m = [];
        for (let h = 0; h <= maxGoals; h++) {
            m[h] = [];
            for (let a = 0; a <= maxGoals; a++) {
                m[h][a] = dcProb(h, a, hLam, aLam, rho);
            }
        }
        return m;
    }

    function probOver(hLam, aLam, threshold, rho) {
        rho = rho || 0;
        const max = Math.max(threshold + 3, 8);
        const mat = scoreMatrix(hLam, aLam, rho, max);
        let under = 0;
        for (let h = 0; h <= max; h++)
            for (let a = 0; a <= max; a++)
                if (h + a <= threshold) under += mat[h][a];
        return Math.min(Math.max(1 - under, 0), 1);
    }

    function probBTTS(hLam, aLam, rho) {
        rho = rho || 0;
        const max = 8;
        const mat = scoreMatrix(hLam, aLam, rho, max);
        let btts = 0;
        for (let h = 1; h <= max; h++)
            for (let a = 1; a <= max; a++)
                btts += mat[h][a];
        return btts;
    }

    // 1X2 probabilities from score matrix
    function prob1X2(hLam, aLam, rho) {
        const max = 8;
        const mat = scoreMatrix(hLam, aLam, rho, max);
        let p1 = 0, pX = 0, p2 = 0;
        for (let h = 0; h <= max; h++)
            for (let a = 0; a <= max; a++) {
                if (h > a) p1 += mat[h][a];
                else if (h === a) pX += mat[h][a];
                else p2 += mat[h][a];
            }
        return { p1, pX, p2 };
    }

    // Elo rating calculation from finished matches
    function calcElo(finishedMatches) {
        const elo = {};
        const K = 32;
        const sorted = [...finishedMatches].sort((a, b) => new Date(a.utcDate) - new Date(b.utcDate));
        for (const m of sorted) {
            const hId = m.homeTeam.id, aId = m.awayTeam.id;
            if (!elo[hId]) elo[hId] = 1500;
            if (!elo[aId]) elo[aId] = 1500;
            const hElo = elo[hId], aElo = elo[aId];
            const expected = 1 / (1 + Math.pow(10, (aElo - hElo - 65) / 400)); // 65 pts home advantage
            let actual;
            if (m.homeGoals > m.awayGoals) actual = 1;
            else if (m.homeGoals === m.awayGoals) actual = 0.5;
            else actual = 0;
            const goalDiff = Math.abs(m.homeGoals - m.awayGoals);
            const goalMult = goalDiff <= 1 ? 1 : goalDiff === 2 ? 1.5 : (1.75 + (goalDiff - 3) * 0.375);
            elo[hId] = hElo + K * goalMult * (actual - expected);
            elo[aId] = aElo + K * goalMult * ((1 - actual) - (1 - expected));
        }
        return elo;
    }

    // League-average attack/defense strengths (Dixon-Coles)
    function calcLeagueStats(standings) {
        let totalGF = 0, totalGA = 0, totalPlayed = 0;
        for (const s of standings) {
            totalGF += s.gf;
            totalGA += s.ga;
            totalPlayed += s.played;
        }
        const avgGoals = totalPlayed > 0 ? totalGF / totalPlayed : 1.3;
        return { avgGoals, totalPlayed };
    }

    // Estimate rho from league data (~-0.13 is typical)
    function estimateRho(avgGoals) {
        return Math.max(-0.2, Math.min(0, -0.05 - 0.03 * (3.0 - avgGoals)));
    }

    function probColor(p) { return p >= 0.65 ? 'prob-high' : p >= 0.40 ? 'prob-mid' : 'prob-low'; }
    function barColor(p) { return p >= 0.65 ? 'var(--green)' : p >= 0.40 ? 'var(--yellow)' : 'var(--red)'; }

    // ==================== HELPERS ====================
    function $(sel) { return document.querySelector(sel); }
    function formatDate(d) { return new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }); }
    function formatTime(d) { return new Date(d).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }); }
    function pct(v) { return Math.round(v * 100) + '%'; }

    function timeAgo(dateStr) {
        const diff = Date.now() - new Date(dateStr).getTime();
        const hours = Math.floor(diff / 3600000);
        if (hours < 1) return '\u0442\u043E\u043B\u044C\u043A\u043E \u0447\u0442\u043E';
        if (hours < 24) return `${hours} \u0447. \u043D\u0430\u0437\u0430\u0434`;
        const days = Math.floor(hours / 24);
        return `${days} \u0434\u043D. \u043D\u0430\u0437\u0430\u0434`;
    }

    // ==================== FORM CALCULATION ====================
    function calcForm(teamId, finishedMatches) {
        const results = [];
        const sorted = [...finishedMatches].sort((a, b) => new Date(b.utcDate) - new Date(a.utcDate));
        for (const m of sorted) {
            if (results.length >= 5) break;
            if (m.homeTeam.id === teamId) {
                if (m.homeGoals > m.awayGoals) results.push('W');
                else if (m.homeGoals === m.awayGoals) results.push('D');
                else results.push('L');
            } else if (m.awayTeam.id === teamId) {
                if (m.awayGoals > m.homeGoals) results.push('W');
                else if (m.awayGoals === m.homeGoals) results.push('D');
                else results.push('L');
            }
        }
        return results;
    }

    // ==================== MAIN ====================
    function renderMain() {
        $('#app').innerHTML = `
        <div class="container">
            <div class="header">
                <h1>\u0424\u0443\u0442\u0431\u043E\u043B\u044C\u043D\u044B\u0435 \u041F\u0440\u043E\u0433\u043D\u043E\u0437\u044B</h1>
                <div class="header-right" id="updateInfo"></div>
            </div>
            <div class="leagues" id="leagueTabs"></div>
            <div id="matchList"></div>
        </div>
        <div id="modalContainer"></div>`;
        renderLeagues();
        selectLeague(LEAGUES[0].code);
    }

    function renderLeagues() {
        $('#leagueTabs').innerHTML = LEAGUES.map(l =>
            `<button class="league-btn" data-code="${l.code}" onclick="selectLeague('${l.code}')">${l.flag} ${l.name}</button>`
        ).join('');
    }

    // ==================== FIXTURES ====================
    async function selectLeague(code) {
        state.currentLeague = code;
        document.querySelectorAll('.league-btn').forEach(b => {
            b.classList.toggle('active', b.dataset.code === code);
        });
        $('#matchList').innerHTML = '<div class="loading"><div class="spinner"></div><br>\u0417\u0430\u0433\u0440\u0443\u0437\u043A\u0430 \u043C\u0430\u0442\u0447\u0435\u0439...</div>';
        try {
            const data = await loadLeague(code);
            if (data.updated) {
                $('#updateInfo').textContent = '\u041E\u0431\u043D\u043E\u0432\u043B\u0435\u043D\u043E: ' + timeAgo(data.updated);
            }
            renderFixtures(data.matches || [], code);
        } catch (e) {
            $('#matchList').innerHTML = `<div class="error-msg">\u041E\u0448\u0438\u0431\u043A\u0430 \u0437\u0430\u0433\u0440\u0443\u0437\u043A\u0438 \u0434\u0430\u043D\u043D\u044B\u0445. \u0414\u0430\u043D\u043D\u044B\u0435 \u0435\u0449\u0451 \u043D\u0435 \u0437\u0430\u0433\u0440\u0443\u0436\u0435\u043D\u044B \u2014 \u043F\u043E\u0434\u043E\u0436\u0434\u0438\u0442\u0435 \u043D\u0435\u0441\u043A\u043E\u043B\u044C\u043A\u043E \u0447\u0430\u0441\u043E\u0432 \u043F\u043E\u0441\u043B\u0435 \u043D\u0430\u0441\u0442\u0440\u043E\u0439\u043A\u0438.</div>`;
        }
    }

    function renderFixtures(matches, leagueCode) {
        matches = matches.filter(m => m.homeTeam.name && m.awayTeam.name && m.homeTeam.name !== 'null' && m.awayTeam.name !== 'null');
        if (!matches.length) {
            $('#matchList').innerHTML = '<div class="empty-msg">\u041D\u0435\u0442 \u043F\u0440\u0435\u0434\u0441\u0442\u043E\u044F\u0449\u0438\u0445 \u043C\u0430\u0442\u0447\u0435\u0439 \u0432 \u044D\u0442\u043E\u0439 \u043B\u0438\u0433\u0435.<br>\u041F\u043E\u043F\u0440\u043E\u0431\u0443\u0439\u0442\u0435 \u0434\u0440\u0443\u0433\u0443\u044E \u043B\u0438\u0433\u0443.</div>';
            return;
        }
        $('#matchList').innerHTML = '<div class="matches">' + matches.map((m, idx) => `
            <div class="match-card" onclick="openPrediction(${idx}, '${leagueCode}')">
                <div class="match-date">${formatDate(m.utcDate)}<br><b>${formatTime(m.utcDate)}</b></div>
                <div class="match-teams">
                    <div class="match-team">
                        <img src="${m.homeTeam.crest || ''}" alt="" onerror="this.style.display='none'">
                        <span>${m.homeTeam.name}</span>
                    </div>
                    <div class="match-team">
                        <img src="${m.awayTeam.crest || ''}" alt="" onerror="this.style.display='none'">
                        <span>${m.awayTeam.name}</span>
                    </div>
                </div>
                <button class="btn btn-green btn-sm">\u041F\u0440\u043E\u0433\u043D\u043E\u0437</button>
            </div>`
        ).join('') + '</div>';
    }

    // ==================== PREDICTION ====================
    function openPrediction(matchIdx, leagueCode) {
        const data = state.leagueData[leagueCode];
        if (!data) return;
        const match = data.matches[matchIdx];
        if (!match) return;

        // Show loading
        $('#modalContainer').innerHTML = `
        <div class="modal-overlay" onclick="if(event.target===this)closeModal()">
            <div class="modal">
                <div class="modal-header">
                    <h2>${match.homeTeam.name} \u2014 ${match.awayTeam.name}</h2>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <div class="modal-body" id="predBody">
                    <div class="loading"><div class="spinner"></div><br>\u0420\u0430\u0441\u0447\u0451\u0442 \u043F\u0440\u043E\u0433\u043D\u043E\u0437\u0430...</div>
                </div>
            </div>
        </div>`;

        // Compute prediction (load odds async)
        setTimeout(async () => {
            const oddsData = await loadOdds(leagueCode);
            const matchOdds = findOddsForMatch(match, oddsData);
            renderPrediction(match, data, matchOdds, oddsData);
        }, 100);
    }

    function renderPrediction(match, data, matchOdds, oddsData) {
        const home = match.homeTeam;
        const away = match.awayTeam;
        const standingsArr = data.standings || [];
        const standings = {};
        standingsArr.forEach(s => { standings[s.id] = s; });

        const hStats = standings[home.id];
        const aStats = standings[away.id];

        // === DIXON-COLES MODEL ===
        const league = calcLeagueStats(standingsArr);
        const avgGoals = league.avgGoals; // league avg goals per team per match
        const HOME_ADV = 1.25; // home teams score ~25% more

        // Attack & defense strengths relative to league average
        let hAttack = 1, hDefense = 1, aAttack = 1, aDefense = 1;
        if (hStats && hStats.played > 0) {
            hAttack = (hStats.gf / hStats.played) / avgGoals;
            hDefense = (hStats.ga / hStats.played) / avgGoals;
        }
        if (aStats && aStats.played > 0) {
            aAttack = (aStats.gf / aStats.played) / avgGoals;
            aDefense = (aStats.ga / aStats.played) / avgGoals;
        }

        // === ELO ADJUSTMENT ===
        const elo = calcElo(data.finished || []);
        const hElo = elo[home.id] || 1500;
        const aElo = elo[away.id] || 1500;
        const eloDiff = hElo - aElo;
        // Elo adjustment: 100 pts diff ~ 5% goal adjustment
        const eloFactor = 1 + eloDiff / 2000;

        // Expected goals (Dixon-Coles with Elo adjustment)
        const homeXG = avgGoals * hAttack * aDefense * HOME_ADV * Math.max(eloFactor, 0.5);
        const awayXG = avgGoals * aAttack * hDefense / HOME_ADV * Math.max(1 / eloFactor, 0.5);
        const totalXG = homeXG + awayXG;

        // Rho parameter for Dixon-Coles correction
        const rho = estimateRho(avgGoals);

        // 1X2 probabilities
        const outcomes = prob1X2(homeXG, awayXG, rho);
        const pOver15 = probOver(homeXG, awayXG, 1, rho);
        const pOver25 = probOver(homeXG, awayXG, 2, rho);
        const pOver35 = probOver(homeXG, awayXG, 3, rho);
        const pBtts = probBTTS(homeXG, awayXG, rho);

        // Estimated shots
        const homeAvgFor = hStats ? hStats.gf / hStats.played : 1.3;
        const awayAvgFor = aStats ? aStats.gf / aStats.played : 1.1;
        const homeShots = Math.round(homeAvgFor / 0.11);
        const awayShots = Math.round(awayAvgFor / 0.11);
        const homeOnTarget = Math.round(homeAvgFor / 0.33);
        const awayOnTarget = Math.round(awayAvgFor / 0.33);

        // Form from finished matches
        const homeForm = calcForm(home.id, data.finished || []);
        const awayForm = calcForm(away.id, data.finished || []);

        const formHtml = (form) => {
            if (!form.length) return '<span style="color:var(--text2)">\u041D\u0435\u0442 \u0434\u0430\u043D\u043D\u044B\u0445</span>';
            return form.map(c => `<div class="form-item form-${c}">${c === 'W' ? '\u0412' : c === 'D' ? '\u041D' : '\u041F'}</div>`).join('');
        };

        // Recent H2H from finished matches
        let h2hHTML = '';
        const h2hMatches = (data.finished || []).filter(m =>
            (m.homeTeam.id === home.id && m.awayTeam.id === away.id) ||
            (m.homeTeam.id === away.id && m.awayTeam.id === home.id)
        ).sort((a, b) => new Date(b.utcDate) - new Date(a.utcDate)).slice(0, 3);

        if (h2hMatches.length > 0) {
            h2hHTML = `
            <div class="pred-section">
                <div class="pred-section-title">\u041B\u0438\u0447\u043D\u044B\u0435 \u0432\u0441\u0442\u0440\u0435\u0447\u0438 (\u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0435)</div>
                ${h2hMatches.map(m => `
                    <div class="h2h-match">
                        <div class="h2h-date">${formatDate(m.utcDate)}</div>
                        <div class="h2h-teams">${m.homeTeam.name}</div>
                        <div class="h2h-score">${m.homeGoals} : ${m.awayGoals}</div>
                        <div class="h2h-teams" style="text-align:right">${m.awayTeam.name}</div>
                    </div>
                `).join('')}
            </div>`;
        }

        // Season stats table
        let statsHTML = '';
        if (hStats && aStats) {
            statsHTML = `
            <div class="pred-section">
                <div class="pred-section-title">\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043A\u0430 \u0437\u0430 \u0441\u0435\u0437\u043E\u043D</div>
                <table class="shots-table">
                    <tr><th></th><th>${home.name}</th><th>${away.name}</th></tr>
                    <tr><td style="color:var(--text2)">\u041C\u0430\u0442\u0447\u0438</td><td>${hStats.played}</td><td>${aStats.played}</td></tr>
                    <tr><td style="color:var(--text2)">\u041F\u043E\u0431\u0435\u0434\u044B</td><td>${hStats.won}</td><td>${aStats.won}</td></tr>
                    <tr><td style="color:var(--text2)">\u041D\u0438\u0447\u044C\u0438</td><td>${hStats.draw}</td><td>${aStats.draw}</td></tr>
                    <tr><td style="color:var(--text2)">\u041F\u043E\u0440\u0430\u0436\u0435\u043D\u0438\u044F</td><td>${hStats.lost}</td><td>${aStats.lost}</td></tr>
                    <tr><td style="color:var(--text2)">\u0417\u0430\u0431\u0438\u0442\u043E</td><td>${hStats.gf}</td><td>${aStats.gf}</td></tr>
                    <tr><td style="color:var(--text2)">\u041F\u0440\u043E\u043F\u0443\u0449\u0435\u043D\u043E</td><td>${hStats.ga}</td><td>${aStats.ga}</td></tr>
                    <tr><td style="color:var(--text2)">\u0420\u0430\u0437\u043D\u0438\u0446\u0430</td><td>${hStats.gd > 0 ? '+' : ''}${hStats.gd}</td><td>${aStats.gd > 0 ? '+' : ''}${aStats.gd}</td></tr>
                    <tr><td style="color:var(--text2)">\u041E\u0447\u043A\u0438</td><td><b>${hStats.pts}</b></td><td><b>${aStats.pts}</b></td></tr>
                </table>
            </div>`;
        }

        // Render
        $('#predBody').innerHTML = `
            <div class="pred-teams">
                <div class="pred-team">
                    <img src="${home.crest || ''}" alt="" onerror="this.style.display='none'">
                    <div class="pred-team-name">${home.name}</div>
                </div>
                <div class="pred-vs">VS</div>
                <div class="pred-team">
                    <img src="${away.crest || ''}" alt="" onerror="this.style.display='none'">
                    <div class="pred-team-name">${away.name}</div>
                </div>
            </div>

            <div class="pred-section">
                <div class="pred-section-title">\u0418\u0441\u0445\u043E\u0434 \u043C\u0430\u0442\u0447\u0430 (1X2)</div>
                <div style="display:flex;gap:8px;margin-bottom:8px">
                    <div style="flex:1;text-align:center;padding:12px;background:var(--card);border-radius:8px">
                        <div style="font-size:12px;color:var(--text2)">\u041F\u043E\u0431\u0435\u0434\u0430 1</div>
                        <div style="font-size:22px;font-weight:700" class="${probColor(outcomes.p1)}">${Math.round(outcomes.p1*100)}%</div>
                    </div>
                    <div style="flex:1;text-align:center;padding:12px;background:var(--card);border-radius:8px">
                        <div style="font-size:12px;color:var(--text2)">\u041D\u0438\u0447\u044C\u044F</div>
                        <div style="font-size:22px;font-weight:700" class="${probColor(outcomes.pX)}">${Math.round(outcomes.pX*100)}%</div>
                    </div>
                    <div style="flex:1;text-align:center;padding:12px;background:var(--card);border-radius:8px">
                        <div style="font-size:12px;color:var(--text2)">\u041F\u043E\u0431\u0435\u0434\u0430 2</div>
                        <div style="font-size:22px;font-weight:700" class="${probColor(outcomes.p2)}">${Math.round(outcomes.p2*100)}%</div>
                    </div>
                </div>
                <div class="pred-row">
                    <span class="pred-label">Elo-\u0440\u0435\u0439\u0442\u0438\u043D\u0433 ${home.name}</span>
                    <span class="pred-value">${Math.round(hElo)}</span>
                </div>
                <div class="pred-row">
                    <span class="pred-label">Elo-\u0440\u0435\u0439\u0442\u0438\u043D\u0433 ${away.name}</span>
                    <span class="pred-value">${Math.round(aElo)}</span>
                </div>
            </div>

            <div class="pred-section">
                <div class="pred-section-title">\u0422\u043E\u0442\u0430\u043B \u0433\u043E\u043B\u043E\u0432</div>
                <div class="pred-row">
                    <span class="pred-label">\u041E\u0436\u0438\u0434\u0430\u0435\u043C\u044B\u0439 \u0442\u043E\u0442\u0430\u043B</span>
                    <span class="pred-value" style="font-size:20px">${totalXG.toFixed(2)}</span>
                </div>
                <div class="pred-row">
                    <span class="pred-label">\u0413\u043E\u043B\u044B ${home.name}</span>
                    <span class="pred-value">${homeXG.toFixed(2)}</span>
                </div>
                <div class="pred-row">
                    <span class="pred-label">\u0413\u043E\u043B\u044B ${away.name}</span>
                    <span class="pred-value">${awayXG.toFixed(2)}</span>
                </div>
                <div style="margin-top:12px">
                    ${renderProbBar('\u0422\u0411 1.5', pOver15)}
                    ${renderProbBar('\u0422\u0411 2.5', pOver25)}
                    ${renderProbBar('\u0422\u0411 3.5', pOver35)}
                </div>
            </div>

            <div class="pred-section">
                <div class="pred-section-title">\u041E\u0431\u0435 \u0437\u0430\u0431\u044C\u044E\u0442 (BTTS)</div>
                ${renderProbBar('\u041E\u0431\u0435 \u0437\u0430\u0431\u044C\u044E\u0442 \u2014 \u0414\u0410', pBtts)}
                ${renderProbBar('\u041E\u0431\u0435 \u0437\u0430\u0431\u044C\u044E\u0442 \u2014 \u041D\u0415\u0422', 1 - pBtts)}
            </div>

            <div class="pred-section">
                <div class="pred-section-title">\u0423\u0434\u0430\u0440\u044B \u0438 \u0448\u0442\u0430\u043D\u0433\u0438 (\u043E\u0446\u0435\u043D\u043A\u0430 \u0437\u0430 \u043C\u0430\u0442\u0447)</div>
                <p style="font-size:12px;color:var(--text2);margin-bottom:8px">
                    \u041E\u0446\u0435\u043D\u043A\u0430 \u043D\u0430 \u043E\u0441\u043D\u043E\u0432\u0435 \u0440\u0435\u0437\u0443\u043B\u044C\u0442\u0430\u0442\u0438\u0432\u043D\u043E\u0441\u0442\u0438. \u00AB\u041C\u0438\u043C\u043E/\u0448\u0442\u0430\u043D\u0433\u0438\u00BB \u0432\u043A\u043B\u044E\u0447\u0430\u0435\u0442 \u0448\u0442\u0430\u043D\u0433\u0438, \u043F\u0435\u0440\u0435\u043A\u043B\u0430\u0434\u0438\u043D\u044B \u0438 \u043F\u0440\u043E\u043C\u0430\u0445\u0438.
                </p>
                <table class="shots-table">
                    <tr><th>\u041A\u043E\u043C\u0430\u043D\u0434\u0430</th><th>~\u0423\u0434\u0430\u0440\u043E\u0432</th><th>~\u0412 \u0441\u0442\u0432\u043E\u0440</th><th>~\u041C\u0438\u043C\u043E/\u0448\u0442\u0430\u043D\u0433\u0438</th></tr>
                    <tr>
                        <td>${home.name}</td>
                        <td>${homeShots}</td>
                        <td>${homeOnTarget}</td>
                        <td>${homeShots - homeOnTarget}</td>
                    </tr>
                    <tr>
                        <td>${away.name}</td>
                        <td>${awayShots}</td>
                        <td>${awayOnTarget}</td>
                        <td>${awayShots - awayOnTarget}</td>
                    </tr>
                </table>
            </div>

            <div class="pred-section">
                <div class="pred-section-title">\u0424\u043E\u0440\u043C\u0430 (\u043F\u043E\u0441\u043B\u0435\u0434\u043D\u0438\u0435 \u043C\u0430\u0442\u0447\u0438)</div>
                <div class="pred-row">
                    <span class="pred-label">${home.name}</span>
                    <div class="form-row">${formHtml(homeForm)}</div>
                </div>
                <div class="pred-row" style="margin-top:8px">
                    <span class="pred-label">${away.name}</span>
                    <div class="form-row">${formHtml(awayForm)}</div>
                </div>
                <p style="font-size:11px;color:var(--text2);margin-top:8px">\u0412 \u2014 \u043F\u043E\u0431\u0435\u0434\u0430, \u041D \u2014 \u043D\u0438\u0447\u044C\u044F, \u041F \u2014 \u043F\u043E\u0440\u0430\u0436\u0435\u043D\u0438\u0435</p>
            </div>

            ${statsHTML}
            ${h2hHTML}

            ${renderOddsHTML(matchOdds, outcomes, oddsData)}

            <p style="font-size:11px;color:var(--text2);text-align:center;margin-top:16px">
\u041C\u043E\u0434\u0435\u043B\u044C: Dixon-Coles + Elo. \u0423\u0447\u0438\u0442\u044B\u0432\u0430\u0435\u0442 \u0441\u0438\u043B\u0443 \u0430\u0442\u0430\u043A\u0438/\u0437\u0430\u0449\u0438\u0442\u044B, \u0434\u043E\u043C\u0430\u0448\u043D\u0435\u0435 \u043F\u0440\u0435\u0438\u043C\u0443\u0449\u0435\u0441\u0442\u0432\u043E, \u043A\u043E\u0440\u0440\u0435\u043B\u044F\u0446\u0438\u044E \u043D\u0438\u0437\u043A\u0438\u0445 \u0441\u0447\u0435\u0442\u043E\u0432 \u0438 \u0434\u0438\u043D\u0430\u043C\u0438\u043A\u0443 \u0444\u043E\u0440\u043C\u044B. \u042D\u0442\u043E \u043C\u0430\u0442\u0435\u043C\u0430\u0442\u0438\u0447\u0435\u0441\u043A\u0430\u044F \u043E\u0446\u0435\u043D\u043A\u0430, \u0430 \u043D\u0435 \u0433\u0430\u0440\u0430\u043D\u0442\u0438\u044F.
            </p>
        `;
    }

    // ==================== ODDS RENDERING ====================
    function renderOddsHTML(odds, modelOutcomes, oddsData) {
        if (!odds) return '';

        let html = '';
        const h2h = odds.h2h || {};
        const totals = odds.totals || {};

        // === ARBITRAGE / VALUE BETS ALERTS ===
        let arbHTML = '';
        if (h2h.arb) {
            const profit = Math.abs(h2h.margin * 100).toFixed(1);
            arbHTML = `
            <div class="arb-alert">
                <div class="arb-alert-icon">&#9889;</div>
                <div class="arb-alert-text">
                    <div class="arb-alert-title">\u0412\u0418\u041B\u041A\u0410 \u041D\u0410\u0419\u0414\u0415\u041D\u0410 (1X2) \u2014 ${profit}% \u043F\u0440\u0438\u0431\u044B\u043B\u044C</div>
                    <div class="arb-alert-detail">\u041F1: ${h2h.bestBk.home} (${h2h.best.home}) | \u041D: ${h2h.bestBk.draw} (${h2h.best.draw}) | \u041F2: ${h2h.bestBk.away} (${h2h.best.away})</div>
                </div>
            </div>`;
        } else if (h2h.margin !== null && h2h.margin !== undefined && h2h.margin < 0.02) {
            arbHTML = `
            <div class="arb-alert arb-near">
                <div class="arb-alert-icon">&#9888;&#65039;</div>
                <div class="arb-alert-text">
                    <div class="arb-alert-title">\u041F\u043E\u0447\u0442\u0438 \u0432\u0438\u043B\u043A\u0430 (1X2) \u2014 \u043C\u0430\u0440\u0436\u0430 ${(h2h.margin * 100).toFixed(1)}%</div>
                    <div class="arb-alert-detail">\u041B\u0443\u0447\u0448\u0438\u0435: \u041F1 ${h2h.best.home} | \u041D ${h2h.best.draw} | \u041F2 ${h2h.best.away}</div>
                </div>
            </div>`;
        }

        if (totals.arb) {
            const profit = Math.abs(totals.margin * 100).toFixed(1);
            arbHTML += `
            <div class="arb-alert" style="margin-top:8px">
                <div class="arb-alert-icon">&#9889;</div>
                <div class="arb-alert-text">
                    <div class="arb-alert-title">\u0412\u0418\u041B\u041A\u0410 \u041D\u0410\u0419\u0414\u0415\u041D\u0410 (\u0422\u043E\u0442\u0430\u043B ${totals.point}) \u2014 ${profit}% \u043F\u0440\u0438\u0431\u044B\u043B\u044C</div>
                    <div class="arb-alert-detail">\u0422\u0411: ${totals.bestBk.over} (${totals.best.over}) | \u0422\u041C: ${totals.bestBk.under} (${totals.best.under})</div>
                </div>
            </div>`;
        }

        // === VALUE BETS ===
        let valueBetsHTML = '';
        if (modelOutcomes && h2h.best && h2h.best.home > 0) {
            const valueBets = [];
            const checks = [
                { label: '\u041F\u043E\u0431\u0435\u0434\u0430 1', modelP: modelOutcomes.p1, odds: h2h.best.home },
                { label: '\u041D\u0438\u0447\u044C\u044F', modelP: modelOutcomes.pX, odds: h2h.best.draw },
                { label: '\u041F\u043E\u0431\u0435\u0434\u0430 2', modelP: modelOutcomes.p2, odds: h2h.best.away },
            ];
            for (const c of checks) {
                const impliedP = 1 / c.odds;
                const edge = c.modelP - impliedP;
                if (edge > 0.05) {
                    valueBets.push({
                        label: c.label,
                        modelP: c.modelP,
                        impliedP: impliedP,
                        odds: c.odds,
                        edge: edge
                    });
                }
            }
            if (valueBets.length > 0) {
                valueBetsHTML = valueBets.map(vb => `
                <div class="value-bet">
                    <div class="value-bet-label">&#127919; VALUE BET: ${vb.label}</div>
                    <div class="value-bet-text">
                        \u041C\u043E\u0434\u0435\u043B\u044C: <b>${Math.round(vb.modelP*100)}%</b> |
                        \u0411\u0443\u043A\u043C\u0435\u043A\u0435\u0440: ${Math.round(vb.impliedP*100)}% (\u043A\u043E\u044D\u0444. ${vb.odds.toFixed(2)}) |
                        \u041F\u0440\u0435\u0438\u043C\u0443\u0449\u0435\u0441\u0442\u0432\u043E: <span class="value-bet-edge">+${(vb.edge*100).toFixed(1)}%</span>
                    </div>
                </div>`).join('');
            }
        }

        // === 1X2 ODDS TABLE ===
        let h2hTableHTML = '';
        if (h2h.bookmakers && h2h.bookmakers.length > 0) {
            const rows = h2h.bookmakers.map(bk => {
                const hBest = h2h.best && bk.home >= h2h.best.home ? ' odds-best' : '';
                const dBest = h2h.best && bk.draw >= h2h.best.draw ? ' odds-best' : '';
                const aBest = h2h.best && bk.away >= h2h.best.away ? ' odds-best' : '';
                return `<tr>
                    <td>${bk.title}</td>
                    <td class="${hBest}">${bk.home.toFixed(2)}</td>
                    <td class="${dBest}">${bk.draw.toFixed(2)}</td>
                    <td class="${aBest}">${bk.away.toFixed(2)}</td>
                </tr>`;
            }).join('');

            h2hTableHTML = `
            <table class="odds-table">
                <tr><th>\u0411\u0443\u043A\u043C\u0435\u043A\u0435\u0440</th><th>\u041F1</th><th>\u041D\u0438\u0447\u044C\u044F</th><th>\u041F2</th></tr>
                ${rows}
                <tr class="odds-best-row">
                    <td>\u041B\u0443\u0447\u0448\u0438\u0435</td>
                    <td class="odds-best">${h2h.best.home.toFixed(2)}</td>
                    <td class="odds-best">${h2h.best.draw.toFixed(2)}</td>
                    <td class="odds-best">${h2h.best.away.toFixed(2)}</td>
                </tr>
            </table>`;
            if (h2h.margin !== null && h2h.margin !== undefined && !h2h.arb) {
                h2hTableHTML += `<div class="arb-normal">\u041C\u0430\u0440\u0436\u0430 \u0431\u0443\u043A\u043C\u0435\u043A\u0435\u0440\u043E\u0432: ${(h2h.margin * 100).toFixed(1)}%</div>`;
            }
        }

        // === TOTALS ODDS TABLE ===
        let totalsTableHTML = '';
        if (totals.bookmakers && totals.bookmakers.length > 0) {
            const point = totals.point || 2.5;
            const rows = totals.bookmakers.map(bk => {
                const oBest = totals.best && bk.over >= totals.best.over ? ' odds-best' : '';
                const uBest = totals.best && bk.under >= totals.best.under ? ' odds-best' : '';
                return `<tr>
                    <td>${bk.title}</td>
                    <td class="${oBest}">${bk.over.toFixed(2)}</td>
                    <td class="${uBest}">${bk.under.toFixed(2)}</td>
                </tr>`;
            }).join('');

            totalsTableHTML = `
            <table class="odds-table">
                <tr><th>\u0411\u0443\u043A\u043C\u0435\u043A\u0435\u0440</th><th>\u0422\u0411 ${point}</th><th>\u0422\u041C ${point}</th></tr>
                ${rows}
                <tr class="odds-best-row">
                    <td>\u041B\u0443\u0447\u0448\u0438\u0435</td>
                    <td class="odds-best">${totals.best.over.toFixed(2)}</td>
                    <td class="odds-best">${totals.best.under.toFixed(2)}</td>
                </tr>
            </table>`;
            if (totals.margin !== null && totals.margin !== undefined && !totals.arb) {
                totalsTableHTML += `<div class="arb-normal">\u041C\u0430\u0440\u0436\u0430 \u0431\u0443\u043A\u043C\u0435\u043A\u0435\u0440\u043E\u0432: ${(totals.margin * 100).toFixed(1)}%</div>`;
            }
        }

        // === COMPOSE ===
        const freshness = oddsData && oddsData.updated ? `<div class="odds-fresh">\u041A\u043E\u044D\u0444\u0444\u0438\u0446\u0438\u0435\u043D\u0442\u044B \u043E\u0431\u043D\u043E\u0432\u043B\u0435\u043D\u044B: ${timeAgo(oddsData.updated)}</div>` : '';

        html = `
        <div class="pred-section">
            <div class="pred-section-title">\u041A\u043E\u044D\u0444\u0444\u0438\u0446\u0438\u0435\u043D\u0442\u044B \u0431\u0443\u043A\u043C\u0435\u043A\u0435\u0440\u043E\u0432</div>
            ${arbHTML}
            ${valueBetsHTML}
            ${h2hTableHTML ? '<div style="margin-bottom:16px">' + h2hTableHTML + '</div>' : ''}
            ${totalsTableHTML}
            ${freshness}
        </div>`;

        return html;
    }

    function renderProbBar(label, prob) {
        const p = Math.round(prob * 100);
        const cls = probColor(prob);
        const color = barColor(prob);
        return `
        <div class="prob-bar">
            <span class="pred-label" style="min-width:140px">${label}</span>
            <div class="prob-bar-track">
                <div class="prob-bar-fill" style="width:${p}%;background:${color}"></div>
            </div>
            <span class="prob-bar-label ${cls}">${p}%</span>
        </div>`;
    }

    function closeModal() { $('#modalContainer').innerHTML = ''; }
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

    // ==================== INIT ====================
    renderMain();
    </script>
</body>
</html>
