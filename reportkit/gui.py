"""Small native Windows interface for the standalone data-quality tool."""

from __future__ import annotations

import webbrowser
from pathlib import Path

from .core import summarize_csv
from .reporting import write_report_bundle


def generate_report(source: str | Path, output: str | Path) -> Path:
    """Generate a complete report bundle and return the HTML report path."""
    source_path = Path(source)
    output_path = Path(output)
    summary = summarize_csv(source_path)
    return write_report_bundle(summary, output_path)["html"]


def main() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("Data Quality Inspector")
    root.geometry("780x620")
    root.minsize(700, 560)

    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
    style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#526174")
    style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"))
    style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(16, 9))

    source_var = tk.StringVar()
    output_var = tk.StringVar()
    status_var = tk.StringVar(value="Ready · local processing only · source files stay unchanged")
    last_report: dict[str, Path | None] = {"path": None}

    project_root = Path(__file__).resolve().parents[1]
    demo = project_root / "examples" / "demo.csv"
    if demo.is_file():
        source_var.set(str(demo))
        output_var.set(str(project_root / "demo-report"))

    outer = ttk.Frame(root, padding=28)
    outer.pack(fill="both", expand=True)

    ttk.Label(outer, text="DATA QUALITY INSPECTOR", foreground="#2563eb", font=("Segoe UI", 9, "bold")).pack(anchor="w")
    ttk.Label(outer, text="Check a CSV before you trust it", style="Title.TLabel").pack(anchor="w", pady=(5, 4))
    ttk.Label(
        outer,
        text="A standalone, local-first tool for missing values, duplicate rows, irregular structure and column statistics.",
        style="Subtitle.TLabel",
        wraplength=700,
    ).pack(anchor="w", pady=(0, 24))

    card = ttk.LabelFrame(outer, text="  New inspection  ", padding=20)
    card.pack(fill="x")

    ttk.Label(card, text="CSV source", style="Section.TLabel").grid(row=0, column=0, sticky="w")
    source_entry = ttk.Entry(card, textvariable=source_var)
    source_entry.grid(row=1, column=0, sticky="ew", pady=(7, 16), padx=(0, 10))

    def choose_source() -> None:
        selected = filedialog.askopenfilename(title="Choose a CSV file", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if selected:
            source_var.set(selected)
            if not output_var.get().strip():
                output_var.set(str(Path(selected).with_name(f"{Path(selected).stem}-report")))

    ttk.Button(card, text="Browse…", command=choose_source).grid(row=1, column=1, sticky="ew", pady=(7, 16))

    ttk.Label(card, text="Report folder", style="Section.TLabel").grid(row=2, column=0, sticky="w")
    output_entry = ttk.Entry(card, textvariable=output_var)
    output_entry.grid(row=3, column=0, sticky="ew", pady=(7, 4), padx=(0, 10))

    def choose_output() -> None:
        selected = filedialog.askdirectory(title="Choose a report folder")
        if selected:
            output_var.set(selected)

    ttk.Button(card, text="Browse…", command=choose_output).grid(row=3, column=1, sticky="ew", pady=(7, 4))
    card.columnconfigure(0, weight=1)

    result_box = ttk.LabelFrame(outer, text="  Output  ", padding=16)
    result_box.pack(fill="x", pady=(18, 0))
    result_text = tk.Text(result_box, height=5, relief="flat", bg="#f5f8fc", fg="#23344d", font=("Consolas", 10), padx=12, pady=10, state="disabled")
    result_text.pack(fill="both", expand=True)

    def set_result(text: str) -> None:
        result_text.configure(state="normal")
        result_text.delete("1.0", "end")
        result_text.insert("1.0", text)
        result_text.configure(state="disabled")

    def run_inspection() -> None:
        source = Path(source_var.get().strip())
        output = Path(output_var.get().strip())
        if not source.is_file():
            messagebox.showerror("Source not found", "Choose an existing CSV file.")
            return
        if not output_var.get().strip():
            messagebox.showerror("Output required", "Choose a report folder.")
            return
        try:
            summary = summarize_csv(source)
            paths = write_report_bundle(summary, output)
        except (OSError, UnicodeError, ValueError) as error:
            status_var.set("Stopped · no source data was changed")
            messagebox.showerror("Inspection stopped", str(error))
            return
        last_report["path"] = paths["html"]
        issues = ", ".join(summary["issues"]) if summary["issues"] else "none detected"
        set_result(
            f"Report complete\n\nRows: {summary['rows']}    Columns: {summary['columns']}\n"
            f"Missing values: {summary['missing_values']}    Duplicate rows: {summary['duplicate_rows']}\n"
            f"Structural issues: {issues}\n\nHTML: {paths['html']}"
        )
        status_var.set("Complete · JSON, Markdown and HTML reports created")

    def open_report() -> None:
        report = last_report["path"]
        if report is None or not report.is_file():
            messagebox.showinfo("No report yet", "Generate a report first.")
            return
        webbrowser.open(report.resolve().as_uri())

    actions = ttk.Frame(outer)
    actions.pack(fill="x", pady=(18, 0))
    ttk.Button(actions, text="Generate report", style="Primary.TButton", command=run_inspection).pack(side="left")
    ttk.Button(actions, text="Open HTML report", command=open_report, padding=(14, 9)).pack(side="left", padx=10)
    ttk.Label(actions, textvariable=status_var, style="Subtitle.TLabel").pack(side="right")

    source_entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
