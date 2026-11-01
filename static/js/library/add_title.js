/**
 * ReNote — Add Title Live Search & Library Actions
 * Asynchronous search and in-place save without page refresh.
 */

(function () {
  'use strict';

  // DOM Elements
  const searchForm = document.getElementById('searchForm');
  const searchInput = document.getElementById('searchInput');
  const mediaTypeSelect = document.getElementById('mediaTypeSelect');
  const searchSpinner = document.getElementById('searchSpinner');
  const searchClearBtn = document.getElementById('searchClearBtn');
  const resultsContainer = document.getElementById('resultsContainer');
  const toastContainer = document.getElementById('toastContainer');

  if (!searchForm || !searchInput || !resultsContainer) return;

  // State
  let debounceTimer = null;
  let activeAbortController = null;
  let lastSearchedQuery = (searchInput.value || '').trim();
  let lastSearchedType = mediaTypeSelect ? mediaTypeSelect.value : 'anime';

  // Get CSRF Token helper
  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) return meta.content;

    const cookieMatch = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    if (cookieMatch) return decodeURIComponent(cookieMatch[1]);

    const hiddenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (hiddenInput) return hiddenInput.value;

    return '';
  }

  // HTML escape helper
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Description word truncation
  function truncateWords(text, count = 25) {
    if (!text) return 'No description available.';
    const words = String(text).trim().split(/\s+/);
    if (words.length <= count) return text;
    return words.slice(0, count).join(' ') + '…';
  }

  // Capitalize media type helper
  function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  // Toast Notification
  function showToast(message, type = 'success') {
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ');
    toast.innerHTML = `
      <span class="toast-icon">${icon}</span>
      <span class="toast-msg">${escapeHtml(message)}</span>
    `;

    toastContainer.appendChild(toast);

    // Animation frames
    requestAnimationFrame(() => {
      toast.classList.add('visible');
    });

    setTimeout(() => {
      toast.classList.remove('visible');
      toast.addEventListener('transitionend', () => toast.remove(), { once: true });
    }, 3500);
  }

  // Render Skeleton Loader
  function renderSkeleton() {
    return `
      <div class="results-grid">
        ${[1, 2, 3, 4].map(() => `
          <div class="result-card skeleton-card">
            <div class="skeleton-cover"></div>
            <div class="card-body">
              <div class="skeleton-line line-title"></div>
              <div class="skeleton-line line-meta"></div>
              <div class="skeleton-line line-desc"></div>
              <div class="skeleton-btn"></div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  }

  // Render a single Media Result Card
  function renderCard(item, csrfToken) {
    const title = item.media_title || 'Untitled';
    const escapedTitle = escapeHtml(title);
    const mediaType = item.media_type || 'anime';
    const year = item.media_year
      ? `<span class="card-year">${escapeHtml(item.media_year)}</span>`
      : '';
    const rating = item.media_rate
      ? `<span class="card-rating">★ ${escapeHtml(item.media_rate)}</span>`
      : '';
    const desc = escapeHtml(truncateWords(item.media_description, 25));

    const coverHtml = item.media_image
      ? `<img src="${escapeHtml(item.media_image)}" alt="${escapedTitle}" loading="lazy">`
      : `<div class="cover-placeholder">${escapedTitle}</div>`;

    const genreInputs = (item.genre || []).map(g =>
      `<input type="hidden" name="genre" value="${escapeHtml(g)}">`
    ).join('\n');

    return `
      <div class="result-card">
        <div class="cover" data-type="${escapeHtml(mediaType)}">
          ${coverHtml}
        </div>
        <div class="card-body">
          <h3 class="card-title">${escapedTitle}</h3>
          <div class="card-meta">
            ${year}
            ${rating}
          </div>
          <p class="card-desc">${desc}</p>
          <form method="post" action="/library/save/" class="add-form">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
            <input type="hidden" name="external_id" value="${escapeHtml(item.external_id || '')}">
            <input type="hidden" name="media_type" value="${escapeHtml(mediaType)}">
            <input type="hidden" name="media_title" value="${escapedTitle}">
            <input type="hidden" name="media_description" value="${escapeHtml(item.media_description || '')}">
            <input type="hidden" name="media_image" value="${escapeHtml(item.media_image || '')}">
            <input type="hidden" name="media_release_date" value="${escapeHtml(item.media_release_date || '')}">
            <input type="hidden" name="media_rate" value="${escapeHtml(item.media_rate || '')}">
            ${genreInputs}
            <button type="submit" class="btn-add">Add to library</button>
          </form>
        </div>
      </div>
    `;
  }

  // Update URL without page reload
  function updateUrl(query, mediaType, push = false) {
    const url = new URL(window.location.href);
    if (query) {
      url.searchParams.set('q', query);
    } else {
      url.searchParams.delete('q');
    }
    url.searchParams.set('media_type', mediaType);

    if (push) {
      window.history.pushState({ q: query, media_type: mediaType }, '', url.toString());
    } else {
      window.history.replaceState({ q: query, media_type: mediaType }, '', url.toString());
    }
  }

  // Perform Live Search
  async function performSearch(query, mediaType, options = { pushUrl: false }) {
    // If empty query, reset to welcoming empty state
    if (!query) {
      if (activeAbortController) {
        activeAbortController.abort();
        activeAbortController = null;
      }
      if (searchSpinner) searchSpinner.hidden = true;
      if (searchClearBtn) searchClearBtn.hidden = true;
      resultsContainer.innerHTML = '<p class="empty-state">Pick a media type and search for something to add.</p>';
      lastSearchedQuery = '';
      lastSearchedType = mediaType;
      updateUrl('', mediaType, options.pushUrl);
      return;
    }

    if (searchClearBtn) searchClearBtn.hidden = false;

    // Avoid duplicate requests
    if (query === lastSearchedQuery && mediaType === lastSearchedType && !options.force) {
      return;
    }

    lastSearchedQuery = query;
    lastSearchedType = mediaType;

    // Cancel in-flight search
    if (activeAbortController) {
      activeAbortController.abort();
    }
    activeAbortController = new AbortController();

    // Show spinner & skeletons
    if (searchSpinner) searchSpinner.hidden = false;
    resultsContainer.innerHTML = renderSkeleton();

    updateUrl(query, mediaType, options.pushUrl);

    try {
      const endpoint = `${searchForm.action || '/library/add/'}?media_type=${encodeURIComponent(mediaType)}&q=${encodeURIComponent(query)}&format=json`;
      const res = await fetch(endpoint, {
        signal: activeAbortController.signal,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Accept': 'application/json',
        },
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = await res.json();
      const csrfToken = getCsrfToken();

      if (data.error) {
        resultsContainer.innerHTML = `<p class="flash-message error">${escapeHtml(data.error)}</p>`;
      } else if (!data.results || data.results.length === 0) {
        resultsContainer.innerHTML = `
          <p class="empty-state">No results for "${escapeHtml(query)}" in ${capitalize(mediaType)}. Try a different search or media type.</p>
        `;
      } else {
        const cardsHtml = data.results.map(item => renderCard(item, csrfToken)).join('');
        resultsContainer.innerHTML = `<div class="results-grid">${cardsHtml}</div>`;
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        // Aborted because a newer search was initiated; ignore
        return;
      }
      console.error('Search error:', err);
      resultsContainer.innerHTML = `
        <p class="flash-message error">Couldn't reach the search service right now. Try again in a moment.</p>
      `;
    } finally {
      if (searchSpinner) searchSpinner.hidden = true;
    }
  }

  // Event: Search Input with debouncing
  searchInput.addEventListener('input', () => {
    const query = searchInput.value.trim();
    const mediaType = mediaTypeSelect ? mediaTypeSelect.value : 'anime';

    if (searchClearBtn) {
      searchClearBtn.hidden = !query;
    }

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      performSearch(query, mediaType, { pushUrl: false });
    }, 350);
  });

  // Event: Media Type select change
  if (mediaTypeSelect) {
    mediaTypeSelect.addEventListener('change', () => {
      const query = searchInput.value.trim();
      const mediaType = mediaTypeSelect.value;
      if (query) {
        performSearch(query, mediaType, { pushUrl: true, force: true });
      }
    });
  }

  // Event: Form submit (immediate search)
  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    clearTimeout(debounceTimer);
    const query = searchInput.value.trim();
    const mediaType = mediaTypeSelect ? mediaTypeSelect.value : 'anime';
    performSearch(query, mediaType, { pushUrl: true, force: true });
  });

  // Event: Clear button click
  if (searchClearBtn) {
    searchClearBtn.addEventListener('click', () => {
      searchInput.value = '';
      searchInput.focus();
      searchClearBtn.hidden = true;
      performSearch('', mediaTypeSelect ? mediaTypeSelect.value : 'anime', { pushUrl: true });
    });
  }

  // Event: In-place Add to Library form submission
  resultsContainer.addEventListener('submit', async (e) => {
    const form = e.target.closest('.add-form');
    if (!form) return;

    e.preventDefault();
    const submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn || submitBtn.disabled) return;

    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="btn-spinner"></span> Saving…';

    try {
      const formData = new FormData(form);
      formData.append('format', 'json');

      const csrfToken = getCsrfToken();

      const response = await fetch(form.action || '/library/save/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        if (data.created) {
          submitBtn.classList.add('btn-added');
          submitBtn.innerHTML = '<span>✓</span> Added';
          showToast(data.message || `Added "${data.media_title}" to your library!`, 'success');
        } else {
          submitBtn.classList.add('btn-added', 'btn-in-library');
          submitBtn.innerHTML = '<span>✓</span> In library';
          showToast(data.message || `"${data.media_title}" is already in your library.`, 'info');
        }
      } else {
        throw new Error(data.error || 'Failed to save');
      }
    } catch (err) {
      console.error('Save error:', err);
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
      showToast('Could not save to library. Please try again.', 'error');
    }
  });

  // Event: Browser Back / Forward navigation
  window.addEventListener('popstate', (e) => {
    const url = new URL(window.location.href);
    const q = url.searchParams.get('q') || '';
    const mediaType = url.searchParams.get('media_type') || 'anime';

    searchInput.value = q;
    if (mediaTypeSelect) mediaTypeSelect.value = mediaType;
    if (searchClearBtn) searchClearBtn.hidden = !q;

    performSearch(q, mediaType, { pushUrl: false, force: true });
  });

  // Initial check: if initial query is present, ensure clear button is visible
  if (searchInput.value.trim() && searchClearBtn) {
    searchClearBtn.hidden = false;
  }
})();
