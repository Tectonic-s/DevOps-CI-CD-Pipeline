/**
 * app.js - Client-Side Controller for CineMatch AI
 * Single-flow search, instant TF-IDF recommendations, visual feature attribution, and search visualizer toggle.
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

        // Requested "Visualize Search" Toggle
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
        headerMovieCount: document.getElementById("header-movie-count"),
        btnOpenWatchlist: document.getElementById("btn-open-watchlist"),
        watchlistCountBadge: document.getElementById("watchlist-count"),
        watchlistDrawerBackdrop: document.getElementById("watchlist-drawer-backdrop"),
        btnCloseWatchlist: document.getElementById("btn-close-watchlist"),
        drawerWatchlistCount: document.getElementById("drawer-watchlist-count"),
        watchlistGrid: document.getElementById("watchlist-grid"),
        btnClearWatchlist: document.getElementById("btn-clear-watchlist"),

        // Modal & Toast
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
                if (elements.headerMovieCount) {
                    elements.headerMovieCount.textContent = data.count || data.movies.length;
                }
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
    // CORE SEARCH EXECUTION LOGIC (BUG-FREE)
    // ==========================================

    function handleSearchInput(rawQuery) {
        const query = (rawQuery || elements.searchInput.value).trim();
        if (!query) {
            showToast("Please enter a title, actor, or story theme to search");
            return;
        }

        // Close dropdown
        elements.autocompleteResults.classList.remove("active");

        // 1. Try exact or close match in allMovies
        const lower = query.toLowerCase();
        const found = state.allMovies.find(m => m.title.toLowerCase() === lower) ||
                      state.allMovies.find(m => m.title.toLowerCase().startsWith(lower)) ||
                      state.allMovies.find(m => m.title.toLowerCase().includes(lower));

        if (found) {
            // Found a specific movie in dataset -> recommend based on it
            state.activeSearchMode = "movie";
            updateQuickPickActive(found.id);
            loadSourceMovieAndRecommend(found.id);
            elements.searchInput.value = found.title;
        } else {
            // Free-text natural language story/plot search
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
            elements.sourceMovieCard.style.display = "flex";
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
                    ${k.term} <span>${k.tfidf_score}</span>
                </div>
            `).join("");
        } else {
            elements.srcTfidfTerms.innerHTML = '<span class="text-muted">No high-weight terms calculated</span>';
        }

        if (elements.resultsHeading) {
            elements.resultsHeading.textContent = `Films Similar to "${movie.title}"`;
        }
        if (elements.resultsSubheading) {
            elements.resultsSubheading.textContent = `Ranked by Cosine Similarity using TF-IDF across narrative synopsis, director (${movie.director}), and themes.`;
        }
    }

    async function fetchRecommendations() {
        const topN = elements.filterTopN.value;
        const genre = elements.filterGenre.value;
        const minRating = elements.filterRating.value;

        elements.recommendationsGrid.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner fa-spin empty-icon"></i>
                <p>Computing 5,000-dimensional TF-IDF vectors and cosine angles...</p>
            </div>
        `;

        try {
            const url = `/api/recommend?movie_id=${state.currentSourceId}&top_n=${topN}&genre=${encodeURIComponent(genre)}&min_rating=${minRating}`;
            const res = await fetch(url);
            const data = await res.json();

            if (data.status === "success") {
                state.currentRecommendations = data.recommendations;
                renderMovieCards(elements.recommendationsGrid, data.recommendations);

                // Smoothly scroll to results so user sees similar movies below search
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
    // PROMPT / STORY VECTOR SEARCH
    // ==========================================

    async function executePromptVectorSearch(prompt) {
        const topN = elements.filterTopN.value;
        const genre = elements.filterGenre.value;
        const minRating = elements.filterRating.value;

        // Hide source movie banner for free-text search
        if (elements.sourceMovieCard) {
            elements.sourceMovieCard.style.display = "none";
        }

        if (elements.resultsHeading) {
            elements.resultsHeading.textContent = `Vector Search Results for: "${prompt}"`;
        }
        if (elements.resultsSubheading) {
            elements.resultsSubheading.textContent = `Closest geometric alignments in TF-IDF term space ranked by angular cosine distance.`;
        }

        elements.recommendationsGrid.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-spinner fa-spin empty-icon"></i>
                <p>Vectorizing prompt query and calculating cosine similarity...</p>
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
                showToast(`Found ${data.recommendations.length} matching films`);

                // Smoothly scroll to recommendations
                if (elements.recommendationsSection) {
                    elements.recommendationsSection.scrollIntoView({ behavior: "smooth", block: "start" });
                }
            } else {
                elements.recommendationsGrid.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-magnifying-glass empty-icon"></i>
                        <p>No films matched the prompt "${prompt}". Try broader keywords like "space", "robot", "action", "mafia".</p>
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
            const isHighMatch = similarityPercent >= 15.0;

            // Visual Feature Attribution (How Similarity Was Found)
            let visualHowFoundHtml = "";
            if (movie.shared_terms && movie.shared_terms.length > 0) {
                // Find highest contribution for relative bar width
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
                            <i class="fa-solid fa-dna"></i>
                            <span>How Similarity Was Found:</span>
                        </div>
                        <div class="feature-contrib-list">
                            ${termsHtml}
                        </div>
                    </div>
                `;
            } else if (movie.matched_terms && movie.matched_terms.length > 0) {
                // For prompt search
                visualHowFoundHtml = `
                    <div class="how-found-box ${state.visualizeSearch ? 'visible' : 'hidden'}">
                        <div class="how-found-header">
                            <i class="fa-solid fa-bullseye"></i>
                            <span>Matched Query Terms:</span>
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
                            <i class="fa-solid fa-chart-simple"></i> ${similarityPercent}% Match
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
                updateQuickPickActive(id);
                loadSourceMovieAndRecommend(id);
                window.scrollTo({ top: elements.sourceMovieCard.offsetTop - 80, behavior: "smooth" });
            });
        });
    }

    // ==========================================
    // AUTOCOMPLETE & SEARCH INPUT HANDLING
    // ==========================================

    elements.searchInput.addEventListener("input", (e) => {
        const query = e.target.value.trim().toLowerCase();
        if (query.length > 0) {
            elements.btnClearSearch.style.display = "block";
            const matches = state.allMovies.filter(m => 
                m.title.toLowerCase().includes(query) || 
                (m.director && m.director.toLowerCase().includes(query)) ||
                (m.genres && m.genres.toLowerCase().includes(query)) ||
                (m.cast && m.cast.toLowerCase().includes(query))
            ).slice(0, 8);

            renderAutocompleteDropdown(matches);
        } else {
            elements.btnClearSearch.style.display = "none";
            elements.autocompleteResults.classList.remove("active");
        }
    });

    // Enter Key Search Trigger
    elements.searchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            handleSearchInput();
        }
    });

    // Search Button Click
    elements.btnSearchSubmit.addEventListener("click", () => {
        handleSearchInput();
    });

    // Clear Search Button
    elements.btnClearSearch.addEventListener("click", () => {
        elements.searchInput.value = "";
        elements.btnClearSearch.style.display = "none";
        elements.autocompleteResults.classList.remove("active");
        elements.searchInput.focus();
    });

    function renderAutocompleteDropdown(matches) {
        if (!matches || matches.length === 0) {
            elements.autocompleteResults.innerHTML = `
                <div class="autocomplete-item no-match" style="cursor:default;">
                    <div class="autocomplete-info">
                        <h4>Press Enter to search vector space for "${elements.searchInput.value}"</h4>
                        <p>Will match story plot and themes automatically</p>
                    </div>
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
                    updateQuickPickActive(id);
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

    // ==========================================
    // "VISUALIZE SEARCH" TOGGLE IMPLEMENTATION
    // ==========================================

    elements.btnToggleVisualize.addEventListener("click", () => {
        state.visualizeSearch = !state.visualizeSearch;

        if (state.visualizeSearch) {
            elements.btnToggleVisualize.classList.add("active");
            elements.visualizeToggleIndicator.textContent = "ON";
            elements.visualizeToggleIndicator.className = "toggle-pill on";
            if (elements.visualMathPanel) elements.visualMathPanel.style.display = "block";
            showToast("Visual Vector DNA & Term Contributions: Enabled");
        } else {
            elements.btnToggleVisualize.classList.remove("active");
            elements.visualizeToggleIndicator.textContent = "OFF";
            elements.visualizeToggleIndicator.className = "toggle-pill off";
            if (elements.visualMathPanel) elements.visualMathPanel.style.display = "none";
            showToast("Visual Vector DNA: Disabled");
        }

        // Toggle visibility of the "how-found-box" on all rendered cards
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

    // Filter Controls
    elements.filterGenre.addEventListener("change", () => {
        if (state.activeSearchMode === "movie") fetchRecommendations();
        else handleSearchInput();
    });

    elements.filterTopN.addEventListener("change", () => {
        if (state.activeSearchMode === "movie") fetchRecommendations();
        else handleSearchInput();
    });

    elements.filterRating.addEventListener("input", (e) => {
        elements.ratingValDisplay.textContent = parseFloat(e.target.value).toFixed(1);
    });

    elements.filterRating.addEventListener("change", () => {
        if (state.activeSearchMode === "movie") fetchRecommendations();
        else handleSearchInput();
    });

    // ==========================================
    // WATCHLIST DRAWER FUNCTIONALITY
    // ==========================================

    elements.btnOpenWatchlist.addEventListener("click", () => {
        renderWatchlistDrawer();
        elements.watchlistDrawerBackdrop.style.display = "flex";
    });

    elements.btnCloseWatchlist.addEventListener("click", () => {
        elements.watchlistDrawerBackdrop.style.display = "none";
    });

    elements.watchlistDrawerBackdrop.addEventListener("click", (e) => {
        if (e.target === elements.watchlistDrawerBackdrop) {
            elements.watchlistDrawerBackdrop.style.display = "none";
        }
    });

    function toggleWatchlist(movieId) {
        const movie = state.allMovies.find(m => m.id === movieId);
        if (!movie) return;

        const idx = state.watchlist.findIndex(m => m.id === movieId);
        if (idx > -1) {
            state.watchlist.splice(idx, 1);
            showToast(`Removed "${movie.title}" from watchlist`);
        } else {
            state.watchlist.push(movie);
            showToast(`Added "${movie.title}" to watchlist`);
        }

        localStorage.setItem("cinematch_watchlist", JSON.stringify(state.watchlist));
        updateWatchlistBadge();

        // Update card buttons
        document.querySelectorAll(`.btn-bookmark-card[data-id="${movieId}"]`).forEach(btn => {
            const isSaved = state.watchlist.some(m => m.id === movieId);
            btn.className = `btn-bookmark-card ${isSaved ? 'bookmarked' : ''}`;
            btn.querySelector("i").className = isSaved ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark';
        });

        if (elements.watchlistDrawerBackdrop.style.display === "flex") {
            renderWatchlistDrawer();
        }
    }

    function updateWatchlistBadge() {
        const count = state.watchlist.length;
        if (elements.watchlistCountBadge) elements.watchlistCountBadge.textContent = count;
        if (elements.drawerWatchlistCount) elements.drawerWatchlistCount.textContent = count;
        if (elements.btnClearWatchlist) {
            elements.btnClearWatchlist.style.display = count > 0 ? "inline-flex" : "none";
        }
    }

    function renderWatchlistDrawer() {
        if (!elements.watchlistGrid) return;

        if (state.watchlist.length === 0) {
            elements.watchlistGrid.innerHTML = `
                <div class="empty-state">
                    <i class="fa-regular fa-bookmark empty-icon"></i>
                    <p>Your watchlist is currently empty. Bookmark any movie to save it here.</p>
                </div>
            `;
            return;
        }

        renderMovieCards(elements.watchlistGrid, state.watchlist);
    }

    if (elements.btnClearWatchlist) {
        elements.btnClearWatchlist.addEventListener("click", () => {
            if (confirm("Clear all items from your watchlist?")) {
                state.watchlist = [];
                localStorage.removeItem("cinematch_watchlist");
                updateWatchlistBadge();
                renderWatchlistDrawer();
                showToast("Watchlist cleared");
            }
        });
    }

    // ==========================================
    // MOVIE DETAILS MODAL
    // ==========================================

    async function openMovieModal(movieId) {
        elements.movieModal.classList.add("active");
        elements.modalContent.innerHTML = `
            <div style="grid-column: 1 / -1; padding: 3rem; text-align: center; color: var(--text-secondary);">
                <i class="fa-solid fa-spinner fa-spin" style="font-size: 2rem; margin-bottom: 1rem; color: var(--accent-gold);"></i>
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
                <h4>Top TF-IDF Salient Keywords</h4>
                <div class="tfidf-tags-list">
                    ${movie.top_keywords.map(k => `
                        <div class="tfidf-tag" title="TF-IDF Weight: ${k.tfidf_score}">
                            ${k.term} <span>${k.tfidf_score}</span>
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
                        <i class="fa-solid fa-compass"></i> Find Similar Films
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
                    <span><i class="fa-solid fa-star" style="color: var(--accent-gold);"></i> ${movie.rating}</span>
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
            elements.movieModal.classList.remove("active");
            updateQuickPickActive(movie.id);
            loadSourceMovieAndRecommend(movie.id);
            window.scrollTo({ top: elements.sourceMovieCard.offsetTop - 80, behavior: "smooth" });
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
        elements.movieModal.classList.remove("active");
    });

    elements.movieModal.addEventListener("click", (e) => {
        if (e.target === elements.movieModal) {
            elements.movieModal.classList.remove("active");
        }
    });

    // Brand logo click resets to top
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
        // ESC key closes modals
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                if (elements.movieModal) elements.movieModal.classList.remove("active");
                if (elements.watchlistDrawerBackdrop) elements.watchlistDrawerBackdrop.style.display = "none";
                if (elements.autocompleteResults) elements.autocompleteResults.classList.remove("active");
            }
        });
    }

    // Start App
    init();
});
