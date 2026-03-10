// ==UserScript==
// @name         Wayback to SolrWayback Panel
// @namespace    solrwayback.panel
// @version      3.4
// @description  SolrWayback helper panel
// @match        https://web.archive.org/*
// @grant        GM_setClipboard
// @author       Jørn Thøgersen (Web Child - ERC Project)
// ==/UserScript==

(function() {
"use strict";

const SOLRWAYBACK_BASE = "http://localhost:8080/solrwayback/search?query=";

function parseWayback() {

    const url = window.location.href;

    const capture = url.match(/\/web\/(\d{14})\/(https?:\/\/[^?#]+)/);

    if (capture) {
        return {
            timestamp: capture[1],
            original: capture[2]
        };
    }

    const calendar = url.match(/\/web\/\*\/(https?:\/\/[^?#]+)/);

    if (calendar) {
        return {
            timestamp: null,
            original: calendar[1]
        };
    }

    return null;
}

function normalize(url) {

    const m = url.match(/^(https?:\/\/[^\/]+)(\/?.*)$/);
    if (!m) return url;

    let host = m[1];
    let path = m[2] || "/";

    if (!path.endsWith("/")) path = "/";

    return host + path;
}

function iso(ts) {

    if (!ts) return null;

    return `${ts.slice(0,4)}-${ts.slice(4,6)}-${ts.slice(6,8)}T${ts.slice(8,10)}:${ts.slice(10,12)}:${ts.slice(12,14)}Z`;
}

function human(ts) {

    if (!ts) return "No timestamp";

    const d = new Date(
        ts.slice(0,4),
        ts.slice(4,6)-1,
        ts.slice(6,8),
        ts.slice(8,10),
        ts.slice(10,12),
        ts.slice(12,14)
    );

    return d.toUTCString();
}

function baseDomain(hostname) {

    const parts = hostname.split(".");
    if (parts.length <= 2) return hostname;

    return parts.slice(-2).join(".");
}

function buildQueries(info) {

    const normalized = normalize(info.original);

    const hostname = (() => {
        try { return new URL(info.original).hostname; }
        catch { return null; }
    })();

    const queries = {};

    if (info.timestamp) {

        const t = iso(info.timestamp);

        queries.exact =
            `url:"${normalized}" AND crawl_date:"${t}"`;

        queries.nearest =
            `url:"${normalized}"`;
    }

    if (hostname) {

        const domain = baseDomain(hostname);

        queries.domain =
            `domain:"${domain}"`;
    }

    return queries;
}

function link(q) {
    return SOLRWAYBACK_BASE + encodeURIComponent(q);
}

function makeDraggable(panel, handle) {

    let offsetX = 0;
    let offsetY = 0;
    let dragging = false;

    handle.addEventListener("mousedown", e => {

        dragging = true;

        offsetX = e.clientX - panel.offsetLeft;
        offsetY = e.clientY - panel.offsetTop;

        document.addEventListener("mousemove", move);
        document.addEventListener("mouseup", stop);
    });

    function move(e) {

        if (!dragging) return;

        panel.style.left = (e.clientX - offsetX) + "px";
        panel.style.top = (e.clientY - offsetY) + "px";
        panel.style.right = "auto";
        panel.style.bottom = "auto";
    }

    function stop() {

        dragging = false;

        document.removeEventListener("mousemove", move);
        document.removeEventListener("mouseup", stop);
    }
}

function createPanel(info, queries) {

    const panel = document.createElement("div");

    panel.style.position = "fixed";
    panel.style.bottom = "20px";
    panel.style.right = "20px";
    panel.style.width = "300px";
    panel.style.background = "#fdfefe";
    panel.style.border = "1px solid #d6e2f5";
    panel.style.borderRadius = "10px";
    panel.style.boxShadow = "0 8px 24px rgba(0,0,0,0.18)";
    panel.style.fontFamily = "system-ui, -apple-system, Segoe UI, Roboto, sans-serif";
    panel.style.fontSize = "13px";
    panel.style.zIndex = "999999";
    panel.style.overflow = "hidden";

    const header = document.createElement("div");

    header.textContent = "SolrWayback";

    header.style.padding = "9px 12px";
    header.style.fontWeight = "600";
    header.style.background = "#e8f0fe";
    header.style.color = "#355c9b";
    header.style.cursor = "move";
    header.style.borderBottom = "1px solid #d6e2f5";

    const body = document.createElement("div");
    body.style.padding = "12px";

    const url = document.createElement("div");
    url.textContent = normalize(info.original);

    url.style.wordBreak = "break-all";
    url.style.color = "#374151";
    url.style.marginBottom = "6px";
    url.style.fontSize = "12.5px";

    const time = document.createElement("div");
    time.textContent = human(info.timestamp);

    time.style.color = "#6b7280";
    time.style.fontSize = "12px";
    time.style.marginBottom = "12px";

    const buttonRow = document.createElement("div");

    function addButton(label, handler) {

        const btn = document.createElement("button");

        btn.textContent = label;

        btn.style.margin = "3px";
        btn.style.padding = "5px 9px";
        btn.style.fontSize = "12px";
        btn.style.border = "1px solid #c9d7f3";
        btn.style.borderRadius = "6px";
        btn.style.background = "#eef4ff";
        btn.style.cursor = "pointer";
        btn.style.color = "#355c9b";
        btn.style.transition = "background 0.15s ease";

        btn.onmouseenter = () => btn.style.background = "#dde9ff";
        btn.onmouseleave = () => btn.style.background = "#eef4ff";

        btn.onclick = handler;

        buttonRow.appendChild(btn);
    }

    if (queries.exact) {

        addButton("Open Exact",
            () => window.open(link(queries.exact), "_blank"));

        addButton("Open Nearest",
            () => window.open(link(queries.nearest), "_blank"));

        addButton("Copy Query",
            () => GM_setClipboard(queries.exact));
    }

    if (queries.domain) {

        addButton("Open Domain",
            () => window.open(link(queries.domain), "_blank"));
    }

    body.appendChild(url);
    body.appendChild(time);
    body.appendChild(buttonRow);

    panel.appendChild(header);
    panel.appendChild(body);

    document.body.appendChild(panel);

    makeDraggable(panel, header);
}

function init() {

    const info = parseWayback();
    if (!info) return;

    const queries = buildQueries(info);

    createPanel(info, queries);
}

setTimeout(init, 800);

})();