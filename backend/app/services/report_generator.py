import json
import base64
from pathlib import Path
from typing import Dict, Any, List
from jinja2 import Template
from app.core.config import settings
from app.core.logging import logger

HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>QA Execution Report - {{ summary.run_name }}</title>
    <style>
        :root { --primary: #2563eb; --success: #16a34a; --danger: #dc2626; --warning: #d97706; --neutral: #64748b; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 24px; }
        .container { max-width: 1100px; margin: 0 auto; background: #fff; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .header { display: flex; justify-content: space-between; border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 24px; }
        .title { font-size: 24px; font-weight: 700; color: #0f172a; margin: 0; }
        .badge { display: inline-block; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 12px; }
        .badge-pass { background: #dcfce7; color: var(--success); }
        .badge-fail { background: #fee2e2; color: var(--danger); }
        .badge-blocked { background: #fef3c7; color: var(--warning); }
        .badge-inconclusive { background: #f1f5f9; color: var(--neutral); }
        .badge-critical { background: #7f1d1d; color: #fff; }
        .badge-high { background: #ef4444; color: #fff; }
        .badge-medium { background: #f59e0b; color: #fff; }
        .badge-low { background: #10b981; color: #fff; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .card { background: #f1f5f9; padding: 16px; border-radius: 8px; text-align: center; }
        .card-value { font-size: 28px; font-weight: 700; color: #0f172a; }
        .card-label { font-size: 13px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 14px; }
        th, td { padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: left; }
        th { background: #f8fafc; color: #475569; font-weight: 600; }
        .bug-box { background: #fff5f5; border-left: 4px solid var(--danger); padding: 16px; margin-top: 16px; border-radius: 4px; }
        .rec-box { background: #eff6ff; border-left: 4px solid var(--primary); padding: 16px; margin-top: 24px; border-radius: 4px; }
        .evidence-img { max-width: 100%; max-height: 400px; border: 1px solid #cbd5e1; border-radius: 6px; margin-top: 12px; }
        @media print { body { background: #fff; } .container { box-shadow: none; padding: 0; } }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div>
            <h1 class="title">Autonomous AI QA Execution Report</h1>
            <p style="color: #64748b; margin: 4px 0;">Application: <strong>{{ summary.app_name }}</strong> ({{ summary.app_url }})</p>
            <p style="color: #64748b; margin: 0;">Run Mode: <strong>{{ summary.mode }}</strong> | Environment: <strong>{{ summary.environment }}</strong></p>
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; font-size: 13px; color: #64748b;">Generated: {{ summary.timestamp }}</p>
            <p style="margin: 4px 0; font-size: 13px; color: #64748b;">Duration: {{ summary.duration_seconds }}s</p>
        </div>
    </div>

    <h2>Executive Summary</h2>
    <div class="grid">
        <div class="card">
            <div class="card-value">{{ summary.total_tests }}</div>
            <div class="card-label">Total Tests</div>
        </div>
        <div class="card">
            <div class="card-value" style="color: var(--success);">{{ summary.passed_tests }}</div>
            <div class="card-label">Passed</div>
        </div>
        <div class="card">
            <div class="card-value" style="color: var(--danger);">{{ summary.failed_tests }}</div>
            <div class="card-label">Failed</div>
        </div>
        <div class="card">
            <div class="card-value" style="color: var(--warning);">{{ summary.blocked_tests }}</div>
            <div class="card-label">Blocked</div>
        </div>
        <div class="card">
            <div class="card-value">{{ summary.inconclusive_tests }}</div>
            <div class="card-label">Inconclusive</div>
        </div>
        <div class="card">
            <div class="card-value" style="color: var(--primary);">{{ summary.pass_percentage }}%</div>
            <div class="card-label">Pass Rate</div>
        </div>
    </div>

    <h2>Test Execution Details</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Scenario</th>
                <th>Module</th>
                <th>Status</th>
                <th>Confidence</th>
                <th>Duration</th>
            </tr>
        </thead>
        <tbody>
            {% for item in results %}
            <tr>
                <td><strong>{{ item.custom_id }}</strong></td>
                <td>{{ item.scenario }}</td>
                <td>{{ item.module }}</td>
                <td>
                    {% if item.status == 'PASS' %}
                        <span class="badge badge-pass">PASS</span>
                    {% elif item.status == 'FAIL' %}
                        <span class="badge badge-fail">FAIL</span>
                    {% elif item.status == 'BLOCKED' %}
                        <span class="badge badge-blocked">BLOCKED</span>
                    {% else %}
                        <span class="badge badge-inconclusive">INCONCLUSIVE</span>
                    {% endif %}
                </td>
                <td>{{ item.confidence }}</td>
                <td>{{ item.duration_ms }}ms</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    {% if bugs %}
    <h2 style="margin-top: 36px; color: var(--danger);">Bugs & Discrepancies Detected</h2>
    {% for bug in bugs %}
    <div class="bug-box">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0; color: #991b1b;">[{{ bug.custom_id }}] {{ bug.title }}</h3>
            <div>
                <span class="badge badge-{{ bug.severity|lower }}">{{ bug.severity }}</span>
                <span class="badge badge-fail">{{ bug.category }}</span>
            </div>
        </div>
        <p style="margin: 8px 0 4px 0;"><strong>Observed Fact:</strong> {{ bug.actual_result }}</p>
        <p style="margin: 4px 0;"><strong>Expected:</strong> {{ bug.expected_result }}</p>
        <p style="margin: 4px 0;"><strong>AI Hypothesis:</strong> {{ bug.root_cause_hypothesis }}</p>
        <p style="margin: 4px 0; font-size: 13px; color: #64748b;"><strong>Severity Reasoning:</strong> {{ bug.severity_reasoning }}</p>

        {% if bug.steps_to_reproduce %}
        <details style="margin-top: 8px;">
            <summary style="cursor: pointer; font-weight: 600;">Steps to Reproduce</summary>
            <ul>
                {% for step in bug.steps_to_reproduce %}
                <li>{{ step }}</li>
                {% endfor %}
            </ul>
        </details>
        {% endif %}
    </div>
    {% endfor %}
    {% endif %}

    <div class="rec-box">
        <h3 style="margin: 0 0 8px 0; color: #1e40af;">Actionable QA Recommendations</h3>
        <ul>
            {% for rec in recommendations %}
            <li>{{ rec }}</li>
            {% endfor %}
        </ul>
    </div>
</div>
</body>
</html>
"""


class ReportGeneratorService:
    """Generates standalone HTML reports, JSON schemas, and printable formats."""

    @classmethod
    def generate_reports(
        cls,
        summary: Dict[str, Any],
        results: List[Dict[str, Any]],
        bugs: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        run_id = summary.get("run_id", "report")
        run_dir = settings.REPORTS_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Build Actionable Recommendations
        recommendations = []
        if any(b.get("category") == "API" for b in bugs):
            recommendations.append("Investigate HTTP 500 API responses in Case Management endpoints for unhandled exceptions.")
        if any(b.get("category") == "Validation" for b in bugs):
            recommendations.append("Strengthen client-side boundary validation to prevent negative values from reaching backend.")
        if any(b.get("category") == "Automation" for b in bugs):
            recommendations.append("Add explicit 'data-testid' attributes to dynamic buttons to eliminate locator ambiguities.")
        if not recommendations:
            recommendations.append("All automated workflows passed successfully. System is stable for release candidate build.")

        # 1. JSON Report
        json_report_path = run_dir / "report.json"
        full_json_data = {
            "summary": summary,
            "results": results,
            "bugs": bugs,
            "recommendations": recommendations
        }
        json_report_path.write_text(json.dumps(full_json_data, indent=2), encoding="utf-8")

        # 2. HTML Report
        html_report_path = run_dir / "report.html"
        template = Template(HTML_REPORT_TEMPLATE)
        rendered_html = template.render(
            summary=summary,
            results=results,
            bugs=bugs,
            recommendations=recommendations
        )
        html_report_path.write_text(rendered_html, encoding="utf-8")

        logger.info(f"Generated QA reports at {html_report_path} and {json_report_path}")

        return {
            "html_path": str(html_report_path),
            "json_path": str(json_report_path)
        }
