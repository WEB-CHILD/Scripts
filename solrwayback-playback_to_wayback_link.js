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
		const existing = document.getElementById("swb-wayback-button");
		if (existing) {
			return;
		}

		const button = document.createElement("button");

		button.id = "swb-wayback-button";
		button.textContent = "Open in Wayback";
		button.title = waybackUrl;

		button.style.position = "fixed";
		button.style.bottom = "20px";
		button.style.right = "20px";
		button.style.zIndex = "999999";
		button.style.padding = "10px 14px";
		button.style.border = "1px solid #2f4f90";
		button.style.borderRadius = "8px";
		button.style.background = "#3b67bd";
		button.style.color = "#ffffff";
		button.style.fontSize = "13px";
		button.style.fontFamily = "system-ui, -apple-system, Segoe UI, Roboto, sans-serif";
		button.style.fontWeight = "600";
		button.style.cursor = "pointer";
		button.style.boxShadow = "0 8px 24px rgba(0, 0, 0, 0.2)";
		button.style.transition = "transform 0.15s ease, background 0.15s ease";

		button.addEventListener("mouseenter", () => {
			button.style.background = "#3258a2";
			button.style.transform = "translateY(-1px)";
		});

		button.addEventListener("mouseleave", () => {
			button.style.background = "#3b67bd";
			button.style.transform = "translateY(0)";
		});

		button.addEventListener("click", () => {
			window.open(waybackUrl, "_blank", "noopener,noreferrer");
		});

		document.body.appendChild(button);
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
