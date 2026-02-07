<script setup lang="ts">
</script>

<template>
    <main class="main-content">
        <div class="content-wrapper">
            <h1 class="page-title">Help & About</h1>

            <div class="help-section">
                <h2>What is Simple Dash?</h2>
                <p>
                    Simple Dash is a privacy-focused email campaign analytics tool that helps you visualize and compare
                    your email marketing performance across multiple campaigns. Upload your campaign reports and instantly
                    see trends, metrics, and insights.
                </p>
            </div>

            <div class="help-section">
                <h2>How It Works</h2>
                <ol class="steps-list">
                    <li>
                        <strong>Upload Your Reports</strong>
                        <p>Export your campaign reports as CSV files from your email marketing platform and upload them to
                            Simple Dash.</p>
                    </li>
                    <li>
                        <strong>Automatic Parsing</strong>
                        <p>Our parser automatically detects your platform and extracts key metrics like open rates, click
                            rates, bounces, and more.</p>
                    </li>
                    <li>
                        <strong>View Your Dashboard</strong>
                        <p>Explore individual campaign performance or view trends across all your campaigns with interactive
                            charts and visualizations.</p>
                    </li>
                </ol>
            </div>

            <div class="help-section">
                <h2>Supported Platforms</h2>
                <div class="platforms-grid">
                    <div class="platform-card">
                        <h3>MailChimp</h3>
                        <p>Export your campaign reports as CSV files from the MailChimp dashboard. Each CSV can contain multiple campaigns, and duplicate campaigns (based on unique ID) will be automatically deduplicated using the most recent upload.</p>
                    </div>
                    <div class="platform-card">
                        <h3>MailerLite Classic</h3>
                        <p>Export campaign reports from MailerLite Classic in CSV format.</p>
                    </div>
                </div>
                <p class="platforms-note">
                    <em>More platforms coming soon! Have a request? Let us know.</em>
                </p>
            </div>

            <div class="help-section">
                <h2>Privacy & Data Storage</h2>
                <div class="privacy-box">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="2" class="privacy-icon">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                    </svg>
                    <div>
                        <h3>Your Data Stays Private</h3>
                        <ul>
                            <li><strong>No server storage:</strong> Your campaign data is never stored on our servers. Files
                                are parsed in real-time and discarded immediately.</li>
                            <li><strong>Local browser storage only:</strong> Parsed data is stored temporarily in your
                                browser's session storage for the dashboard view.</li>
                            <li><strong>Cleared when you leave:</strong> All data is automatically cleared when you close the
                                tab or navigate away.</li>
                            <li><strong>No accounts or tracking:</strong> No sign-up required, no cookies, no tracking.</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="help-section">
                <h2>File Requirements</h2>
                <ul class="requirements-list">
                    <li><strong>Format:</strong> CSV files only</li>
                    <li><strong>Maximum file size:</strong> 10MB per file</li>
                    <li><strong>Maximum files:</strong> 12 files per upload</li>
                    <li><strong>Platform detection:</strong> Automatic (MailChimp and MailerLite Classic formats
                        recognized)</li>
                </ul>
            </div>

            <div class="help-section">
                <h2>Tips for Best Results</h2>
                <ul class="tips-list">
                    <li>Upload multiple campaigns to unlock trend analysis and the send-time heatmap</li>
                    <li>Make sure your CSV files are exported directly from your email platform without modifications</li>
                    <li>Campaign data is sorted chronologically by send date for accurate trend visualization</li>
                    <li>If some files fail to parse, successfully parsed campaigns will still be displayed with a warning
                        banner</li>
                    <li>For MailChimp: Duplicate campaigns (same unique ID) across multiple files will be automatically
                        deduplicated, keeping the version from the most recent upload</li>
                </ul>
            </div>

            <div class="help-section">
                <h2>Troubleshooting</h2>
                <div class="faq">
                    <div class="faq-item">
                        <h3>My file failed to upload</h3>
                        <p>Make sure your file is:</p>
                        <ul>
                            <li>A valid CSV file from MailChimp or MailerLite Classic</li>
                            <li>Under 10MB in size</li>
                            <li>Not modified or corrupted</li>
                        </ul>
                    </div>
                    <div class="faq-item">
                        <h3>I don't see my data on the dashboard</h3>
                        <p>This can happen if:</p>
                        <ul>
                            <li>All uploaded files failed to parse (check for error messages)</li>
                            <li>You're using a private/incognito window and session storage is disabled</li>
                            <li>Your browser doesn't support session storage</li>
                        </ul>
                    </div>
                    <div class="faq-item">
                        <h3>Can I export or save my dashboard?</h3>
                        <p>Currently, Simple Dash doesn't offer export functionality. You can take screenshots of your
                            dashboard or re-upload your files anytime to view the data again.</p>
                    </div>
                </div>
            </div>

            <div class="help-section footer-section">
                <p class="footer-text">
                    Simple Dash is created by <a href="https://derekw.co/?utm_medium=referral&utm_source=simple-dash"
                        target="_blank" rel="noopener">derekw</a>
                </p>
            </div>
        </div>
    </main>
</template>

<style scoped>
.main-content {
    min-height: calc(100vh - var(--top-bar-height));
    background-color: #fafafa;
}

.content-wrapper {
    max-width: 900px;
    padding: 48px 32px;
    margin: 0 auto;
}

.page-title {
    font-size: 36px;
    font-weight: 700;
    color: #222222;
    margin: 0 0 48px 0;
    text-align: center;
}

.help-section {
    background-color: #ffffff;
    padding: 32px;
    border-radius: 8px;
    margin-bottom: 32px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.help-section h2 {
    font-size: 24px;
    font-weight: 700;
    color: #222222;
    margin: 0 0 20px 0;
}

.help-section h3 {
    font-size: 18px;
    font-weight: 600;
    color: #222222;
    margin: 0 0 12px 0;
}

.help-section p {
    font-size: 16px;
    line-height: 1.6;
    color: #444444;
    margin: 0 0 16px 0;
}

.help-section p:last-child {
    margin-bottom: 0;
}

.steps-list {
    list-style: none;
    padding: 0;
    margin: 0;
    counter-reset: step-counter;
}

.steps-list li {
    counter-increment: step-counter;
    position: relative;
    padding-left: 60px;
    margin-bottom: 24px;
}

.steps-list li:last-child {
    margin-bottom: 0;
}

.steps-list li::before {
    content: counter(step-counter);
    position: absolute;
    left: 0;
    top: 0;
    width: 40px;
    height: 40px;
    background-color: #dd3333;
    color: #ffffff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 18px;
}

.steps-list li strong {
    display: block;
    font-size: 18px;
    color: #222222;
    margin-bottom: 8px;
}

.steps-list li p {
    margin: 0;
    color: #666666;
}

.platforms-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.platform-card {
    padding: 20px;
    background-color: #fafafa;
    border: 2px solid #dd3333;
    border-radius: 8px;
}

.platform-card h3 {
    color: #dd3333;
    margin-bottom: 8px;
}

.platform-card p {
    margin: 0;
    font-size: 14px;
    color: #666666;
}

.platforms-note {
    text-align: center;
    color: #999999;
    font-size: 14px;
}

.privacy-box {
    display: flex;
    gap: 24px;
    padding: 24px;
    background-color: #f0f9ff;
    border: 2px solid #0ea5e9;
    border-radius: 8px;
}

.privacy-icon {
    width: 48px;
    height: 48px;
    color: #0ea5e9;
    flex-shrink: 0;
}

.privacy-box h3 {
    color: #0369a1;
    margin-bottom: 16px;
}

.privacy-box ul {
    margin: 0;
    padding-left: 20px;
}

.privacy-box li {
    margin-bottom: 12px;
    color: #444444;
    line-height: 1.5;
}

.privacy-box li:last-child {
    margin-bottom: 0;
}

.requirements-list,
.tips-list {
    margin: 0;
    padding-left: 24px;
}

.requirements-list li,
.tips-list li {
    margin-bottom: 12px;
    color: #444444;
    line-height: 1.6;
}

.requirements-list li:last-child,
.tips-list li:last-child {
    margin-bottom: 0;
}

.faq {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.faq-item {
    padding: 20px;
    background-color: #fafafa;
    border-left: 4px solid #dd3333;
    border-radius: 4px;
}

.faq-item h3 {
    font-size: 16px;
    color: #dd3333;
    margin-bottom: 12px;
}

.faq-item p {
    margin-bottom: 8px;
    font-size: 15px;
}

.faq-item ul {
    margin: 0;
    padding-left: 24px;
}

.faq-item li {
    margin-bottom: 8px;
    font-size: 14px;
    color: #666666;
}

.faq-item li:last-child {
    margin-bottom: 0;
}

.footer-section {
    text-align: center;
    background-color: transparent;
    box-shadow: none;
}

.footer-text {
    font-size: 14px;
    color: #999999;
}

.footer-text a {
    color: #dd3333;
    text-decoration: none;
    font-weight: 600;
}

.footer-text a:hover {
    text-decoration: underline;
}

@media (max-width: 768px) {
    .content-wrapper {
        padding: 32px 20px;
    }

    .help-section {
        padding: 24px 20px;
    }

    .privacy-box {
        flex-direction: column;
        align-items: center;
        text-align: left;
    }

    .privacy-icon {
        width: 40px;
        height: 40px;
    }

    .platforms-grid {
        grid-template-columns: 1fr;
    }
}
</style>
