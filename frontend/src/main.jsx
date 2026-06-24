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

// Backend issue codes/messages stay English (stable contract for CSV/report exports
// and tests). The operator UI renders Chinese labels per code, falling back to the
// backend message for any unmapped code.
const ISSUE_LABELS = {
  duplicate_order_id: { title: "重复订单号", message: "订单号出现多次。" },
  invalid_phone: { title: "无效手机号", message: "手机号不是 11 位中国大陆手机号码。" },
  missing_sku: { title: "缺失 SKU", message: "订单引用的 SKU 不在 SKU 表中。" },
  negative_quantity: { title: "负数量", message: "订单数量为负数。" },
  missing_shipping_address: { title: "缺失收货地址", message: "收货地址为空。" },
  invalid_order_date: { title: "无效下单日期", message: "下单日期无法解析。" },
  duplicate_sku: { title: "重复 SKU", message: "SKU 在 SKU 表中出现多次。" },
  negative_sku_cost: { title: "负成本", message: "SKU 成本为负数。" },
  refund_unknown_order: { title: "退款无对应订单", message: "退款引用的订单不在订单表中。" },
  refund_exceeds_order_amount: { title: "退款超过订单金额", message: "退款金额大于匹配的正向订单金额。" },
  invalid_quantity: { title: "数量无法解析", message: "订单数量无法解析为数字。" },
  invalid_unit_price: { title: "单价无法解析", message: "订单单价无法解析为数字。" },
  invalid_cost: { title: "成本无法解析", message: "SKU 成本无法解析为数字。" },
  invalid_refund_amount: { title: "退款金额无法解析", message: "退款金额无法解析为数字。" }
};

const fallbackBundle = {
  metrics: {
    order_rows: 6,
    sku_rows: 3,
    refund_rows: 2,
    gross_sales: 626.5,
    refund_amount: 100,
    estimated_gross_margin: 212.5,
    clean_order_count: 1,
    excluded_order_count: 5,
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
  const [uploadMessage, setUploadMessage] = React.useState("使用示例数据，或上传订单、SKU、退款三个商家导出文件。");

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
      setUploadMessage("请先选择订单、SKU 和退款三个文件，再运行分析。");
      return;
    }
    setLoading(true);
    setUploadMessage("正在上传文件并执行质检…");
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
      setUploadMessage("上传文件分析完成。");
    } catch (error) {
      setUploadMessage(`上传分析失败：${error.message}`);
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
          <div className="eyebrow">本地优先 · 电商数据质检</div>
          <h1>ShopSheet</h1>
        </div>
        <div className="actions">
          <button className="ghostButton" onClick={refreshReport} type="button">
            <RefreshCw size={17} />
            刷新
          </button>
        </div>
      </header>

      <section className="statusLine">
        <span className={source === "api" ? "statusOk" : "statusWarn"}>
          {source === "api" ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
          {source === "api" ? "实时接口数据" : "演示回退数据"}
        </span>
        <span>{loading ? "正在刷新分析…" : "演示数据集：订单、SKU 成本、退款"}</span>
      </section>

      <section className="uploadBand" aria-label="上传商家导出文件">
        <FileInput
          label="订单文件"
          name="order_file"
          onChange={(event) => updateFile("order_file", event.target.files)}
          value={files.order_file}
        />
        <FileInput
          label="SKU 文件"
          name="sku_file"
          onChange={(event) => updateFile("sku_file", event.target.files)}
          value={files.sku_file}
        />
        <FileInput
          label="退款文件"
          name="refund_file"
          onChange={(event) => updateFile("refund_file", event.target.files)}
          value={files.refund_file}
        />
        <button className="analyzeButton" onClick={analyzeUploads} type="button">
          <ShieldCheck size={17} />
          分析上传文件
        </button>
        <p>{uploadMessage}</p>
      </section>

      <section className="downloadBand" aria-label="商家交付物">
        <div>
          <h2>交付物打包</h2>
          <p>下载经审核后可向后续环节流转的文件。</p>
        </div>
        <button
          className="ghostButton"
          onClick={() => downloadDeliverable("clean_orders.csv")}
          type="button"
        >
          <Download size={17} />
          合格订单
        </button>
        <button
          className="ghostButton"
          onClick={() => downloadDeliverable("issue_rows.csv")}
          type="button"
        >
          <Download size={17} />
          问题行
        </button>
        <button
          className="primaryButton"
          onClick={() => downloadDeliverable("quality_report.md")}
          type="button"
        >
          <Download size={17} />
          质检报告
        </button>
      </section>

      <section className="metricGrid" aria-label="核心指标">
        <Metric label="订单行数" value={metrics.order_rows} />
        <Metric label="合格行" value={metrics.clean_order_count ?? cleanOrders.length} tone="ok" />
        <Metric label="销售额" value={money(metrics.gross_sales)} />
        <Metric label="退款" value={money(metrics.refund_amount)} />
        <Metric label="毛利" value={money(metrics.estimated_gross_margin)} />
        <Metric label="问题行" value={issueTotal} tone={issueTotal > 0 ? "risk" : "ok"} />
      </section>

      <section className="contentGrid">
        <div className="mainColumn">
          <section className="panel issuePanel">
            <div className="sectionHeader">
              <div>
                <h2>问题队列</h2>
                <p>发货、对账或毛利核算前需要复核的行。</p>
              </div>
              <ShieldCheck size={22} />
            </div>
            <div className="issueList">
              {issues.map((issue) => (
                <article className="issueRow" key={issue.code}>
                  <div>
                    <strong>{issueTitle(issue)}</strong>
                    <p>{issueMessage(issue)}</p>
                  </div>
                  <div className="issueMeta">
                    <span>{issue.count} 行</span>
                    <span>{issue.rows?.join("、")}</span>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="panel tablePanel">
            <div className="sectionHeader">
              <div>
                <h2>合格订单预览</h2>
                <p>规范化字段与计算出的订单级金额。</p>
              </div>
              <FileSpreadsheet size={22} />
            </div>
            <div className="tableWrap">
              <table>
                <thead>
                  <tr>
                    <th>订单</th>
                    <th>SKU</th>
                    <th>数量</th>
                    <th>单价</th>
                    <th>行金额</th>
                    <th>预估毛利</th>
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
          <h2>复核摘要</h2>
          <p>
            本次演示检查重复订单、缺失 SKU 引用、无效手机号、缺失地址、负数量以及退款不匹配等问题。
          </p>
          <dl>
            <div>
              <dt>已分析数据</dt>
              <dd>{metrics.order_rows + metrics.sku_rows + metrics.refund_rows} 行</dd>
            </div>
            <div>
              <dt>待处理</dt>
              <dd>{issueTotal} 个行级问题</dd>
            </div>
            <div>
              <dt>下一步操作</dt>
              <dd>修正问题行，重跑报告，导出合格订单包。</dd>
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
      <input
        className="fileNativeInput"
        accept=".csv,.xlsx,.xlsm"
        name={name}
        onChange={onChange}
        type="file"
      />
      <span className="fileTrigger">选择文件</span>
      <strong>{value?.name ?? "未选择文件"}</strong>
    </label>
  );
}

function money(value) {
  return Number(value ?? 0).toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

function issueTitle(issue) {
  return ISSUE_LABELS[issue.code]?.title ?? issue.code.replaceAll("_", " ");
}

function issueMessage(issue) {
  return ISSUE_LABELS[issue.code]?.message ?? issue.message;
}

createRoot(document.getElementById("root")).render(<App />);
