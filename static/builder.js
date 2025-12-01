/**
 * Website Builder - Frontend Logic
 * Works with saved onboarding answers to generate and preview website
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const heroHeadlineInput = document.getElementById('heroHeadline');
    const heroSubheadlineInput = document.getElementById('heroSubheadline');
    const heroCtaInput = document.getElementById('heroCta');
    const primaryColorInput = document.getElementById('primaryColor');
    const primaryColorText = document.getElementById('primaryColorText');
    const regenerateBtn = document.getElementById('regenerateBtn');
    const websitePreview = document.getElementById('websitePreview');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const buildBtn = document.getElementById('startBuildBtn');
    const briefStatus = document.getElementById('briefStatus');
    const deployBtn = document.getElementById('deployBtn');
    const successModal = document.getElementById('successModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const downloadSourceBtn = document.getElementById('downloadSourceBtn');

    let currentHtml = '';
    let isGenerating = false;

    // Color picker sync
    if (primaryColorInput && primaryColorText) {
        primaryColorInput.addEventListener('input', (e) => {
            primaryColorText.value = e.target.value;
        });
        primaryColorText.addEventListener('input', (e) => {
            if (/^#[0-9A-Fa-f]{6}$/.test(e.target.value)) {
                primaryColorInput.value = e.target.value;
            }
        });
    }

    // Event listeners
    if (buildBtn) buildBtn.addEventListener('click', startGeneration);
    if (regenerateBtn) regenerateBtn.addEventListener('click', regenerateWebsite);
    if (deployBtn) deployBtn.addEventListener('click', () => successModal?.classList.remove('hidden'));
    if (closeModalBtn) closeModalBtn.addEventListener('click', () => successModal?.classList.add('hidden'));
    if (downloadSourceBtn) downloadSourceBtn.addEventListener('click', downloadSite);

    // Initialize
    init();

    async function init() {
        setStatus('Checking onboarding status...', false);
        
        // Check for existing preview first
        const hasPreview = await checkExistingPreview();
        
        // Check onboarding status
        await checkOnboardingStatus();
        
        if (!hasPreview) {
            showStartOverlay();
        }
    }

    async function checkOnboardingStatus() {
        try {
            const res = await fetch('/api/router/progress');
            const data = await res.json();
            
            if (data.complete) {
                setStatus(`✅ Onboarding complete! (${data.current_question}/${data.total_questions} questions answered)`, false);
                if (buildBtn) buildBtn.disabled = false;
            } else {
                setStatus(`⚠️ Complete onboarding first (${data.current_question}/${data.total_questions} questions)`, true);
                if (buildBtn) buildBtn.disabled = true;
            }
        } catch (e) {
            console.error('Status check error:', e);
            setStatus('Unable to check status', true);
        }
    }

    async function checkExistingPreview() {
        try {
            const res = await fetch('/api/builder/preview');
            if (res.ok) {
                const html = await res.text();
                if (html && !html.includes('"error"') && html.includes('<!DOCTYPE')) {
                    updatePreview(html);
                    hideStartOverlay();
                    return true;
                }
            }
        } catch (e) {
            console.log('No existing preview');
        }
        return false;
    }

    function showStartOverlay() {
        let overlay = document.getElementById('startOverlay');
        if (!overlay && websitePreview) {
            overlay = document.createElement('div');
            overlay.id = 'startOverlay';
            overlay.className = 'absolute inset-0 bg-gray-900 flex items-center justify-center z-10';
            overlay.innerHTML = `
                <div class="text-center p-8 max-w-lg">
                    <div class="text-7xl mb-6">🏗️</div>
                    <h2 class="text-3xl font-bold text-white mb-4">Build Your Website</h2>
                    <p class="text-gray-400 mb-6 text-lg">
                        Complete the 10-question onboarding in the chatbot first, 
                        then click "Build Website" to generate your personalized site.
                    </p>
                    <div class="bg-gray-800 rounded-lg p-4 text-left">
                        <p class="text-sm text-gray-300 mb-2">📝 Your answers will be used to create:</p>
                        <ul class="text-sm text-gray-400 space-y-1">
                            <li>• Custom headline & messaging</li>
                            <li>• Features section</li>
                            <li>• Pricing information</li>
                            <li>• Trust signals & testimonials</li>
                        </ul>
                    </div>
                </div>
            `;
            websitePreview.parentElement.appendChild(overlay);
        }
        if (overlay) overlay.classList.remove('hidden');
    }

    function hideStartOverlay() {
        const overlay = document.getElementById('startOverlay');
        if (overlay) overlay.classList.add('hidden');
    }

    async function startGeneration() {
        if (isGenerating) return;
        
        // Double-check onboarding status
        try {
            const res = await fetch('/api/router/progress');
            const data = await res.json();
            if (!data.complete) {
                setStatus('❌ Please complete all 10 onboarding questions first!', true);
                return;
            }
        } catch (e) {
            setStatus('❌ Unable to verify onboarding status', true);
            return;
        }
        
        isGenerating = true;
        hideStartOverlay();
        showLoading('Starting website generation...');
        setStatus('🔄 Generating your website...', false);
        if (buildBtn) buildBtn.disabled = true;

        try {
            const res = await fetch('/api/builder/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });

            const data = await res.json();

            if (data.status === 'running') {
                pollStatus();
            } else if (data.status === 'error') {
                hideLoading();
                setStatus('❌ ' + data.message, true);
                showStartOverlay();
                isGenerating = false;
                if (buildBtn) buildBtn.disabled = false;
            }
        } catch (e) {
            console.error('Generation error:', e);
            hideLoading();
            setStatus('❌ Failed to start generation', true);
            showStartOverlay();
            isGenerating = false;
            if (buildBtn) buildBtn.disabled = false;
        }
    }

    function pollStatus() {
        const interval = setInterval(async () => {
            try {
                const res = await fetch('/api/builder/status');
                const data = await res.json();

                updateLoadingMessage(data.message || 'Working...');

                if (data.status === 'completed') {
                    clearInterval(interval);
                    hideLoading();
                    isGenerating = false;
                    if (buildBtn) buildBtn.disabled = false;
                    
                    // Load preview
                    const previewRes = await fetch('/api/builder/preview');
                    if (previewRes.ok) {
                        const html = await previewRes.text();
                        updatePreview(html);
                        setStatus('✅ Website generated successfully! Use tweaks to customize.', false);
                    }
                } else if (data.status === 'error') {
                    clearInterval(interval);
                    hideLoading();
                    isGenerating = false;
                    if (buildBtn) buildBtn.disabled = false;
                    setStatus('❌ ' + data.message, true);
                    showStartOverlay();
                }
            } catch (e) {
                console.error('Poll error:', e);
            }
        }, 2000);
    }

    async function regenerateWebsite() {
        const headline = heroHeadlineInput?.value.trim();
        const subheadline = heroSubheadlineInput?.value.trim();
        const cta = heroCtaInput?.value.trim();
        const color = primaryColorText?.value.trim();

        if (!headline && !subheadline && !cta && !color) {
            alert('Enter at least one change (headline, subheadline, CTA, or color)');
            return;
        }

        const tweaks = {};
        if (headline) tweaks.headline = headline;
        if (subheadline) tweaks.subheadline = subheadline;
        if (cta) tweaks.cta = cta;
        if (color && /^#[0-9A-Fa-f]{6}$/.test(color)) tweaks.color = color;

        showLoading('Applying your changes...');
        if (regenerateBtn) regenerateBtn.disabled = true;
        setStatus('🔄 Regenerating...', false);

        try {
            const res = await fetch('/api/builder/regenerate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tweaks })
            });

            const data = await res.json();

            if (data.status === 'success' && data.html) {
                updatePreview(data.html);
                setStatus('✅ Website updated with your changes!', false);
                
                // Clear inputs after successful update
                if (heroHeadlineInput) heroHeadlineInput.value = '';
                if (heroSubheadlineInput) heroSubheadlineInput.value = '';
                if (heroCtaInput) heroCtaInput.value = '';
            } else {
                setStatus('❌ ' + (data.message || 'Update failed'), true);
            }
        } catch (e) {
            console.error('Regenerate error:', e);
            setStatus('❌ Failed to update website', true);
        }

        hideLoading();
        if (regenerateBtn) regenerateBtn.disabled = false;
    }

    function updatePreview(html) {
        currentHtml = html;
        if (websitePreview) {
            const blob = new Blob([html], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            websitePreview.src = url;
        }
        hideStartOverlay();
    }

    async function downloadSite() {
        try {
            const res = await fetch('/api/builder/download');
            if (!res.ok) {
                alert('Generate the website first');
                return;
            }
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'my-website.html';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (e) {
            alert('Download failed');
        }
    }

    function showLoading(msg) {
        if (loadingOverlay) {
            loadingOverlay.classList.remove('hidden');
            updateLoadingMessage(msg);
        }
    }

    function updateLoadingMessage(msg) {
        if (loadingOverlay) {
            const msgEl = loadingOverlay.querySelector('p');
            if (msgEl) msgEl.textContent = msg;
        }
    }

    function hideLoading() {
        if (loadingOverlay) loadingOverlay.classList.add('hidden');
    }

    function setStatus(msg, isError) {
        if (briefStatus) {
            briefStatus.textContent = msg;
            briefStatus.className = 'text-sm mt-4 ' + (isError ? 'text-red-400' : 'text-green-400');
        }
    }
});
