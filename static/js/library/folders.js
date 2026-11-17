/**
 * ReNote Folders & Multi-Select Management
 * Handles folder creation, title addition, selection mode, and bulk deletion.
 */

document.addEventListener('DOMContentLoaded', () => {
  // ---------------------------------------------------------------------------
  // Modal Utilities
  // ---------------------------------------------------------------------------
  function openModal(modalEl) {
    if (!modalEl) return;
    modalEl.removeAttribute('hidden');
    document.body.classList.add('modal-open');
    const firstInput = modalEl.querySelector('input:not([type="hidden"]), textarea');
    if (firstInput) {
      setTimeout(() => firstInput.focus(), 60);
    }
  }

  function closeModal(modalEl) {
    if (!modalEl) return;
    modalEl.setAttribute('hidden', '');
    document.body.classList.remove('modal-open');
  }

  // Close modals on Escape key or clicking outside dialog
  document.querySelectorAll('.custom-modal-backdrop').forEach((backdrop) => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        closeModal(backdrop);
      }
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.custom-modal-backdrop:not([hidden])').forEach((modal) => {
        closeModal(modal);
      });
    }
  });

  // ---------------------------------------------------------------------------
  // 1. Create New Folder Modal & Form
  // ---------------------------------------------------------------------------
  const newFolderModal = document.getElementById('newFolderModal');
  const btnOpenNewFolder = document.getElementById('btnOpenNewFolderModal');
  const btnOpenNewFolderEmpty = document.getElementById('btnOpenNewFolderModalEmpty');
  const btnCloseNewFolder = document.getElementById('btnCloseNewFolderModal');
  const btnCancelNewFolder = document.getElementById('btnCancelNewFolder');
  const folderNameInput = document.getElementById('folderNameInput');
  const folderDescInput = document.getElementById('folderDescInput');
  const folderNameCharCount = document.getElementById('folderNameCharCount');
  const folderDescCharCount = document.getElementById('folderDescCharCount');

  if (btnOpenNewFolder) {
    btnOpenNewFolder.addEventListener('click', () => openModal(newFolderModal));
  }
  if (btnOpenNewFolderEmpty) {
    btnOpenNewFolderEmpty.addEventListener('click', () => openModal(newFolderModal));
  }
  if (btnCloseNewFolder) {
    btnCloseNewFolder.addEventListener('click', () => closeModal(newFolderModal));
  }
  if (btnCancelNewFolder) {
    btnCancelNewFolder.addEventListener('click', () => closeModal(newFolderModal));
  }

  // Character counters
  if (folderNameInput && folderNameCharCount) {
    folderNameInput.addEventListener('input', () => {
      folderNameCharCount.textContent = folderNameInput.value.length;
    });
  }
  if (folderDescInput && folderDescCharCount) {
    folderDescInput.addEventListener('input', () => {
      folderDescCharCount.textContent = folderDescInput.value.length;
    });
  }

  // ---------------------------------------------------------------------------
  // 2. Folder Detail: Multi-Select Mode & Bulk Removal
  // ---------------------------------------------------------------------------
  const folderMain = document.getElementById('folderDetailMain');
  const folderItemsGrid = document.getElementById('folderItemsGrid');
  const btnToggleEditMode = document.getElementById('btnToggleEditMode');
  const multiSelectToolbar = document.getElementById('multiSelectToolbar');
  const selectedCountDisplay = document.getElementById('selectedCountDisplay');
  const btnToggleSelectAll = document.getElementById('btnToggleSelectAll');
  const btnDeleteSelected = document.getElementById('btnDeleteSelected');
  const btnExitEditMode = document.getElementById('btnExitEditMode');
  const folderCountBadge = document.getElementById('folderItemsCountBadge');
  const folderDynamicEmptyState = document.getElementById('folderDynamicEmptyState');

  let isEditMode = false;

  function updateSelectionState() {
    if (!folderItemsGrid) return;
    const cards = Array.from(folderItemsGrid.querySelectorAll('.folder-item-card'));
    const selectedCards = cards.filter((card) => card.classList.contains('is-selected'));
    const count = selectedCards.length;

    if (selectedCountDisplay) {
      selectedCountDisplay.textContent = `${count} selected`;
    }

    if (btnDeleteSelected) {
      btnDeleteSelected.disabled = count === 0;
      btnDeleteSelected.querySelector('span').textContent = count > 0 ? `Delete Selected (${count})` : 'Delete Selected';
    }

    if (btnToggleSelectAll) {
      if (cards.length > 0 && count === cards.length) {
        btnToggleSelectAll.textContent = 'Deselect All';
      } else {
        btnToggleSelectAll.textContent = 'Select All';
      }
    }
  }

  function setEditMode(enable) {
    isEditMode = enable;
    if (!folderItemsGrid) return;

    if (isEditMode) {
      folderItemsGrid.classList.add('edit-mode');
      if (multiSelectToolbar) {
        multiSelectToolbar.removeAttribute('hidden');
      }
      if (btnToggleEditMode) {
        btnToggleEditMode.classList.add('active');
        const label = document.getElementById('btnEditLabel');
        if (label) label.textContent = 'Editing...';
      }
    } else {
      folderItemsGrid.classList.remove('edit-mode');
      if (multiSelectToolbar) {
        multiSelectToolbar.setAttribute('hidden', '');
      }
      if (btnToggleEditMode) {
        btnToggleEditMode.classList.remove('active');
        const label = document.getElementById('btnEditLabel');
        if (label) label.textContent = 'Edit';
      }
      // Clear all selected states when exiting
      folderItemsGrid.querySelectorAll('.folder-item-card.is-selected').forEach((card) => {
        card.classList.remove('is-selected');
      });
    }
    updateSelectionState();
  }

  if (btnToggleEditMode) {
    btnToggleEditMode.addEventListener('click', () => {
      setEditMode(!isEditMode);
    });
  }

  if (btnExitEditMode) {
    btnExitEditMode.addEventListener('click', () => {
      setEditMode(false);
    });
  }

  // Handle card click inside folder items grid
  if (folderItemsGrid) {
    folderItemsGrid.addEventListener('click', (e) => {
      if (!isEditMode) return;

      const card = e.target.closest('.folder-item-card');
      if (!card) return;

      // Prevent navigating link in edit mode
      e.preventDefault();
      e.stopPropagation();

      card.classList.toggle('is-selected');
      updateSelectionState();
    });
  }

  // Select All / Deselect All
  if (btnToggleSelectAll && folderItemsGrid) {
    btnToggleSelectAll.addEventListener('click', () => {
      const cards = Array.from(folderItemsGrid.querySelectorAll('.folder-item-card'));
      const allSelected = cards.every((card) => card.classList.contains('is-selected'));

      cards.forEach((card) => {
        if (allSelected) {
          card.classList.remove('is-selected');
        } else {
          card.classList.add('is-selected');
        }
      });
      updateSelectionState();
    });
  }

  // Bulk Delete Action ("Delete all at once")
  if (btnDeleteSelected && folderMain) {
    btnDeleteSelected.addEventListener('click', async () => {
      const selectedCards = Array.from(folderItemsGrid.querySelectorAll('.folder-item-card.is-selected'));
      const count = selectedCards.length;
      if (count === 0) return;

      const confirmMsg = count === 1
        ? 'Remove this title from this folder?'
        : `Remove all ${count} selected titles from this folder?`;

      if (!window.confirm(confirmMsg)) return;

      const itemIds = selectedCards.map((card) => card.getAttribute('data-item-id')).filter(Boolean);
      const removeUrl = folderMain.getAttribute('data-remove-url');
      const csrfToken = folderMain.getAttribute('data-csrf') || (document.querySelector('[name=csrfmiddlewaretoken]')?.value);

      btnDeleteSelected.disabled = true;
      btnDeleteSelected.querySelector('span').textContent = 'Removing...';

      try {
        const response = await fetch(removeUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
          },
          body: JSON.stringify({ item_ids: itemIds }),
        });

        const data = await response.json();

        if (response.ok && data.success) {
          // Animate and remove cards
          selectedCards.forEach((card) => {
            card.classList.add('item-removing');
          });

          setTimeout(() => {
            selectedCards.forEach((card) => card.remove());

            // Recalculate remaining cards
            const remainingCards = folderItemsGrid.querySelectorAll('.folder-item-card');
            const remainingCount = remainingCards.length;

            if (folderCountBadge) {
              folderCountBadge.textContent = `${remainingCount} title${remainingCount !== 1 ? 's' : ''}`;
            }

            if (remainingCount === 0) {
              setEditMode(false);
              folderItemsGrid.style.display = 'none';
              if (btnToggleEditMode) btnToggleEditMode.style.display = 'none';
              if (folderDynamicEmptyState) folderDynamicEmptyState.style.display = 'flex';
            } else {
              updateSelectionState();
              setEditMode(false);
            }
          }, 300);
        } else {
          alert('Could not remove selected titles. Please try again.');
          btnDeleteSelected.disabled = false;
          updateSelectionState();
        }
      } catch (err) {
        console.error('Error removing items:', err);
        alert('A network error occurred. Please refresh and try again.');
        btnDeleteSelected.disabled = false;
        updateSelectionState();
      }
    });
  }

  // ---------------------------------------------------------------------------
  // 3. Add Titles to Folder Modal
  // ---------------------------------------------------------------------------
  const addTitlesModal = document.getElementById('addTitlesModal');
  const btnOpenAddTitlesModal = document.getElementById('btnOpenAddTitlesModal');
  const btnOpenAddTitlesModalEmpty = document.getElementById('btnOpenAddTitlesModalEmpty');
  const btnCloseAddTitlesModal = document.getElementById('btnCloseAddTitlesModal');
  const btnCancelAddTitles = document.getElementById('btnCancelAddTitles');
  const btnCancelAddTitlesEmpty = document.getElementById('btnCancelAddTitlesEmpty');
  const addTitlesSearchInput = document.getElementById('addTitlesSearchInput');
  const btnAddTitlesSearchClear = document.getElementById('btnAddTitlesSearchClear');
  const availableTitlesList = document.getElementById('availableTitlesList');
  const btnModalSelectAllAvailable = document.getElementById('btnModalSelectAllAvailable');
  const btnSubmitAddTitles = document.getElementById('btnSubmitAddTitles');
  const modalNoResultsMsg = document.getElementById('modalNoResultsMsg');
  const availableTitlesCount = document.getElementById('availableTitlesCount');

  if (btnOpenAddTitlesModal) {
    btnOpenAddTitlesModal.addEventListener('click', () => openModal(addTitlesModal));
  }
  if (btnOpenAddTitlesModalEmpty) {
    btnOpenAddTitlesModalEmpty.addEventListener('click', () => openModal(addTitlesModal));
  }
  if (btnCloseAddTitlesModal) {
    btnCloseAddTitlesModal.addEventListener('click', () => closeModal(addTitlesModal));
  }
  if (btnCancelAddTitles) {
    btnCancelAddTitles.addEventListener('click', () => closeModal(addTitlesModal));
  }
  if (btnCancelAddTitlesEmpty) {
    btnCancelAddTitlesEmpty.addEventListener('click', () => closeModal(addTitlesModal));
  }

  function updateAddTitlesModalSelection() {
    if (!availableTitlesList || !btnSubmitAddTitles) return;
    const checkedCheckboxes = availableTitlesList.querySelectorAll('.available-checkbox:checked');
    const count = checkedCheckboxes.length;

    btnSubmitAddTitles.disabled = count === 0;
    btnSubmitAddTitles.textContent = count > 0 ? `Add Selected (${count})` : 'Add Selected (0)';

    // Update parent item styles
    availableTitlesList.querySelectorAll('.available-title-item').forEach((item) => {
      const cb = item.querySelector('.available-checkbox');
      if (cb && cb.checked) {
        item.classList.add('selected');
      } else {
        item.classList.remove('selected');
      }
    });
  }

  if (availableTitlesList) {
    availableTitlesList.addEventListener('change', (e) => {
      if (e.target.matches('.available-checkbox')) {
        updateAddTitlesModalSelection();
      }
    });
  }

  // Filter titles inside Add Titles Modal
  if (addTitlesSearchInput && availableTitlesList) {
    addTitlesSearchInput.addEventListener('input', () => {
      const query = addTitlesSearchInput.value.trim().toLowerCase();
      const items = Array.from(availableTitlesList.querySelectorAll('.available-title-item'));
      let visibleCount = 0;

      if (btnAddTitlesSearchClear) {
        btnAddTitlesSearchClear.hidden = query.length === 0;
      }

      items.forEach((item) => {
        const title = item.getAttribute('data-title') || '';
        const type = item.getAttribute('data-type') || '';
        const matches = query === '' || title.includes(query) || type.includes(query);

        item.style.display = matches ? 'flex' : 'none';
        if (matches) visibleCount++;
      });

      if (modalNoResultsMsg) {
        modalNoResultsMsg.style.display = visibleCount === 0 ? 'block' : 'none';
      }
      if (availableTitlesCount) {
        availableTitlesCount.textContent = `${visibleCount} available`;
      }
    });

    if (btnAddTitlesSearchClear) {
      btnAddTitlesSearchClear.addEventListener('click', () => {
        addTitlesSearchInput.value = '';
        addTitlesSearchInput.dispatchEvent(new Event('input'));
        addTitlesSearchInput.focus();
      });
    }
  }

  // Select all visible items in Add Titles Modal
  if (btnModalSelectAllAvailable && availableTitlesList) {
    btnModalSelectAllAvailable.addEventListener('click', () => {
      const visibleCheckboxes = Array.from(availableTitlesList.querySelectorAll('.available-title-item'))
        .filter((item) => item.style.display !== 'none')
        .map((item) => item.querySelector('.available-checkbox'))
        .filter(Boolean);

      const allChecked = visibleCheckboxes.length > 0 && visibleCheckboxes.every((cb) => cb.checked);

      visibleCheckboxes.forEach((cb) => {
        cb.checked = !allChecked;
      });

      btnModalSelectAllAvailable.textContent = allChecked ? 'Select All' : 'Deselect All';
      updateAddTitlesModalSelection();
    });
  }

  // ---------------------------------------------------------------------------
  // 4. Delete Folder Confirmation Modal
  // ---------------------------------------------------------------------------
  const deleteFolderModal = document.getElementById('deleteFolderModal');
  const btnOpenDeleteFolderModal = document.getElementById('btnOpenDeleteFolderModal');
  const btnCloseDeleteFolderModal = document.getElementById('btnCloseDeleteFolderModal');
  const btnCancelDeleteFolder = document.getElementById('btnCancelDeleteFolder');

  if (btnOpenDeleteFolderModal) {
    btnOpenDeleteFolderModal.addEventListener('click', () => openModal(deleteFolderModal));
  }
  if (btnCloseDeleteFolderModal) {
    btnCloseDeleteFolderModal.addEventListener('click', () => closeModal(deleteFolderModal));
  }
  if (btnCancelDeleteFolder) {
    btnCancelDeleteFolder.addEventListener('click', () => closeModal(deleteFolderModal));
  }
});
