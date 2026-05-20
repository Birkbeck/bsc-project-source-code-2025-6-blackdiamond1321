/* FinTrack market */

import { api } from './api.js';
import { formatCurrency } from './format.js';

/* Refresh every 30 seconds */
const REFRESH_MS = 30_000;

/* Load stocks and crypto in parallel */
const load = async () => {
    try {
        const [stocks, crypto] = await Promise.all([
            api.getStocks(),
            api.getCrypto(),
        ]);
        renderGrid(document.getElementById('stocks_grid'), stocks.quotes);
        renderGrid(document.getElementById('crypto_grid'), crypto.quotes);

        /* Timestamp */
        const ts = Math.max(stocks.fetched_at, crypto.fetched_at) * 1000;
        document.getElementById('market_updated').textContent =
            'Last updated ' + new Date(ts).toLocaleTimeString('en-GB');
    } catch (err) {
        document.getElementById('market_updated').textContent =
            'Failed to load market data';
    }
};

/* Build the cards for one grid */
const renderGrid = (target, quotes) => {
    if (!quotes.length) {
        target.innerHTML = '<p style="color:var(--text2)">No data</p>';
        return;
    }
    target.innerHTML = quotes.map(q => {
        const up   = q.change_pct >= 0;
        const sign = up ? '+' : '';
        /* Folder + filename based on the ticker.
           Stocks: /images/stocks/aapl.png
           Crypto: /images/crypto/btc.png (strip "-USD") */
        const folder = q.symbol.includes('-USD') ? 'crypto' : 'stocks';
        const slug   = q.symbol.toLowerCase().split('-')[0];
        return `
            <div class="market-card">
                <div class="market-card-head">
                    <img src="/images/${folder}/${slug}.png" alt="icon"
                         class="market-card-icon"
                         onerror="this.removeAttribute('src')">
                    <div class="market-card-titles">
                        <span class="market-card-symbol">${q.symbol}</span>
                        <span class="market-card-name">${q.name}</span>
                    </div>
                </div>
                <div class="market-card-foot">
                    <span class="market-card-price">${formatCurrency(q.price)}</span>
                    <span class="market-card-change market-card-change--${up ? 'up' : 'down'}">${sign}${q.change_pct.toFixed(2)}%</span>
                </div>
            </div>
        `;
    }).join('');
};

load();
setInterval(load, REFRESH_MS);