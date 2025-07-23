// Market Research Platform - Frontend JavaScript

class MarketApp {
    constructor() {
        this.currentTab = 'recap';
        this.availableAssets = {};
        this.selectedAssets = {
            stocks: [],
            forex: [],
            indices: []
        };
        
        this.init();
    }

    _getAssetTypeKey(singularType) {
        if (singularType === 'index') return 'indices';
        if (singularType === 'forex') return 'forex';
        return singularType + 's'; // 'stock' -> 'stocks'
    }

    
    init() {
        // Initialize tab functionality
        this.initTabs();
        
        // Load available assets
        this.loadAvailableAssets();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Set default date range (last 7 days) - FIXED
        this.setDefaultDateRange();
    }
    
    initTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.dataset.tab;
                
                // Update button states
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                // Update content visibility
                tabContents.forEach(content => content.classList.remove('active'));
                const targetContent = document.getElementById(`${targetTab}-tab`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
                
                this.currentTab = targetTab;
                
                // Load content if switching to market tab
                if (targetTab === 'market') {
                    // If no assets selected, set defaults
                    if (!this.hasSelections()) {
                        setTimeout(() => {
                            this.setDefaultAssetSelection();
                        }, 100);
                    } else if (this.hasSelections()) {
                        // Refresh data for existing selections
                        this.loadMarketData();
                    }
                }
            });
        });
    }
    
    setupEventListeners() {
        // Market recap form
        const recapForm = document.getElementById('recap-form');
        if (recapForm) {
            recapForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.generateRecap();
            });
        }
        
        // Asset selection checkboxes
        document.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox' && e.target.dataset.asset) {
                this.handleAssetSelection(e.target);
            }
        });
        
        // Market data refresh button
        const refreshBtn = document.getElementById('refresh-market-data');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadMarketData();
            });
        }
    }
    
    setDefaultDateRange() {
        // FIXED: Better date handling with proper formatting
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - 7);
        
        // Format dates properly for HTML date input (YYYY-MM-DD)
        const formatDateForInput = (date) => {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0'); // Add leading zero
            const day = String(date.getDate()).padStart(2, '0'); // Add leading zero
            return `${year}-${month}-${day}`;
        };
        
        // Wait for DOM to be ready and set values
        const setDateValues = () => {
            const startInput = document.getElementById('start-date');
            const endInput = document.getElementById('end-date');
            
            if (startInput && endInput) {
                startInput.value = formatDateForInput(startDate);
                endInput.value = formatDateForInput(endDate);
                console.log('✅ Date values set:', {
                    start: startInput.value,
                    end: endInput.value
                });
            } else {
                console.log('⚠️ Date inputs not found, retrying...');
                // Retry after a short delay if elements not found
                setTimeout(setDateValues, 100);
            }
        };
        
        // Set dates immediately if DOM is ready, otherwise wait
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', setDateValues);
        } else {
            setDateValues();
        }
    }
    
    formatDate(date) {
        // DEPRECATED: Use the improved formatting above
        return date.toISOString().split('T')[0];
    }
    
    async loadAvailableAssets() {
        try {
            console.log('Loading available assets...');
            const response = await fetch('/api/available-assets');
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Loaded assets:', data);
            
            this.availableAssets = data;
            this.renderAssetSelection();
            
            console.log('Asset selection rendered');
            
        } catch (error) {
            console.error('Error loading available assets:', error);
            this.showAlert('Error loading asset list: ' + error.message, 'error');
        }
    }
    
    renderAssetSelection() {
        // Render stocks
        const stocksContainer = document.getElementById('stocks-selection');
        if (stocksContainer && this.availableAssets.stocks) {
            stocksContainer.innerHTML = this.renderAssetCheckboxes(this.availableAssets.stocks, 'stock');
        }
        
        // Render forex
        const forexContainer = document.getElementById('forex-selection');
        if (forexContainer && this.availableAssets.forex) {
            forexContainer.innerHTML = this.renderAssetCheckboxes(this.availableAssets.forex, 'forex');
        }
        
        // Render indices
        const indicesContainer = document.getElementById('indices-selection');
        if (indicesContainer && this.availableAssets.indices) {
            indicesContainer.innerHTML = this.renderAssetCheckboxes(this.availableAssets.indices, 'index');
        }
        
        // Update selection counts
        this.updateSelectionCount();
    }
    
    renderAssetCheckboxes(assets, type) {
        const assetTypeKey = this._getAssetTypeKey(type); // Use the helper function
        return assets.map(asset => `
            <div class="checkbox-item">
                <input type="checkbox" 
                       id="${type}-${asset.symbol}" 
                       data-asset="${type}" 
                       data-symbol="${asset.symbol}"
                       ${this.selectedAssets[assetTypeKey]?.includes(asset.symbol) ? 'checked' : ''}>
                <label for="${type}-${asset.symbol}" style="cursor: pointer; user-select: none;">
                    ${asset.name || asset.symbol}
                </label>
            </div>
        `).join('');
    }
    
     setDefaultAssetSelection() {
        // Check if assets are loaded
        if (!this.availableAssets.stocks || !this.availableAssets.forex || !this.availableAssets.indices) {
            console.log('Assets not loaded yet, waiting...');
            setTimeout(() => this.setDefaultAssetSelection(), 500);
            return;
        }
        
        // Select first 5 items from each category by default
        const defaultSelections = {
            stocks: this.availableAssets.stocks.slice(0, 5).map(a => a.symbol),
            forex: this.availableAssets.forex.slice(0, 5).map(a => a.symbol),
            indices: this.availableAssets.indices.slice(0, 5).map(a => a.symbol)
        };
        
        console.log('Setting default selections:', defaultSelections);
        this.selectedAssets = defaultSelections;
        
        // --- START OF FIX ---
        // Update checkboxes with correct logic
        Object.keys(defaultSelections).forEach(pluralType => {
            let singularType;
            switch (pluralType) {
                case 'stocks':
                    singularType = 'stock';
                    break;
                case 'forex':
                    singularType = 'forex';
                    break;
                case 'indices':
                    singularType = 'index';
                    break;
            }

            if (singularType) {
                defaultSelections[pluralType].forEach(symbol => {
                    const checkbox = document.getElementById(`${singularType}-${symbol}`);
                    if (checkbox) {
                        checkbox.checked = true;
                    } else {
                        console.log(`Checkbox not found: ${singularType}-${symbol}`);
                    }
                });
            }
        });
        // --- END OF FIX ---
        
        // Update selection counts
        this.updateSelectionCount();
        
        // Load market data
        this.loadMarketData();
    }
    
    handleAssetSelection(checkbox) {
        const assetType = this._getAssetTypeKey(checkbox.dataset.asset); // Use the helper function
        const symbol = checkbox.dataset.symbol;
        
        if (checkbox.checked) {
            // Check if we already have 5 selected
            if (this.selectedAssets[assetType].length >= 5) {
                checkbox.checked = false;
                this.showAlert(`You can only select up to 5 ${checkbox.dataset.asset} assets`, 'error');
                return;
            }
            
            if (!this.selectedAssets[assetType].includes(symbol)) {
                this.selectedAssets[assetType].push(symbol);
            }
        } else {
            this.selectedAssets[assetType] = this.selectedAssets[assetType].filter(s => s !== symbol);
        }
        
        // Update selection count display
        this.updateSelectionCount();
        
        // Auto-refresh market data if on market tab and we have selections
        if (this.currentTab === 'market' && this.hasSelections()) {
            this.loadMarketData();
        }
    }
    
    hasSelections() {
        return this.selectedAssets.stocks.length > 0 || 
               this.selectedAssets.forex.length > 0 || 
               this.selectedAssets.indices.length > 0;
    }
    
    updateSelectionCount() {
        // Update selection count displays
        const stockCount = document.getElementById('stock-count');
        const forexCount = document.getElementById('forex-count');
        const indexCount = document.getElementById('index-count');
        
        if (stockCount) stockCount.textContent = `(${this.selectedAssets.stocks.length}/5)`;
        if (forexCount) forexCount.textContent = `(${this.selectedAssets.forex.length}/5)`;
        if (indexCount) indexCount.textContent = `(${this.selectedAssets.indices.length}/5)`;
    }
    
    async generateRecap() {
        const generateBtn = document.getElementById('generate-recap-btn');
        const resultContainer = document.getElementById('recap-result');
        
        try {
            generateBtn.disabled = true;
            generateBtn.textContent = 'Generating...';
            
            resultContainer.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                </div>
                <p class="text-center">Generating market recap...</p>
            `;
            
            const formData = new FormData(document.getElementById('recap-form'));
            const requestData = {
                start_date: formData.get('start_date'),
                end_date: formData.get('end_date'),
                language: formData.get('language'),
                max_articles: 200, // Fixed value - always use 200 articles
                ai_temperature: parseFloat(formData.get('ai_temperature')) || 0.7,
                report_length: parseInt(formData.get('report_length')) || 1200,
                analysis_depth: formData.get('analysis_depth') || 'standard',
                include_sectors: formData.get('include_sectors') === 'on',
                include_compliance: formData.get('include_compliance') === 'on',
                include_outlook: formData.get('include_outlook') === 'on',
                include_references: formData.get('include_references') === 'on'
            };
            
            // Validate dates before sending
            if (!requestData.start_date || !requestData.end_date) {
                throw new Error('Please select both start and end dates');
            }
            
            console.log('📤 Sending request:', requestData);
            
            const response = await fetch('/api/generate-recap', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Store the raw report for download
                window.currentReport = data.report;
                window.currentDateRange = data.date_range;
                
                // Get report length description
                const reportLengthDesc = this.getReportLengthDescription(requestData.report_length);
                
                resultContainer.innerHTML = `
                    <div class="alert alert-success">
                        ✅ Report generated successfully! 
                        Analyzed ${data.articles_count} articles for ${data.date_range}
                        <div style="margin-top: 0.5rem;">
                            <strong>Sources:</strong> Benzinga Financial News API | 
                            <strong>Language:</strong> ${requestData.language} | 
                            <strong>Length:</strong> ${reportLengthDesc}
                        </div>
                    </div>
                    <div class="report-content">
                        ${this.formatReportContent(data.report)}
                    </div>
                    <div class="card mt-3">
                        <div class="card-header">
                            <h3>📥 Download Options</h3>
                        </div>
                        <div style="display: flex; gap: 1rem; flex-wrap: wrap; padding: 1rem 0;">
                            <button onclick="downloadCurrentReport()" class="btn btn-secondary">
                                📄 Download Text Report
                            </button>
                            <button onclick="copyCurrentReport()" class="btn btn-secondary">
                                📋 Copy to Clipboard
                            </button>
                            <button onclick="window.print()" class="btn btn-secondary">
                                🖨️ Print Report
                            </button>
                        </div>
                    </div>
                `;
            } else {
                resultContainer.innerHTML = `
                    <div class="alert alert-error">
                        ❌ Error: ${data.error}
                    </div>
                `;
            }
            
        } catch (error) {
            console.error('Error generating recap:', error);
            resultContainer.innerHTML = `
                <div class="alert alert-error">
                    ❌ Error generating report: ${error.message}
                </div>
            `;
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Market Recap';
        }
    }
    
    getReportLengthDescription(length) {
        const lengthMap = {
            800: 'Brief (800 words)',
            1200: 'Standard (1200 words)',
            1600: 'Detailed (1600 words)',
            2000: 'Comprehensive (2000 words)'
        };
        return lengthMap[length] || `${length} words`;
    }
    
    formatReportContent(content) {
        // Enhanced Markdown to HTML conversion
        let html = content
            // 1. Convert ## Headings to <h3>
            .replace(/^## (.*$)/gim, '<h3>$1</h3>')
            
            // 2. Convert **bold** text to <strong>
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            
            // 3. Convert Markdown links [Text](URL) to HTML <a> tags
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" style="color: var(--primary-orange); text-decoration: none;">$1 ↗</a>')
            
            // 4. Convert bullet points (* item) to HTML lists - FIXED VERSION
            .replace(/^\* (.*$)/gim, '<li>$1</li>')
            
            // 5. Convert numbered lists but force them to be bullets instead
            .replace(/^\d+\.\s+(.*$)/gim, '<li>$1</li>')
            
            // 6. Wrap consecutive list items in <ul> tags
            .replace(/(<li>.*<\/li>)/gs, (match) => {
                // Split into individual list items
                const items = match.split('</li>').filter(item => item.trim()).map(item => item + '</li>');
                return '<ul>' + items.join('') + '</ul>';
            })
            
            // 7. Clean up any double <ul> tags
            .replace(/<\/ul>\s*<ul>/g, '')
            
            // 8. Convert double newlines to paragraphs
            .replace(/\n\n/g, '</p><p>')
            
            // 9. Convert single newlines to line breaks
            .replace(/\n/g, '<br>');

        // Wrap the entire content in paragraph tags
        return `<p>${html}</p>`;
    }
    
    async loadMarketData() {
        const marketDataContainer = document.getElementById('market-data-container');
        const refreshBtn = document.getElementById('refresh-market-data');
        
        try {
            if (refreshBtn) refreshBtn.disabled = true;
            
            marketDataContainer.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                </div>
                <p class="text-center">Loading market data...</p>
            `;
            
            const response = await fetch('/api/market-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.selectedAssets)
            });
            
            const data = await response.json();
            
            if (data.success) {
                marketDataContainer.innerHTML = this.renderMarketData(data.data, data.last_updated);
            } else {
                marketDataContainer.innerHTML = `
                    <div class="alert alert-error">
                        ❌ Error: ${data.error}
                    </div>
                `;
            }
            
        } catch (error) {
            console.error('Error loading market data:', error);
            marketDataContainer.innerHTML = `
                <div class="alert alert-error">
                    ❌ Error loading market data. Please try again.
                </div>
            `;
        } finally {
            if (refreshBtn) refreshBtn.disabled = false;
        }
    }
    
    renderMarketData(data, lastUpdated) {
        let html = `
            <div class="alert alert-success">
                📊 Market data loaded successfully
                <small style="float: right;">Last updated: ${lastUpdated}</small>
            </div>
        `;
        
        // Render each category
        ['stocks', 'forex', 'indices'].forEach(category => {
            if (data[category] && data[category].length > 0) {
                html += this.renderDataTable(data[category], category.charAt(0).toUpperCase() + category.slice(1));
            }
        });
        
        return html;
    }
    
    renderDataTable(items, title) {
        return `
            <div class="card">
                <div class="card-header">
                    <h3>${title}</h3>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Name</th>
                            <th>Current Price</th>
                            <th>Weekly Change</th>
                            <th>Monthly Change</th>
                            <th>Link</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${items.map(item => `
                            <tr>
                                <td><strong>${item.symbol}</strong></td>
                                <td>${item.name}</td>
                                <td>${this.formatPrice(item.current_price)}</td>
                                <td class="${item.weekly_change >= 0 ? 'positive' : 'negative'}">
                                    ${this.formatPercentage(item.weekly_change)}
                                </td>
                                <td class="${item.monthly_change >= 0 ? 'positive' : 'negative'}">
                                    ${this.formatPercentage(item.monthly_change)}
                                </td>
                                <td>
                                    <a href="${item.link}" target="_blank" style="color: var(--primary-orange);">
                                        Yahoo Finance ↗
                                    </a>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    formatPrice(price) {
        if (price === null || price === undefined) return 'N/A';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(price);
    }
    
    formatPercentage(value) {
        if (value === null || value === undefined) return 'N/A';
        const sign = value >= 0 ? '+' : '';
        return `${sign}${value.toFixed(2)}%`;
    }
    
    showAlert(message, type = 'success') {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            ${type === 'success' ? '✅' : '❌'} ${message}
            <button onclick="this.parentElement.remove()" style="float: right; background: none; border: none; font-size: 1.2rem; cursor: pointer;">&times;</button>
        `;
        
        // Insert at top of container
        const container = document.querySelector('.container');
        if (container && container.firstChild) {
            container.insertBefore(alert, container.firstChild);
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MarketApp();
});

// FIXED: Global utility functions for download/copy
function copyCurrentReport() {
    if (window.currentReport) {
        copyToClipboard(window.currentReport, 'Report copied to clipboard!');
    } else {
        alert('No report available to copy.');
    }
}

function downloadCurrentReport() {
    if (window.currentReport && window.currentDateRange) {
        const filename = `market-recap-${window.currentDateRange.replace(/\s+/g, "-").replace(/,/g, "")}.txt`;
        downloadReport(window.currentReport, filename);
    } else {
        alert('No report available to download.');
    }
}

function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
    navigator.clipboard.writeText(text).then(() => {
        // Show success notification
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success';
        alertDiv.innerHTML = `✅ ${successMessage}`;
        alertDiv.style.position = 'fixed';
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '10000';
        alertDiv.style.maxWidth = '300px';
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            if (document.body.contains(alertDiv)) {
                document.body.removeChild(alertDiv);
            }
        }, 3000);
    }).catch((error) => {
        console.error('Copy failed:', error);
        // Show error notification
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-error';
        alertDiv.innerHTML = '❌ Failed to copy to clipboard';
        alertDiv.style.position = 'fixed';
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '10000';
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            if (document.body.contains(alertDiv)) {
                document.body.removeChild(alertDiv);
            }
        }, 3000);
    });
}

function downloadReport(content, filename) {
    // Add professional header to downloaded report
    const reportHeader = `MARKET RESEARCH PLATFORM
Professional Financial Analysis Report
Generated: ${new Date().toLocaleString()}
========================================

IMPORTANT DISCLAIMER:
This report is for informational purposes only and does not constitute 
investment or trading advice. Past performance is not indicative of future results.

========================================

`;
    
    // Clean the content for text download (remove HTML tags)
    const cleanContent = content
        .replace(/<[^>]*>/g, '') // Remove HTML tags
        .replace(/&nbsp;/g, ' ') // Replace HTML entities
        .replace(/&amp;/g, '&')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&quot;/g, '"')
        .replace(/&#039;/g, "'");
    
    const fullContent = reportHeader + cleanContent + `

========================================
© ${new Date().getFullYear()} Market Research Platform
Professional market data and financial news analysis
`;

    const element = document.createElement('a');
    const file = new Blob([fullContent], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}