/**
 * app.js - Client-Side Controller for CineMatch AI
 * Handles API calls, dynamic rendering, tab switching, TF-IDF comparisons, and local watchlist.
 */

document.addEventListener("DOMContentLoaded", () => {
    // State Store
    const state = {
        allMovies: [],
        currentSourceId: 1, // Default: Inception
        currentRecommendations: [],
        watchlist: JSON.parse(localStorage.getItem("cinematch_watchlist") || "[]"),
        corpusStats: null
    };

    // DOM Elements
    const elements = {
        // Nav Tabs
        tabs: document.querySelectorAll(".nav-tab"),
        panes: document.querySelectorAll(".tab-pane"),
        watchlistCountBadge: document.getElementById("watchlist-count"),
        headerVocabSize: document.getElementById("header-vocab-size"),

        // Tab 1: Movie Recommendation
        searchInput: document.getElementById("movie-search-input"),
        autocompleteResults: document.getElementById("autocomplete-results"),
        btnClearSearch: document.getElementById("btn-clear-search"),
        quickPickChips: document.getElementById("quick-pick-chips"),
        filterGenre: document.getElementById("filter-genre"),
        filterRating: document.getElementById("filter-rating"),
        ratingValDisplay: document.getElementById("rating-val-display"),
        filterTopN: document.getElementById("filter-top-n"),
        btnTriggerRecommend: document.getElementById("btn-trigger-recommend"),
        
        // Source Movie Showcase
        srcPoster: document.getElementById("src-poster"),
        srcTitle: document.getElementById("src-title"),
        srcYear: document.getElementById("src-year"),
        srcRating: document.getElementById("src-rating"),
        srcRuntime: document.getElementById("src-runtime"),
        srcDirector: document.getElementById("src-director"),
        srcGenres: document.getElementById("src-genres"),
        srcOverview: document.getElementById("src-overview"),
        srcTfidfTerms: document.getElementById("src-tfidf-terms"),
        recommendationsGrid: document.getElementById("recommendations-grid"),

        // Tab 2: Prompt Search
        promptInput: document.getElementById("prompt-input"),
        btnSearchPrompt: document.getElementById("btn-search-prompt"),
        promptResultsGrid: document.getElementById("prompt-results-grid"),
        promptQueryDisplay: document.getElementById("prompt-query-display"),
        presetBtns: document.querySelectorAll(".preset-btn"),

        // Tab 3: Compare
        compareSelectA: document.getElementById("compare-select-a"),
        compareSelectB: document.getElementById("compare-select-b"),
        comparePreviewA: document.getElementById("compare-preview-a"),
        comparePreviewB: document.getElementById("compare-preview-b"),
        btnRunCompare: document.getElementById("btn-run-compare"),
        compareResultContainer: document.getElementById("compare-result-container"),
        compareScorePercent: document.getElementById("compare-score-percent"),
        compareRawCosine: document.getElementById("compare-raw-cosine"),
        compareTitlePair: document.getElementById("compare-title-pair"),
        compareTermsTbody: document.getElementById("compare-terms-tbody"),

        // Tab 4: Visualizer
        visTotalMovies: document.getElementById("vis-total-movies"),
        visVocabSize: document.getElementById("vis-vocab-size"),
        cloudHighIdf: document.getElementById("cloud-high-idf"),
        cloudLowIdf: document.getElementById("cloud-low-idf"),

        // Tab 5: Watchlist
        watchlistGrid: document.getElementById("watchlist-grid"),
        btnClearWatchlist: document.getElementById("btn-clear-watchlist"),

        // Modal & Toast
        movieModal: document.getElementById("movie-modal"),
        modalContent: document.getElementById("modal-content"),
        btnCloseModal: document.getElementById("btn-close-modal"),
        toastNotify: document.getElementById("toast-notify"),
        toastText: document.getElementById("toast-text")
    };

    // ==========================================
    // INITIALIZATION & DATA FETCHING
    // ==========================================

    async function init() {
        setupEventListeners();
        updateWatchlistBadge();
        await fetchAllMovies();
        await fetchStats();
        await loadSourceMovieAndRecommend(state.currentSourceId);
        populateCompareSelectors();
    }

    async function fetchAllMovies() {
        try {
            const res = await fetch("/api/movies");
            const data = await res.json();
            if (data.status === "success") {
                state.allMovies = data.movies;
            }
        } catch (err) {
            console.error("Failed to load movies:", err);
            showToast("Failed to load movies catalog");
        }
    }

    async function fetchStats() {
        try {
            const res = await fetch("/api/stats");
            const data = await res.json();
            if (data.status === "success") {
                state.corpusStats = data.stats;
                renderStats(data.stats);
            }
        } catch (err) {
            console.error("Failed to fetch stats:", err);
        }
    }

    function renderStats(stats) {
        if (elements.headerVocabSize) {
            elements.headerVocabSize.textContent = stats.vocab_size.toLocaleString();
        }
        if (elements.visTotalMovies) {
            elements.visTotalMovies.textContent = stats.total_movies;
        }
        if (elements.visVocabSize) {
            elements.visVocabSize.textContent = stats.vocab_size.toLocaleString();
        }

        // Populate Genre dropdown filter
        if (elements.filterGenre && stats.genres) {
            elements.filterGenre.innerHTML = '<option value="All">All Genres</option>';
            stats.genres.forEach(g => {
                const opt = document.createElement("option");
                opt.value = g;
                opt.textContent = g;
                elements.filterGenre.appendChild(opt);
            });
        }

        // Render TF-IDF visualizer terms clouds
        if (elements.cloudHighIdf && stats.sample_high_idf_terms) {
            elements.cloudHighIdf.innerHTML = stats.sample_high_idf_terms.map(item => `
                <span class="cloud-pill high" title="IDF: ${item.idf}">${item.term} <strong>(${item.idf})</strong></span>
            `).join("");
        }

        if (elements.cloudLowIdf && stats.sample_common_terms) {
            elements.cloudLowIdf.innerHTML = stats.sample_common_terms.map(item => `
                <span class="cloud-pill" title="IDF: ${item.idf}">${item.term} <strong>(${item.idf})</strong></span>
            `).join("");
        }
    }

    // ==========================================
    // SOURCE MOVIE & RECOMMENDATION LOGIC
    // ==========================================

    async function loadSourceMovieAndRecommend(movieId) {
        state.currentSourceId = movieId;
        
        // Fetch Movie Details
        try {
            const movieRes = await fetch(`/api/movie/${movieId}`);
            const movieData = await movieRes.json();
            if (movieData.status === "success") {
                renderSourceMovieBanner(movieData.movie);
            }
        } catch (err) {
            console.error(err);
        }

        // Fetch Recommendations
        await fetchRecommendations();
    }

    function renderSourceMovieBanner(movie) {
        elements.srcPoster.src = movie.poster_url || "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80";
        elements.srcPoster.alt = movie.title;
        elements.srcTitle.textContent = movie.title;
        elements.srcYear.textContent = movie.year;
        elements.srcRating.textContent = movie.rating;
        elements.srcRuntime.textContent = movie.runtime;
        elements.srcDirector.textContent = movie.director;
        elements.srcOverview.textContent = movie.overview;

        // Render Genres
        const genres = movie.genres ? movie.genres.split(",") : [];
        elements.srcGenres.innerHTML = genres.map(g => `<span class="genre-pill">${g.trim()}</span>`).join("");

        // Render Top TF-IDF Terms
        if (movie.top_keywords && movie.top_keywords.length > 0) {
            elements.srcTfidfTerms.innerHTML = movie.top_keywords.map(k => `
                <div class="tfidf-tag">
                    ${k.term} <span>${k.tfidf_score}</span>
                </div>
            `).join("");
        } else {
            elements.srcTfidfTerms.innerHTML = '<span class="text-muted">No terms calculated</span>';
        }
    }

    async function fetchRecommendations() {
        const topN = elements.filterTopN.value;
        const genre = elements.filterGenre.value;
        const minRating = elements.filterRating.value;

        elements.recommendationsGrid.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner fa-spin empty-icon"></i>
                <p>Vectorizing corpus and computing Cosine Similarities...</p>
            </div>
        `;

        try {
            const url = `/api/recommend?movie_id=${state.currentSourceId}&top_n=${topN}&genre=${encodeURIComponent(genre)}&min_rating=${minRating}`;
            const res = await fetch(url);
            const data = await res.json();

            if (data.status === "success") {
                state.currentRecommendations = data.recommendations;
                renderMovieCards(elements.recommendationsGrid, data.recommendations);
            } else {
                elements.recommendationsGrid.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-triangle-exclamation empty-icon"></i>
                        <p>${data.message || 'No recommendations found.'}</p>
                    </div>
                `;
            }
        } catch (err) {
            console.error("Error fetching recommendations:", err);
            elements.recommendationsGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-circle-exclamation empty-icon"></i>
                    <p>Failed to load recommendations. Please try again.</p>
                </div>
            `;
        }
    }

    // ==========================================
    // RENDER MOVIE CARDS (REUSABLE)
    // ==========================================

    function renderMovieCards(container, movies, isWatchlist = false) {
        if (!movies || movies.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-film empty-icon"></i>
                    <p>No matching movies found for the selected criteria.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = movies.map(movie => {
            const isBookmarked = state.watchlist.some(m => m.id === movie.id);
            const genres = movie.genres ? movie.genres.split(",").slice(0, 3) : [];
            const isHighMatch = movie.similarity_percent && movie.similarity_percent >= 5.0;

            const sharedTermsHtml = movie.shared_terms && movie.shared_terms.length > 0 ? `
                <div class="shared-terms-container">
                    <span class="shared-terms-label"><i class="fa-solid fa-link"></i> Thematic DNA:</span>
                    <div class="shared-terms-chips">
                        ${movie.shared_terms.map(t => `<span class="shared-term-chip" title="Contribution: ${t.contribution}">${t.term}</span>`).join("")}
                    </div>
                </div>
            ` : '';

            const similarityBadgeHtml = movie.similarity_percent !== undefined ? `
                <div class="similarity-badge ${isHighMatch ? 'high-match' : ''}">
                    ${movie.similarity_percent}% Affinity
                </div>
            ` : '';

            return `
                <div class="movie-card" data-id="${movie.id}">
                    <div class="movie-card-poster-wrap">
                        <img src="${movie.poster_url || 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80'}" alt="${movie.title}" class="movie-card-poster" loading="lazy">
                        ${similarityBadgeHtml}
                        <button class="btn-bookmark-card ${isBookmarked ? 'bookmarked' : ''}" data-id="${movie.id}" title="${isBookmarked ? 'Remove from Watchlist' : 'Add to Watchlist'}">
                            <i class="${isBookmarked ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i>
                        </button>
                    </div>

                    <div class="movie-card-body">
                        <div class="movie-card-header">
                            <span>${movie.year}</span>
                            <span class="movie-card-rating"><i class="fa-solid fa-star"></i> ${movie.rating}</span>
                        </div>
                        <h3 class="movie-card-title">${movie.title}</h3>
                        <div class="movie-card-genres">
                            ${genres.map(g => `<span class="mini-genre-pill">${g.trim()}</span>`).join("")}
                        </div>
                        <p class="movie-card-overview">${movie.overview || ''}</p>
                        
                        ${sharedTermsHtml}

                        <div class="movie-card-actions">
                            <button class="btn-card-action primary btn-inspect" data-id="${movie.id}">
                                <i class="fa-regular fa-file-lines"></i> Details
                            </button>
                            <button class="btn-card-action btn-find-similar" data-id="${movie.id}">
                                <i class="fa-solid fa-compass"></i> Find Similar
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join("");

        // Attach action handlers for newly rendered cards
        container.querySelectorAll(".btn-bookmark-card").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                const id = parseInt(btn.dataset.id);
                toggleWatchlist(id);
            });
        });

        container.querySelectorAll(".btn-inspect").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                const id = parseInt(btn.dataset.id);
                openMovieModal(id);
            });
        });

        container.querySelectorAll(".btn-find-similar").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.stopPropagation();
                const id = parseInt(btn.dataset.id);
                switchTab("tab-recommend");
                loadSourceMovieAndRecommend(id);
                window.scrollTo({ top: 0, behavior: "smooth" });
            });
        });
    }

    // ==========================================
    // AUTOCOMPLETE SEARCH LOGIC
    // ==========================================

    elements.searchInput.addEventListener("input", (e) => {
        const query = e.target.value.trim().toLowerCase();
        if (query.length > 0) {
            elements.btnClearSearch.style.display = "block";
            const matches = state.allMovies.filter(m => 
                m.title.toLowerCase().includes(query) || 
                (m.director && m.director.toLowerCase().includes(query)) ||
                (m.genres && m.genres.toLowerCase().includes(query))
            ).slice(0, 8);

            renderAutocompleteDropdown(matches);
        } else {
            elements.btnClearSearch.style.display = "none";
            elements.autocompleteResults.classList.remove("active");
        }
    });

    elements.btnClearSearch.addEventListener("click", () => {
        elements.searchInput.value = "";
        elements.btnClearSearch.style.display = "none";
        elements.autocompleteResults.classList.remove("active");
    });

    function renderAutocompleteDropdown(matches) {
        if (!matches || matches.length === 0) {
            elements.autocompleteResults.innerHTML = `
                <div class="autocomplete-item" style="cursor:default;">
                    <div class="autocomplete-info"><p>No movies found matching query</p></div>
                </div>
            `;
            elements.autocompleteResults.classList.add("active");
            return;
        }

        elements.autocompleteResults.innerHTML = matches.map(movie => `
            <div class="autocomplete-item" data-id="${movie.id}">
                <img src="${movie.poster_url}" alt="${movie.title}" class="autocomplete-poster">
                <div class="autocomplete-info">
                    <h4>${movie.title} (${movie.year})</h4>
                    <p>${movie.genres} • Dir: ${movie.director}</p>
                </div>
            </div>
        `).join("");

        elements.autocompleteResults.classList.add("active");

        elements.autocompleteResults.querySelectorAll(".autocomplete-item").forEach(item => {
            item.addEventListener("click", () => {
                const id = parseInt(item.dataset.id);
                if (id) {
                    elements.searchInput.value = "";
                    elements.btnClearSearch.style.display = "none";
                    elements.autocompleteResults.classList.remove("active");
                    loadSourceMovieAndRecommend(id);
                }
            });
        });
    }

    // Close autocomplete on click outside
    document.addEventListener("click", (e) => {
        if (!elements.searchInput.contains(e.target) && !elements.autocompleteResults.contains(e.target)) {
            elements.autocompleteResults.classList.remove("active");
        }
    });

    // Quick pick chips
    elements.quickPickChips.querySelectorAll(".chip").forEach(chip => {
        chip.addEventListener("click", () => {
            elements.quickPickChips.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
            chip.classList.add("active");
            const id = parseInt(chip.dataset.id);
            loadSourceMovieAndRecommend(id);
        });
    });

    // Rating Slider Display
    elements.filterRating.addEventListener("input", (e) => {
        elements.ratingValDisplay.textContent = parseFloat(e.target.value).toFixed(1);
    });

    // Refresh trigger
    elements.btnTriggerRecommend.addEventListener("click", () => {
        fetchRecommendations();
    });

    // ==========================================
    // TAB 2: PROMPT SEARCH LOGIC
    // ==========================================

    elements.btnSearchPrompt.addEventListener("click", () => {
        const prompt = elements.promptInput.value.trim();
        if (!prompt) {
            showToast("Please enter a plot idea or mood description");
            return;
        }
        executePromptSearch(prompt);
    });

    elements.presetBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const text = btn.dataset.text;
            elements.promptInput.value = text;
            executePromptSearch(text);
        });
    });

    async function executePromptSearch(prompt) {
        elements.promptQueryDisplay.textContent = `Analyzing: "${prompt}"`;
        elements.promptResultsGrid.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner fa-spin empty-icon"></i>
                <p>Vectorizing prompt through TF-IDF and calculating Cosine Similarity...</p>
            </div>
        `;

        try {
            const res = await fetch("/api/recommend-prompt", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt: prompt,
                    top_n: 8
                })
            });
            const data = await res.json();

            if (data.status === "success") {
                renderMovieCards(elements.promptResultsGrid, data.recommendations);
            } else {
                elements.promptResultsGrid.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-triangle-exclamation empty-icon"></i>
                        <p>${data.message || 'No matches found.'}</p>
                    </div>
                `;
            }
        } catch (err) {
            console.error("Prompt search failed:", err);
            elements.promptResultsGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-circle-exclamation empty-icon"></i>
                    <p>Failed to process prompt. Please try again.</p>
                </div>
            `;
        }
    }

    // ==========================================
    // TAB 3: COMPARE 2 MOVIES LOGIC
    // ==========================================

    function populateCompareSelectors() {
        if (!state.allMovies || state.allMovies.length === 0) return;

        const makeOptions = (selectedId) => {
            return state.allMovies.map(m => `
                <option value="${m.id}" ${m.id === selectedId ? 'selected' : ''}>${m.title} (${m.year})</option>
            `).join("");
        };

        elements.compareSelectA.innerHTML = makeOptions(1); // Inception
        elements.compareSelectB.innerHTML = makeOptions(2); // Interstellar

        renderComparePreview("A", 1);
        renderComparePreview("B", 2);

        elements.compareSelectA.addEventListener("change", (e) => {
            renderComparePreview("A", parseInt(e.target.value));
        });

        elements.compareSelectB.addEventListener("change", (e) => {
            renderComparePreview("B", parseInt(e.target.value));
        });

        elements.btnRunCompare.addEventListener("click", () => {
            const idA = parseInt(elements.compareSelectA.value);
            const idB = parseInt(elements.compareSelectB.value);
            runMovieComparison(idA, idB);
        });
    }

    function renderComparePreview(slot, movieId) {
        const movie = state.allMovies.find(m => m.id === movieId);
        const container = slot === "A" ? elements.comparePreviewA : elements.comparePreviewB;
        if (!movie) return;

        container.innerHTML = `
            <div style="display:flex; gap:1rem; align-items:center;">
                <img src="${movie.poster_url}" alt="${movie.title}" style="width:70px; height:100px; object-fit:cover; border-radius:6px;">
                <div>
                    <h4 style="color:#fff; font-size:1.05rem;">${movie.title}</h4>
                    <p style="color:var(--text-secondary); font-size:0.85rem;">${movie.year} • ${movie.genres}</p>
                    <p style="color:var(--accent-amber); font-size:0.85rem;"><i class="fa-solid fa-star"></i> ${movie.rating} / 10</p>
                </div>
            </div>
        `;
    }

    async function runMovieComparison(movieA, movieB) {
        try {
            const res = await fetch(`/api/explain?movie_a=${movieA}&movie_b=${movieB}`);
            const data = await res.json();

            if (data.status === "success") {
                elements.compareResultContainer.style.display = "block";
                elements.compareScorePercent.textContent = `${data.similarity_percent}%`;
                elements.compareRawCosine.textContent = data.cosine_similarity.toFixed(4);
                elements.compareTitlePair.textContent = `${data.movie_a.title} & ${data.movie_b.title}`;

                // Calculate max contribution for relative bar scaling
                const maxContrib = data.shared_terms.length > 0 ? Math.max(...data.shared_terms.map(t => t.contribution)) : 1;

                if (data.shared_terms.length > 0) {
                    elements.compareTermsTbody.innerHTML = data.shared_terms.map(item => {
                        const pct = Math.min(100, Math.round((item.contribution / maxContrib) * 100));
                        return `
                            <tr>
                                <td><code style="color:var(--primary); font-size:0.95rem;">${item.term}</code></td>
                                <td><strong>${item.contribution.toFixed(4)}</strong></td>
                                <td style="width: 40%;">
                                    <div class="contrib-bar-wrap">
                                        <div class="contrib-bar-fill" style="width: ${pct}%;"></div>
                                    </div>
                                </td>
                            </tr>
                        `;
                    }).join("");
                } else {
                    elements.compareTermsTbody.innerHTML = `
                        <tr>
                            <td colspan="3" style="text-align:center; color:var(--text-muted);">
                                No significant overlapping TF-IDF terms between these films.
                            </td>
                        </tr>
                    `;
                }

                elements.compareResultContainer.scrollIntoView({ behavior: "smooth" });
            }
        } catch (err) {
            console.error("Comparison failed:", err);
            showToast("Failed to compute movie comparison");
        }
    }

    // ==========================================
    // WATCHLIST MANAGEMENT
    // ==========================================

    function toggleWatchlist(movieId) {
        const movie = state.allMovies.find(m => m.id === movieId);
        if (!movie) return;

        const idx = state.watchlist.findIndex(m => m.id === movieId);
        if (idx >= 0) {
            state.watchlist.splice(idx, 1);
            showToast(`Removed "${movie.title}" from Watchlist`);
        } else {
            state.watchlist.push(movie);
            showToast(`Added "${movie.title}" to Watchlist`);
        }

        localStorage.setItem("cinematch_watchlist", JSON.stringify(state.watchlist));
        updateWatchlistBadge();

        // Refresh card bookmark icon states in current grids
        document.querySelectorAll(`.btn-bookmark-card[data-id="${movieId}"]`).forEach(btn => {
            const isBookmarked = state.watchlist.some(m => m.id === movieId);
            btn.classList.toggle("bookmarked", isBookmarked);
            btn.querySelector("i").className = isBookmarked ? "fa-solid fa-bookmark" : "fa-regular fa-bookmark";
        });

        // Re-render watchlist if currently on that tab
        if (document.getElementById("tab-watchlist").classList.contains("active")) {
            renderWatchlist();
        }
    }

    function updateWatchlistBadge() {
        elements.watchlistCountBadge.textContent = state.watchlist.length;
        if (elements.btnClearWatchlist) {
            elements.btnClearWatchlist.style.display = state.watchlist.length > 0 ? "inline-flex" : "none";
        }
    }

    function renderWatchlist() {
        if (state.watchlist.length === 0) {
            elements.watchlistGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fa-regular fa-bookmark empty-icon"></i>
                    <p>Your watchlist is currently empty. Bookmark movies by clicking the bookmark icon on any card!</p>
                </div>
            `;
            elements.btnClearWatchlist.style.display = "none";
            return;
        }

        elements.btnClearWatchlist.style.display = "inline-flex";
        renderMovieCards(elements.watchlistGrid, state.watchlist, true);
    }

    if (elements.btnClearWatchlist) {
        elements.btnClearWatchlist.addEventListener("click", () => {
            state.watchlist = [];
            localStorage.setItem("cinematch_watchlist", "[]");
            updateWatchlistBadge();
            renderWatchlist();
            showToast("Watchlist cleared");
        });
    }

    // ==========================================
    // MODAL INSPECTOR
    // ==========================================

    async function openMovieModal(movieId) {
        try {
            const res = await fetch(`/api/movie/${movieId}`);
            const data = await res.json();
            if (data.status === "success") {
                const m = data.movie;
                elements.modalContent.innerHTML = `
                    <div>
                        <img src="${m.poster_url}" alt="${m.title}" class="modal-poster">
                    </div>
                    <div>
                        <div style="display:flex; gap:1rem; align-items:center; margin-bottom:0.5rem; color:var(--text-secondary); font-size:0.85rem;">
                            <span>${m.year}</span>
                            <span>•</span>
                            <span style="color:var(--accent-amber);"><i class="fa-solid fa-star"></i> ${m.rating}</span>
                            <span>•</span>
                            <span><i class="fa-regular fa-clock"></i> ${m.runtime} min</span>
                        </div>
                        <h2 style="font-family:var(--font-heading); font-size:2rem; color:#fff; margin-bottom:0.75rem;">${m.title}</h2>
                        <p style="color:var(--accent-cyan); font-weight:600; font-size:0.9rem; margin-bottom:0.75rem;">Director: ${m.director}</p>
                        <p style="color:var(--text-muted); font-size:0.85rem; margin-bottom:1.25rem;">Cast: ${m.cast}</p>
                        
                        <h4 style="font-family:var(--font-heading); color:#fff; margin-bottom:0.5rem;">Synopsis</h4>
                        <p style="color:var(--text-secondary); font-size:0.95rem; line-height:1.6; margin-bottom:1.5rem;">${m.overview}</p>

                        <h4 style="font-family:var(--font-heading); color:#fff; margin-bottom:0.5rem;"><i class="fa-solid fa-fingerprint"></i> High-Weight TF-IDF Features for this Title</h4>
                        <div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:1.5rem;">
                            ${m.top_keywords.map(k => `
                                <div class="tfidf-tag">
                                    ${k.term} <span>${k.tfidf_score}</span>
                                </div>
                            `).join("")}
                        </div>

                        <div style="display:flex; gap:1rem;">
                            <button class="btn-primary" id="modal-recommend-btn">
                                <i class="fa-solid fa-wand-magic-sparkles"></i> Recommend Based On This
                            </button>
                        </div>
                    </div>
                `;

                document.getElementById("modal-recommend-btn").addEventListener("click", () => {
                    closeMovieModal();
                    switchTab("tab-recommend");
                    loadSourceMovieAndRecommend(movieId);
                    window.scrollTo({ top: 0, behavior: "smooth" });
                });

                elements.movieModal.classList.add("active");
            }
        } catch (err) {
            console.error("Failed to load movie modal:", err);
        }
    }

    function closeMovieModal() {
        elements.movieModal.classList.remove("active");
    }

    elements.btnCloseModal.addEventListener("click", closeMovieModal);
    elements.movieModal.addEventListener("click", (e) => {
        if (e.target === elements.movieModal) closeMovieModal();
    });

    // ==========================================
    // TAB SWITCHING & EVENT LISTENERS
    // ==========================================

    function switchTab(targetTabId) {
        elements.tabs.forEach(tab => {
            tab.classList.toggle("active", tab.dataset.tab === targetTabId);
        });

        elements.panes.forEach(pane => {
            pane.classList.toggle("active", pane.id === targetTabId);
        });

        if (targetTabId === "tab-watchlist") {
            renderWatchlist();
        }
    }

    function setupEventListeners() {
        elements.tabs.forEach(tab => {
            tab.addEventListener("click", () => {
                switchTab(tab.dataset.tab);
            });
        });

        const brandBtn = document.getElementById("brand-logo-btn");
        if (brandBtn) {
            brandBtn.addEventListener("click", () => {
                switchTab("tab-recommend");
            });
        }
    }

    // Toast Utility
    let toastTimeout;
    function showToast(message) {
        clearTimeout(toastTimeout);
        elements.toastText.textContent = message;
        elements.toastNotify.classList.add("active");
        toastTimeout = setTimeout(() => {
            elements.toastNotify.classList.remove("active");
        }, 3000);
    }

    // Launch!
    init();
});
