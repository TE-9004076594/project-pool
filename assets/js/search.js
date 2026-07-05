/**
 * ProjectSearch - 前端搜索引擎
 * 支持实时搜索(防抖)、分类过滤、语言过滤、Star 范围过滤、多字段排序
 */
class ProjectSearch {
    constructor(options = {}) {
        this.searchIndex = null;
        this.allProjects = [];
        this.filteredProjects = [];
        this.debounceTimer = null;
        this.debounceDelay = options.debounceDelay || 300;
        this.scroller = null;
        this.filters = {
            categories: [],
            languages: [],
            licenses: [],
            minStars: 0,
            maxStars: Infinity,
        };
        this.sortBy = options.sortBy || 'stars';
        this.sortOrder = options.sortOrder || 'desc';

        // 绑定过滤回调
        this.onFilterChange = options.onFilterChange || null;
    }

    /**
     * 加载搜索索引
     */
    async loadIndex(url) {
        try {
            const response = await fetch(url);
            this.searchIndex = await response.json();
            this.allProjects = this.searchIndex.projects || [];
            this.filteredProjects = [...this.allProjects];
            this.applySorting();
            this.renderFacets();
            console.log(`搜索索引已加载: ${this.allProjects.length} 个项目`);
            return true;
        } catch (e) {
            console.error('加载搜索索引失败:', e);
            return false;
        }
    }

    /**
     * 实时搜索(防抖)
     */
    search(query) {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        this.debounceTimer = setTimeout(() => {
            this._performSearch(query);
        }, this.debounceDelay);
    }

    /**
     * 执行搜索
     */
    _performSearch(query) {
        if (!query || query.trim() === '') {
            this.filteredProjects = [...this.allProjects];
        } else {
            const lowerQuery = query.toLowerCase().trim();
            this.filteredProjects = this.allProjects.filter(project => {
                return (
                    (project.name && project.name.toLowerCase().includes(lowerQuery)) ||
                    (project.description_zh && project.description_zh.toLowerCase().includes(lowerQuery)) ||
                    (project.description_en && project.description_en.toLowerCase().includes(lowerQuery)) ||
                    (project.category_zh && project.category_zh.toLowerCase().includes(lowerQuery)) ||
                    (project.category && project.category.toLowerCase().includes(lowerQuery)) ||
                    (project.language && project.language.toLowerCase().includes(lowerQuery)) ||
                    (project.topics && project.topics.some(t => t.toLowerCase().includes(lowerQuery)))
                );
            });
        }

        this.applyFilters();
        this.applySorting();
        this.renderResults();
    }

    /**
     * 应用过滤条件
     */
    applyFilters() {
        this.filteredProjects = this.filteredProjects.filter(project => {
            // 分类过滤
            if (this.filters.categories.length > 0 &&
                !this.filters.categories.includes(project.category)) {
                return false;
            }

            // 语言过滤
            if (this.filters.languages.length > 0 &&
                !this.filters.languages.includes(project.language)) {
                return false;
            }

            // Star 范围过滤
            if (project.stars < this.filters.minStars ||
                project.stars > this.filters.maxStars) {
                return false;
            }

            return true;
        });
    }

    /**
     * 应用排序
     */
    applySorting() {
        const { sortBy, sortOrder } = this;
        const multiplier = sortOrder === 'asc' ? 1 : -1;

        this.filteredProjects.sort((a, b) => {
            switch (sortBy) {
                case 'stars':
                    return multiplier * ((a.stars || 0) - (b.stars || 0));
                case 'name':
                    return multiplier * (a.name || '').localeCompare(b.name || '');
                case 'updated':
                    const dateA = new Date(a.updated_at || 0);
                    const dateB = new Date(b.updated_at || 0);
                    return multiplier * (dateA - dateB);
                default:
                    return multiplier * ((a.stars || 0) - (b.stars || 0));
            }
        });
    }

    /**
     * 设置分类过滤
     */
    setCategoryFilter(categories) {
        this.filters.categories = categories;
        this.search(document.getElementById('search-input')?.value || '');
    }

    /**
     * 切换分类过滤
     */
    toggleCategory(category) {
        const idx = this.filters.categories.indexOf(category);
        if (idx > -1) {
            this.filters.categories.splice(idx, 1);
        } else {
            this.filters.categories.push(category);
        }
        this.search(document.getElementById('search-input')?.value || '');
    }

    /**
     * 设置语言过滤
     */
    setLanguageFilter(languages) {
        this.filters.languages = languages;
        this.search(document.getElementById('search-input')?.value || '');
    }

    /**
     * 切换语言过滤
     */
    toggleLanguage(language) {
        const idx = this.filters.languages.indexOf(language);
        if (idx > -1) {
            this.filters.languages.splice(idx, 1);
        } else {
            this.filters.languages.push(language);
        }
        this.search(document.getElementById('search-input')?.value || '');
    }

    /**
     * 设置 Star 范围
     */
    setStarRange(min, max) {
        this.filters.minStars = min || 0;
        this.filters.maxStars = max || Infinity;
        this.search(document.getElementById('search-input')?.value || '');
    }

    /**
     * 设置排序
     */
    setSort(sortBy, sortOrder) {
        if (sortBy) this.sortBy = sortBy;
        if (sortOrder) this.sortOrder = sortOrder;
        this.applySorting();
        this.renderResults();
    }

    /**
     * 渲染过滤选项
     */
    renderFacets() {
        if (!this.searchIndex || !this.searchIndex.facets) return;

        const { categories, languages, licenses } = this.searchIndex.facets;

        this._renderFacetGroup('filter-categories', categories, (cat) => {
            this.toggleCategory(cat);
        });

        this._renderFacetGroup('filter-languages', languages, (lang) => {
            this.toggleLanguage(lang);
        });
    }

    /**
     * 渲染过滤组
     */
    _renderFacetGroup(containerId, items, onClick) {
        const container = document.getElementById(containerId);
        if (!container || !items) return;

        const sorted = Object.entries(items).sort((a, b) => b[1] - a[1]);
        container.innerHTML = sorted.map(([key, count]) => {
            const isActive = this.filters.categories.includes(key) ||
                             this.filters.languages.includes(key);
            return `<span class="filter-chip ${isActive ? 'active' : ''}" data-key="${key}" onclick="this.classList.toggle('active'); onClick('${key}')">
                ${key} <span class="chip-count">${count}</span>
            </span>`;
        }).join('');
    }

    /**
     * 渲染搜索结果
     */
    renderResults() {
        const countEl = document.getElementById('result-count');
        if (countEl) {
            countEl.textContent = `共找到 ${this.filteredProjects.length} 个项目`;
        }

        // 使用虚拟滚动渲染
        if (this.scroller) {
            this.scroller.setItems(this.filteredProjects);
        } else {
            // 没有虚拟滚动时的后备渲染
            const container = document.getElementById('search-results');
            if (!container) return;
            container.innerHTML = this.filteredProjects.map(project => `
                <div class="mdc-card project-card" onclick="location.href='projects/${project.slug}/index.html'">
                    <div class="card-header">
                        <h3 class="project-name">${project.name}</h3>
                        <span class="badge badge-category">${project.category_zh || project.category}</span>
                    </div>
                    <p class="project-description">${project.description_zh || project.description_en}</p>
                    <div class="card-meta">
                        <span class="meta-item">⭐ ${(project.stars || 0).toLocaleString()}</span>
                        <span class="meta-item">💻 ${project.language || 'N/A'}</span>
                        <span class="meta-item">📄 ${project.license || 'N/A'}</span>
                    </div>
                </div>
            `).join('');
        }
    }

    /**
     * 重置所有过滤
     */
    resetFilters() {
        this.filters.categories = [];
        this.filters.languages = [];
        this.filters.licenses = [];
        this.filters.minStars = 0;
        this.filters.maxStars = Infinity;
        document.querySelectorAll('.filter-chip.active').forEach(el => {
            el.classList.remove('active');
        });
        document.querySelectorAll('.star-range input').forEach(el => {
            el.value = '';
        });
        this.search(document.getElementById('search-input')?.value || '');
    }
}
