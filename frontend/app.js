// Configuration
const API_CONFIG = {
    baseURL: 'http://localhost:7860',
    apiKey: 'ecopackai_secure_key_2025',
    endpoints: {
        recommendations: '/api/recommendations',
        health: '/api/health'
    }
};

// State Management
let currentData = null;
let sortColumn = null;
let sortDirection = 'asc';
let backendConnected = false;

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    checkBackendConnection();
    initializeForm();
    setupEventListeners();
});

// Check Backend Connection
async function checkBackendConnection() {
    const statusEl = document.getElementById('backendStatus');
    
    statusEl.className = 'backend-status-dot checking';
    statusEl.title = 'Checking backend...';
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.health}`, {
            method: 'GET',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            backendConnected = true;
            statusEl.className = 'backend-status-dot connected';
            statusEl.title = 'Backend Connected';
        } else {
            throw new Error('Backend responded with error');
        }
    } catch (error) {
        backendConnected = false;
        statusEl.className = 'backend-status-dot disconnected';
        statusEl.title = 'Backend Offline - Please start backend server';
        console.error('Backend connection failed:', error);
    }
}

// Form Initialization
function initializeForm() {
    const form = document.getElementById('productForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!validateForm(form)) {
            return;
        }
        
        const formData = collectFormData();
        await submitRequest(formData);
    });
    
    form.addEventListener('reset', () => {
        form.classList.remove('was-validated');
        document.getElementById('results').classList.add('d-none');
        scrollToSection('input');
    });
}

// Setup Event Listeners
function setupEventListeners() {
    // Add input validation on blur
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', () => {
            validateField(input);
        });
        
        input.addEventListener('input', () => {
            if (input.classList.contains('is-invalid')) {
                validateField(input);
            }
        });
    });
}

// Form Validation
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('.form-control[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(input) {
    let isValid = true;
    
    if (input.hasAttribute('required') && !input.value.trim()) {
        isValid = false;
    }
    
    if (input.type === 'number') {
        const value = parseFloat(input.value);
        const min = input.hasAttribute('min') ? parseFloat(input.min) : -Infinity;
        const max = input.hasAttribute('max') ? parseFloat(input.max) : Infinity;
        
        if (isNaN(value) || value < min || value > max) {
            isValid = false;
        }
    }
    
    if (isValid) {
        input.classList.remove('is-invalid');
    } else {
        input.classList.add('is-invalid');
    }
    
    return isValid;
}

// Collect Form Data
function collectFormData() {
    const formData = {
        product_name: document.getElementById('productName').value.trim(),
        category: document.getElementById('category').value,
        weight: parseFloat(document.getElementById('weight').value),
        volume: parseFloat(document.getElementById('volume').value),
        fragility: document.getElementById('fragility').value,
        temperature: parseFloat(document.getElementById('temperature').value),
        humidity: parseInt(document.getElementById('humidity').value),
        shelf_life: parseInt(document.getElementById('shelfLife').value),
        quantity: parseInt(document.getElementById('quantity').value),
        priority: document.getElementById('priority').value,
        special_requirements: document.getElementById('specialRequirements').value.trim()
    };
    
    // Transform to backend API format with more detailed requirements
    return {
        product_requirements: {
            strength_required: formData.fragility === 'Low' ? 20 : formData.fragility === 'Medium' ? 40 : 60,
            weight_capacity: formData.weight,
            biodegradability_preference: formData.priority === 'Sustainability' ? 'high' : 'medium',
            budget_constraint: formData.priority === 'Cost' ? 70 : formData.priority === 'Sustainability' ? 100 : 120,
            recyclability_preference: formData.priority === 'Sustainability' ? 'high' : 'medium',
            temperature_sensitive: formData.temperature < 10 || formData.temperature > 30,
            moisture_sensitive: formData.category === 'Electronics' || formData.category === 'Pharmaceuticals',
            category: formData.category,
            humidity: formData.humidity,
            shelf_life: formData.shelf_life,
            priority: formData.priority
        },
        top_n: 5
    };
}

// Submit Request to API
async function submitRequest(data) {
    const submitBtn = document.querySelector('button[type="submit"]');
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.recommendations}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_CONFIG.apiKey
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            let errorMessage = `Server error: ${response.status}`;
            try {
                const error = await response.json();
                errorMessage = error.error || error.message || errorMessage;
            } catch (e) {
                // If JSON parsing fails, use status text
                errorMessage = response.statusText || errorMessage;
            }
            throw new Error(errorMessage);
        }
        
        const result = await response.json();
        
        console.log('Backend Response:', result); // Debug log
        
        // Handle different response formats
        let materials = null;
        if (result.data && result.data.recommendations) {
            materials = result.data.recommendations;
        } else if (result.recommendations) {
            materials = result.recommendations;
        } else if (result.materials) {
            materials = result.materials;
        } else if (Array.isArray(result)) {
            materials = result;
        } else if (result.data && Array.isArray(result.data)) {
            materials = result.data;
        }
        
        console.log('Extracted Materials:', materials); // Debug log
        
        if (materials && materials.length > 0) {
            currentData = materials;
            displayResults(materials);
            showToast('success', 'Analysis complete! Scroll down to view recommendations.');
            setTimeout(() => scrollToSection('results'), 300);
        } else {
            throw new Error('No recommendations received from server');
        }
        
    } catch (error) {
        console.error('API Error:', error);
        
        // Provide more specific error messages
        let errorMsg = error.message;
        if (error.message.includes('Failed to fetch')) {
            errorMsg = 'Cannot connect to backend server. Please ensure the backend is running on http://localhost:7860';
        } else if (error.message.includes('NetworkError')) {
            errorMsg = 'Network error. Please check your connection and ensure the backend server is running.';
        }
        
        showToast('error', errorMsg);
    } finally {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
}

// Display Results
function displayResults(materials) {
    document.getElementById('results').classList.remove('d-none');
    
    // Top 3 Recommendation Cards
    displayRecommendationCards(materials.slice(0, 3));
    
    // Comparison Table
    displayComparisonTable(materials);
    
    // Metrics
    displayMetrics(materials);
}

// Display Recommendation Cards
function displayRecommendationCards(topMaterials) {
    const grid = document.getElementById('recommendationsGrid');
    grid.innerHTML = '';
    
    topMaterials.forEach((material, index) => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        
        const score = parseFloat(material.suitability_score) || 85;
        const cost = parseFloat(material.predicted_cost || material.cost_per_kg || material.actual_cost_per_kg) || 0;
        const co2 = parseFloat(material.predicted_co2 || material.co2_emission || material.actual_co2_emission) || 0;
        const name = material.material_name || material.name || `Material ${index + 1}`;
        const materialType = material.material_type || 'Bio';
        const strength = parseFloat(material.strength_mpa) || 0;
        const recyclable = parseInt(material.recyclability_percent) || 0;
        const reason = material.recommendation_reason || 'Excellent match for your requirements; highly biodegradable; low carbon footprint';
        
        card.innerHTML = `
            <div class="card-rank rank-${index + 1}">${index + 1}</div>
            <div class="card-material">${name}</div>
            
            <div class="card-metrics">
                <div class="metric-item">
                    <div class="metric-label">Cost/kg</div>
                    <div class="metric-value">$${cost.toFixed(2)}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">CO₂</div>
                    <div class="metric-value">${co2.toFixed(2)}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Strength</div>
                    <div class="metric-value">${strength.toFixed(2)} MPa</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">Recyclable</div>
                    <div class="metric-value">${recyclable}%</div>
                </div>
            </div>
            
            <div class="card-score">
                <div class="score-label">
                    <span>Suitability Score</span>
                    <span>${score.toFixed(0)}%</span>
                </div>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${score}%"></div>
                </div>
            </div>
            
            <div class="card-properties">
                <small><strong>Type:</strong> ${materialType}</small><br>
                <small><strong>Reason:</strong> ${reason}</small>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

// Generate Property Badges
function generatePropertyBadges(material) {
    const badges = [];
    
    if (material.recyclable !== false) {
        badges.push('<span class="property-badge badge-success">Recyclable</span>');
    }
    if (material.biodegradable === true) {
        badges.push('<span class="property-badge badge-info">Biodegradable</span>');
    }
    if (material.durability === 'High' || material.strength > 70) {
        badges.push('<span class="property-badge badge-info">Durable</span>');
    }
    if (material.cost_effective !== false) {
        badges.push('<span class="property-badge badge-warning">Cost-Effective</span>');
    }
    
    if (badges.length === 0) {
        badges.push('<span class="property-badge badge-success">Sustainable</span>');
    }
    
    return badges.join('');
}

// Display Comparison Table
function displayComparisonTable(materials) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    
    materials.forEach((material, index) => {
        const row = document.createElement('tr');
        
        const score = material.suitability_score || 85;
        const cost = material.predicted_cost || material.actual_cost_per_kg || 0;
        const co2 = material.predicted_co2 || material.actual_co2_emission || 0;
        const name = material.material_name || material.material_type || `Material ${index + 1}`;
        
        const co2Class = co2 < 1.5 ? 'co2-low' : co2 < 2.5 ? 'co2-medium' : 'co2-high';
        
        row.innerHTML = `
            <td class="table-rank">${index + 1}</td>
            <td class="table-material">${name}</td>
            <td class="table-cost">$${cost.toFixed(2)}</td>
            <td><span class="co2-badge ${co2Class}">${co2.toFixed(2)}</span></td>
            <td>${material.strength_mpa || 0} MPa</td>
            <td>${material.recyclability_percent || 0}%</td>
            <td>
                <div class="score-cell">
                    <div class="mini-bar">
                        <div class="mini-fill" style="width: ${score}%"></div>
                    </div>
                    <span>${score}%</span>
                </div>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

// Display Metrics
function displayMetrics(materials) {
    const grid = document.getElementById('metricsGrid');
    grid.innerHTML = '';
    
    const avgCost = materials.reduce((sum, m) => sum + (m.predicted_cost || m.actual_cost_per_kg || 0), 0) / materials.length;
    const avgCO2 = materials.reduce((sum, m) => sum + (m.predicted_co2 || m.actual_co2_emission || 0), 0) / materials.length;
    const avgScore = materials.reduce((sum, m) => sum + (m.suitability_score || 0), 0) / materials.length;
    const ecoCount = materials.filter(m => m.recyclable !== false || m.biodegradable === true).length;
    
    const metrics = [
        { label: 'Best Match', value: materials[0].material_type || materials[0].name || 'Material 1', icon: 'trophy-fill' },
        { label: 'Avg Cost', value: `$${avgCost.toFixed(2)}`, icon: 'currency-dollar' },
        { label: 'Avg CO₂', value: `${avgCO2.toFixed(1)} kg`, icon: 'cloud-fill' },
        { label: 'Avg Score', value: `${avgScore.toFixed(1)}%`, icon: 'star-fill' }
    ];
    
    metrics.forEach(metric => {
        const card = document.createElement('div');
        card.className = 'metric-card';
        card.innerHTML = `
            <div class="metric-card-content">
                <div class="metric-card-label">${metric.label}</div>
                <div class="metric-card-value">${metric.value}</div>
            </div>
            <i class="bi bi-${metric.icon} metric-card-icon"></i>
        `;
        grid.appendChild(card);
    });
}

// Table Sorting
function sortTable(column) {
    if (!currentData) return;
    
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'asc';
    }
    
    const sorted = [...currentData].sort((a, b) => {
        let aVal, bVal;
        
        switch(column) {
            case 'rank':
                return 0; // Keep original order
            case 'material':
                aVal = a.material_type || a.name || '';
                bVal = b.material_type || b.name || '';
                return sortDirection === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            case 'cost':
                aVal = a.estimated_cost || a.cost || 0;
                bVal = b.estimated_cost || b.cost || 0;
                break;
            case 'co2':
                aVal = a.co2_emission || a.co2 || 0;
                bVal = b.co2_emission || b.co2 || 0;
                break;
            case 'score':
                aVal = a.suitability_score || a.score || 0;
                bVal = b.suitability_score || b.score || 0;
                break;
            default:
                return 0;
        }
        
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
    });
    
    displayComparisonTable(sorted);
}

// Scroll to Section
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        // Show dashboard section when navigated to
        if (sectionId === 'dashboard') {
            element.style.display = 'block';
            loadDashboardData();
        }
        
        const headerOffset = 80;
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
}

// Dashboard Functions
let dashboardData = null;

async function loadDashboardData() {
    const loading = document.getElementById('dashboardLoading');
    const content = document.getElementById('dashboardContent');
    const empty = document.getElementById('dashboardEmpty');
    
    loading.style.display = 'block';
    content.style.display = 'none';
    empty.style.display = 'none';
    
    try {
        const response = await fetch(`${API_CONFIG.baseURL}/api/analytics`, {
            headers: {
                'X-API-Key': API_CONFIG.apiKey,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) throw new Error('Failed to load analytics');
        
        const result = await response.json();
        dashboardData = result.data;
        
        loading.style.display = 'none';
        
        if (dashboardData.total_requests === 0) {
            empty.style.display = 'block';
            return;
        }
        
        content.style.display = 'block';
        updateDashboardMetrics();
        renderDashboardCharts();
    } catch (error) {
        console.error('Dashboard error:', error);
        loading.innerHTML = '<div class="alert alert-danger">Error loading dashboard data</div>';
    }
}

function updateDashboardMetrics() {
    const co2Pct = parseFloat(dashboardData.co2_reduction_pct) || 0;
    const co2Saved = parseFloat(dashboardData.co2_saved) || 0;
    const costSaved = parseFloat(dashboardData.cost_saved) || 0;
    const totalReq = parseInt(dashboardData.total_requests) || 0;
    
    document.getElementById('dash-co2-pct').textContent = `${co2Pct.toFixed(1)}%`;
    document.getElementById('dash-co2-saved').textContent = `${co2Saved.toFixed(2)} kg saved`;
    document.getElementById('dash-cost').textContent = `$${costSaved.toFixed(2)}`;
    document.getElementById('dash-total').textContent = totalReq;
    
    const materials = dashboardData.material_usage || {};
    const topMat = Object.entries(materials).sort((a, b) => b[1] - a[1])[0];
    if (topMat) {
        document.getElementById('dash-top-mat').textContent = topMat[0];
        document.getElementById('dash-mat-count').textContent = `${topMat[1]} uses`;
    } else {
        document.getElementById('dash-top-mat').textContent = 'N/A';
        document.getElementById('dash-mat-count').textContent = '0 uses';
    }
}

function renderDashboardCharts() {
    // CO2 Chart - Enhanced bar chart with gradient and accurate values
    Plotly.newPlot('dashCo2Chart', [{
        x: ['Traditional Packaging', 'AI-Recommended Solution'],
        y: [3.0, parseFloat(dashboardData.avg_co2)],
        type: 'bar',
        marker: { 
            color: ['rgba(239, 68, 68, 0.9)', 'rgba(16, 185, 129, 0.9)'],
            line: { color: ['#dc2626', '#059669'], width: 3 }
        },
        text: [`${(3.0).toFixed(2)} kg CO₂`, `${parseFloat(dashboardData.avg_co2).toFixed(2)} kg CO₂`],
        textposition: 'outside',
        textfont: { size: 14, weight: 'bold', color: '#1f2937' }
    }], {
        title: { text: 'Environmental Impact Comparison', font: { size: 14, weight: 'bold' } },
        height: 320,
        margin: { t: 60, b: 60, l: 70, r: 30 },
        yaxis: { 
            title: 'CO₂ Emission (kg per kg material)', 
            titlefont: { size: 13, color: '#374151' },
            gridcolor: '#e5e7eb',
            zerolinecolor: '#9ca3af'
        },
        xaxis: { titlefont: { size: 12 } },
        paper_bgcolor: 'rgba(255,255,255,0.95)',
        plot_bgcolor: 'rgba(248, 250, 252, 0.8)',
        font: { family: 'Inter, system-ui, sans-serif' }
    }, { displayModeBar: false, responsive: true });

    // Cost Chart - Enhanced with accurate calculations
    const costSavings = ((100.0 - parseFloat(dashboardData.avg_cost)) / 100.0 * 100).toFixed(1);
    Plotly.newPlot('dashCostChart', [{
        x: ['Traditional Method', 'AI-Optimized Selection'],
        y: [100.0, parseFloat(dashboardData.avg_cost)],
        type: 'bar',
        marker: { 
            color: ['rgba(251, 146, 60, 0.9)', 'rgba(59, 130, 246, 0.9)'],
            line: { color: ['#f97316', '#2563eb'], width: 3 }
        },
        text: [`$${(100.0).toFixed(2)}/kg`, `$${parseFloat(dashboardData.avg_cost).toFixed(2)}/kg<br>${costSavings}% Savings`],
        textposition: 'outside',
        textfont: { size: 13, weight: 'bold', color: '#1f2937' }
    }], {
        title: { text: 'Cost Efficiency Analysis', font: { size: 14, weight: 'bold' } },
        height: 320,
        margin: { t: 60, b: 60, l: 70, r: 30 },
        yaxis: { 
            title: 'Cost per Kilogram (USD)', 
            titlefont: { size: 13, color: '#374151' },
            gridcolor: '#e5e7eb',
            zerolinecolor: '#9ca3af'
        },
        xaxis: { titlefont: { size: 12 } },
        paper_bgcolor: 'rgba(255,255,255,0.95)',
        plot_bgcolor: 'rgba(248, 250, 252, 0.8)',
        font: { family: 'Inter, system-ui, sans-serif' }
    }, { displayModeBar: false, responsive: true });

    // Material Chart - Enhanced donut chart with vibrant colors
    const materials = Object.keys(dashboardData.material_usage);
    const counts = Object.values(dashboardData.material_usage);
    const totalCount = counts.reduce((a, b) => a + b, 0);
    
    const pieColors = {
        'Plastic': '#ef4444',  'Paper': '#f59e0b',    'Bio': '#10b981',      
        'Fiber': '#3b82f6',    'Metal': '#8b5cf6',    'Glass': '#06b6d4',
        'Cardboard': '#f97316', 'Bamboo': '#84cc16',  'Hemp': '#14b8a6'
    };
    
    const chartColors = materials.map(m => pieColors[m] || '#6366f1');
    const percentages = counts.map(c => ((c / totalCount) * 100).toFixed(1));
    
    Plotly.newPlot('dashMaterialChart', [{
        labels: materials.map((m, i) => `${m} (${percentages[i]}%)`),
        values: counts,
        type: 'pie',
        marker: { 
            colors: chartColors,
            line: { color: 'white', width: 3 }
        },
        textinfo: 'label',
        textfont: { size: 12, weight: 'bold' },
        hovertemplate: '<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
        hole: 0.4,
        pull: materials.map((_, i) => i === 0 ? 0.08 : 0.02)
    }], {
        title: { text: 'Material Selection Distribution', font: { size: 14, weight: 'bold' } },
        height: 340,
        margin: { t: 50, b: 30, l: 20, r: 20 },
        showlegend: true,
        legend: { 
            orientation: 'v', 
            x: 1.05, 
            y: 0.5,
            font: { size: 11 }
        },
        paper_bgcolor: 'rgba(255,255,255,0.95)',
        annotations: [{
            text: `Total<br>${totalCount}`,
            x: 0.5, y: 0.5,
            font: { size: 18, weight: 'bold', color: '#1f2937' },
            showarrow: false
        }]
    }, { displayModeBar: false, responsive: true });

    // Trend Chart - Enhanced multi-metric visualization
    const recent = dashboardData.recommendations.slice(-20).reverse();
    const requestLabels = recent.map((_, i) => `Request ${recent.length - i}`);
    
    Plotly.newPlot('dashTrendChart', [
        {
            x: requestLabels,
            y: recent.map(r => parseFloat(r.co2_emission || 0)),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'CO₂ Emission (kg)',
            line: { color: '#10b981', width: 3, shape: 'spline' },
            marker: { size: 9, color: '#059669', line: { color: 'white', width: 2 } },
            hovertemplate: 'CO₂: %{y:.2f} kg<extra></extra>'
        },
        {
            x: requestLabels,
            y: recent.map(r => parseFloat(r.cost_per_kg || 0)),
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Cost ($/kg)',
            yaxis: 'y2',
            line: { color: '#3b82f6', width: 3, shape: 'spline' },
            marker: { size: 9, color: '#2563eb', line: { color: 'white', width: 2 } },
            hovertemplate: 'Cost: $%{y:.2f}/kg<extra></extra>'
        }
    ], {
        title: { text: 'Performance Trends Over Time', font: { size: 14, weight: 'bold' } },
        height: 340,
        margin: { t: 50, b: 80, l: 70, r: 70 },
        yaxis: { 
            title: 'CO₂ Emission (kg)', 
            titlefont: { size: 12, color: '#10b981' }, 
            tickfont: { color: '#10b981' },
            gridcolor: '#e5e7eb'
        },
        yaxis2: { 
            title: 'Cost ($/kg)', 
            titlefont: { size: 12, color: '#3b82f6' }, 
            tickfont: { color: '#3b82f6' }, 
            overlaying: 'y', 
            side: 'right' 
        },
        xaxis: { 
            title: 'Recent Recommendations', 
            titlefont: { size: 12 },
            tickangle: -45,
            tickfont: { size: 10 }
        },
        legend: { 
            orientation: 'h', 
            y: -0.25, 
            x: 0.5, 
            xanchor: 'center',
            font: { size: 11 }
        },
        paper_bgcolor: 'rgba(255,255,255,0.95)',
        plot_bgcolor: 'rgba(248, 250, 252, 0.8)',
        font: { family: 'Inter, system-ui, sans-serif' }
    }, { displayModeBar: false, responsive: true });
    
    // Additional Chart: Recyclability Analysis
    if (dashboardData.recommendations.length > 0) {
        const recyclabilityData = recent.map(r => ({
            material: r.material_type || 'Unknown',
            recyclability: parseFloat(r.recyclability_percent || 0),
            strength: parseFloat(r.strength_mpa || 0)
        }));
        
        Plotly.newPlot('dashRecyclabilityChart', [{
            x: recyclabilityData.map(d => d.material),
            y: recyclabilityData.map(d => d.recyclability),
            type: 'bar',
            marker: {
                color: recyclabilityData.map(d => 
                    d.recyclability >= 80 ? '#10b981' : 
                    d.recyclability >= 50 ? '#f59e0b' : '#ef4444'
                ),
                line: { width: 2, color: '#fff' }
            },
            text: recyclabilityData.map(d => `${d.recyclability}%`),
            textposition: 'outside',
            hovertemplate: '<b>%{x}</b><br>Recyclability: %{y}%<extra></extra>'
        }], {
            title: { text: 'Material Recyclability Scores', font: { size: 14, weight: 'bold' } },
            height: 320,
            margin: { t: 50, b: 80, l: 60, r: 30 },
            yaxis: { 
                title: 'Recyclability (%)', 
                range: [0, 100],
                gridcolor: '#e5e7eb'
            },
            xaxis: { 
                tickangle: -45,
                tickfont: { size: 10 }
            },
            paper_bgcolor: 'rgba(255,255,255,0.95)',
            plot_bgcolor: 'rgba(248, 250, 252, 0.8)'
        }, { displayModeBar: false, responsive: true });
    }
}

function exportDashboardPDF() {
    if (!dashboardData) {
        showToast('error', 'No dashboard data available to export');
        return;
    }
    
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('p', 'mm', 'a4');
    let yPos = 20;
    
    // Header with branding
    doc.setFillColor(99, 102, 241);
    doc.rect(0, 0, 210, 35, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont(undefined, 'bold');
    doc.text('EcoPackAI Analytics Report', 105, 15, { align: 'center' });
    doc.setFontSize(11);
    doc.setFont(undefined, 'normal');
    doc.text('Generated: ' + new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString(), 105, 25, { align: 'center' });
    
    yPos = 45;
    doc.setTextColor(0, 0, 0);
    
    // Executive Summary
    doc.setFontSize(16);
    doc.setFont(undefined, 'bold');
    doc.text('Executive Summary', 20, yPos);
    yPos += 10;
    
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    const summary = [
        'This report provides comprehensive analytics for ' + dashboardData.total_requests + ' material recommendation requests.',
        'Our AI-powered system has achieved ' + dashboardData.co2_reduction_pct.toFixed(1) + '% reduction in CO2 emissions,',
        'saving ' + dashboardData.co2_saved.toFixed(2) + ' kg of CO2 and $' + dashboardData.cost_saved.toFixed(2) + ' in costs.'
    ];
    summary.forEach(line => {
        doc.text(line, 20, yPos);
        yPos += 6;
    });
    
    yPos += 5;
    
    // Key Performance Indicators
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text('Key Performance Indicators', 20, yPos);
    yPos += 8;
    
    // KPI Cards
    const kpis = [
        { label: 'Total Recommendations', value: String(dashboardData.total_requests), color: [243, 156, 18] },
        { label: 'CO2 Reduction', value: dashboardData.co2_reduction_pct.toFixed(1) + '%', color: [16, 185, 129] },
        { label: 'Total CO2 Saved', value: dashboardData.co2_saved.toFixed(2) + ' kg', color: [52, 152, 219] },
        { label: 'Cost Savings', value: '$' + dashboardData.cost_saved.toFixed(2), color: [155, 89, 182] },
        { label: 'Average CO2/kg', value: dashboardData.avg_co2.toFixed(2) + ' kg', color: [46, 204, 113] },
        { label: 'Average Cost/kg', value: '$' + dashboardData.avg_cost.toFixed(2), color: [52, 73, 94] }
    ];
    
    kpis.forEach((kpi, idx) => {
        const xPos = 20 + (idx % 2) * 90;
        const boxY = yPos + Math.floor(idx / 2) * 20;
        
        doc.setFillColor(kpi.color[0], kpi.color[1], kpi.color[2]);
        doc.roundedRect(xPos, boxY, 85, 15, 2, 2, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(9);
        doc.setFont(undefined, 'normal');
        doc.text(kpi.label, xPos + 3, boxY + 5);
        doc.setFontSize(12);
        doc.setFont(undefined, 'bold');
        doc.text(kpi.value, xPos + 3, boxY + 12);
    });
    
    yPos += 65;
    doc.setTextColor(0, 0, 0);
    
    // Material Usage Breakdown
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text('Material Usage Distribution', 20, yPos);
    yPos += 8;
    
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    const materials = Object.entries(dashboardData.material_usage).sort((a, b) => b[1] - a[1]);
    const totalMaterials = materials.reduce((sum, [, count]) => sum + count, 0);
    
    materials.forEach(([material, count], idx) => {
        const percentage = ((count / totalMaterials) * 100).toFixed(1);
        const barWidth = (count / totalMaterials) * 150;
        const barY = yPos + (idx * 10);
        
        // Draw bar
        doc.setFillColor(99, 102, 241);
        doc.rect(70, barY - 4, barWidth, 6, 'F');
        
        // Material name and stats
        doc.text(material + ':', 20, barY);
        doc.text(count + ' uses (' + percentage + '%)', 155, barY);
    });
    
    yPos += materials.length * 10 + 10;
    
    // Environmental Impact Comparison
    if (yPos > 240) {
        doc.addPage();
        yPos = 20;
    }
    
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text('Environmental Impact Comparison', 20, yPos);
    yPos += 10;
    
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    
    // Table header
    doc.setFillColor(99, 102, 241);
    doc.rect(20, yPos - 5, 170, 8, 'F');
    doc.setTextColor(255, 255, 255);
    doc.text('Method', 25, yPos);
    doc.text('CO2 (kg/kg)', 80, yPos);
    doc.text('Cost ($/kg)', 125, yPos);
    doc.text('Improvement', 155, yPos);
    yPos += 8;
    
    doc.setTextColor(0, 0, 0);
    
    // Traditional row
    doc.setFillColor(245, 245, 245);
    doc.rect(20, yPos - 5, 170, 8, 'F');
    doc.text('Traditional', 25, yPos);
    doc.text('3.00', 80, yPos);
    doc.text('$100.00', 125, yPos);
    doc.text('Baseline', 155, yPos);
    yPos += 8;
    
    // AI-Recommended row
    doc.text('AI-Recommended', 25, yPos);
    doc.text(dashboardData.avg_co2.toFixed(2), 80, yPos);
    doc.text('$' + dashboardData.avg_cost.toFixed(2), 125, yPos);
    doc.setTextColor(16, 185, 129);
    doc.text(dashboardData.co2_reduction_pct.toFixed(1) + '% reduction', 155, yPos);
    doc.setTextColor(0, 0, 0);
    yPos += 15;
    
    // Recent Recommendations Table
    if (yPos > 230) {
        doc.addPage();
        yPos = 20;
    }
    
    doc.setFontSize(14);
    doc.setFont(undefined, 'bold');
    doc.text('Recent Recommendations (Last 10)', 20, yPos);
    yPos += 8;
    
    doc.setFontSize(9);
    doc.setFont(undefined, 'normal');
    
    // Table header
    doc.setFillColor(99, 102, 241);
    doc.rect(20, yPos - 4, 170, 7, 'F');
    doc.setTextColor(255, 255, 255);
    doc.text('#', 22, yPos);
    doc.text('Material', 30, yPos);
    doc.text('CO2 (kg)', 80, yPos);
    doc.text('Cost ($/kg)', 110, yPos);
    doc.text('Recyclability', 145, yPos);
    doc.text('Strength', 175, yPos);
    yPos += 7;
    
    doc.setTextColor(0, 0, 0);
    const recentRecs = dashboardData.recommendations.slice(-10).reverse();
    recentRecs.forEach((rec, idx) => {
        if (idx % 2 === 0) {
            doc.setFillColor(248, 250, 252);
            doc.rect(20, yPos - 4, 170, 7, 'F');
        }
        
        doc.text(String(idx + 1), 22, yPos);
        doc.text(String(rec.material_type || 'N/A').substring(0, 15), 30, yPos);
        doc.text(parseFloat(rec.co2_emission || 0).toFixed(2), 80, yPos);
        doc.text(parseFloat(rec.cost_per_kg || 0).toFixed(2), 110, yPos);
        doc.text(parseInt(rec.recyclability_percent || 0) + '%', 145, yPos);
        doc.text(parseFloat(rec.strength_mpa || 0).toFixed(1) + ' MPa', 175, yPos);
        yPos += 7;
        
        if (yPos > 270 && idx < recentRecs.length - 1) {
            doc.addPage();
            yPos = 20;
        }
    });
    
    // Footer on last page
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(128, 128, 128);
        doc.text('Page ' + i + ' of ' + pageCount, 105, 287, { align: 'center' });
        doc.text('EcoPackAI 2026 | Confidential Analytics Report', 105, 292, { align: 'center' });
    }
    
    doc.save('ecopackai_analytics_' + new Date().toISOString().split('T')[0] + '.pdf');
    showToast('success', 'PDF report exported successfully!');
}

function exportDashboardExcel() {
    if (!dashboardData) {
        showToast('error', 'No dashboard data available to export');
        return;
    }
    
    const wb = XLSX.utils.book_new();
    
    // Sheet 1: Summary Dashboard
    const summaryData = [
        ['EcoPackAI Analytics Dashboard'],
        [`Generated: ${new Date().toLocaleString()}`],
        [],
        ['Key Performance Indicators'],
        ['Metric', 'Value', 'Unit'],
        ['Total Recommendations', dashboardData.total_requests, 'count'],
        ['CO₂ Reduction Percentage', dashboardData.co2_reduction_pct.toFixed(2), '%'],
        ['Total CO₂ Saved', dashboardData.co2_saved.toFixed(2), 'kg'],
        ['Total Cost Savings', dashboardData.cost_saved.toFixed(2), 'USD'],
        ['Average CO₂ per kg', dashboardData.avg_co2.toFixed(2), 'kg/kg'],
        ['Average Cost per kg', dashboardData.avg_cost.toFixed(2), 'USD/kg'],
        [],
        ['Comparison with Traditional Methods'],
        ['Method', 'CO₂ Emission (kg/kg)', 'Cost ($/kg)', 'Improvement'],
        ['Traditional Packaging', 3.00, 100.00, 'Baseline'],
        ['AI-Recommended', dashboardData.avg_co2.toFixed(2), dashboardData.avg_cost.toFixed(2), 
         `${dashboardData.co2_reduction_pct.toFixed(1)}% reduction`],
        [],
        ['Environmental Impact'],
        ['Metric', 'Traditional', 'AI-Optimized', 'Savings'],
        ['CO₂ Footprint', '3.00 kg/kg', `${dashboardData.avg_co2.toFixed(2)} kg/kg`, 
         `${(3.0 - dashboardData.avg_co2).toFixed(2)} kg/kg`],
        ['Material Cost', '$100.00/kg', `$${dashboardData.avg_cost.toFixed(2)}/kg`, 
         `$${(100.0 - dashboardData.avg_cost).toFixed(2)}/kg`]
    ];
    
    const wsSummary = XLSX.utils.aoa_to_sheet(summaryData);
    
    // Style the summary sheet
    wsSummary['!cols'] = [{ wch: 30 }, { wch: 20 }, { wch: 15 }];
    wsSummary['A1'].s = { font: { bold: true, sz: 16 } };
    
    XLSX.utils.book_append_sheet(wb, wsSummary, 'Summary');
    
    // Sheet 2: Material Distribution
    const materialData = [
        ['Material Usage Distribution'],
        [`Total Recommendations: ${dashboardData.total_requests}`],
        [],
        ['Material Type', 'Usage Count', 'Percentage', 'Rank']
    ];
    
    const materials = Object.entries(dashboardData.material_usage)
        .sort((a, b) => b[1] - a[1]);
    const totalMaterials = materials.reduce((sum, [, count]) => sum + count, 0);
    
    materials.forEach(([material, count], idx) => {
        const percentage = ((count / totalMaterials) * 100).toFixed(2);
        materialData.push([material, count, `${percentage}%`, idx + 1]);
    });
    
    materialData.push([]);
    materialData.push(['Top Material', materials[0][0]]);
    materialData.push(['Top Usage Count', materials[0][1]]);
    materialData.push(['Market Share', `${((materials[0][1] / totalMaterials) * 100).toFixed(2)}%`]);
    
    const wsMaterials = XLSX.utils.aoa_to_sheet(materialData);
    wsMaterials['!cols'] = [{ wch: 20 }, { wch: 15 }, { wch: 15 }, { wch: 10 }];
    
    XLSX.utils.book_append_sheet(wb, wsMaterials, 'Material Distribution');
    
    // Sheet 3: Detailed Recommendations
    const recsData = [
        ['All Recommendation Records'],
        [`Total Records: ${dashboardData.recommendations.length}`],
        [],
        ['ID', 'Material Type', 'CO₂ Emission (kg)', 'Cost ($/kg)', 
         'Recyclability (%)', 'Strength (MPa)', 'Biodegradability (%)', 'Timestamp']
    ];
    
    dashboardData.recommendations.forEach((rec, idx) => {
        recsData.push([
            idx + 1,
            rec.material_type || 'N/A',
            parseFloat(rec.co2_emission || 0).toFixed(4),
            parseFloat(rec.cost_per_kg || 0).toFixed(4),
            parseInt(rec.recyclability_percent || 0),
            parseFloat(rec.strength_mpa || 0).toFixed(2),
            parseInt(rec.biodegradability || 0),
            rec.timestamp || new Date().toISOString()
        ]);
    });
    
    // Add statistics at the bottom
    recsData.push([]);
    recsData.push(['Statistics Summary']);
    recsData.push(['Metric', 'Value']);
    recsData.push(['Total Records', dashboardData.recommendations.length]);
    recsData.push(['Avg CO₂', dashboardData.avg_co2.toFixed(4)]);
    recsData.push(['Avg Cost', dashboardData.avg_cost.toFixed(4)]);
    recsData.push(['Min CO₂', Math.min(...dashboardData.recommendations.map(r => parseFloat(r.co2_emission || 0))).toFixed(4)]);
    recsData.push(['Max CO₂', Math.max(...dashboardData.recommendations.map(r => parseFloat(r.co2_emission || 0))).toFixed(4)]);
    recsData.push(['Min Cost', Math.min(...dashboardData.recommendations.map(r => parseFloat(r.cost_per_kg || 0))).toFixed(4)]);
    recsData.push(['Max Cost', Math.max(...dashboardData.recommendations.map(r => parseFloat(r.cost_per_kg || 0))).toFixed(4)]);
    
    const wsRecs = XLSX.utils.aoa_to_sheet(recsData);
    wsRecs['!cols'] = [
        { wch: 8 }, { wch: 18 }, { wch: 18 }, { wch: 15 }, 
        { wch: 17 }, { wch: 15 }, { wch: 20 }, { wch: 20 }
    ];
    
    XLSX.utils.book_append_sheet(wb, wsRecs, 'All Recommendations');
    
    // Sheet 4: Performance Analytics
    const performanceData = [
        ['Performance Metrics Over Time'],
        ['Recent 20 Recommendations Analysis'],
        [],
        ['Request #', 'Material', 'CO₂ (kg)', 'Cost ($/kg)', 'Recyclability (%)', 
         'CO₂ vs Baseline', 'Cost vs Baseline']
    ];
    
    const recent = dashboardData.recommendations.slice(-20);
    recent.forEach((rec, idx) => {
        const co2Improvement = ((3.0 - parseFloat(rec.co2_emission || 0)) / 3.0 * 100).toFixed(1);
        const costImprovement = ((100.0 - parseFloat(rec.cost_per_kg || 0)) / 100.0 * 100).toFixed(1);
        
        performanceData.push([
            recent.length - idx,
            rec.material_type || 'N/A',
            parseFloat(rec.co2_emission || 0).toFixed(4),
            parseFloat(rec.cost_per_kg || 0).toFixed(4),
            parseInt(rec.recyclability_percent || 0),
            `${co2Improvement}% better`,
            `${costImprovement}% better`
        ]);
    });
    
    performanceData.push([]);
    performanceData.push(['Trend Analysis']);
    performanceData.push(['Average CO₂ (Recent 20)', 
        (recent.reduce((sum, r) => sum + parseFloat(r.co2_emission || 0), 0) / recent.length).toFixed(4)]);
    performanceData.push(['Average Cost (Recent 20)', 
        (recent.reduce((sum, r) => sum + parseFloat(r.cost_per_kg || 0), 0) / recent.length).toFixed(4)]);
    performanceData.push(['Average Recyclability (Recent 20)', 
        Math.round(recent.reduce((sum, r) => sum + parseInt(r.recyclability_percent || 0), 0) / recent.length)]);
    
    const wsPerformance = XLSX.utils.aoa_to_sheet(performanceData);
    wsPerformance['!cols'] = [
        { wch: 12 }, { wch: 18 }, { wch: 12 }, { wch: 14 }, 
        { wch: 17 }, { wch: 18 }, { wch: 18 }
    ];
    
    XLSX.utils.book_append_sheet(wb, wsPerformance, 'Performance Trends');
    
    // Sheet 5: Environmental Impact Analysis
    const impactData = [
        ['Environmental Impact Analysis'],
        ['Sustainability Metrics & Comparisons'],
        [],
        ['Category', 'Metric', 'Value', 'Impact Level']
    ];
    
    impactData.push(['Carbon Footprint', 'Total CO₂ Saved', `${dashboardData.co2_saved.toFixed(2)} kg`, 
        dashboardData.co2_saved > 100 ? 'High Impact' : dashboardData.co2_saved > 50 ? 'Medium Impact' : 'Growing Impact']);
    impactData.push(['Carbon Footprint', 'CO₂ Reduction Rate', `${dashboardData.co2_reduction_pct.toFixed(1)}%`, 
        dashboardData.co2_reduction_pct > 30 ? 'Excellent' : dashboardData.co2_reduction_pct > 15 ? 'Good' : 'Fair']);
    impactData.push(['Resource Efficiency', 'Avg Recyclability', 
        `${Math.round(dashboardData.recommendations.reduce((sum, r) => sum + parseInt(r.recyclability_percent || 0), 0) / dashboardData.recommendations.length)}%`,
        'Sustainable']);
    impactData.push(['Cost Efficiency', 'Total Savings', `$${dashboardData.cost_saved.toFixed(2)}`, 
        dashboardData.cost_saved > 1000 ? 'Significant' : dashboardData.cost_saved > 500 ? 'Moderate' : 'Building']);
    impactData.push(['Material Diversity', 'Unique Materials Used', materials.length, 
        materials.length > 5 ? 'Diverse' : 'Focused']);
    
    impactData.push([]);
    impactData.push(['Equivalent Environmental Savings']);
    impactData.push(['Trees Planted Equivalent', Math.round(dashboardData.co2_saved / 21.77) + ' trees', 
        'Based on avg tree CO₂ absorption (21.77 kg/year)']);
    impactData.push(['Car Miles Not Driven', Math.round(dashboardData.co2_saved / 0.404) + ' miles', 
        'Based on avg car CO₂ emission (0.404 kg/mile)']);
    impactData.push(['Plastic Bottles Recycled', Math.round(dashboardData.co2_saved / 0.085) + ' bottles', 
        'Based on recycling impact (0.085 kg CO₂/bottle)']);
    
    const wsImpact = XLSX.utils.aoa_to_sheet(impactData);
    wsImpact['!cols'] = [{ wch: 22 }, { wch: 25 }, { wch: 20 }, { wch: 20 }];
    
    XLSX.utils.book_append_sheet(wb, wsImpact, 'Environmental Impact');
    
    // Save the workbook
    const fileName = `ecopackai_analytics_${new Date().toISOString().split('T')[0]}.xlsx`;
    XLSX.writeFile(wb, fileName);
    showToast('success', 'Excel report with 5 sheets exported successfully!');
}

// Toast Notifications
function showToast(type, message) {
    const toastId = type === 'error' ? 'errorToast' : 'successToast';
    const messageId = type === 'error' ? 'errorMessage' : 'successMessage';
    
    const toast = document.getElementById(toastId);
    const messageEl = document.getElementById(messageId);
    
    messageEl.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 5000);
}

function closeToast(toastId) {
    document.getElementById(toastId).classList.remove('show');
}

// Export for global access
window.scrollToSection = scrollToSection;
window.sortTable = sortTable;
window.closeToast = closeToast;window.loadDashboardData = loadDashboardData;
window.exportDashboardPDF = exportDashboardPDF;
window.exportDashboardExcel = exportDashboardExcel;