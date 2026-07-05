/**
 * VirtualScroller - 虚拟滚动
 * 只渲染可视区域的 DOM 元素,优化大量列表渲染性能
 */
class VirtualScroller {
    constructor(container, options = {}) {
        this.container = container;
        this.itemHeight = options.itemHeight || 180;
        this.bufferSize = options.bufferSize || 5;
        this.items = [];
        this.visibleStart = 0;
        this.visibleEnd = 0;
        this.animationFrame = null;
        this.init();
    }

    /**
     * 初始化虚拟滚动 DOM 结构
     */
    init() {
        this.container.innerHTML = '';

        this.scrollContainer = document.createElement('div');
        this.scrollContainer.className = 'virtual-scroll-container';
        this.scrollContainer.style.height = this.container.style.height || '600px';

        this.contentPlaceholder = document.createElement('div');
        this.contentPlaceholder.className = 'virtual-scroll-content';

        this.visibleContainer = document.createElement('div');
        this.visibleContainer.className = 'virtual-scroll-visible';

        this.scrollContainer.appendChild(this.contentPlaceholder);
        this.scrollContainer.appendChild(this.visibleContainer);
        this.container.appendChild(this.scrollContainer);

        this.scrollContainer.addEventListener('scroll', () => {
            if (this.animationFrame) {
                cancelAnimationFrame(this.animationFrame);
            }
            this.animationFrame = requestAnimationFrame(() => this.onScroll());
        });
    }

    /**
     * 设置数据
     */
    setItems(items) {
        this.items = items;
        this.totalHeight = items.length * this.itemHeight;
        this.contentPlaceholder.style.height = `${this.totalHeight}px`;
        this.onScroll();
    }

    /**
     * 滚动事件处理
     */
    onScroll() {
        const scrollTop = this.scrollContainer.scrollTop;
        const viewportHeight = this.scrollContainer.clientHeight;

        this.visibleStart = Math.max(0,
            Math.floor(scrollTop / this.itemHeight) - this.bufferSize
        );
        this.visibleEnd = Math.min(
            this.items.length,
            Math.ceil((scrollTop + viewportHeight) / this.itemHeight) + this.bufferSize
        );

        this.renderVisibleItems();
        this.animationFrame = null;
    }

    /**
     * 渲染可见项目
     */
    renderVisibleItems() {
        const visibleItems = this.items.slice(this.visibleStart, this.visibleEnd);

        this.visibleContainer.innerHTML = '';
        this.visibleContainer.style.transform = `translateY(${this.visibleStart * this.itemHeight}px)`;

        visibleItems.forEach((project, index) => {
            const el = this._createCard(project, index);
            this.visibleContainer.appendChild(el);
        });
    }

    /**
     * 创建项目卡片 DOM
     */
    _createCard(project, index) {
        const card = document.createElement('div');
        card.className = 'mdc-card project-card';
        card.style.position = 'absolute';
        card.style.top = `${index * this.itemHeight}px`;
        card.style.left = '0';
        card.style.right = '0';
        card.style.margin = '0 0 8px';

        card.innerHTML = `
            <div class="card-header">
                <h3 class="project-name">${this._escapeHtml(project.name)}</h3>
                <span class="badge badge-category">${this._escapeHtml(project.category_zh || project.category)}</span>
            </div>
            <p class="project-description">${this._escapeHtml(project.description_zh || project.description_en || '')}</p>
            <div class="card-meta">
                <span class="meta-item">⭐ ${(project.stars || 0).toLocaleString()}</span>
                <span class="meta-item">💻 ${this._escapeHtml(project.language || 'N/A')}</span>
                <span class="meta-item">📄 ${this._escapeHtml(project.license || 'N/A')}</span>
            </div>
        `;

        card.addEventListener('click', () => {
            window.location.href = `projects/${project.slug}/index.html`;
        });

        card.style.cursor = 'pointer';
        return card;
    }

    /**
     * HTML 转义
     */
    _escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
