// ==UserScript==
// @name         Wayback → SolrWayback Query Generator
// @namespace    local.solrwayback.helper
// @version      1.1
// @description  Generate SolrWayback query from Internet Archive URLs
// @match        https://web.archive.org/web/*
// @grant        GM_setClipboard
// @author       Jørn Thøgersen (Web Child - ERC project)
// ==/UserScript==

(function() {
    'use strict';

    const SOLRWAYBACK_BASE = "http://localhost:8080/solrwayback/search?query=";

    function parseWaybackURL() {
        const match = window.location.href.match(/\/web\/(\d{14})\/(https?:\/\/[^?#]+)/);
        if (!match) return null;

        const timestamp = match[1];
        const originalUrl = match[2];

        return { timestamp, originalUrl };
    }

    function timestampToISO(ts) {
        return `${ts.slice(0,4)}-${ts.slice(4,6)}-${ts.slice(6,8)}T${ts.slice(8,10)}:${ts.slice(10,12)}:${ts.slice(12,14)}Z`;
    }

    // Preserve hostname AND port exactly as written
    function normalizeUrlPreservePort(url) {
        const m = url.match(/^(https?:\/\/[^\/]+)(\/?.*)$/);
        if (!m) return url;

        let host = m[1];
        let path = m[2] || "/";

        if (!path.endsWith("/")) {
            path = "/";
        }

        return host + path;
    }

    function buildSolrQuery(url, isoDate) {
        return `url:"${url}" AND crawl_date:"${isoDate}"`;
    }

    function buildFullLink(query) {
        return SOLRWAYBACK_BASE + encodeURIComponent(query);
    }

    function addButton(query, link) {
        const btn = document.createElement("button");
        btn.textContent = "Open in SolrWayback";
        btn.style.position = "fixed";
        btn.style.bottom = "20px";
        btn.style.right = "20px";
        btn.style.zIndex = 9999;
        btn.style.padding = "8px 14px";
        btn.style.background = "#1565c0";
        btn.style.color = "white";
        btn.style.border = "none";
        btn.style.borderRadius = "5px";
        btn.style.cursor = "pointer";

        btn.onclick = () => {
            GM_setClipboard(query);
            window.open(link, "_blank");
        };

        document.body.appendChild(btn);
    }

    function run() {
        const parsed = parseWaybackURL();
        if (!parsed) return;

        const isoDate = timestampToISO(parsed.timestamp);
        const normalizedUrl = normalizeUrlPreservePort(parsed.originalUrl);

        const query = buildSolrQuery(normalizedUrl, isoDate);
        const link = buildFullLink(query);

        console.log("SolrWayback query:", query);
        console.log("SolrWayback link:", link);

        addButton(query, link);
    }

    run();
})();