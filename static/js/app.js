/**
 * app.js - Client-Side Controller for CineMatch AI
 * Smart Computing using Python - TF-IDF Vector Space Model & Cosine Similarity Inspector
 */

document.addEventListener("DOMContentLoaded", () => {
    // State Store
    const state = {
        allMovies: [],
        currentSourceId: 1, // Default: Inception
        currentMovieData: null,
        currentRecommendations: [],
        visualizeSearch: true, // Toggle for showing/hiding mathematical feature attribution
        watchlist: JSON.parse(localStorage.getItem("cinematch_watchlist") || "[]"),
        corpusStats: null,
        activeSearchMode: "movie" // "movie" or "prompt"
    };

    // DOM Elements
    const elements = {
        // Search & Autocomplete
        searchInput: document.getElementById("movie-search-input"),
        autocompleteResults: document.getElementById("autocomplete-results"),
        btnClearSearch: document.getElementById("btn-clear-search"),
        btnSearchSubmit: document.getElementById("btn-search-submit"),
        quickPickChips: document.getElementById("quick-pick-chips"),

        // Filter Controls
        filterGenre: document.getElementById("filter-genre"),
        filterRating: document.getElementById("filter-rating"),
        ratingValDisplay: document.getElementById("rating-val-display"),
        filterTopN: document.getElementById("filter-top-n"),

        // "Visualize Search" Toggle
        btnToggleVisualize: document.getElementById("btn-toggle-visualize"),
        visualizeToggleIndicator: document.getElementById("visualize-toggle-indicator"),
        visualMathPanel: document.getElementById("visual-math-panel"),

        // Active Anchor / Source Movie Card
        sourceMovieCard: document.getElementById("source-movie-card"),
        srcPoster: document.getElementById("src-poster"),
        srcTitle: document.getElementById("src-title"),
        srcYear: document.getElementById("src-year"),
        srcRating: document.getElementById("src-rating"),
        srcRuntime: document.getElementById("src-runtime"),
        srcDirector: document.getElementById("src-director"),
        srcGenres: document.getElementById("src-genres"),
        srcOverview: document.getElementById("src-overview"),
        srcTfidfTerms: document.getElementById("src-tfidf-terms"),

        // Recommendations Grid
        resultsHeading: document.getElementById("results-heading"),
        resultsSubheading: document.getElementById("results-subheading"),
        recommendationsGrid: document.getElementById("recommendations-grid"),

        // Header & Watchlist Drawer
        headerMatrixShape: document.getElementById("header-matrix-shape"),
        dashMatrixDim: document.getElementById("dash-matrix-dim"),
        dashSparsityVal: document.getElementById("dash-sparsity-val"),
        btnOpenAlgoBlueprint: document.getElementById("btn-open-algo-blueprint"),
        btnQuickAlgoView: document.getElementById("btn-quick-algo-view"),
        btnOpenWatchlist: document.getElementById("btn-open-watchlist"),
        watchlistCountBadge: document.getElementById("watchlist-count"),
        watchlistDrawerBackdrop: document.getElementById("watchlist-drawer-backdrop"),
        btnCloseWatchlist: document.getElementById("btn-close-watchlist"),
        drawerWatchlistCount: document.getElementById("drawer-watchlist-count"),
        watchlistGrid: document.getElementById("watchlist-grid"),
        btnClearWatchlist: document.getElementById("btn-clear-watchlist"),

        // Modals
        blueprintModal: document.getElementById("blueprint-modal"),
        btnCloseBlueprintModal: document.getElementById("btn-close-blueprint-modal"),
        blueprintRareTerms: document.getElementById("blueprint-rare-terms"),
        blueprintCommonTerms: document.getElementById("blueprint-common-terms"),

        vectorMathModal: document.getElementById("vector-math-modal"),
        btnCloseMathModal: document.getElementById("btn-close-math-modal"),
        mathPairBanner: document.getElementById("math-pair-banner"),
        mathBreakdownTbody: document.getElementById("math-breakdown-tbody"),
        mathFormulaSummary: document.getElementById("math-formula-summary"),

        brandLogoBtn: document.getElementById("brand-logo-btn"),
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
        // Load default movie (Inception)
        await loadSourceMovieAndRecommend(state.currentSourceId);
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
            showToast("Failed to connect to movies API");
        }
    }

    async function fetchStats() {
        try {
            const res = await fetch("/api/stats");
            const data = await res.json();
            if (data.status === "success") {
                state.corpusStats = data.stats;
                populateGenreFilter(data.stats.genres || []);

                // Populate dashboard and header metrics
                if (elements.headerMatrixShape) {
                    elements.headerMatrixShape.textContent = `ℝ²⁴⁷ ˣ ⁵⁰⁰⁰`;
                }
                if (elements.dashMatrixDim) {
                    elements.dashMatrixDim.textContent = `${data.stats.total_movies} × ${data.stats.vocab_size.toLocaleString()}`;
                }
                if (elements.dashSparsityVal && data.stats.sparsity_percent) {
                    elements.dashSparsityVal.textContent = `${data.stats.sparsity_percent}%`;
                }
            }
        } catch (err) {
            console.error("Failed to fetch stats:", err);
        }
    }

    function populateGenreFilter(genres) {
        if (!elements.filterGenre) return;
        elements.filterGenre.innerHTML = '<option value="All">All Genres</option>';
        genres.forEach(g => {
            const opt = document.createElement("option");
            opt.value = g;
            opt.textContent = g;
            elements.filterGenre.appendChild(opt);
        });
    }

    // ==========================================
    // SEARCH EXECUTION LOGIC
    // ==========================================

    function handleSearchInput(rawQuery) {
        const query = (rawQuery || elements.searchInput.value).trim();
        if (!query) {
            showToast("Please enter a title, actor, or story theme to search");
            return;
        }

        // Close dropdown
        elements.autocompleteResults.classList.remove("active");

        // Try exact or substring match in allMovies
        const lower = query.toLowerCase();
        const found = state.allMovies.find(m => m.title.toLowerCase() === lower) ||
                      state.allMovies.find(m => m.title.toLowerCase().startsWith(lower)) ||
                      state.allMovies.find(m => m.title.toLowerCase().includes(lower));

        if (found) {
            state.activeSearchMode = "movie";
            updateQuickPickActive(found.id);
            loadSourceMovieAndRecommend(found.id);
            elements.searchInput.value = found.title;
        } else {
            // Free-text natural language vector search
            state.activeSearchMode = "prompt";
            executePromptVectorSearch(query);
        }
    }

    function updateQuickPickActive(movieId) {
        if (!elements.quickPickChips) return;
        elements.quickPickChips.querySelectorAll(".chip").forEach(c => {
            if (parseInt(c.dataset.id) === movieId) {
                c.classList.add("active");
            } else {
                c.classList.remove("active");
            }
        });
    }

    // ==========================================
    // RECOMMEND BY MOVIE ID
    // ==========================================

    async function loadSourceMovieAndRecommend(movieId) {
        state.currentSourceId = movieId;
        state.activeSearchMode = "movie";

        if (elements.sourceMovieCard) {
            elements.sourceMovieCard.style.display = "grid";
        }

        // Fetch Movie Details
        try {
            const movieRes = await fetch(`/api/movie/${movieId}`);
            const movieData = await movieRes.json();
            if (movieData.status === "success") {
                state.currentMovieData = movieData.movie;
                renderSourceMovieBanner(movieData.movie);
            }
        } catch (err) {
            console.error(err);
        }

        // Fetch Similar Recommendations
        await fetchRecommendations();
    }

    function renderSourceMovieBanner(movie) {
        if (!elements.sourceMovieCard) return;

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
            elements.srcTfidfTerms.innerHTML = movie.top_keywords.slice(0, 8).map(k => `
                <div class="tfidf-tag" title="Term Frequency x Inverse Document Frequency: ${k.tfidf_score}">
                    ${k.term} <span>w=${k.tfidf_score}</span>
                </div>
            `).join("");
        } else {
            elements.srcTfidfTerms.innerHTML = '<span class="text-muted">No high-weight terms calculated</span>';
        }

        if (elements.resultsHeading) {
            elements.resultsHeading.innerHTML = `Vector Space Recommendations for "<strong>${movie.title}</strong>"`;
        }
        if (elements.resultsSubheading) {
            elements.resultsSubheading.textContent = `Ranked by angular cosine distance cos(θ) = u · v in ℝ⁵⁰⁰⁰ based on synopsis, director (${movie.director}), and themes.`;
        }
    }

    async function fetchRecommendations() {
        const topN = elements.filterTopN.value;
        const genre = elements.filterGenre.value;
        const minRating = elements.filterRating.value;

        elements.recommendationsGrid.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner fa-spin empty-icon"></i>
                <p>Computing 5,000-dimensional TF-IDF vectors and cosine dot products...</p>
            </div>
        `;

        try {
            const url = `/api/recommend?movie_id=${state.currentSourceId}&top_n=${topN}&genre=${encodeURIComponent(genre)}&min_rating=${minRating}`;
            const res = await fetch(url);
            const data = await res.json();

            if (data.status === "success") {
                state.currentRecommendations = data.recommendations;
                renderMovieCards(elements.recommendationsGrid, data.recommendations);

                // Smoothly scroll down so user sees similar movies below search
                if (elements.sourceMovieCard && elements.sourceMovieCard.style.display !== "none") {
                    elements.sourceMovieCard.scrollIntoView({ behavior: "smooth", block: "start" });
                }
            } else {
                elements.recommendationsGrid.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-triangle-exclamation empty-icon"></i>
                        <p>${data.message || 'No recommendations found matching filters.'}</p>
                    </div>
                `;
            }
        } catch (err) {
            console.error("Error fetching recommendations:", err);
            elements.recommendationsGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-circle-exclamation empty-icon"></i>
                    <p>Failed to load recommendations. Please retry.</p>
                </div>
            `;
        }
    }

    // ==========================================
    // PROMPT FREE-TEXT VECTOR SEARCH
    // ==========================================

    async function executePromptVectorSearch(prompt) {
        state.activeSearchMode = "prompt";
        if (elements.sourceMovieCard) {
            elements.sourceMovieCard.style.display = "none";
        }

        const topN = elements.filterTopN.value;
        const genre = elements.filterGenre.value;
        const minRating = elements.filterRating.value;

        if (elements.resultsHeading) {
            elements.resultsHeading.innerHTML = `Vector Search Results for "<strong>${prompt}</strong>"`;
        }
        if (elements.resultsSubheading) {
            elements.resultsSubheading.textContent = `Closest geometric alignments in TF-IDF term space ranked by angular cosine distance cos(θ).`;
        }

        elements.recommendationsGrid.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner fa-spin empty-icon"></i>
                <p>Vectorizing prompt query and calculating cosine similarity in ℝ⁵⁰⁰⁰...</p>
            </div>
        `;

        try {
            const res = await fetch("/api/recommend-prompt", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt: prompt,
                    top_n: parseInt(topN),
                    genre: genre,
                    min_rating: parseFloat(minRating)
                })
            });
            const data = await res.json();

            if (data.status === "success" && data.recommendations.length > 0) {
                state.currentRecommendations = data.recommendations;
                renderMovieCards(elements.recommendationsGrid, data.recommendations);
                showToast(`Found ${data.recommendations.length} matching films in vector space`);

                if (elements.recommendationsSection) {
                    elements.recommendationsSection.scrollIntoView({ behavior: "smooth", block: "start" });
                }
            } else {
                elements.recommendationsGrid.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-magnifying-glass empty-icon"></i>
                        <p>No films matched the prompt "${prompt}". Try broader terms like "space", "robot", "action", "mafia".</p>
                    </div>
                `;
            }
        } catch (err) {
            console.error("Prompt search error:", err);
            elements.recommendationsGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-circle-exclamation empty-icon"></i>
                    <p>Prompt search failed. Please try again.</p>
                </div>
            `;
        }
    }

    // ==========================================
    // RENDER MOVIE CARDS & VISUAL SIMILARITY
    // ==========================================

    function getOneLineReason(movie) {
        if (movie.similarity_reason) return movie.similarity_reason;
        if (state.currentMovieData) {
            const src = state.currentMovieData;
            if (src.director && movie.director && src.director.toLowerCase() === movie.director.toLowerCase()) {
                return `Directed by ${src.director} with signature cinematic motifs.`;
            }
            if (movie.shared_terms && movie.shared_terms.length > 0) {
                const term = movie.shared_terms[0].term.replace(/_/g, ' ');
                return `Shares core themes in ${term} and character dynamics.`;
            }
        }
        if (movie.genres) {
            const topGenre = movie.genres.split(",")[0].trim();
            return `Matches high-stakes ${topGenre} narrative pacing and tone.`;
        }
        return "Shares narrative themes, tone, and character dynamics.";
    }

    function renderMovieCards(container, movies) {
        if (!movies || movies.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-film empty-icon"></i>
                    <p>No matching films found for the selected criteria.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = movies.map(movie => {
            const isBookmarked = state.watchlist.some(m => m.id === movie.id);
            const genres = movie.genres ? movie.genres.split(",").slice(0, 3) : [];
            const similarityPercent = movie.similarity_percent !== undefined ? movie.similarity_percent : (movie.cosine_similarity ? (movie.cosine_similarity * 100).toFixed(1) : 0);
            const cosScore = movie.similarity_score !== undefined ? movie.similarity_score : (similarityPercent / 100).toFixed(4);
            const isHighMatch = similarityPercent >= 15.0;

            // Visual Feature Attribution (How Similarity Was Found)
            let visualHowFoundHtml = "";
            if (movie.shared_terms && movie.shared_terms.length > 0) {
                const maxContrib = Math.max(...movie.shared_terms.map(t => t.contribution || 0.01), 0.01);

                const termsHtml = movie.shared_terms.slice(0, 6).map(t => {
                    const barPercent = Math.min(Math.round(((t.contribution || 0.01) / maxContrib) * 100), 100);
                    return `
                        <div class="feature-contrib-item">
                            <div class="feature-contrib-meta">
                                <span class="feature-term"><code>${t.term}</code></span>
                                <span class="feature-score">+${t.contribution}</span>
                            </div>
                            <div class="feature-bar-track">
                                <div class="feature-bar-fill" style="width: ${barPercent}%"></div>
                            </div>
                        </div>
                    `;
                }).join("");

                visualHowFoundHtml = `
                    <div class="how-found-box ${state.visualizeSearch ? 'visible' : 'hidden'}">
                        <div class="how-found-header">
                            <i class="fa-solid fa-square-root-variable"></i>
                            <span>Vector Dot Product Contributions (w_A × w_B):</span>
                        </div>
                        <div class="feature-contrib-list">
                            ${termsHtml}
                        </div>
                    </div>
                `;
            } else if (movie.matched_terms && movie.matched_terms.length > 0) {
                visualHowFoundHtml = `
                    <div class="how-found-box ${state.visualizeSearch ? 'visible' : 'hidden'}">
                        <div class="how-found-header">
                            <i class="fa-solid fa-bullseye"></i>
                            <span>Matched Query N-Grams:</span>
                        </div>
                        <div class="shared-terms-chips" style="margin-top:0.5rem;">
                            ${movie.matched_terms.map(t => `<span class="shared-term-chip">${t}</span>`).join("")}
                        </div>
                    </div>
                `;
            }

            const oneLineReason = getOneLineReason(movie);

            return `
                <div class="movie-card" data-id="${movie.id}">
                    <div class="movie-card-poster-wrap">
                        <img src="${movie.poster_url || 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80'}" alt="${movie.title}" class="movie-card-poster" loading="lazy">
                        <div class="similarity-badge ${isHighMatch ? 'high-match' : ''}">
                            <i class="fa-solid fa-square-root-variable"></i> cos(θ) = ${cosScore} (${similarityPercent}%)
                        </div>
                        <button class="btn-bookmark-card ${isBookmarked ? 'bookmarked' : ''}" data-id="${movie.id}" title="${isBookmarked ? 'Remove from Watchlist' : 'Save to Watchlist'}">
                            <i class="${isBookmarked ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i>
                        </button>
                    </div>

                    <div class="movie-card-body">
                        <div class="movie-card-header">
                            <span class="movie-card-year">${movie.year}</span>
                            <span class="movie-card-rating"><i class="fa-solid fa-star"></i> ${movie.rating}</span>
                        </div>
                        <h3 class="movie-card-title">${movie.title}</h3>
                        <div class="movie-card-genres">
                            ${genres.map(g => `<span class="mini-genre-pill">${g.trim()}</span>`).join("")}
                        </div>

                        <!-- One-line similarity reason -->
                        <div class="similarity-reason-box">
                            <span class="similarity-reason-tag"><i class="fa-solid fa-sparkles"></i> Why similar:</span>
                            <p class="similarity-reason-text">${oneLineReason}</p>
                        </div>

                        <p class="movie-card-overview">${movie.overview || ''}</p>

                        ${visualHowFoundHtml}

                        <div class="movie-card-actions">
                            <button class="btn-card-action primary btn-inspect" data-id="${movie.id}" title="View details">
                                <i class="fa-regular fa-file-lines"></i> Details
                            </button>
                            <button class="btn-card-action btn-inspect-vector-math" data-id="${movie.id}" title="Inspect component-wise dot product">
                                <i class="fa-solid fa-calculator"></i> Vector Math
                            </button>
                            <button class="btn-card-action btn-find-similar" data-id="${movie.id}" title="Use as anchor">
                                <i class="fa-solid fa-compass"></i> Similar
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
            btn.addEventListener("click", () => {
                const id = parseInt(btn.dataset.id);
                openMovieModal(id);
            });
        });

        container.querySelectorAll(".btn-inspect-vector-math").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = parseInt(btn.dataset.id);
                openVectorMathModal(state.currentSourceId, id);
            });
        });

        container.querySelectorAll(".btn-find-similar").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = parseInt(btn.dataset.id);
                updateQuickPickActive(id);
                loadSourceMovieAndRecommend(id);
                elements.searchInput.value = "";
            });
        });
    }

    // ==========================================
    // AUTOCOMPLETE DROPDOWN
    // ==========================================

    elements.searchInput.addEventListener("input", (e) => {
        const query = e.target.value.trim().toLowerCase();
        if (query.length > 0) {
            elements.btnClearSearch.style.display = "block";
        } else {
            elements.btnClearSearch.style.display = "none";
        }

        if (query.length < 2) {
            elements.autocompleteResults.classList.remove("active");
            return;
        }

        const matches = state.allMovies
            .filter(m => m.title.toLowerCase().includes(query) || (m.director && m.director.toLowerCase().includes(query)))
            .slice(0, 7);

        renderAutocompleteDropdown(matches);
    });

    elements.searchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            handleSearchInput();
        }
    });

    elements.btnSearchSubmit.addEventListener("click", () => {
        handleSearchInput();
    });

    elements.btnClearSearch.addEventListener("click", () => {
        elements.searchInput.value = "";
        elements.btnClearSearch.style.display = "none";
        elements.autocompleteResults.classList.remove("active");
        elements.searchInput.focus();
    });

    function renderAutocompleteDropdown(matches) {
        if (matches.length === 0) {
            elements.autocompleteResults.innerHTML = `
                <div class="autocomplete-item empty">
                    <span>No exact title match. Press <kbd>Enter</kbd> to execute free-text vector search</span>
                </div>
            `;
            elements.autocompleteResults.classList.add("active");
            return;
        }

        elements.autocompleteResults.innerHTML = matches.map(movie => `
            <div class="autocomplete-item" data-id="${movie.id}">
                <img src="${movie.poster_url}" alt="${movie.title}" class="autocomplete-poster">
                <div class="autocomplete-info">
                    <span class="autocomplete-title">${movie.title}</span>
                    <span class="autocomplete-meta">${movie.year} • ${movie.director || 'N/A'} • ★ ${movie.rating}</span>
                </div>
            </div>
        `).join("");

        elements.autocompleteResults.classList.add("active");

        elements.autocompleteResults.querySelectorAll(".autocomplete-item:not(.empty)").forEach(item => {
            item.addEventListener("click", () => {
                const id = parseInt(item.dataset.id);
                const sel = state.allMovies.find(m => m.id === id);
                if (sel) {
                    elements.searchInput.value = sel.title;
                    updateQuickPickActive(id);
                    loadSourceMovieAndRecommend(id);
                }
                elements.autocompleteResults.classList.remove("active");
            });
        });
    }

    document.addEventListener("click", (e) => {
        if (!e.target.closest(".search-box-wrapper")) {
            elements.autocompleteResults.classList.remove("active");
        }
    });

    // Quick Pick Chips
    if (elements.quickPickChips) {
        elements.quickPickChips.querySelectorAll(".chip").forEach(chip => {
            chip.addEventListener("click", () => {
                const id = parseInt(chip.dataset.id);
                updateQuickPickActive(id);
                loadSourceMovieAndRecommend(id);
                const movie = state.allMovies.find(m => m.id === id);
                if (movie) elements.searchInput.value = movie.title;
            });
        });
    }

    // ==========================================
    // FILTER CONTROLS & "VISUALIZE SEARCH" TOGGLE
    // ==========================================

    elements.filterGenre.addEventListener("change", () => {
        if (state.activeSearchMode === "movie") {
            fetchRecommendations();
        } else {
            executePromptVectorSearch(elements.searchInput.value.trim());
        }
    });

    elements.filterTopN.addEventListener("change", () => {
        if (state.activeSearchMode === "movie") {
            fetchRecommendations();
        } else {
            executePromptVectorSearch(elements.searchInput.value.trim());
        }
    });

    elements.filterRating.addEventListener("input", (e) => {
        elements.ratingValDisplay.textContent = parseFloat(e.target.value).toFixed(1);
    });

    elements.filterRating.addEventListener("change", () => {
        if (state.activeSearchMode === "movie") {
            fetchRecommendations();
        } else {
            executePromptVectorSearch(elements.searchInput.value.trim());
        }
    });

    // "Visualize Search" Toggle
    elements.btnToggleVisualize.addEventListener("click", () => {
        state.visualizeSearch = !state.visualizeSearch;
        
        if (state.visualizeSearch) {
            elements.btnToggleVisualize.classList.add("active");
            elements.visualizeToggleIndicator.textContent = "ON";
            elements.visualizeToggleIndicator.className = "toggle-pill on";
            if (elements.visualMathPanel) elements.visualMathPanel.style.display = "block";
        } else {
            elements.btnToggleVisualize.classList.remove("active");
            elements.visualizeToggleIndicator.textContent = "OFF";
            elements.visualizeToggleIndicator.className = "toggle-pill off";
            if (elements.visualMathPanel) elements.visualMathPanel.style.display = "none";
        }

        // Toggle visibility of how-found-box on all rendered cards
        document.querySelectorAll(".how-found-box").forEach(box => {
            if (state.visualizeSearch) {
                box.classList.remove("hidden");
                box.classList.add("visible");
            } else {
                box.classList.remove("visible");
                box.classList.add("hidden");
            }
        });
    });

    // ==========================================
    // ALGORITHM BLUEPRINT MODAL
    // ==========================================

    function openBlueprintModal() {
        if (!elements.blueprintModal) return;
        elements.blueprintModal.style.display = "flex";

        if (state.corpusStats) {
            // Render High IDF rare terms
            if (elements.blueprintRareTerms && state.corpusStats.sample_high_idf_terms) {
                elements.blueprintRareTerms.innerHTML = state.corpusStats.sample_high_idf_terms.map(t => `
                    <div class="idf-pill">
                        ${t.term} <span>IDF: ${t.idf}</span>
                    </div>
                `).join("");
            }

            // Render Low IDF common terms
            if (elements.blueprintCommonTerms && state.corpusStats.sample_common_terms) {
                elements.blueprintCommonTerms.innerHTML = state.corpusStats.sample_common_terms.map(t => `
                    <div class="idf-pill">
                        ${t.term} <span>IDF: ${t.idf}</span>
                    </div>
                `).join("");
            }
        }
    }

    if (elements.btnOpenAlgoBlueprint) {
        elements.btnOpenAlgoBlueprint.addEventListener("click", openBlueprintModal);
    }
    if (elements.btnQuickAlgoView) {
        elements.btnQuickAlgoView.addEventListener("click", openBlueprintModal);
    }
    if (elements.btnCloseBlueprintModal) {
        elements.btnCloseBlueprintModal.addEventListener("click", () => {
            elements.blueprintModal.style.display = "none";
        });
    }
    if (elements.blueprintModal) {
        elements.blueprintModal.addEventListener("click", (e) => {
            if (e.target === elements.blueprintModal) {
                elements.blueprintModal.style.display = "none";
            }
        });
    }

    // ==========================================
    // PAIRWISE VECTOR MATH MODAL (DOT PRODUCT)
    // ==========================================

    async function openVectorMathModal(sourceId, targetId) {
        if (!elements.vectorMathModal) return;
        elements.vectorMathModal.style.display = "flex";

        elements.mathPairBanner.innerHTML = `
            <div style="text-align:center; width:100%; padding:1rem;">
                <i class="fa-solid fa-spinner fa-spin" style="font-size:1.5rem; color:var(--accent-mint);"></i>
                <p style="margin-top:0.5rem; font-size:0.85rem;">Calculating component-wise TF-IDF dot product in ℝ⁵⁰⁰⁰...</p>
            </div>
        `;
        elements.mathBreakdownTbody.innerHTML = '';
        elements.mathFormulaSummary.innerHTML = '';

        try {
            const res = await fetch(`/api/explain?movie_a=${sourceId}&movie_b=${targetId}`);
            const data = await res.json();

            if (data.status === "success") {
                renderVectorMathModal(data);
            } else {
                elements.mathPairBanner.innerHTML = `<p class="text-muted">${data.message || 'Error comparing vectors.'}</p>`;
            }
        } catch (err) {
            console.error("Vector math error:", err);
            elements.mathPairBanner.innerHTML = `<p class="text-muted">Failed to load vector math breakdown.</p>`;
        }
    }

    function renderVectorMathModal(data) {
        const totalCosine = data.cosine_similarity;
        const totalPercent = data.similarity_percent;

        elements.mathPairBanner.innerHTML = `
            <div>
                <span class="text-xs uppercase text-muted font-bold">Pairwise Comparison</span>
                <div class="pair-film-name">${data.movie_a.title} &nbsp;⟷&nbsp; ${data.movie_b.title}</div>
            </div>
            <div style="text-align:right;">
                <span class="text-xs uppercase text-muted font-bold">Cosine Inner Product</span>
                <div class="pair-math-score">cos(θ) = ${totalCosine} (${totalPercent}%)</div>
            </div>
        `;

        if (!data.shared_terms || data.shared_terms.length === 0) {
            elements.mathBreakdownTbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align:center; padding:1.5rem; color:var(--text-muted);">
                        No high-magnitude shared n-grams found in the top component vectors.
                    </td>
                </tr>
            `;
            elements.mathFormulaSummary.innerHTML = `Cosine distance computed: cos(θ) = ${totalCosine}. Films share generic corpus narrative tokens.`;
            return;
        }

        let totalContrib = 0;
        const rowsHtml = data.shared_terms.map(t => {
            const wA = t.weight_a !== undefined ? t.weight_a : '—';
            const wB = t.weight_b !== undefined ? t.weight_b : '—';
            const contrib = t.contribution;
            totalContrib += contrib;
            const pctOfCosine = totalCosine > 0 ? ((contrib / totalCosine) * 100).toFixed(1) : '0';

            return `
                <tr>
                    <td><strong><code>${t.term}</code></strong></td>
                    <td><span style="font-family:'JetBrains Mono';">${wA}</span></td>
                    <td><span style="font-family:'JetBrains Mono';">${wB}</span></td>
                    <td><strong style="color:var(--accent-mint); font-family:'JetBrains Mono';">+${contrib}</strong></td>
                    <td><span class="text-muted">${pctOfCosine}%</span></td>
                </tr>
            `;
        }).join("");

        elements.mathBreakdownTbody.innerHTML = rowsHtml;

        const capturedPct = totalCosine > 0 ? Math.min(Math.round((totalContrib / totalCosine) * 100), 100) : 0;
        elements.mathFormulaSummary.innerHTML = `
            <strong>Mathematical Summary:</strong> The inner product across all 5,000 dimensions evaluates to <code>cos(θ) = u · v = ${totalCosine}</code>. 
            The top ${data.shared_terms.length} shared dimensions shown above account for <strong>${capturedPct}%</strong> of the total angular affinity between <em>${data.movie_a.title}</em> and <em>${data.movie_b.title}</em>.
        `;
    }

    if (elements.btnCloseMathModal) {
        elements.btnCloseMathModal.addEventListener("click", () => {
            elements.vectorMathModal.style.display = "none";
        });
    }
    if (elements.vectorMathModal) {
        elements.vectorMathModal.addEventListener("click", (e) => {
            if (e.target === elements.vectorMathModal) {
                elements.vectorMathModal.style.display = "none";
            }
        });
    }

    // ==========================================
    // WATCHLIST DRAWER
    // ==========================================

    function updateWatchlistBadge() {
        const count = state.watchlist.length;
        if (elements.watchlistCountBadge) elements.watchlistCountBadge.textContent = count;
        if (elements.drawerWatchlistCount) elements.drawerWatchlistCount.textContent = count;
        if (elements.btnClearWatchlist) {
            elements.btnClearWatchlist.style.display = count > 0 ? "inline-flex" : "none";
        }
    }

    function toggleWatchlist(movieId) {
        const idx = state.watchlist.findIndex(m => m.id === movieId);
        if (idx >= 0) {
            state.watchlist.splice(idx, 1);
            showToast("Removed from Watchlist");
        } else {
            const movie = state.allMovies.find(m => m.id === movieId) ||
                          state.currentRecommendations.find(m => m.id === movieId) ||
                          (state.currentMovieData && state.currentMovieData.id === movieId ? state.currentMovieData : null);
            if (movie) {
                state.watchlist.push(movie);
                showToast(`Saved "${movie.title}" to Watchlist`);
            }
        }

        localStorage.setItem("cinematch_watchlist", JSON.stringify(state.watchlist));
        updateWatchlistBadge();

        // Update card bookmark buttons in UI
        document.querySelectorAll(`.btn-bookmark-card[data-id="${movieId}"]`).forEach(btn => {
            const isBookmarked = state.watchlist.some(m => m.id === movieId);
            btn.className = `btn-bookmark-card ${isBookmarked ? 'bookmarked' : ''}`;
            btn.querySelector("i").className = isBookmarked ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark';
        });

        if (elements.watchlistDrawerBackdrop.style.display === "flex") {
            renderWatchlistDrawer();
        }
    }

    elements.btnOpenWatchlist.addEventListener("click", () => {
        elements.watchlistDrawerBackdrop.style.display = "flex";
        renderWatchlistDrawer();
    });

    elements.btnCloseWatchlist.addEventListener("click", () => {
        elements.watchlistDrawerBackdrop.style.display = "none";
    });

    elements.watchlistDrawerBackdrop.addEventListener("click", (e) => {
        if (e.target === elements.watchlistDrawerBackdrop) {
            elements.watchlistDrawerBackdrop.style.display = "none";
        }
    });

    if (elements.btnClearWatchlist) {
        elements.btnClearWatchlist.addEventListener("click", () => {
            if (confirm("Clear all movies from your watchlist?")) {
                state.watchlist = [];
                localStorage.setItem("cinematch_watchlist", "[]");
                updateWatchlistBadge();
                renderWatchlistDrawer();
                showToast("Watchlist cleared");
            }
        });
    }

    function renderWatchlistDrawer() {
        if (!elements.watchlistGrid) return;
        if (state.watchlist.length === 0) {
            elements.watchlistGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fa-regular fa-bookmark empty-icon"></i>
                    <p>Your watchlist is currently empty. Click the bookmark icon on any film card to save it.</p>
                </div>
            `;
            return;
        }

        renderMovieCards(elements.watchlistGrid, state.watchlist);
    }

    // ==========================================
    // MOVIE DETAIL MODAL
    // ==========================================

    async function openMovieModal(movieId) {
        elements.movieModal.style.display = "flex";
        elements.modalContent.innerHTML = `
            <div style="grid-column: 1 / -1; padding: 3rem; text-align: center; color: var(--text-secondary);">
                <i class="fa-solid fa-spinner fa-spin" style="font-size: 2rem; margin-bottom: 1rem; color: var(--accent-mint);"></i>
                <p>Loading film vectors and metadata...</p>
            </div>
        `;

        try {
            const res = await fetch(`/api/movie/${movieId}`);
            const data = await res.json();
            if (data.status === "success") {
                renderModalContent(data.movie);
            }
        } catch (err) {
            console.error("Modal fetch error:", err);
            elements.modalContent.innerHTML = '<p class="text-muted">Failed to load movie details.</p>';
        }
    }

    function renderModalContent(movie) {
        const genres = movie.genres ? movie.genres.split(",") : [];
        const isBookmarked = state.watchlist.some(m => m.id === movie.id);

        const keywordsHtml = movie.top_keywords && movie.top_keywords.length > 0 ? `
            <div class="modal-section">
                <h4>Top TF-IDF Salient Features in $\\vec{v}$</h4>
                <div class="tfidf-tags-list">
                    ${movie.top_keywords.map(k => `
                        <div class="tfidf-tag" title="TF-IDF Weight: ${k.tfidf_score}">
                            ${k.term} <span>w=${k.tfidf_score}</span>
                        </div>
                    `).join("")}
                </div>
            </div>
        ` : '';

        elements.modalContent.innerHTML = `
            <div class="modal-poster-col">
                <img src="${movie.poster_url}" alt="${movie.title}" class="modal-poster">
                <div style="margin-top: 1rem; display: flex; flex-direction: column; gap: 0.5rem;">
                    <button class="btn-primary" id="modal-find-similar-btn" style="width: 100%;">
                        <i class="fa-solid fa-compass"></i> Use as Anchor Film
                    </button>
                    <button class="btn-secondary" id="modal-bookmark-btn" style="width: 100%;">
                        <i class="${isBookmarked ? 'fa-solid' : 'fa-regular'} fa-bookmark"></i>
                        <span>${isBookmarked ? 'Saved in Watchlist' : 'Add to Watchlist'}</span>
                    </button>
                </div>
            </div>

            <div class="modal-info-col">
                <div class="modal-meta-row">
                    <span>${movie.year}</span>
                    <span class="meta-dot"></span>
                    <span><i class="fa-solid fa-star" style="color: #d97706;"></i> ${movie.rating}</span>
                    <span class="meta-dot"></span>
                    <span><i class="fa-regular fa-clock"></i> ${movie.runtime} min</span>
                </div>

                <h2 class="modal-title">${movie.title}</h2>
                <div class="genre-pill-list">
                    ${genres.map(g => `<span class="genre-pill">${g.trim()}</span>`).join("")}
                </div>

                <div class="modal-crew">
                    <p><strong>Director:</strong> ${movie.director || 'N/A'}</p>
                    <p><strong>Lead Cast:</strong> ${movie.cast || 'N/A'}</p>
                </div>

                <div class="modal-section">
                    <h4>Narrative Synopsis</h4>
                    <p class="modal-overview">${movie.overview}</p>
                </div>

                ${keywordsHtml}
            </div>
        `;

        document.getElementById("modal-find-similar-btn").addEventListener("click", () => {
            elements.movieModal.style.display = "none";
            updateQuickPickActive(movie.id);
            loadSourceMovieAndRecommend(movie.id);
        });

        document.getElementById("modal-bookmark-btn").addEventListener("click", () => {
            toggleWatchlist(movie.id);
            const saved = state.watchlist.some(m => m.id === movie.id);
            const btn = document.getElementById("modal-bookmark-btn");
            btn.querySelector("i").className = saved ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark';
            btn.querySelector("span").textContent = saved ? 'Saved in Watchlist' : 'Add to Watchlist';
        });
    }

    elements.btnCloseModal.addEventListener("click", () => {
        elements.movieModal.style.display = "none";
    });

    elements.movieModal.addEventListener("click", (e) => {
        if (e.target === elements.movieModal) {
            elements.movieModal.style.display = "none";
        }
    });

    if (elements.brandLogoBtn) {
        elements.brandLogoBtn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
            elements.searchInput.focus();
        });
    }

    // ==========================================
    // TOAST HELPER
    // ==========================================

    function showToast(message) {
        if (!elements.toastNotify || !elements.toastText) return;
        elements.toastText.textContent = message;
        elements.toastNotify.classList.add("active");
        setTimeout(() => {
            elements.toastNotify.classList.remove("active");
        }, 2500);
    }

    function setupEventListeners() {
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                if (elements.movieModal) elements.movieModal.style.display = "none";
                if (elements.blueprintModal) elements.blueprintModal.style.display = "none";
                if (elements.vectorMathModal) elements.vectorMathModal.style.display = "none";
                if (elements.watchlistDrawerBackdrop) elements.watchlistDrawerBackdrop.style.display = "none";
                if (elements.autocompleteResults) elements.autocompleteResults.classList.remove("active");
            }
        });
    }

    // Start App
    init();
});
