/**
 * app.js - Client-Side Controller for CineMatch AI
 * Live TF-IDF Word Breakdown Animation & Recommendation Engine
 * Smart Computing using Python - Demonstration Package
 */

document.addEventListener("DOMContentLoaded", () => {
    // Standard English NLP Stopword Corpus for Visual Discarding
    const STOPWORDS = new Set([
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
        "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", 
        "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", 
        "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", 
        "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", 
        "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", 
        "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", 
        "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", 
        "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", 
        "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", 
        "with", "would", "you", "your", "yours", "yourself", "yourselves"
    ]);

    // State Store
    const state = {
        allMovies: [],
        currentSourceId: 1, // Default: Inception
        currentMovieData: null,
        currentRecommendations: [],
        showMatchedChips: true,
        watchlist: JSON.parse(localStorage.getItem("cinematch_watchlist") || "[]"),
        corpusStats: null,
        activeSearchMode: "movie", // "movie" or "prompt"
        playbackSpeed: 0.25, // 0.25x slow-mo playback default
        animationTimeouts: []
    };

    // DOM Elements
    const elements = {
        // Search & Autocomplete
        searchInput: document.getElementById("movie-search-input"),
        autocompleteResults: document.getElementById("autocomplete-results"),
        btnClearSearch: document.getElementById("btn-clear-search"),
        btnSearchSubmit: document.getElementById("btn-search-submit"),
        quickPickChips: document.getElementById("quick-pick-chips"),

        // Animation Stage Elements
        animationStageCard: document.getElementById("animation-stage-card"),
        animStageTitle: document.getElementById("anim-stage-title"),
        btnReplayAnim: document.getElementById("btn-replay-anim"),
        btnSkipAnim: document.getElementById("btn-skip-anim"),
        pillStep1: document.getElementById("pill-step-1"),
        pillStep2: document.getElementById("pill-step-2"),
        pillStep3: document.getElementById("pill-step-3"),
        connector1: document.getElementById("connector-1"),
        connector2: document.getElementById("connector-2"),
        animPhaseStatus: document.getElementById("anim-phase-status"),
        animTokensContainer: document.getElementById("anim-tokens-container"),
        animMatchingBlock: document.getElementById("anim-matching-block"),
        animMatchesGrid: document.getElementById("anim-matches-grid"),

        // Source Movie Banner
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

        // Filters
        filterGenre: document.getElementById("filter-genre"),
        filterRating: document.getElementById("filter-rating"),
        ratingValDisplay: document.getElementById("rating-val-display"),
        filterTopN: document.getElementById("filter-top-n"),
        btnToggleVisualize: document.getElementById("btn-toggle-visualize"),
        visualizeToggleIndicator: document.getElementById("visualize-toggle-indicator"),

        // Recommendations Grid
        resultsHeading: document.getElementById("results-heading"),
        resultsSubheading: document.getElementById("results-subheading"),
        recommendationsGrid: document.getElementById("recommendations-grid"),

        // Blueprint Modal
        blueprintModal: document.getElementById("blueprint-modal"),
        btnOpenAlgoBlueprint: document.getElementById("btn-open-algo-blueprint"),
        btnCloseBlueprintModal: document.getElementById("btn-close-blueprint-modal"),
        blueprintRareTerms: document.getElementById("blueprint-rare-terms"),
        blueprintCommonTerms: document.getElementById("blueprint-common-terms"),

        // Watchlist Drawer
        btnOpenWatchlist: document.getElementById("btn-open-watchlist"),
        watchlistCountBadge: document.getElementById("watchlist-count"),
        watchlistDrawerBackdrop: document.getElementById("watchlist-drawer-backdrop"),
        btnCloseWatchlist: document.getElementById("btn-close-watchlist"),
        drawerWatchlistCount: document.getElementById("drawer-watchlist-count"),
        watchlistGrid: document.getElementById("watchlist-grid"),
        btnClearWatchlist: document.getElementById("btn-clear-watchlist"),

        // Detail Modal
        movieModal: document.getElementById("movie-modal"),
        modalContent: document.getElementById("modal-content"),
        btnCloseModal: document.getElementById("btn-close-modal"),
        brandLogoBtn: document.getElementById("brand-logo-btn"),
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
        // Load default movie (Inception) and run initial animation
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
        const query = (rawQuery || (elements.searchInput ? elements.searchInput.value : "")).trim();
        if (!query) {
            showToast("Please select a film to demo the TF-IDF animation");
            return;
        }

        if (elements.autocompleteResults) elements.autocompleteResults.classList.remove("active");

        const lower = query.toLowerCase();
        const found = state.allMovies.find(m => m.title.toLowerCase() === lower) ||
                      state.allMovies.find(m => m.title.toLowerCase().startsWith(lower)) ||
                      state.allMovies.find(m => m.title.toLowerCase().includes(lower));

        if (found) {
            state.activeSearchMode = "movie";
            updateQuickPickActive(found.id);
            loadSourceMovieAndRecommend(found.id);
            if (elements.searchInput) elements.searchInput.value = found.title;
        } else {
            // Free-text plot search
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

        const genres = movie.genres ? movie.genres.split(",") : [];
        elements.srcGenres.innerHTML = genres.map(g => `<span class="genre-pill">${g.trim()}</span>`).join("");

        if (movie.top_keywords && movie.top_keywords.length > 0) {
            elements.srcTfidfTerms.innerHTML = movie.top_keywords.slice(0, 8).map(k => `
                <div class="tfidf-tag" title="TF-IDF Weight: ${k.tfidf_score}">
                    <i class="fa-solid fa-tag"></i> ${k.term}
                </div>
            `).join("");
        } else {
            elements.srcTfidfTerms.innerHTML = '<span class="text-muted">No keywords calculated</span>';
        }

        if (elements.resultsHeading) {
            elements.resultsHeading.innerHTML = `Similar Movies Found for "<strong>${movie.title}</strong>"`;
        }
    }

    async function fetchRecommendations() {
        const topN = elements.filterTopN.value;
        const genre = elements.filterGenre.value;
        const minRating = elements.filterRating.value;

        try {
            const url = `/api/recommend?movie_id=${state.currentSourceId}&top_n=${topN}&genre=${encodeURIComponent(genre)}&min_rating=${minRating}`;
            const res = await fetch(url);
            const data = await res.json();

            if (data.status === "success") {
                state.currentRecommendations = data.recommendations;
                renderMovieCards(elements.recommendationsGrid, data.recommendations);

                // TRIGGER THE ANIMATION: Break up searched movie into words, discard stopwords, and show matches!
                if (state.currentMovieData) {
                    runTfidfWordBreakdownAnimation(state.currentMovieData, data.recommendations);
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
            elements.resultsHeading.innerHTML = `Matching Movies for "<strong>${prompt}</strong>"`;
        }

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

                // Run animation on the prompt text!
                const syntheticPromptMovie = {
                    title: prompt,
                    overview: prompt,
                    top_keywords: (data.recommendations[0]?.matched_terms || []).map(t => ({ term: t, tfidf_score: 0.2 }))
                };
                runTfidfWordBreakdownAnimation(syntheticPromptMovie, data.recommendations);

                showToast(`Found ${data.recommendations.length} matching films`);
            } else {
                elements.recommendationsGrid.innerHTML = `
                    <div class="empty-state">
                        <i class="fa-solid fa-magnifying-glass empty-icon"></i>
                        <p>No films matched the prompt "${prompt}". Try words like "space", "robot", "action", "mafia".</p>
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

    // ==========================================================================
    // THE CORE ANIMATION: Word Breakdown, Stopword Discarding, & Target Matching
    // ==========================================================================

    function clearAnimationTimers() {
        state.animationTimeouts.forEach(t => clearTimeout(t));
        state.animationTimeouts = [];
    }

    function runTfidfWordBreakdownAnimation(sourceMovie, recommendations) {
        clearAnimationTimers();

        if (!elements.animationStageCard) return;
        elements.animationStageCard.style.display = "block";

        // Smooth scroll to animation stage so user sees it in action
        elements.animationStageCard.scrollIntoView({ behavior: "smooth", block: "nearest" });

        elements.animStageTitle.textContent = `Analyzing & Breaking Down: "${sourceMovie.title}"`;

        // Reset step progress indicators
        elements.pillStep1.className = "anim-step-pill active";
        elements.pillStep2.className = "anim-step-pill";
        elements.pillStep3.className = "anim-step-pill";
        elements.connector1.className = "anim-step-connector";
        elements.connector2.className = "anim-step-connector";
        elements.animMatchingBlock.style.display = "none";
        elements.animMatchesGrid.innerHTML = "";

        // Extract description words
        const rawWords = (sourceMovie.overview || "")
            .replace(/[^\w\s-]/g, "")
            .split(/\s+/)
            .filter(w => w.trim().length > 0)
            .slice(0, 26); // Focus on first 26 words for clean visual presentation

        // Extract critical, highly rare TF-IDF keywords
        const criticalKeyterms = (sourceMovie.top_keywords || []).map(k => k.term.toLowerCase());
        const criticalTokens = new Set();
        criticalKeyterms.forEach(k => {
            k.split(/\s+/).forEach(w => {
                if (w.length > 2 && !STOPWORDS.has(w)) {
                    criticalTokens.add(w);
                }
            });
        });

        // Playback speed factor (0.25x = 4x slower)
        const currentSpeed = state.playbackSpeed || 0.25;
        const speedFactor = 1 / currentSpeed;

        // PHASE 1: Populate all word chips with stagger animation
        elements.animPhaseStatus.innerHTML = `<i class="fa-solid fa-scissors text-mint"></i> Step 1: Breaking description into ${rawWords.length} individual word tokens (${currentSpeed}x speed)...`;
        
        elements.animTokensContainer.innerHTML = rawWords.map((word, i) => {
            const tokenDelay = Math.round(i * 35 * speedFactor);
            const animDuration = Math.round(300 * Math.min(speedFactor, 2.5));
            return `
                <span class="anim-word-token" id="token-${i}" style="animation-delay: ${tokenDelay}ms; animation-duration: ${animDuration}ms;">
                    <span class="token-word">${word}</span>
                </span>
            `;
        }).join("");

        // PHASE 2: Discard common words and keep ONLY highly rare, critical TF-IDF keywords
        const t1Delay = Math.round(950 * speedFactor);
        const t1 = setTimeout(() => {
            elements.pillStep1.className = "anim-step-pill completed";
            elements.connector1.className = "anim-step-connector active";
            elements.pillStep2.className = "anim-step-pill active";

            elements.animPhaseStatus.innerHTML = `<i class="fa-solid fa-filter text-amber"></i> Step 2: Discarding generic words & keeping ONLY rare, critical TF-IDF keywords...`;

            rawWords.forEach((word, i) => {
                const wordEvalDelay = Math.round(i * 20 * speedFactor);
                const subTimer = setTimeout(() => {
                    const el = document.getElementById(`token-${i}`);
                    if (!el) return;

                    const lower = word.toLowerCase();
                    const isStopword = STOPWORDS.has(lower) || lower.length <= 2;
                    
                    // Strict filter: Keep ONLY highly rare, critical words belonging to this movie's TF-IDF features!
                    const isCritical = !isStopword && (
                        criticalTokens.has(lower) ||
                        criticalKeyterms.some(kw => kw.includes(lower) || (lower.length > 4 && kw.startsWith(lower.slice(0, 4))))
                    );

                    if (isCritical) {
                        el.classList.add("retained");
                        el.innerHTML = `
                            <i class="fa-solid fa-star text-amber"></i>
                            <span class="token-word">${word}</span>
                            <span class="token-status-tag">critical (rare)</span>
                        `;
                    } else if (isStopword) {
                        el.classList.add("discarded");
                        el.innerHTML = `
                            <span class="token-word">${word}</span>
                            <span class="token-status-tag"><i class="fa-solid fa-xmark"></i> stopword</span>
                        `;
                    } else {
                        // Common / Low-IDF word is discarded!
                        el.classList.add("discarded", "low-idf");
                        el.innerHTML = `
                            <span class="token-word">${word}</span>
                            <span class="token-status-tag"><i class="fa-solid fa-xmark"></i> common</span>
                        `;
                    }
                }, wordEvalDelay);
                state.animationTimeouts.push(subTimer);
            });
        }, t1Delay);
        state.animationTimeouts.push(t1);

        // PHASE 3: Match candidate movies using overlapping words
        const t2Delay = Math.round(2000 * speedFactor);
        const t2 = setTimeout(() => {
            elements.pillStep2.className = "anim-step-pill completed";
            elements.connector2.className = "anim-step-connector active";
            elements.pillStep3.className = "anim-step-pill active";

            elements.animPhaseStatus.innerHTML = `<i class="fa-solid fa-bolt text-mint"></i> Step 3: Finding candidate movies that share these exact keywords in their descriptions!`;

            elements.animMatchingBlock.style.display = "flex";

            // Take top 3 recommendations to showcase description overlap
            const topMatches = recommendations.slice(0, 3);
            elements.animMatchesGrid.innerHTML = topMatches.map((movie, idx) => {
                // Highlight shared terms in overview
                let snippet = movie.overview || "";
                if (snippet.length > 130) snippet = snippet.slice(0, 130) + "...";

                const sharedList = (movie.shared_terms || [])
                    .map(t => t.term.replace(/_/g, " "))
                    .filter(t => !['action', 'drama', 'thriller', 'adventure', 'sci-fi', 'scifi', 'crime'].includes(t.toLowerCase()))
                    .slice(0, 3);

                sharedList.forEach(term => {
                    if (term.length > 2) {
                        const regex = new RegExp(`(${term})`, "gi");
                        snippet = snippet.replace(regex, `<mark class="match-highlight">$1</mark>`);
                    }
                });

                const matchedTags = sharedList.slice(0, 3).map(t => `<span class="match-highlight"><i class="fa-solid fa-star text-amber"></i> ${t}</span>`).join(" ");
                const matchDelay = Math.round(idx * 250 * speedFactor);

                return `
                    <div class="anim-match-card" style="animation-delay: ${matchDelay}ms;">
                        <img src="${movie.poster_url}" alt="${movie.title}" class="anim-match-thumb">
                        <div class="anim-match-info">
                            <div class="anim-match-title">${movie.title}</div>
                            <div class="anim-match-score"><i class="fa-solid fa-chart-simple"></i> ${movie.similarity_percent}% Word Match</div>
                            <div class="anim-match-desc-snippet">${snippet}</div>
                            <div class="match-words-badge">
                                <i class="fa-solid fa-check-double"></i> Overlap: ${matchedTags || 'Thematic alignment'}
                            </div>
                        </div>
                    </div>
                `;
            }).join("");
        }, t2Delay);
        state.animationTimeouts.push(t2);

        // PHASE 4: Animation Complete
        const t3Delay = Math.round(3100 * speedFactor);
        const t3 = setTimeout(() => {
            elements.pillStep3.className = "anim-step-pill completed";
            elements.animPhaseStatus.innerHTML = `<i class="fa-solid fa-circle-check text-emerald"></i> Done! Found ${recommendations.length} movies matching "${sourceMovie.title}" via description keywords.`;
        }, t3Delay);
        state.animationTimeouts.push(t3);
    }

    // Skip Button: Immediately jump to completed state
    if (elements.btnSkipAnim) {
        elements.btnSkipAnim.addEventListener("click", () => {
            clearAnimationTimers();
            elements.pillStep1.className = "anim-step-pill completed";
            elements.connector1.className = "anim-step-connector active";
            elements.pillStep2.className = "anim-step-pill completed";
            elements.connector2.className = "anim-step-connector active";
            elements.pillStep3.className = "anim-step-pill completed";

            elements.animPhaseStatus.innerHTML = `<i class="fa-solid fa-circle-check text-emerald"></i> Skipped to recommendations.`;

            // Mark retained chips
            document.querySelectorAll(".anim-word-token").forEach(el => {
                const text = el.querySelector(".token-word")?.textContent?.toLowerCase() || "";
                const isStopword = STOPWORDS.has(text) || text.length <= 2;
                const isCritical = !isStopword && (
                    criticalTokens.has(text) ||
                    criticalKeyterms.some(kw => kw.includes(text) || (text.length > 4 && kw.startsWith(text.slice(0, 4))))
                );
                if (isCritical) {
                    el.classList.add("retained");
                } else {
                    el.classList.add("discarded");
                }
            });

            // Smooth scroll down to full recommendations
            if (elements.recommendationsSection) {
                elements.recommendationsSection.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    }

    // Replay Button: Run animation again
    if (elements.btnReplayAnim) {
        elements.btnReplayAnim.addEventListener("click", () => {
            if (state.currentMovieData && state.currentRecommendations.length > 0) {
                runTfidfWordBreakdownAnimation(state.currentMovieData, state.currentRecommendations);
            }
        });
    }

    // Speed Selector Buttons (0.25x default)
    document.querySelectorAll(".btn-speed").forEach(btn => {
        btn.addEventListener("click", () => {
            const speed = parseFloat(btn.dataset.speed || "0.25");
            state.playbackSpeed = speed;
            document.querySelectorAll(".btn-speed").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            if (state.currentMovieData && state.currentRecommendations.length > 0) {
                runTfidfWordBreakdownAnimation(state.currentMovieData, state.currentRecommendations);
            }
        });
    });

    // ==========================================
    // RENDER MOVIE CARDS & REASONS
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
                return `Shares description keywords in "${term}" and character dynamics.`;
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

            // Matched keyword chips from description
            let matchedChipsHtml = "";
            if (movie.shared_terms && movie.shared_terms.length > 0) {
                const termsHtml = movie.shared_terms.slice(0, 4).map(t => {
                    const clean = t.term.replace(/_/g, " ");
                    return `<span class="shared-term-chip"><i class="fa-solid fa-tag"></i> ${clean}</span>`;
                }).join("");

                matchedChipsHtml = `
                    <div class="how-found-box ${state.showMatchedChips ? 'visible' : 'hidden'}">
                        <div class="how-found-header">
                            <i class="fa-solid fa-link text-mint"></i>
                            <span>Matched Description Words:</span>
                        </div>
                        <div style="display:flex; flex-wrap:wrap; gap:0.35rem; margin-top:0.4rem;">
                            ${termsHtml}
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

                        ${matchedChipsHtml}

                        <div class="movie-card-actions">
                            <button class="btn-card-action primary btn-inspect" data-id="${movie.id}" title="View details">
                                <i class="fa-regular fa-file-lines"></i> Details
                            </button>
                            <button class="btn-card-action btn-find-similar" data-id="${movie.id}" title="Search similar to this film">
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
            btn.addEventListener("click", () => {
                const id = parseInt(btn.dataset.id);
                openMovieModal(id);
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
    // AUTOCOMPLETE DROPDOWN & SEARCH (Optional)
    // ==========================================

    if (elements.searchInput) {
        elements.searchInput.addEventListener("input", (e) => {
            const query = e.target.value.trim().toLowerCase();
            if (elements.btnClearSearch) {
                elements.btnClearSearch.style.display = query.length > 0 ? "block" : "none";
            }

            if (!elements.autocompleteResults) return;

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
    }

    if (elements.btnSearchSubmit) {
        elements.btnSearchSubmit.addEventListener("click", () => {
            handleSearchInput();
        });
    }

    if (elements.btnClearSearch) {
        elements.btnClearSearch.addEventListener("click", () => {
            if (elements.searchInput) {
                elements.searchInput.value = "";
                elements.searchInput.focus();
            }
            elements.btnClearSearch.style.display = "none";
            if (elements.autocompleteResults) {
                elements.autocompleteResults.classList.remove("active");
            }
        });
    }

    function renderAutocompleteDropdown(matches) {
        if (!elements.autocompleteResults) return;

        if (matches.length === 0) {
            elements.autocompleteResults.innerHTML = `
                <div class="autocomplete-item empty">
                    <span>No exact title match.</span>
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
                    if (elements.searchInput) elements.searchInput.value = sel.title;
                    updateQuickPickActive(id);
                    loadSourceMovieAndRecommend(id);
                }
                elements.autocompleteResults.classList.remove("active");
            });
        });
    }

    document.addEventListener("click", (e) => {
        if (elements.autocompleteResults && !e.target.closest(".search-box-wrapper")) {
            elements.autocompleteResults.classList.remove("active");
        }
    });

    // Quick Pick Chips Demo Selector
    if (elements.quickPickChips) {
        elements.quickPickChips.querySelectorAll(".chip").forEach(chip => {
            chip.addEventListener("click", () => {
                const id = parseInt(chip.dataset.id);
                updateQuickPickActive(id);
                loadSourceMovieAndRecommend(id);
                const movie = state.allMovies.find(m => m.id === id);
                if (movie && elements.searchInput) elements.searchInput.value = movie.title;
            });
        });
    }

    // ==========================================
    // FILTERS & TOGGLES
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

    elements.btnToggleVisualize.addEventListener("click", () => {
        state.showMatchedChips = !state.showMatchedChips;
        
        if (state.showMatchedChips) {
            elements.btnToggleVisualize.classList.add("active");
            elements.visualizeToggleIndicator.textContent = "ON";
            elements.visualizeToggleIndicator.className = "toggle-pill on";
        } else {
            elements.btnToggleVisualize.classList.remove("active");
            elements.visualizeToggleIndicator.textContent = "OFF";
            elements.visualizeToggleIndicator.className = "toggle-pill off";
        }

        document.querySelectorAll(".how-found-box").forEach(box => {
            if (state.showMatchedChips) {
                box.classList.remove("hidden");
                box.classList.add("visible");
            } else {
                box.classList.remove("visible");
                box.classList.add("hidden");
            }
        });
    });

    // ==========================================
    // ALGORITHM BLUEPRINT MODAL (ALL FORMULAS KEPT HERE)
    // ==========================================

    function openBlueprintModal() {
        if (!elements.blueprintModal) return;
        elements.blueprintModal.style.display = "flex";

        if (state.corpusStats) {
            if (elements.blueprintRareTerms && state.corpusStats.sample_high_idf_terms) {
                elements.blueprintRareTerms.innerHTML = state.corpusStats.sample_high_idf_terms.map(t => `
                    <div class="idf-pill">
                        ${t.term} <span>IDF: ${t.idf}</span>
                    </div>
                `).join("");
            }

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
                <p>Loading film keywords and details...</p>
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
                <h4>Extracted TF-IDF Salient Keywords</h4>
                <div class="tfidf-tags-list">
                    ${movie.top_keywords.map(k => `
                        <div class="tfidf-tag">
                            <i class="fa-solid fa-tag"></i> ${k.term}
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
                        <i class="fa-solid fa-compass"></i> Animate & Find Similar
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
                    <h4>Description</h4>
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
            if (elements.searchInput) elements.searchInput.focus();
        });
    }

    // ==========================================
    // TOAST & KEYBOARD HELPERS
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
                if (elements.watchlistDrawerBackdrop) elements.watchlistDrawerBackdrop.style.display = "none";
                if (elements.autocompleteResults) elements.autocompleteResults.classList.remove("active");
            }
        });
    }

    // Start App
    init();
});
