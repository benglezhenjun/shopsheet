import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..", "..");

test("merchant can upload sample files and download deliverables", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "ShopSheet" })).toBeVisible();
  await expect(page.getByText("实时接口数据")).toBeVisible();

  await page
    .locator('input[name="order_file"]')
    .setInputFiles(path.join(repoRoot, "examples", "orders_messy.csv"));
  await page
    .locator('input[name="sku_file"]')
    .setInputFiles(path.join(repoRoot, "examples", "skus.csv"));
  await page
    .locator('input[name="refund_file"]')
    .setInputFiles(path.join(repoRoot, "examples", "refunds.csv"));

  await page.getByRole("button", { name: "分析上传文件" }).click();

  await expect(page.getByText("上传文件分析完成。")).toBeVisible();
  const kpis = page.getByLabel("核心指标");
  const issueRowsCard = kpis.locator(".metric").filter({ hasText: "问题行" });
  const cleanRowsCard = kpis.locator(".metric").filter({ hasText: "合格行" });
  await expect(issueRowsCard.locator("strong")).toHaveText("7");
  await expect(cleanRowsCard.locator("strong")).toHaveText("1");
  await expect(page.getByText("重复订单号")).toBeVisible();

  await expectDownload(page, "合格订单", "clean_orders.csv", "O-1001,SKU-RED-M");
  await expectDownload(page, "问题行", "issue_rows.csv", "source_table");
  await expectDownload(page, "质检报告", "quality_report.md", "# ShopSheet Quality Report");
});

test("merchant gets a clear message before choosing all files", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "分析上传文件" }).click();

  await expect(
    page.getByText("请先选择订单、SKU 和退款三个文件，再运行分析。")
  ).toBeVisible();
});

test("merchant sees a readable validation error for bad table headers", async ({ page }) => {
  await page.goto("/");

  await page.locator('input[name="order_file"]').setInputFiles({
    name: "bad_orders.csv",
    mimeType: "text/csv",
    buffer: Buffer.from("订单编号\nO-1001\n", "utf-8")
  });
  await page
    .locator('input[name="sku_file"]')
    .setInputFiles(path.join(repoRoot, "examples", "skus.csv"));
  await page
    .locator('input[name="refund_file"]')
    .setInputFiles(path.join(repoRoot, "examples", "refunds.csv"));

  await page.getByRole("button", { name: "分析上传文件" }).click();

  await expect(page.getByText(/上传分析失败：Missing required order columns/)).toBeVisible();
});

test("merchant sees a readable validation error for oversized uploads", async ({ page }) => {
  await page.goto("/");

  await page.locator('input[name="order_file"]').setInputFiles({
    name: "orders.csv",
    mimeType: "text/csv",
    buffer: Buffer.concat([
      Buffer.from("not_order_column\n", "utf-8"),
      Buffer.alloc(5 * 1024 * 1024 + 1, "x")
    ])
  });
  await page
    .locator('input[name="sku_file"]')
    .setInputFiles(path.join(repoRoot, "examples", "skus.csv"));
  await page
    .locator('input[name="refund_file"]')
    .setInputFiles(path.join(repoRoot, "examples", "refunds.csv"));

  await page.getByRole("button", { name: "分析上传文件" }).click();

  await expect(
    page.getByText("上传分析失败：orders file exceeds 5 MB upload limit")
  ).toBeVisible();
});

async function expectDownload(page, buttonName, expectedFilename, expectedText) {
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: buttonName }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe(expectedFilename);
  const downloadPath = await download.path();
  expect(fs.readFileSync(downloadPath, "utf-8")).toContain(expectedText);
}
