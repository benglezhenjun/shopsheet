import React from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  CheckCircle2,
  Download,
  FileSpreadsheet,
  RefreshCw,
  ShieldCheck
} from "lucide-react";
import "./styles.css";

const fallbackBundle = {
  metrics: {
    order_rows: 6,
    sku_rows: 3,
    refund_rows: 2,
    gross_sales: 626.5,
    refund_amount: 100,
    estimated_gross_margin: 271.5,
    issue_count: 7
  },
  issues: [
    {
      code: "duplicate_order_id",
      message: "Order ID appears more than once.",
      count: 2,
      rows: [3, 4]
    },
    {
      code: "invalid_phone",
      message: "Phone value is not an 11-digit mainland China mobile number.",
      count: 1,
      rows: [3]
    },
    {
      code: "missing_sku",
      message: "Order references a SKU that is not present in the SKU table.",
      count: 1,
      rows: [5]
    }
  ],
  clean_orders: [
    {
      order_id: "O-1001",
      sku: "SKU-RED-M",
      quantity: 2,
      unit_price: 79.9,
      phone: "13800138000",
      shipping_address: "Shanghai Pudong",
      line_amount: 159.8,
      estimated_line_margin: 89.8
    },
    {
      order_id: "O-1002",
      sku: "SKU-BLUE-S",
      quantity: 1,
      unit_price: 129,
      phone: "not-a-phone",
      shipping_address: "Hangzhou Xihu",
      line_amount: 129,
      estimated_line_margin: 59
    },
    {
      order_id: "O-1003",
      sku: "SKU-MISSING",
      quantity: 1,
      unit_price: 59,
      phone: "13700137000",
      shipping_address: "Beijing Chaoyang",
      line_amount: 59,
      estimated_line_margin: 59
    }
  ],
  markdown_report: "# ShopSheet Quality Report\n\nDemo report loaded from fallback data."
};

function App() {
  const [bundle, setBundle] = React.useState(fallbackBundle);
  const [source, setSource] = React.useState("fallback");
  const [loading, setLoading] = React.useState(true);
  const [files, setFiles] = React.useState({
    order_file: null,
    sku_file: null,
    refund_file: null
  });
  const [uploadMessage, setUploadMessage] = React.useState("Use the sample data or upload three merchant export files.");

  const refreshReport = React.useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/demo-report");
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }
      setBundle(await response.json());
      setSource("api");
    } catch {
      setBundle(fallbackBundle);
      setSource("fallback");
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    refreshReport();
  }, [refreshReport]);

  async function analyzeUploads() {
    if (!files.order_file || !files.sku_file || !files.refund_file) {
      setUploadMessage("Choose order, SKU, and refund files before running analysis.");
      return;
    }
    setLoading(true);
    setUploadMessage("Uploading files and running checks...");
    try {
      const formData = new FormData();
      formData.append("order_file", files.order_file);
      formData.append("sku_file", files.sku_file);
      formData.append("refund_file", files.refund_file);
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail ?? `API returned ${response.status}`);
      }
      setBundle(await response.json());
      setSource("api");
      setUploadMessage("Uploaded files analyzed successfully.");
    } catch (error) {
      setUploadMessage(`Upload analysis failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  function updateFile(field, selectedFiles) {
    setFiles((current) => ({ ...current, [field]: selectedFiles?.[0] ?? null }));
  }

  function downloadDeliverable(filename) {
    const content = bundle.export_files?.[filename];
    if (!content) {
      window.location.href = `/api/demo-export/${filename}`;
      return;
    }
    const type = filename.endsWith(".md") ? "text/markdown" : "text/csv";
    const blob = new Blob([content], { type: `${type};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }

  const metrics = bundle.metrics;
  const issueTotal = metrics.issue_count ?? bundle.issue_rows?.length ?? 0;
  const cleanOrders = bundle.clean_orders ?? [];
  const issues = bundle.issues ?? [];

  return (
    <main className="workspace">
      <header className="topbar">
        <div>
          <div className="eyebrow">Local-first ecommerce data QA</div>
          <h1>ShopSheet</h1>
        </div>
        <div className="actions">
          <button className="ghostButton" onClick={refreshReport} type="button">
            <RefreshCw size={17} />
            Refresh
          </button>
        </div>
      </header>

      <section className="statusLine">
        <span className={source === "api" ? "statusOk" : "statusWarn"}>
          {source === "api" ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
          {source === "api" ? "Live API data" : "Fallback demo data"}
        </span>
        <span>{loading ? "Refreshing analysis..." : "Demo dataset: orders, SKU cost, refunds"}</span>
      </section>

      <section className="uploadBand" aria-label="Upload merchant exports">
        <FileInput
          label="Order file"
          name="order_file"
          onChange={(event) => updateFile("order_file", event.target.files)}
          value={files.order_file}
        />
        <FileInput
          label="SKU file"
          name="sku_file"
          onChange={(event) => updateFile("sku_file", event.target.files)}
          value={files.sku_file}
        />
        <FileInput
          label="Refund file"
          name="refund_file"
          onChange={(event) => updateFile("refund_file", event.target.files)}
          value={files.refund_file}
        />
        <button className="analyzeButton" onClick={analyzeUploads} type="button">
          <ShieldCheck size={17} />
          Analyze uploads
        </button>
        <p>{uploadMessage}</p>
      </section>

      <section className="downloadBand" aria-label="Merchant deliverables">
        <div>
          <h2>Deliverable package</h2>
          <p>Download the files an operator can send forward after review.</p>
        </div>
        <button
          className="ghostButton"
          onClick={() => downloadDeliverable("clean_orders.csv")}
          type="button"
        >
          <Download size={17} />
          Clean orders
        </button>
        <button
          className="ghostButton"
          onClick={() => downloadDeliverable("issue_rows.csv")}
          type="button"
        >
          <Download size={17} />
          Issue rows
        </button>
        <button
          className="primaryButton"
          onClick={() => downloadDeliverable("quality_report.md")}
          type="button"
        >
          <Download size={17} />
          Report
        </button>
      </section>

      <section className="metricGrid" aria-label="Selected KPIs">
        <Metric label="Order rows" value={metrics.order_rows} />
        <Metric label="Gross sales" value={money(metrics.gross_sales)} />
        <Metric label="Refunds" value={money(metrics.refund_amount)} />
        <Metric label="Gross margin" value={money(metrics.estimated_gross_margin)} />
        <Metric label="Issue rows" value={issueTotal} tone={issueTotal > 0 ? "risk" : "ok"} />
      </section>

      <section className="contentGrid">
        <div className="mainColumn">
          <section className="panel issuePanel">
            <div className="sectionHeader">
              <div>
                <h2>Issue queue</h2>
                <p>Rows that need review before shipping, reconciliation, or margin review.</p>
              </div>
              <ShieldCheck size={22} />
            </div>
            <div className="issueList">
              {issues.map((issue) => (
                <article className="issueRow" key={issue.code}>
                  <div>
                    <strong>{formatCode(issue.code)}</strong>
                    <p>{issue.message}</p>
                  </div>
                  <div className="issueMeta">
                    <span>{issue.count} rows</span>
                    <span>{issue.rows?.join(", ")}</span>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="panel tablePanel">
            <div className="sectionHeader">
              <div>
                <h2>Clean order preview</h2>
                <p>Canonical columns and calculated order-level amounts.</p>
              </div>
              <FileSpreadsheet size={22} />
            </div>
            <div className="tableWrap">
              <table>
                <thead>
                  <tr>
                    <th>Order</th>
                    <th>SKU</th>
                    <th>Qty</th>
                    <th>Unit price</th>
                    <th>Line amount</th>
                    <th>Est. margin</th>
                  </tr>
                </thead>
                <tbody>
                  {cleanOrders.slice(0, 8).map((order) => (
                    <tr key={`${order.order_id}-${order.sku}-${order.phone}`}>
                      <td>{order.order_id}</td>
                      <td>{order.sku}</td>
                      <td>{order.quantity}</td>
                      <td>{money(order.unit_price)}</td>
                      <td>{money(order.line_amount)}</td>
                      <td>{money(order.estimated_line_margin)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>

        <aside className="inspector">
          <h2>Review summary</h2>
          <p>
            This demo run checks duplicate orders, missing SKU references, invalid phone
            values, missing addresses, negative quantities, and refund mismatches.
          </p>
          <dl>
            <div>
              <dt>Files analyzed</dt>
              <dd>{metrics.order_rows + metrics.sku_rows + metrics.refund_rows} rows</dd>
            </div>
            <div>
              <dt>Action needed</dt>
              <dd>{issueTotal} row-level issues</dd>
            </div>
            <div>
              <dt>Operator next step</dt>
              <dd>Fix rows, rerun report, export clean package.</dd>
            </div>
          </dl>
          <pre>{bundle.markdown_report?.slice(0, 480)}</pre>
        </aside>
      </section>
    </main>
  );
}

function Metric({ label, value, tone = "neutral" }) {
  return (
    <div className={`metric ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function FileInput({ label, name, onChange, value }) {
  return (
    <label className="fileInput">
      <span>{label}</span>
      <input accept=".csv,.xlsx,.xlsm" name={name} onChange={onChange} type="file" />
      <strong>{value?.name ?? "No file selected"}</strong>
    </label>
  );
}

function money(value) {
  return Number(value ?? 0).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

function formatCode(code) {
  return code.replaceAll("_", " ");
}

createRoot(document.getElementById("root")).render(<App />);
