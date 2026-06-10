// ==UserScript==
// @name         SolrWayback Playback to Wayback Link
// @namespace    solrwayback.to.wayback
// @version      1.0
// @description  Adds a button that opens the equivalent Internet Archive playback URL
// @match        http://localhost:8080/solrwayback/services/web/*
// @match        https://localhost:8080/solrwayback/services/web/*
// @match        http://127.0.0.1:8080/solrwayback/services/web/*
// @match        https://127.0.0.1:8080/solrwayback/services/web/*
// @grant        none
// @author       Jørn Thøgersen (Web Child - ERC Project)
// ==/UserScript==

(function () {
	"use strict";

	const WAYBACK_BASE = "https://web.archive.org/web/";

	function parsePlaybackUrl() {
		const match = window.location.href.match(
			/\/solrwayback\/services\/web\/(\d{14})\/+(https?:\/\/.+)$/i
		);

		if (!match) {
			return null;
		}

		const timestamp = match[1];
		let originalUrl = match[2];

		try {
			originalUrl = decodeURIComponent(originalUrl);
		} catch {
			// If not URL-encoded, keep the original value.
		}

		return {
			timestamp,
			originalUrl
		};
	}

	function buildWaybackUrl(info) {
		return `${WAYBACK_BASE}${info.timestamp}/${info.originalUrl}`;
	}

	function createOpenButton(waybackUrl) {
		const existing = document.getElementById("swb-wayback-button-host");
		if (existing) {
			return;
		}

		// Use a Shadow DOM host so the button's styles are completely isolated
		// from the archived page's CSS (including frameset pages).
		const host = document.createElement("div");
		host.id = "swb-wayback-button-host";

		const hs = host.style;
		hs.setProperty("all", "initial", "important");
		hs.setProperty("position", "fixed", "important");
		hs.setProperty("bottom", "20px", "important");
		hs.setProperty("right", "20px", "important");
		hs.setProperty("top", "auto", "important");
		hs.setProperty("left", "auto", "important");
		hs.setProperty("z-index", "2147483647", "important");
		hs.setProperty("display", "block", "important");
		hs.setProperty("visibility", "visible", "important");
		hs.setProperty("opacity", "1", "important");
		hs.setProperty("pointer-events", "auto", "important");

		const shadow = host.attachShadow({ mode: "closed" });

		const style = document.createElement("style");
		style.textContent = `
			button {
				display: block;
				padding: 10px 14px;
				border: 1px solid #2f4f90;
				border-radius: 8px;
				background: #3b67bd;
				color: #ffffff;
				font-size: 13px;
				font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
				font-weight: 600;
				cursor: pointer;
				box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
				transition: transform 0.15s ease, background 0.15s ease;
			}
			button:hover {
				background: #3258a2;
				transform: translateY(-1px);
			}
		`;

		const button = document.createElement("button");
		button.textContent = "Open in Wayback";
		button.title = waybackUrl;

		button.addEventListener("click", () => {
			window.open(waybackUrl, "_blank", "noopener,noreferrer");
		});

		shadow.appendChild(style);
		shadow.appendChild(button);

		// Append to <html> rather than <body> so the host sits above frameset
		// frames, which otherwise cover the entire viewport.
		document.documentElement.appendChild(host);
	}

	function init() {
		const info = parsePlaybackUrl();
		if (!info) {
			return;
		}

		const waybackUrl = buildWaybackUrl(info);
		createOpenButton(waybackUrl);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
