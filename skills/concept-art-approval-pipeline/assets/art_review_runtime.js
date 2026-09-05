(function (root) {
  "use strict";

  const STORAGE_PREFIX = "sample_studio.art-isolation-review.v1";
  const VERDICT_SCHEMA = "sample_studio.art_isolation_review_verdict";
  const REVIEW_SCOPE = "human_visual_isolation_only";
  const DOWNSTREAM_CLAIMS = Object.freeze({
    art_bible_integrated: false,
    source_generation_ready: false,
    generated_asset_approved: false,
    texture_repair_approved: false,
    runtime_promotion_approved: false,
    rights_clearance_approved: false,
    in_game_approval_claimed: false,
  });

  function identityKey(candidate) {
    return `${candidate.candidate_id}@${candidate.candidate_digest}`;
  }

  function storageKey(batchId, candidate) {
    return `${STORAGE_PREFIX}:${batchId}:${candidate.candidate_id}:${candidate.candidate_digest}`;
  }

  function createMemoryStorage() {
    const values = new Map();
    return {
      getItem(key) {
        return values.has(key) ? values.get(key) : null;
      },
      setItem(key, value) {
        values.set(key, String(value));
      },
      removeItem(key) {
        values.delete(key);
      },
    };
  }

  function availableStorage() {
    try {
      if (!root.localStorage) {
        return createMemoryStorage();
      }
      const probe = `${STORAGE_PREFIX}:probe`;
      root.localStorage.setItem(probe, "1");
      root.localStorage.removeItem(probe);
      return root.localStorage;
    } catch (_error) {
      return createMemoryStorage();
    }
  }

  function normalizeSaved(value) {
    if (!value || typeof value !== "object") {
      return { decision: null, notes: "" };
    }
    const decision = value.decision === "accept" || value.decision === "reject"
      ? value.decision
      : null;
    return {
      decision,
      notes: typeof value.notes === "string" ? value.notes : "",
    };
  }

  class ReviewController {
    constructor(config, storage) {
      if (!config || !Array.isArray(config.candidates)) {
        throw new Error("review config must contain candidates");
      }
      this.config = config;
      this.storage = storage || availableStorage();
      this.states = new Map();
      for (const candidate of config.candidates) {
        const raw = this.storage.getItem(storageKey(config.batch_id, candidate));
        let parsed = null;
        if (raw !== null) {
          try {
            parsed = JSON.parse(raw);
          } catch (_error) {
            parsed = null;
          }
        }
        this.states.set(identityKey(candidate), normalizeSaved(parsed));
      }
    }

    candidate(candidateId, candidateDigest) {
      const found = this.config.candidates.find(
        (item) => item.candidate_id === candidateId && item.candidate_digest === candidateDigest
      );
      if (!found) {
        throw new Error(`unknown candidate identity: ${candidateId}@${candidateDigest}`);
      }
      return found;
    }

    state(candidate) {
      return this.states.get(identityKey(candidate));
    }

    save(candidate) {
      this.storage.setItem(
        storageKey(this.config.batch_id, candidate),
        JSON.stringify(this.state(candidate))
      );
    }

    setDecision(candidateId, candidateDigest, decision) {
      if (decision !== "accept" && decision !== "reject" && decision !== null) {
        throw new Error(`invalid decision: ${decision}`);
      }
      const candidate = this.candidate(candidateId, candidateDigest);
      this.state(candidate).decision = decision;
      this.save(candidate);
      return this.summary();
    }

    setNotes(candidateId, candidateDigest, notes) {
      const candidate = this.candidate(candidateId, candidateDigest);
      this.state(candidate).notes = String(notes || "");
      this.save(candidate);
      return this.summary();
    }

    summary() {
      let accepted = 0;
      let rejected = 0;
      for (const state of this.states.values()) {
        if (state.decision === "accept") accepted += 1;
        if (state.decision === "reject") rejected += 1;
      }
      const total = this.config.candidates.length;
      return {
        accepted,
        rejected,
        resolved: accepted + rejected,
        pending: total - accepted - rejected,
        total,
      };
    }

    buildVerdict() {
      const summary = this.summary();
      if (summary.pending !== 0) {
        throw new Error(`cannot export: ${summary.pending} candidate(s) remain pending`);
      }
      const accepted = [];
      const rejected = [];
      const notes = {};
      for (const candidate of this.config.candidates) {
        const state = this.state(candidate);
        const identity = {
          candidate_id: candidate.candidate_id,
          candidate_digest: candidate.candidate_digest,
        };
        (state.decision === "accept" ? accepted : rejected).push(identity);
        if (state.notes.trim()) {
          notes[identityKey(candidate)] = state.notes;
        }
      }
      return {
        schema_name: VERDICT_SCHEMA,
        schema_version: 1,
        batch_id: this.config.batch_id,
        review_gate: this.config.review_gate,
        review_scope: REVIEW_SCOPE,
        accepted_candidates: accepted,
        rejected_candidates: rejected,
        notes_by_candidate_identity: notes,
        downstream_claims: { ...DOWNSTREAM_CLAIMS },
      };
    }
  }

  async function copyText(text, environment) {
    const env = environment || root;
    if (env.navigator && env.navigator.clipboard && env.navigator.clipboard.writeText) {
      try {
        await env.navigator.clipboard.writeText(text);
        return "clipboard";
      } catch (_error) {
        // Local file origins frequently expose Clipboard API but deny writes.
        // Continue to the legacy selection-based copy path in that case.
      }
    }
    const document = env.document;
    if (!document || !document.execCommand) {
      throw new Error("clipboard copy is unavailable; copy the displayed JSON manually");
    }
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    const copied = document.execCommand("copy");
    document.body.removeChild(textarea);
    if (!copied) {
      throw new Error("clipboard copy failed; copy the displayed JSON manually");
    }
    return "execCommand";
  }

  function initializePage(document) {
    const configNode = document.getElementById("art-review-config");
    if (!configNode) return null;
    const config = JSON.parse(configNode.textContent);
    const controller = new ReviewController(config);
    const cards = Array.from(document.querySelectorAll("[data-candidate-id]"));
    const progress = document.getElementById("review-progress");
    const totals = document.getElementById("review-totals");
    const pendingOnly = document.getElementById("pending-only");
    const exportButton = document.getElementById("export-verdict");
    const exportOutput = document.getElementById("verdict-output");
    const reviewStatus = document.getElementById("review-status");

    function cardCandidate(card) {
      return controller.candidate(card.dataset.candidateId, card.dataset.candidateDigest);
    }

    function render() {
      const summary = controller.summary();
      progress.textContent = `${summary.resolved}/${summary.total} reviewed`;
      totals.textContent = `${summary.accepted} accepted · ${summary.rejected} rejected · ${summary.pending} pending`;
      exportButton.disabled = summary.pending !== 0;
      if (summary.pending !== 0) {
        exportButton.textContent = "Copy verdict for Codex";
      }
      for (const card of cards) {
        const candidate = cardCandidate(card);
        const state = controller.state(candidate);
        card.dataset.reviewState = state.decision || "pending";
        card.hidden = Boolean(pendingOnly.checked && state.decision);
        for (const button of card.querySelectorAll("[data-decision]")) {
          button.setAttribute("aria-pressed", String(button.dataset.decision === state.decision));
        }
      }
    }

    for (const card of cards) {
      const candidate = cardCandidate(card);
      const state = controller.state(candidate);
      const notes = card.querySelector("[data-review-notes]");
      notes.value = state.notes;
      for (const button of card.querySelectorAll("[data-decision]")) {
        button.addEventListener("click", () => {
          const decision = button.dataset.decision === "clear" ? null : button.dataset.decision;
          controller.setDecision(candidate.candidate_id, candidate.candidate_digest, decision);
          exportOutput.value = "";
          reviewStatus.textContent = "Decision saved in this browser.";
          exportButton.textContent = "Copy verdict for Codex";
          render();
        });
      }
      notes.addEventListener("input", () => {
        controller.setNotes(candidate.candidate_id, candidate.candidate_digest, notes.value);
        exportOutput.value = "";
        reviewStatus.textContent = "Notes saved in this browser.";
        exportButton.textContent = "Copy verdict for Codex";
      });
    }

    pendingOnly.addEventListener("change", render);
    exportButton.addEventListener("click", async () => {
      try {
        const text = `${JSON.stringify(controller.buildVerdict(), null, 2)}\n`;
        exportOutput.value = text;
        const method = await copyText(text);
        exportButton.textContent = "Copied — paste into Codex";
        reviewStatus.textContent = method === "clipboard"
          ? "Complete verdict copied. Paste it into Codex."
          : "Complete verdict copied with the local fallback. Paste it into Codex.";
      } catch (error) {
        exportButton.textContent = "Copy verdict for Codex";
        exportOutput.focus();
        exportOutput.select();
        reviewStatus.textContent = `${error.message}. The complete JSON below is selected for manual copy.`;
      }
    });
    render();
    return controller;
  }

  const api = {
    DOWNSTREAM_CLAIMS,
    REVIEW_SCOPE,
    ReviewController,
    copyText,
    createMemoryStorage,
    identityKey,
    initializePage,
    storageKey,
  };
  root.SampleArtIsolationReview = api;
  if (root.document) {
    if (root.document.readyState === "loading") {
      root.document.addEventListener("DOMContentLoaded", () => initializePage(root.document));
    } else {
      initializePage(root.document);
    }
  }
})(typeof globalThis !== "undefined" ? globalThis : this);
