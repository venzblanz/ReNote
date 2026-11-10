
(function () {
  'use strict';

  const searchForm = document.getElementById('searchForm');
  const searchInput = document.getElementById('searchInput');
  const mediaTypeSelect = document.getElementById('mediaTypeSelect');
  const genreSelect = document.getElementById('genreSelect');
  const searchGenreChipsRow = document.getElementById('searchGenreChipsRow');
  const searchSpinner = document.getElementById('searchSpinner');
  const searchClearBtn = document.getElementById('searchClearBtn');
  const resultsContainer = document.getElementById('resultsContainer');
  const toastContainer = document.getElementById('toastContainer');
  const mediaGenresDataEl = document.getElementById('mediaGenresData');

  if (!searchForm || !searchInput || !resultsContainer) return;

  let mediaGenres = {};
  if (mediaGenresDataEl) {
    try {
      mediaGenres = JSON.parse(mediaGenresDataEl.textContent || '{}');
    } catch (e) {
      console.warn('Failed to parse media genres', e);
    }
  }

  let debounceTimer = null;
  let activeAbortController = null;
  let lastSearchedQuery = (searchInput.value || '').trim();
  let lastSearchedType = mediaTypeSelect ? mediaTypeSelect.value : 'anime';
  let lastSearchedGenre = genreSelect ? genreSelect.value : 'all';

  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta && meta.content) return meta.content;

    const cookieMatch = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    if (cookieMatch) return decodeURIComponent(cookieMatch[1]);

    const hiddenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (hiddenInput) return hiddenInput.value;

    return '';
  }

  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function truncateWords(text, count = 25) {
    if (!text) return 'No description available.';
    const words = String(text).trim().split(/\s+/);
    if (words.length <= count) return text;
    return words.slice(0, count).join(' ') + '…';
  }

  function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  function showToast(message, type = 'success') {
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
    toast.innerHTML = `
      <span class="toast-icon">${icon}</span>
      <span class="toast-msg">${escapeHtml(message)}</span>
    `;

    toastContainer.appendChild(toast);

    requestAnimationFrame(() => {
      toast.classList.add('visible');
    });

    setTimeout(() => {
      toast.classList.remove('visible');
      toast.addEventListener('transitionend', () => toast.remove(), { once: true });
    }, 3500);
  }

  function renderSkeleton() {
    return `
      <div class="results-grid">
        ${[1, 2, 3, 4, 5, 6].map(() => `
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

  function renderCard(item, csrfToken) {
    const title = item.media_title || 'Untitled';
    const escapedTitle = escapeHtml(title);
    const mediaType = item.media_type || (mediaTypeSelect ? mediaTypeSelect.value : 'anime');
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

    const genreInputs = (item.genre || [])
      .map((g) => `<input type="hidden" name="genre" value="${escapeHtml(g)}">`)
      .join('\n');

    return `
      <div class="result-card">
        <div class="cover" data-type="${escapeHtml(mediaType)}" title="View details for ${escapedTitle}">
          ${coverHtml}
        </div>
        <div class="card-body">
          <h3 class="card-title">
            <a href="#preview" class="card-title-link js-preview-trigger" title="View details for ${escapedTitle}">${escapedTitle}</a>
          </h3>
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

  function updateGenreOptions(mediaType, selectedGenre = 'all') {
    const genresList = mediaGenres[mediaType] || mediaGenres['anime'] || [];

    if (genreSelect) {
      genreSelect.innerHTML = '<option value="all">All Genres</option>';
      genresList.forEach((g) => {
        const opt = document.createElement('option');
        opt.value = g;
        opt.textContent = g;
        if (g.toLowerCase() === (selectedGenre || '').toLowerCase()) {
          opt.selected = true;
        }
        genreSelect.appendChild(opt);
      });
      if (selectedGenre && selectedGenre.toLowerCase() !== 'all') {
        genreSelect.value = selectedGenre;
      }
    }

    if (searchGenreChipsRow) {
      searchGenreChipsRow.innerHTML = `<button type="button" class="genre-chip ${!selectedGenre || selectedGenre.toLowerCase() === 'all' ? 'active' : ''}" data-genre="all">All</button>`;
      genresList.forEach((g) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `genre-chip ${selectedGenre && selectedGenre.toLowerCase() === g.toLowerCase() ? 'active' : ''}`;
        btn.dataset.genre = g;
        btn.textContent = g;
        searchGenreChipsRow.appendChild(btn);
      });
    }
  }

  function updateUrl(query, mediaType, genre, push = false) {
    const url = new URL(window.location.href);
    if (query) {
      url.searchParams.set('q', query);
    } else {
      url.searchParams.delete('q');
    }
    url.searchParams.set('media_type', mediaType);

    if (genre && genre.toLowerCase() !== 'all') {
      url.searchParams.set('genre', genre);
    } else {
      url.searchParams.delete('genre');
    }

    if (push) {
      window.history.pushState({ q: query, media_type: mediaType, genre: genre }, '', url.toString());
    } else {
      window.history.replaceState({ q: query, media_type: mediaType, genre: genre }, '', url.toString());
    }
  }

  async function performSearch(query, mediaType, genre = 'all', options = { pushUrl: false }) {
    const cleanQuery = (query || '').trim();
    const cleanGenre = (genre || 'all').trim();
    const isGenreActive = cleanGenre && cleanGenre.toLowerCase() !== 'all';

    if (!cleanQuery && !isGenreActive) {
      if (activeAbortController) {
        activeAbortController.abort();
        activeAbortController = null;
      }
      if (searchSpinner) searchSpinner.hidden = true;
      if (searchClearBtn) searchClearBtn.hidden = true;
      resultsContainer.innerHTML =
        '<p class="empty-state">Pick a media type and search by title, or pick a genre above to explore titles.</p>';
      lastSearchedQuery = '';
      lastSearchedType = mediaType;
      lastSearchedGenre = 'all';
      updateUrl('', mediaType, 'all', options.pushUrl);
      return;
    }

    if (searchClearBtn) {
      searchClearBtn.hidden = !cleanQuery;
    }

    if (
      cleanQuery === lastSearchedQuery &&
      mediaType === lastSearchedType &&
      cleanGenre.toLowerCase() === lastSearchedGenre.toLowerCase() &&
      !options.force
    ) {
      return;
    }

    lastSearchedQuery = cleanQuery;
    lastSearchedType = mediaType;
    lastSearchedGenre = cleanGenre;

    if (activeAbortController) {
      activeAbortController.abort();
    }
    activeAbortController = new AbortController();

    if (searchSpinner) searchSpinner.hidden = false;
    resultsContainer.innerHTML = renderSkeleton();

    updateUrl(cleanQuery, mediaType, cleanGenre, options.pushUrl);

    try {
      const genreParam = isGenreActive ? `&genre=${encodeURIComponent(cleanGenre)}` : '';
      const queryParam = cleanQuery ? `&q=${encodeURIComponent(cleanQuery)}` : '';
      const endpoint = `${searchForm.action || '/library/add/'}?media_type=${encodeURIComponent(mediaType)}${queryParam}${genreParam}&format=json`;

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
        const filterDesc = [
          cleanQuery ? `"${cleanQuery}"` : '',
          isGenreActive ? `in genre ${cleanGenre}` : '',
          `in ${capitalize(mediaType)}`,
        ]
          .filter(Boolean)
          .join(' ');
        resultsContainer.innerHTML = `
          <p class="empty-state">No results found for ${escapeHtml(filterDesc)}. Try a different search term or genre.</p>
        `;
      } else {
        const cardsHtml = data.results.map((item) => renderCard(item, csrfToken)).join('');
        resultsContainer.innerHTML = `<div class="results-grid">${cardsHtml}</div>`;
      }
    } catch (err) {
      if (err.name === 'AbortError') {
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

  searchInput.addEventListener('input', () => {
    const query = searchInput.value.trim();
    const mediaType = mediaTypeSelect ? mediaTypeSelect.value : 'anime';
    const genre = genreSelect ? genreSelect.value : 'all';

    if (searchClearBtn) {
      searchClearBtn.hidden = !query;
    }

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      performSearch(query, mediaType, genre, { pushUrl: false });
    }, 350);
  });

  if (mediaTypeSelect) {
    mediaTypeSelect.addEventListener('change', () => {
      const mediaType = mediaTypeSelect.value;
      updateGenreOptions(mediaType, 'all');
      const query = searchInput.value.trim();
      performSearch(query, mediaType, 'all', { pushUrl: true, force: true });
    });
  }

  if (genreSelect) {
    genreSelect.addEventListener('change', () => {
      const genre = genreSelect.value;
      if (searchGenreChipsRow) {
        searchGenreChipsRow.querySelectorAll('.genre-chip').forEach((c) => {
          c.classList.toggle('active', (c.dataset.genre || '').toLowerCase() === genre.toLowerCase());
        });
      }
      const query = searchInput.value.trim();
      const mediaType = mediaTypeSelect ? mediaTypeSelect.value : 'anime';
      performSearch(query, mediaType, genre, { pushUrl: true, force: true });
    });
  }

  if (searchGenreChipsRow) {
    searchGenreChipsRow.addEventListener('click', (e) => {
      const chip = e.target.closest('.genre-chip');
      if (!chip) return;
      const genre = chip.dataset.genre || 'all';

      if (genreSelect) {
        genreSelect.value = genre;
      }
      searchGenreChipsRow.querySelectorAll('.genre-chip').forEach((c) => {
        c.classList.toggle('active', (c.dataset.genre || '').toLowerCase() === genre.toLowerCase());
      });

      const query = searchInput.value.trim();
      const mediaType = mediaTypeSelect ? mediaTypeSelect.value : 'anime';
      performSearch(query, mediaType, genre, { pushUrl: true, force: true });
    });
  }

  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    clearTimeout(debounceTimer);
    const query = searchInput.value.trim();
    const mediaType = mediaTypeSelect ? mediaTypeSelect.value : 'anime';
    const genre = genreSelect ? genreSelect.value : 'all';
    performSearch(query, mediaType, genre, { pushUrl: true, force: true });
  });

  if (searchClearBtn) {
    searchClearBtn.addEventListener('click', () => {
      searchInput.value = '';
      searchInput.focus();
      searchClearBtn.hidden = true;
      const mediaType = mediaTypeSelect ? mediaTypeSelect.value : 'anime';
      const genre = genreSelect ? genreSelect.value : 'all';
      performSearch('', mediaType, genre, { pushUrl: true, force: true });
    });
  }

  function openResultPreview(card) {
    const addForm = card.querySelector('.add-form');
    if (!addForm) return;

    const previewForm = document.createElement('form');
    previewForm.method = 'POST';
    previewForm.action = resultsContainer.dataset.previewUrl || '/library/preview/';
    previewForm.style.display = 'none';

    const appendField = (name, value) => {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = name;
      input.value = value ?? '';
      previewForm.appendChild(input);
    };

    appendField('csrfmiddlewaretoken', getCsrfToken());

    addForm.querySelectorAll('input[type="hidden"]').forEach((field) => {
      if (field.name && field.name !== 'csrfmiddlewaretoken') {
        appendField(field.name, field.value);
      }
    });

    appendField('search_q', searchInput.value.trim());
    appendField('search_media_type', mediaTypeSelect ? mediaTypeSelect.value : 'anime');
    appendField('search_genre', genreSelect ? genreSelect.value : 'all');

    document.body.appendChild(previewForm);
    previewForm.submit();
  }

  resultsContainer.addEventListener('click', (e) => {
    if (e.target.closest('.add-form')) return;

    const card = e.target.closest('.result-card:not(.skeleton-card)');
    if (!card) return;

    if (e.target.closest('.js-preview-trigger')) {
      e.preventDefault();
    }
    openResultPreview(card);
  });

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

  window.addEventListener('popstate', (e) => {
    const url = new URL(window.location.href);
    const q = url.searchParams.get('q') || '';
    const mediaType = url.searchParams.get('media_type') || 'anime';
    const genre = url.searchParams.get('genre') || 'all';

    searchInput.value = q;
    if (mediaTypeSelect) mediaTypeSelect.value = mediaType;
    updateGenreOptions(mediaType, genre);
    if (searchClearBtn) searchClearBtn.hidden = !q;

    performSearch(q, mediaType, genre, { pushUrl: false, force: true });
  });

  if (searchInput.value.trim() && searchClearBtn) {
    searchClearBtn.hidden = false;
  }
})();
