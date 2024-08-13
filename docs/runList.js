// runList.js
class RunList {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.runs = [];
    }

    addRun(taskId, modelName, countryName, scenarioName) {
        const run = {
            taskId,
            modelName,
            countryName,
            scenarioName,
            status: 'Pending',
            timestamp: new Date().toLocaleString(),
            downloadUrl: null,
            fileId: null
        };
        this.runs.unshift(run);
        this.render();
        return run;
    }

    updateRunStatus(taskId, status, downloadUrl = null, fileId = null) {
        const run = this.runs.find(r => r.taskId === taskId);
        if (run) {
            run.status = status;
            run.downloadUrl = downloadUrl;
            run.fileId = fileId;
            this.render();
        }
    }

    render() {
        this.container.innerHTML = '';
        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Model</th>
                    <th>Country</th>
                    <th>Scenario</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;
        const tbody = table.querySelector('tbody');
        this.runs.forEach(run => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${run.timestamp}</td>
                <td>${run.modelName}</td>
                <td>${run.countryName}</td>
                <td>${run.scenarioName}</td>
                <td>${run.status}</td>
                <td>${this.getActionButtons(run)}</td>
            `;
            tbody.appendChild(tr);
        });
        this.container.appendChild(table);
    }

    getActionButtons(run) {
        let buttons = '';
        if (run.status === 'Success' && run.downloadUrl) {
            buttons += `<a href="${run.downloadUrl}" download class="action-btn download-btn">Download</a>`;
            if (run.fileId) {
                buttons += `
                    <a href="https://api.forecasthealth.org/summary/standard/${run.fileId}" target="_blank" class="action-btn download-btn">Summary</a>
                `;
            }
        } else if (run.status === 'Pending' || run.status === 'In Progress') {
            buttons = `<button onclick="runList.checkStatus('${run.taskId}')" class="action-btn status-btn">Check Status</button>`;
        }
        return buttons;
    }

    extractFileIdFromUrl(url) {
        const match = url.match(/\/users\/standard\/results\/([^\/]+)\/pipeline_results\.zip/);
        return match ? match[1] : null;
    }

    checkStatus(taskId) {
        const statusUrl = `https://api.forecasthealth.org/pipeline/status/${taskId}`;
        fetch(statusUrl)
            .then(response => response.json())
            .then(data => {
                console.log('Received status:', data.status);
                if (data.status === "SUCCESS" && data.result && data.result.download_url) {
                    const fileId = this.extractFileIdFromUrl(data.result.download_url);
                    this.updateRunStatus(taskId, 'Success', data.result.download_url, fileId);
                } else if (data.status === "PENDING" || data.status === "PROGRESS") {
                    this.updateRunStatus(taskId, 'In Progress');
                } else {
                    this.updateRunStatus(taskId, 'Error');
                }
            })
            .catch(error => {
                console.error('Error checking status:', error);
                this.updateRunStatus(taskId, 'Error');
            });
    }
}

// Global instance
const runList = new RunList('runList');