import React, { useEffect, useState, useMemo, useRef } from "react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import {
  LayoutDashboard, Users, Plus, FileText, GitCompare, Layers,
  CheckSquare, History, Settings, ChevronLeft, ChevronRight,
  Mic, Upload, Scan, FileUp, PenLine, Play, Pause,
  Download, Edit2, AlertTriangle, CheckCircle, XCircle, Clock,
  Search, Filter, ChevronDown, MoreHorizontal,
  Cpu, Database, Server, User, X, Check, Eye,
  RefreshCw, Shield, AlertCircle, Calendar, FileAudio,
  Stethoscope, ClipboardList, Zap, BookOpen, Folder,
  TrendingUp, List, Layers as LayersIcon
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import {
  type ApiCustomer,
  type ApiDocument,
  type ApiTask,
  completeTask,
  createCustomer,
  createManualDocument,
  listCustomers,
  listDocuments,
  listTasks,
  getDashboard,
  getDocument,
  getDocumentPageImage,
  listHistory,
  compareDocuments,
  runClinicalReview,
  runAiAction,
  finalizeDocument,
  updateDocumentText,
  ocrFile,
  transcribeFile,
} from "../api/client";

const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));

type Screen =
  | "dashboard" | "customers" | "customer-workspace"
  | "new-processing" | "documents" | "asr-review" | "ocr-review"
  | "compare" | "clinical-review" | "batch" | "tasks" | "history" | "settings";

// ─── Sample Data ──────────────────────────────────────────────

const customers = [
  { id: "PT-001847", name: "Sarah Chen",       dob: "1978-03-14", docs: 12, lastActivity: "Jan 15, 2024", status: "active",   risk: "amber" },
  { id: "PT-001848", name: "Marcus Williams",  dob: "1965-07-22", docs: 8,  lastActivity: "Jan 15, 2024", status: "active",   risk: "green" },
  { id: "PT-001849", name: "Elena Rodriguez",  dob: "1989-11-05", docs: 3,  lastActivity: "Jan 15, 2024", status: "active",   risk: "red",   duplicate: true },
  { id: "PT-001850", name: "James O'Brien",    dob: "1952-09-18", docs: 24, lastActivity: "Dec 10, 2023", status: "archived", risk: "green" },
  { id: "PT-001851", name: "Priya Patel",      dob: "1991-06-30", docs: 6,  lastActivity: "Jan 14, 2024", status: "active",   risk: "green" },
  { id: "PT-001852", name: "David Kim",        dob: "1983-02-17", docs: 9,  lastActivity: "Jan 13, 2024", status: "active",   risk: "amber" },
];

const activityData = [
  { day: "Mon", asr: 12, ocr: 8 },
  { day: "Tue", asr: 15, ocr: 11 },
  { day: "Wed", asr: 9,  ocr: 7 },
  { day: "Thu", asr: 18, ocr: 14 },
  { day: "Fri", asr: 22, ocr: 16 },
  { day: "Sat", asr: 6,  ocr: 4 },
  { day: "Sun", asr: 11, ocr: 8 },
];

const queueItems = [
  { id: "Q-1042", customer: "Marcus Williams", type: "Upload Audio",   status: "processing", progress: 45, model: "Mega-ASR" },
  { id: "Q-1043", customer: "Sarah Chen",      type: "Scan Document",  status: "queued",     progress: 0,  model: "OCR-v2" },
  { id: "Q-1044", customer: "Elena Rodriguez", type: "Upload PDF",     status: "processing", progress: 78, model: "OCR-v2" },
];

const pendingReviews = [
  { id: "R-201", customer: "Sarah Chen",      doc: "Visit Note — Jan 15, 2024", type: "clinical", priority: "high" },
  { id: "R-202", customer: "Marcus Williams", doc: "Audio Recording — Jan 15",  type: "asr",      priority: "medium" },
  { id: "R-203", customer: "Priya Patel",     doc: "Scan — Jan 14, 2024",       type: "ocr",      priority: "low" },
];

const allTasks = [
  { id: 1, title: "Verify Metformin dosage — ASR records 1000 mg, prescription shows 100 mg", customer: "Sarah Chen",      priority: "high",   due: "Today",         overdue: false },
  { id: 2, title: "Schedule 3-month follow-up appointment",                                    customer: "Marcus Williams", priority: "medium", due: "Tomorrow",      overdue: false },
  { id: 3, title: "Complete pending clinical review",                                           customer: "Elena Rodriguez", priority: "high",   due: "Jan 13, 2024",  overdue: true  },
  { id: 4, title: "Confirm allergy — penicillin noted in one record, denied in another",        customer: "David Kim",       priority: "high",   due: "Today",         overdue: false },
  { id: 5, title: "Update emergency contact details",                                           customer: "Priya Patel",     priority: "low",    due: "Jan 20, 2024",  overdue: false },
];

const historyItems = [
  { id: "H-3001", time: "14:32", date: "Jan 15, 2024", customer: "Sarah Chen",      action: "Audio Upload → ASR Complete",          model: "Mega-ASR",   confidence: 94.2, status: "complete"        },
  { id: "H-3002", time: "13:45", date: "Jan 15, 2024", customer: "Elena Rodriguez", action: "PDF Upload → OCR Complete",             model: "OCR-v2",     confidence: 87.1, status: "review-required" },
  { id: "H-3003", time: "12:18", date: "Jan 15, 2024", customer: "Marcus Williams", action: "Manual Note → Saved",                   model: "—",          confidence: null, status: "complete"        },
  { id: "H-3004", time: "11:55", date: "Jan 15, 2024", customer: "Priya Patel",     action: "Scan → OCR Processing Failed",          model: "OCR-v2",     confidence: null, status: "error"           },
  { id: "H-3005", time: "10:30", date: "Jan 15, 2024", customer: "Sarah Chen",      action: "Clinical Review → Accepted with caveats", model: "Ollama/llama3", confidence: null, status: "complete"   },
  { id: "H-3006", time: "09:15", date: "Jan 14, 2024", customer: "David Kim",       action: "Audio Upload → ASR Complete",          model: "Qwen3-ASR",  confidence: 91.8, status: "complete"        },
];

type CustomerRow = typeof customers[number] & { backendId?: string };
type DocumentRow = {
  id: string;
  name: string;
  customer: string;
  type: string;
  confidence: number | null;
  status: string;
  date: string;
  customerId?: string | null;
};
type TaskRow = {
  id: string | number;
  backendId?: string;
  customerId?: string | null;
  title: string;
  customer: string;
  priority: string;
  due: string;
  overdue: boolean;
};

function formatDisplayDate(value?: string | null) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function documentType(sourceType: string) {
  if (sourceType.includes("audio")) return "ASR";
  if (sourceType.includes("ocr") || sourceType.includes("image") || sourceType.includes("pdf")) return "OCR";
  if (sourceType.includes("manual")) return "Manual";
  return sourceType;
}

function mapCustomer(customer: ApiCustomer, documentCount: number): CustomerRow {
  return {
    id: customer.customer_code || customer.id,
    backendId: customer.id,
    name: customer.full_name,
    dob: customer.date_of_birth ?? "—",
    docs: documentCount,
    lastActivity: formatDisplayDate(customer.updated_at),
    status: customer.status as CustomerRow["status"],
    risk: customer.duplicate_warning ? "amber" : "green",
    duplicate: customer.duplicate_warning || undefined,
  };
}

function mapDocument(document: ApiDocument, customerName: string): DocumentRow {
  const confidence = document.average_confidence ?? null;
  return {
    id: document.document_id,
    name: document.source_name,
    customer: customerName,
    type: documentType(document.source_type),
    confidence: confidence !== null && confidence <= 1 ? confidence * 100 : confidence,
    status: document.status,
    date: formatDisplayDate(document.created_at),
    customerId: document.customer_id,
  };
}

function mapTask(task: ApiTask, customerName: string): TaskRow {
  const dueDate = task.due_date ? new Date(task.due_date) : null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return {
    id: task.id,
    backendId: task.id,
    customerId: task.customer_id,
    title: task.task_text,
    customer: customerName,
    priority: task.priority,
    due: task.due_date ? formatDisplayDate(task.due_date) : "No due date",
    overdue: !!dueDate && dueDate < today && task.status !== "complete",
  };
}

// ─── Shared UI ────────────────────────────────────────────────

function StatusDot({ status }: { status: "online" | "warning" | "offline" | "connecting" }) {
  return (
    <span className={cn(
      "inline-block w-2 h-2 rounded-full flex-shrink-0",
      status === "online"     && "bg-emerald-500",
      status === "warning"    && "bg-amber-400",
      status === "offline"    && "bg-red-500",
      status === "connecting" && "bg-amber-400 animate-pulse"
    )} />
  );
}

type BadgeVariant = "default" | "green" | "amber" | "red" | "blue" | "teal" | "blocked" |
  "outline" | "active" | "archived" | "processing" | "queued" | "error" | "complete" | "review-required";

function Badge({ variant = "default", children }: { variant?: BadgeVariant; children: React.ReactNode }) {
  const styles: Record<string, string> = {
    default:         "bg-muted text-muted-foreground",
    green:           "bg-emerald-50 text-emerald-700 border border-emerald-200",
    amber:           "bg-amber-50 text-amber-700 border border-amber-200",
    red:             "bg-red-50 text-red-700 border border-red-200",
    blue:            "bg-blue-50 text-blue-700 border border-blue-200",
    teal:            "bg-teal-50 text-teal-700 border border-teal-200",
    blocked:         "bg-slate-100 text-slate-600 border border-slate-300",
    outline:         "border border-border text-foreground bg-transparent",
    active:          "bg-emerald-50 text-emerald-700 border border-emerald-200",
    archived:        "bg-muted text-muted-foreground border border-border",
    processing:      "bg-blue-50 text-blue-700 border border-blue-200",
    queued:          "bg-slate-50 text-slate-600 border border-slate-200",
    error:           "bg-red-50 text-red-700 border border-red-200",
    complete:        "bg-emerald-50 text-emerald-700 border border-emerald-200",
    "review-required": "bg-amber-50 text-amber-700 border border-amber-200",
  };
  return (
    <span className={cn("inline-flex items-center px-2 py-0.5 rounded text-xs font-medium whitespace-nowrap", styles[variant] ?? styles.default)}>
      {children}
    </span>
  );
}

function Btn({
  variant = "primary", size = "md", icon, children, onClick, className, disabled,
}: {
  variant?: "primary" | "secondary" | "ghost" | "danger" | "outline";
  size?: "sm" | "md" | "lg";
  icon?: React.ReactNode;
  children?: React.ReactNode;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
}) {
  const base = "inline-flex items-center gap-1.5 font-medium rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50 disabled:pointer-events-none";
  const variants = {
    primary:   "bg-primary text-primary-foreground hover:bg-primary/90",
    secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
    ghost:     "hover:bg-muted text-foreground",
    danger:    "bg-destructive text-destructive-foreground hover:bg-destructive/90",
    outline:   "border border-border text-foreground bg-card hover:bg-muted",
  };
  const sizes = { sm: "px-2.5 py-1 text-xs", md: "px-3.5 py-1.5 text-sm", lg: "px-5 py-2.5 text-sm" };
  return (
    <button className={cn(base, variants[variant], sizes[size], className)} onClick={onClick} disabled={disabled}>
      {icon && <span className="flex-shrink-0">{icon}</span>}
      {children}
    </button>
  );
}

function Card({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("bg-card border border-border rounded-lg", className)}>{children}</div>;
}

function KPICard({ label, value, sub, icon, trend, color = "blue" }: {
  label: string; value: string; sub?: string; icon: React.ReactNode; trend?: string; color?: string;
}) {
  const iconBg: Record<string, string> = {
    blue:  "bg-blue-50 text-blue-600",
    green: "bg-emerald-50 text-emerald-600",
    amber: "bg-amber-50 text-amber-600",
    teal:  "bg-teal-50 text-teal-600",
  };
  return (
    <Card className="p-5">
      <div className="flex items-start justify-between mb-3">
        <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center", iconBg[color] ?? iconBg.blue)}>{icon}</div>
        {trend && <span className="text-xs text-emerald-600 font-medium">{trend}</span>}
      </div>
      <div className="text-2xl font-semibold text-foreground">{value}</div>
      <div className="text-sm text-muted-foreground mt-0.5">{label}</div>
      {sub && <div className="text-xs text-muted-foreground mt-1">{sub}</div>}
    </Card>
  );
}

function ConfidenceLabel({ val }: { val: number | null }) {
  if (val === null) return <span className="text-muted-foreground">—</span>;
  return (
    <span className={cn("text-sm font-medium font-mono",
      val >= 95 ? "text-emerald-700" : val >= 85 ? "text-amber-700" : "text-red-700"
    )}>{val}%</span>
  );
}

// ─── Waveform ─────────────────────────────────────────────────

function WaveformViz({ progress = 0.35, onSeek }: { progress?: number; onSeek?: (p: number) => void }) {
  const bars = useMemo(() =>
    Array.from({ length: 96 }, (_, i) =>
      Math.max(4, 6 + Math.abs(Math.sin(i * 0.37 + 0.3)) * 22 + Math.abs(Math.sin(i * 1.25 + 0.9)) * 14)
    ), []
  );
  return (
    <div
      className="flex items-center gap-px h-14 cursor-pointer select-none w-full"
      onClick={(e) => {
        const r = e.currentTarget.getBoundingClientRect();
        onSeek?.((e.clientX - r.left) / r.width);
      }}
    >
      {bars.map((h, i) => (
        <div
          key={i}
          className={cn("flex-1 rounded-sm", i / bars.length < progress ? "bg-primary" : "bg-muted")}
          style={{ height: `${h}px` }}
        />
      ))}
    </div>
  );
}

// ─── Sidebar ──────────────────────────────────────────────────

const navItems = [
  { id: "dashboard",         label: "Dashboard",       icon: LayoutDashboard },
  { id: "customers",         label: "Customers",       icon: Users },
  { id: "new-processing",    label: "New Processing",  icon: Plus },
  { id: "documents",         label: "Documents",       icon: FileText },
  { id: "compare",           label: "Compare",         icon: GitCompare },
  { id: "batch",             label: "Batch",           icon: Layers },
  { id: "tasks",             label: "Tasks",           icon: CheckSquare },
  { id: "history",           label: "History",         icon: History },
  { id: "settings",          label: "Settings",        icon: Settings },
] as const;

const services = [
  { label: "ASR",    status: "online"     as const },
  { label: "OCR",    status: "online"     as const },
  { label: "Ollama", status: "connecting" as const },
  { label: "DB",     status: "online"     as const },
];

function Sidebar({ current, onNavigate, collapsed, onToggle }: {
  current: Screen; onNavigate: (s: Screen) => void; collapsed: boolean; onToggle: () => void;
}) {
  return (
    <aside className={cn(
      "flex flex-col h-full bg-card border-r border-border transition-all duration-300 flex-shrink-0",
      collapsed ? "w-16" : "w-60"
    )}>
      <div className="flex items-center gap-3 px-4 py-4 border-b border-border min-h-[60px]">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
          <Zap className="w-4 h-4 text-white" />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <div className="text-sm font-semibold text-foreground leading-tight">NoteFlow</div>
            <div className="text-xs text-muted-foreground">AI Platform</div>
          </div>
        )}
        <button onClick={onToggle} className="ml-auto text-muted-foreground hover:text-foreground transition-colors flex-shrink-0">
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
        {navItems.map(({ id, label, icon: Icon }) => {
          const active = current === id || (id === "customers" && current === "customer-workspace");
          return (
            <button
              key={id}
              onClick={() => onNavigate(id as Screen)}
              title={collapsed ? label : undefined}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                active ? "bg-primary text-primary-foreground font-medium" : "text-muted-foreground hover:text-foreground hover:bg-muted",
                collapsed && "justify-center px-2"
              )}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {!collapsed && <span>{label}</span>}
            </button>
          );
        })}
      </nav>

      <div className="px-3 py-4 border-t border-border">
        {!collapsed ? (
          <div className="space-y-2">
            <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">Services</div>
            {services.map(s => (
              <div key={s.label} className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-1.5 text-muted-foreground">
                  <StatusDot status={s.status} />{s.label}
                </span>
                <span className={s.status === "online" ? "text-emerald-600" : "text-amber-600"}>
                  {s.status === "connecting" ? "Connecting" : "Online"}
                </span>
              </div>
            ))}
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-1.5 text-muted-foreground">
                <StatusDot status="online" />Local
              </span>
              <span className="text-emerald-600">Active</span>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-1.5">
            {services.map(s => <StatusDot key={s.label} status={s.status} />)}
          </div>
        )}
      </div>
    </aside>
  );
}

// ─── Top Bar ──────────────────────────────────────────────────

function TopBar({ title, subtitle, actions, breadcrumbs }: {
  title: string; subtitle?: string; actions?: React.ReactNode;
  breadcrumbs?: Array<{ label: string; onClick?: () => void }>;
}) {
  return (
    <header className="flex items-center justify-between px-6 py-3.5 bg-card border-b border-border min-h-[60px] flex-shrink-0">
      <div>
        {breadcrumbs && (
          <div className="flex items-center gap-1 text-xs text-muted-foreground mb-0.5">
            {breadcrumbs.map((b, i) => (
              <span key={i} className="flex items-center gap-1">
                {i > 0 && <ChevronRight className="w-3 h-3" />}
                <span className={b.onClick ? "cursor-pointer hover:text-foreground transition-colors" : ""} onClick={b.onClick}>{b.label}</span>
              </span>
            ))}
          </div>
        )}
        <h1 className="text-base font-semibold text-foreground">{title}</h1>
        {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </header>
  );
}

// ─── Dashboard ────────────────────────────────────────────────

function DashboardScreen({ onNavigate }: { onNavigate: (s: Screen) => void }) {
  const [dashboard, setDashboard] = useState<Awaited<ReturnType<typeof getDashboard>> | null>(null);
  const refresh = () => getDashboard().then(setDashboard).catch(() => setDashboard(null));
  useEffect(() => { refresh(); }, []);
  const liveQueue = (dashboard?.queue ?? []).map(item => ({ ...item, customer: item.name, doc: item.type, type: item.type === "audio" ? "asr" : "ocr", priority: "medium", progress: item.status === "complete" ? 100 : 35, model: "backend" }));
  const liveReviews = liveQueue;
  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar
        title="Dashboard"
        subtitle={dashboard ? new Date(dashboard.date).toLocaleDateString() : "Loading live dashboard"}
        actions={
          <>
            <Btn variant="outline" size="sm" icon={<RefreshCw className="w-3.5 h-3.5" />} onClick={refresh}>Refresh</Btn>
            <Btn variant="primary" size="sm" icon={<Plus className="w-3.5 h-3.5" />} onClick={() => onNavigate("new-processing")}>New Processing</Btn>
          </>
        }
      />
      <div className="flex-1 overflow-y-auto p-6 space-y-5">
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
          <KPICard label="Documents Today" value={String(dashboard?.documents_today ?? 0)} sub="Live backend count" icon={<FileText className="w-5 h-5" />} color="blue" />
          <KPICard label="Pending Reviews" value={String(dashboard?.pending_reviews ?? 0)} sub="Live backend count" icon={<AlertCircle className="w-5 h-5" />} color="amber" />
          <KPICard label="Processing Queue" value={String(dashboard?.processing_queue ?? 0)} sub="Live backend count" icon={<Clock className="w-5 h-5" />} color="teal" />
          <KPICard label="Total Processed" value={String(dashboard?.total_processed ?? 0)} sub="Persisted documents" icon={<TrendingUp className="w-5 h-5" />} color="green" />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
          <Card className="xl:col-span-2 p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-foreground">Processing Activity</h3>
                <p className="text-xs text-muted-foreground">Last 7 days — ASR &amp; OCR jobs</p>
              </div>
              <Badge variant="outline">This Week</Badge>
            </div>
            <ResponsiveContainer width="100%" height={160}>
              <AreaChart data={dashboard?.activity ?? []} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="gAsr" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#1E3A5F" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#1E3A5F" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gOcr" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#1B7A7A" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#1B7A7A" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" vertical={false} />
                <XAxis dataKey="day" tick={{ fontSize: 11, fill: "#64748B" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#64748B" }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6, border: "1px solid rgba(0,0,0,0.1)", boxShadow: "0 2px 8px rgba(0,0,0,.08)" }} />
                <Area type="monotone" dataKey="asr" name="ASR" stroke="#1E3A5F" strokeWidth={2} fill="url(#gAsr)" />
                <Area type="monotone" dataKey="ocr" name="OCR" stroke="#1B7A7A" strokeWidth={2} fill="url(#gOcr)" />
              </AreaChart>
            </ResponsiveContainer>
            <div className="flex items-center gap-5 mt-2">
              <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className="w-3 h-0.5 bg-primary inline-block rounded-full" />ASR Jobs
              </span>
              <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className="w-3 h-0.5 bg-[#1B7A7A] inline-block rounded-full" />OCR Jobs
              </span>
            </div>
          </Card>

          <Card className="p-5">
            <h3 className="text-sm font-semibold text-foreground mb-4">Service Health</h3>
            <div className="space-y-3">
              {[
                { label: "Mega-ASR",      icon: <Mic       className="w-4 h-4" />, status: "online"     as const, detail: "v2.4.1 · GPU 34%" },
                { label: "Qwen3-ASR",     icon: <FileAudio className="w-4 h-4" />, status: "online"     as const, detail: "v3.1 · GPU 12%" },
                { label: "OCR Engine",    icon: <Scan      className="w-4 h-4" />, status: "online"     as const, detail: "v1.8.0 · CPU" },
                { label: "Ollama",        icon: <Cpu       className="w-4 h-4" />, status: "connecting" as const, detail: "llama3:8b loading" },
                { label: "PostgreSQL",    icon: <Database  className="w-4 h-4" />, status: "online"     as const, detail: "Local · 2.1 GB" },
                { label: "Local Storage", icon: <Server    className="w-4 h-4" />, status: "online"     as const, detail: "84.2 GB free" },
              ].map(svc => (
                <div key={svc.label} className="flex items-center gap-3">
                  <div className={cn("w-8 h-8 rounded-md flex items-center justify-center flex-shrink-0",
                    svc.status === "online" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"
                  )}>
                    {svc.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-medium text-foreground">{svc.label}</div>
                    <div className="text-xs text-muted-foreground truncate">{svc.detail}</div>
                  </div>
                  <StatusDot status={svc.status} />
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
          <Card>
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-border">
              <h3 className="text-sm font-semibold text-foreground">Processing Queue</h3>
              <Badge variant="blue">{liveQueue.length} active</Badge>
            </div>
            <div className="divide-y divide-border">
              {liveQueue.map(item => (
                <div key={item.id} className="px-5 py-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className="text-sm font-medium text-foreground">{item.customer}</span>
                      <span className="text-xs text-muted-foreground ml-2">{item.type}</span>
                    </div>
                    <Badge variant={item.status as BadgeVariant}>
                      {item.status === "processing" ? "Processing" : "Queued"}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                      <div
                        className={cn("h-full rounded-full transition-all", item.status === "processing" ? "bg-primary" : "bg-muted-foreground/30")}
                        style={{ width: `${item.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground font-mono w-8 text-right">{item.progress}%</span>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1.5">Model: {item.model} · {item.id}</div>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-border">
              <h3 className="text-sm font-semibold text-foreground">Pending Reviews</h3>
              <Btn variant="ghost" size="sm" onClick={() => onNavigate("history")}>View all</Btn>
            </div>
            <div className="divide-y divide-border">
              {liveReviews.map(r => (
                <div key={r.id} className="px-5 py-4 flex items-start justify-between gap-3 hover:bg-muted/20 transition-colors cursor-pointer">
                  <div className="flex items-start gap-3">
                    <div className={cn("w-8 h-8 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5",
                      r.type === "clinical" ? "bg-amber-50 text-amber-700" :
                      r.type === "asr"      ? "bg-blue-50  text-blue-700"  : "bg-teal-50 text-teal-700"
                    )}>
                      {r.type === "clinical" ? <Stethoscope className="w-4 h-4" /> :
                       r.type === "asr"      ? <FileAudio   className="w-4 h-4" /> : <Scan className="w-4 h-4" />}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-foreground">{r.customer}</div>
                      <div className="text-xs text-muted-foreground">{r.doc}</div>
                    </div>
                  </div>
                  <Badge variant={r.priority === "high" ? "red" : r.priority === "medium" ? "amber" : "outline"}>
                    {r.priority}
                  </Badge>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

// ─── Customers ────────────────────────────────────────────────

function CustomersScreen({
  customerRows = [],
  onCreateCustomer,
  onNavigate,
}: {
  customerRows?: CustomerRow[];
  onCreateCustomer?: () => void;
  onNavigate: (s: Screen) => void;
}) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"all" | "active" | "archived">("all");

  const filtered = customerRows.filter(c =>
    (filter === "all" || c.status === filter) &&
    (c.name.toLowerCase().includes(search.toLowerCase()) || c.id.includes(search))
  );

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar
        title="Customers"
        subtitle={`${customerRows.filter(c => c.status === "active").length} active profiles`}
        actions={<Btn variant="primary" size="sm" icon={<Plus className="w-3.5 h-3.5" />} onClick={onCreateCustomer}>New Customer</Btn>}
      />
      <div className="flex-1 overflow-y-auto p-6">
        <Card>
          <div className="flex items-center gap-3 px-5 py-3.5 border-b border-border flex-wrap gap-y-2">
            <div className="relative flex-1 min-w-48">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search name or patient ID..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 text-sm bg-input-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring placeholder:text-muted-foreground"
              />
            </div>
            <div className="flex items-center gap-1 bg-muted rounded-md p-1">
              {(["all", "active", "archived"] as const).map(f => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={cn("px-3 py-1 text-xs rounded font-medium capitalize transition-colors",
                    filter === f ? "bg-card shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {f}
                </button>
              ))}
            </div>
            <Btn variant="outline" size="sm" icon={<Filter className="w-3.5 h-3.5" />}>Filter</Btn>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  {["Patient", "Date of Birth", "ID", "Documents", "Last Activity", "Status", ""].map(h => (
                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-5 py-2.5 whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map(c => (
                  <tr key={c.id} className="hover:bg-muted/20 transition-colors cursor-pointer group" onClick={() => onNavigate("customer-workspace")}>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-semibold text-primary flex-shrink-0">
                          {c.name.split(" ").map(n => n[0]).join("")}
                        </div>
                        <div>
                          <div className="font-medium text-foreground flex items-center gap-1.5">
                            {c.name}
                            {(c as any).duplicate && (
                              <AlertTriangle className="w-3.5 h-3.5 text-amber-500" title="Potential duplicate record" />
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-muted-foreground">{c.dob}</td>
                    <td className="px-5 py-3.5">
                      <span className="font-mono text-xs bg-muted px-2 py-0.5 rounded">{c.id}</span>
                    </td>
                    <td className="px-5 py-3.5 text-muted-foreground">{c.docs}</td>
                    <td className="px-5 py-3.5 text-muted-foreground">{c.lastActivity}</td>
                    <td className="px-5 py-3.5">
                      <Badge variant={c.status as BadgeVariant}>{c.status}</Badge>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Btn variant="ghost" size="sm" icon={<Eye className="w-3.5 h-3.5" />}>View</Btn>
                        <button className="w-7 h-7 rounded flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted transition-colors">
                          <MoreHorizontal className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filtered.length === 0 && (
              <div className="text-center py-14 text-muted-foreground">
                <Users className="w-8 h-8 mx-auto mb-2 opacity-25" />
                <p className="text-sm">No customers match your search</p>
              </div>
            )}
          </div>

          <div className="px-5 py-3 border-t border-border flex items-center justify-between text-xs text-muted-foreground">
            <span>Showing {filtered.length} of {customerRows.length} customers</span>
            <span>Page 1 of 1</span>
          </div>
        </Card>
      </div>
    </div>
  );
}

// ─── Customer Workspace ───────────────────────────────────────

function CustomerWorkspaceScreen({ onNavigate }: { onNavigate: (s: Screen) => void }) {
  const [tab, setTab] = useState("documents");

  const docs = [
    { id: "D-1001", name: "Visit Note — Jan 15, 2024",     type: "ASR",    model: "Mega-ASR", confidence: 94.2, status: "review-required", date: "Jan 15, 2024" },
    { id: "D-1002", name: "Prescription Scan — Jan 12",    type: "OCR",    model: "OCR-v2",   confidence: 87.1, status: "complete",         date: "Jan 12, 2024" },
    { id: "D-1003", name: "Lab Results PDF — Jan 8",       type: "OCR",    model: "OCR-v2",   confidence: 96.3, status: "complete",         date: "Jan 8, 2024" },
    { id: "D-1004", name: "Manual Note — Follow-up",       type: "Manual", model: "—",        confidence: null, status: "complete",         date: "Jan 5, 2024" },
  ];

  const patientTasks = allTasks.filter(t => t.customer === "Sarah Chen");

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar
        title="Sarah Chen"
        subtitle="PT-001847 · DOB: March 14, 1978"
        breadcrumbs={[{ label: "Customers", onClick: () => onNavigate("customers") }, { label: "Sarah Chen" }]}
        actions={
          <>
            <Badge variant="amber">Review Required</Badge>
            <Btn variant="outline" size="sm" icon={<Download className="w-3.5 h-3.5" />}>Export</Btn>
            <Btn variant="primary" size="sm" icon={<Plus className="w-3.5 h-3.5" />} onClick={() => onNavigate("new-processing")}>New Processing</Btn>
          </>
        }
      />

      <div className="flex items-center gap-4 px-6 py-2.5 bg-amber-50 border-b border-amber-200 flex-shrink-0">
        <div className="flex items-center gap-2 text-xs text-amber-800">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span className="font-medium">1 clinical review pending</span>
          <span className="text-amber-600">· 2 critical medication discrepancies</span>
        </div>
        <Btn size="sm" variant="outline" className="border-amber-300 text-amber-800 hover:bg-amber-100 ml-auto" onClick={() => onNavigate("clinical-review")}>
          Open Clinical Review
        </Btn>
      </div>

      <div className="flex border-b border-border bg-card px-6 flex-shrink-0">
        {["Documents", "Audio", "Scans", "Analyses", "Tasks", "Activity"].map(t => (
          <button
            key={t}
            onClick={() => setTab(t.toLowerCase())}
            className={cn("px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap",
              tab === t.toLowerCase() ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {tab === "documents" && (
          <Card>
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-border">
              <span className="text-sm font-semibold text-foreground">All Documents</span>
              <Btn variant="outline" size="sm" icon={<Filter className="w-3.5 h-3.5" />}>Filter</Btn>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  {["Document", "Type", "Model", "Confidence", "Status", "Date", ""].map(h => (
                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-5 py-2.5">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {docs.map(doc => (
                  <tr key={doc.id} className="hover:bg-muted/20 transition-colors cursor-pointer group">
                    <td className="px-5 py-3.5">
                      <div className="font-medium text-foreground">{doc.name}</div>
                      <div className="text-xs text-muted-foreground font-mono">{doc.id}</div>
                    </td>
                    <td className="px-5 py-3.5"><Badge variant="outline">{doc.type}</Badge></td>
                    <td className="px-5 py-3.5 text-xs font-mono text-muted-foreground">{doc.model}</td>
                    <td className="px-5 py-3.5"><ConfidenceLabel val={doc.confidence} /></td>
                    <td className="px-5 py-3.5"><Badge variant={doc.status as BadgeVariant}>{doc.status === "review-required" ? "Review Required" : "Complete"}</Badge></td>
                    <td className="px-5 py-3.5 text-xs text-muted-foreground">{doc.date}</td>
                    <td className="px-5 py-3.5">
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                        <Btn variant="ghost" size="sm" icon={<Eye className="w-3.5 h-3.5" />}
                          onClick={() => onNavigate(doc.type === "ASR" ? "asr-review" : "ocr-review")}>
                          Review
                        </Btn>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}

        {tab === "tasks" && (
          <div className="space-y-3">
            {patientTasks.map(task => (
              <Card key={task.id} className="p-4 flex items-start gap-3">
                <div className={cn("w-1 self-stretch rounded-full flex-shrink-0",
                  task.priority === "high" ? "bg-red-500" : task.priority === "medium" ? "bg-amber-500" : "bg-emerald-500"
                )} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-foreground">{task.title}</div>
                  <div className="flex items-center gap-2 mt-1.5">
                    <span className="text-xs text-muted-foreground">Due: {task.due}</span>
                    {task.overdue && <Badge variant="red">Overdue</Badge>}
                  </div>
                </div>
                <div className="flex gap-1.5 flex-shrink-0">
                  <Btn variant="outline" size="sm">Edit</Btn>
                  <Btn variant="ghost" size="sm"><Check className="w-4 h-4" /></Btn>
                </div>
              </Card>
            ))}
          </div>
        )}

        {tab !== "documents" && tab !== "tasks" && (
          <div className="flex flex-col items-center justify-center h-40 text-muted-foreground">
            <Folder className="w-10 h-10 mb-3 opacity-20" />
            <p className="text-sm">No {tab} recorded for this patient yet</p>
            <Btn variant="outline" size="sm" className="mt-3" icon={<Plus className="w-3.5 h-3.5" />} onClick={() => onNavigate("new-processing")}>
              Add {tab.replace(/s$/, "")}
            </Btn>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── New Processing ───────────────────────────────────────────

function NewProcessingScreen({
  customerRows = [],
  onSaveManualNote,
  onProcessed,
}: {
  customerRows?: CustomerRow[];
  onSaveManualNote?: (payload: { customerId?: string; sourceName: string; text: string }) => Promise<void>;
  onProcessed?: (document: ApiDocument) => Promise<void>;
}) {
  const [mode, setMode] = useState<"record" | "upload-audio" | "scan" | "upload-pdf" | "note">("record");
  const [customer, setCustomer] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [noteTitle, setNoteTitle] = useState("Visit Note — January 15, 2024");
  const [noteText, setNoteText] = useState("Patient presents with ongoing management of Type 2 Diabetes Mellitus. HbA1c at last check was 7.2%. Current medications include Metformin 1000mg BD and Empagliflozin 10mg OD. Blood pressure 128/82 mmHg today. No new symptoms.");
  const [asrLanguage, setAsrLanguage] = useState("en");
  const [savingNote, setSavingNote] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState<"idle" | "uploading" | "transcribing" | "extracting text" | "done">("idle");
  const [aiResult, setAiResult] = useState<string>("");
  const [aiError, setAiError] = useState<string>("");
  const [audioFile, setAudioFile] = useState<File>();
  const [documentFile, setDocumentFile] = useState<File>();
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const audioInputRef = useRef<HTMLInputElement>(null);
  const documentInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder>();
  const mediaStreamRef = useRef<MediaStream>();
  const recordedChunksRef = useRef<Blob[]>([]);
  const shouldUploadRecordingRef = useRef(false);
  const selectableCustomers = useMemo(
    () => customerRows.filter(c => c.status === "active" && Boolean(c.backendId)),
    [customerRows],
  );

  useEffect(() => {
    const validSelection = selectableCustomers.some(c => c.backendId === customer);
    if (!validSelection) {
      setCustomer(selectableCustomers[0]?.backendId ?? "");
    }
  }, [customer, selectableCustomers]);

  useEffect(() => {
    if (!isRecording) return;
    const timer = window.setInterval(() => setRecordingSeconds(value => value + 1), 1000);
    return () => window.clearInterval(timer);
  }, [isRecording]);

  useEffect(() => () => {
    shouldUploadRecordingRef.current = false;
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") recorder.stop();
    mediaStreamRef.current?.getTracks().forEach(track => track.stop());
  }, []);

  const reportError = (error: unknown) => {
    const message = error instanceof Error ? error.message : String(error);
    console.error(message);
    window.alert(message);
  };

  const submitTranscription = async (selectedFile = audioFile) => {
    if (!selectedFile || processing) return;
    if (!customer) { reportError("Select a customer before starting transcription."); return; }
    setProcessing(true);
    setProcessingStage("uploading");
    try {
      setProcessingStage("transcribing");
      const document = await transcribeFile(selectedFile, customer, asrLanguage);
      setProcessingStage("done");
      await onProcessed?.(document);
    } catch (error) {
      reportError(error);
    } finally {
      setProcessing(false);
    }
  };

  const submitOcr = async () => {
    if (!documentFile || processing) return;
    if (!customer) { reportError("Select a customer before starting OCR processing."); return; }
    setProcessing(true);
    setProcessingStage("uploading");
    try {
      setProcessingStage("extracting text");
      const document = await ocrFile(documentFile, customer, "en");
      setProcessingStage("done");
      await onProcessed?.(document);
    } catch (error) {
      reportError(error);
    } finally {
      setProcessing(false);
    }
  };

  const stopRecording = (upload: boolean) => {
    shouldUploadRecordingRef.current = upload;
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") recorder.stop();
  };

  const toggleRecording = async () => {
    if (isRecording) {
      stopRecording(true);
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const preferredTypes = ["audio/webm;codecs=opus", "audio/ogg;codecs=opus", "audio/mp4"];
      const mimeType = preferredTypes.find(type => MediaRecorder.isTypeSupported(type));
      const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      recordedChunksRef.current = [];
      shouldUploadRecordingRef.current = true;
      mediaStreamRef.current = stream;
      mediaRecorderRef.current = recorder;
      setRecordingSeconds(0);
      recorder.ondataavailable = event => {
        if (event.data.size) recordedChunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        setIsRecording(false);
        stream.getTracks().forEach(track => track.stop());
        mediaStreamRef.current = undefined;
        if (!shouldUploadRecordingRef.current || !recordedChunksRef.current.length) return;
        const actualType = recorder.mimeType || "audio/webm";
        const extension = actualType.includes("ogg") ? "ogg" : actualType.includes("mp4") ? "m4a" : "webm";
        const recordedFile = new File(recordedChunksRef.current, `recording.${extension}`, { type: actualType });
        setAudioFile(recordedFile);
        await submitTranscription(recordedFile);
      };
      recorder.start();
      setIsRecording(true);
    } catch (error) {
      reportError(error);
    }
  };

  const selectMode = (nextMode: typeof mode) => {
    if (isRecording) stopRecording(false);
    setMode(nextMode);
  };

  const saveManualNote = async () => {
    if (!onSaveManualNote || savingNote) return;
    if (!customer) { reportError("Select a customer before saving this note."); return; }
    setSavingNote(true);
    try {
      await onSaveManualNote({ customerId: customer, sourceName: noteTitle, text: noteText });
    } finally {
      setSavingNote(false);
    }
  };

  const runAi = async (action: "summarize" | "key-points" | "format-note") => {
    setAiError("");
    try { setAiResult(JSON.stringify(await runAiAction(action, noteText), null, 2)); }
    catch (error) { setAiError(error instanceof Error ? error.message : "AI action failed"); }
  };

  const runClinicalCheck = async () => {
    setAiError("");
    if (!customer) { setAiError("Select a customer before running the clinical check."); return; }
    try {
      const document = await createManualDocument({ customer_id: customer, source_name: noteTitle, text: noteText });
      const result = await runClinicalReview([document.document_id]);
      setAiResult(JSON.stringify(result, null, 2));
    } catch (error) { setAiError(error instanceof Error ? error.message : "Clinical review failed"); }
  };

  const modes = [
    { id: "record",       icon: Mic,     label: "Record Audio" },
    { id: "upload-audio", icon: FileAudio, label: "Upload Audio" },
    { id: "scan",         icon: Scan,    label: "Scan Document" },
    { id: "upload-pdf",   icon: FileUp,  label: "Upload PDF" },
    { id: "note",         icon: PenLine, label: "Type Note" },
  ] as const;

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar title="New Processing" subtitle="Select a customer and processing mode" />
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl mx-auto space-y-5">
          <Card className="p-5">
            <label className="text-sm font-medium text-foreground block mb-2">Customer *</label>
            <div className="relative">
              <Users className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <select
                value={customer}
                onChange={e => setCustomer(e.target.value)}
                className="w-full pl-9 pr-8 py-2 text-sm bg-input-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring appearance-none"
              >
                {!selectableCustomers.length && <option value="" disabled>No active customers available</option>}
                {selectableCustomers.map(c => (
                  <option key={c.id} value={c.backendId ?? c.id}>{c.id} — {c.name}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
            </div>
          </Card>

          <div className="grid grid-cols-5 gap-2">
            {modes.map(({ id, icon: Icon, label }) => (
              <button
                key={id}
                onClick={() => selectMode(id)}
                className={cn(
                  "flex flex-col items-center gap-2 py-4 px-2 rounded-lg border-2 transition-all text-center",
                  mode === id
                    ? "border-primary bg-primary/5 text-primary"
                    : "border-border bg-card text-muted-foreground hover:border-primary/40 hover:text-foreground"
                )}
              >
                <Icon className="w-5 h-5" />
                <span className="text-xs font-medium leading-tight">{label}</span>
              </button>
            ))}
          </div>

          <Card className="p-6">
            {mode === "record" && (
              <div className="text-center space-y-4">
                <div className={cn(
                  "w-20 h-20 rounded-full flex items-center justify-center mx-auto transition-all duration-300",
                  isRecording ? "bg-red-100 ring-4 ring-red-200 ring-offset-2" : "bg-primary/10"
                )}>
                  <Mic className={cn("w-8 h-8", isRecording ? "text-red-600" : "text-primary")} />
                </div>
                {isRecording && (
                  <div className="space-y-1">
                    <div className="text-3xl font-mono font-semibold text-red-600">
                      {String(Math.floor(recordingSeconds / 60)).padStart(2, "0")}:{String(recordingSeconds % 60).padStart(2, "0")}
                    </div>
                    <div className="flex justify-center gap-px h-8 items-center">
                      {Array.from({ length: 20 }, (_, i) => (
                        <div key={i} className="w-1 bg-red-400 rounded-full animate-pulse"
                          style={{ height: `${12 + Math.abs(Math.sin(i * 0.8)) * 12}px`, animationDelay: `${i * 50}ms` }} />
                      ))}
                    </div>
                  </div>
                )}
                <p className="text-sm text-muted-foreground">
                  {isRecording ? "Recording in progress — speak clearly into microphone" : "Click to begin recording"}
                </p>
                <Btn
                  variant={isRecording ? "danger" : "primary"}
                  size="lg"
                  icon={isRecording ? <XCircle className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                  onClick={toggleRecording}
                  className="justify-center"
                >
                  {isRecording ? "Stop Recording" : "Start Recording"}
                </Btn>
                <div className="flex items-center justify-center gap-3 text-sm">
                  <label className="text-muted-foreground">ASR Model</label>
                  <select className="text-sm bg-input-background border border-border rounded px-2.5 py-1 focus:outline-none focus:ring-2 focus:ring-ring">
                    <option>Mega-ASR v2.4</option>
                    <option>Qwen3-ASR v3.1</option>
                  </select>
                </div>
              </div>
            )}

            {mode === "upload-audio" && (
              <div className="space-y-4">
                <input
                  ref={audioInputRef}
                  type="file"
                  accept=".wav,.mp3,.m4a,.flac,.ogg,.webm,audio/*"
                  className="hidden"
                  onChange={event => setAudioFile(event.target.files?.[0])}
                />
                <div
                  className="border-2 border-dashed border-border rounded-lg p-10 text-center hover:border-primary/50 transition-colors cursor-pointer"
                  onDragOver={event => event.preventDefault()}
                  onDrop={event => {
                    event.preventDefault();
                    setAudioFile(event.dataTransfer.files[0]);
                  }}
                >
                  <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm font-medium text-foreground">Drop audio file here</p>
                  <p className="text-xs text-muted-foreground mt-1">MP3, WAV, M4A, OGG · up to 100 MB</p>
                  <Btn variant="outline" size="sm" className="mt-3" onClick={() => audioInputRef.current?.click()}>Browse Files</Btn>
                </div>
                {[
                  { label: "ASR Model",  type: "select", opts: ["Mega-ASR v2.4", "Qwen3-ASR v3.1"] },
                  { label: "Language",   type: "select", opts: ["English (en-AU)", "English (en-US)", "Mandarin (zh-CN)"] },
                ].map(f => (
                  <div key={f.label} className="flex items-center gap-4">
                    <label className="text-sm text-muted-foreground w-32 flex-shrink-0">{f.label}</label>
                    <select
                      value={f.label === "Language" ? asrLanguage : undefined}
                      onChange={f.label === "Language" ? event => setAsrLanguage(event.target.value) : undefined}
                      className="flex-1 text-sm bg-input-background border border-border rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-ring"
                    >
                      {f.opts.map(o => {
                        const value = o.includes("Mandarin") ? "zh-CN" : o.includes("en-US") ? "en-US" : "en";
                        return <option key={o} value={f.label === "Language" ? value : o}>{o}</option>;
                      })}
                    </select>
                  </div>
                ))}
                <Btn variant="primary" size="lg" className="w-full justify-center" onClick={() => submitTranscription()} disabled={!audioFile || processing}>Start Transcription</Btn>
              </div>
            )}

            {(mode === "scan" || mode === "upload-pdf") && (
              <div className="space-y-4">
                <input
                  ref={documentInputRef}
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg,.webp,.tif,.tiff,image/*"
                  className="hidden"
                  onChange={event => setDocumentFile(event.target.files?.[0])}
                />
                <input
                  ref={cameraInputRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  className="hidden"
                  onChange={event => setDocumentFile(event.target.files?.[0])}
                />
                <div
                  className="border-2 border-dashed border-border rounded-lg p-10 text-center hover:border-primary/50 transition-colors cursor-pointer"
                  onDragOver={event => event.preventDefault()}
                  onDrop={event => {
                    event.preventDefault();
                    setDocumentFile(event.dataTransfer.files[0]);
                  }}
                >
                  {mode === "scan" ? <Scan className="w-8 h-8 text-muted-foreground mx-auto mb-2" /> : <FileUp className="w-8 h-8 text-muted-foreground mx-auto mb-2" />}
                  <p className="text-sm font-medium text-foreground">
                    {mode === "scan" ? "Capture via scanner or camera" : "Drop PDF or image here"}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {mode === "scan" ? "Use connected scanner device" : "PDF, PNG, JPG, TIFF · up to 50 MB"}
                  </p>
                  <div className="flex gap-2 justify-center mt-3">
                    {mode === "scan" && <Btn variant="primary" size="sm" icon={<Scan className="w-3.5 h-3.5" />} onClick={() => cameraInputRef.current?.click()}>Open Scanner</Btn>}
                    <Btn variant="outline" size="sm" onClick={() => documentInputRef.current?.click()}>Browse Files</Btn>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <label className="text-sm text-muted-foreground w-32 flex-shrink-0">OCR Engine</label>
                  <select className="flex-1 text-sm bg-input-background border border-border rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-ring">
                    <option>OCR-v2 (Recommended)</option>
                    <option>OCR-v1 (Legacy)</option>
                  </select>
                </div>
                <div className="flex items-center gap-4">
                  <label className="text-sm text-muted-foreground w-32 flex-shrink-0">Extract Fields</label>
                  <div className="flex gap-4">
                    {["Medications", "Dates", "Dosages", "Lab Values"].map(f => (
                      <label key={f} className="flex items-center gap-1.5 text-sm text-foreground cursor-pointer">
                        <input type="checkbox" defaultChecked={f !== "Lab Values"} className="rounded" />{f}
                      </label>
                    ))}
                  </div>
                </div>
                <Btn variant="primary" size="lg" className="w-full justify-center" onClick={submitOcr} disabled={!documentFile || processing}>Start OCR Processing</Btn>
              </div>
            )}

            {mode === "note" && (
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-foreground block mb-1.5">Note Title</label>
                  <input
                    type="text"
                    value={noteTitle}
                    onChange={e => setNoteTitle(e.target.value)}
                    className="w-full px-3 py-2 text-sm bg-input-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-foreground block mb-1.5">Content</label>
                  <textarea
                    rows={8}
                    value={noteText}
                    onChange={e => setNoteText(e.target.value)}
                    className="w-full px-3 py-2 text-sm bg-input-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring resize-none leading-relaxed"
                  />
                </div>
                <div className="flex gap-3">
                  <Btn variant="primary" icon={<Check className="w-4 h-4" />} onClick={saveManualNote} disabled={savingNote}>Save Note</Btn>
                  <Btn variant="outline" icon={<Stethoscope className="w-4 h-4" />} onClick={runClinicalCheck}>Run Clinical Check</Btn>
                </div>
                <div className="flex flex-wrap gap-2 pt-2">
                  {(["summarize", "key-points", "format-note"] as const).map(action => <Btn key={action} variant="ghost" size="sm" onClick={() => runAi(action)}>{action}</Btn>)}
                </div>
                {(aiResult || aiError) && <pre className={cn("text-xs whitespace-pre-wrap rounded border p-3", aiError ? "text-red-700 border-red-200 bg-red-50" : "text-foreground bg-muted/30")}>{aiError || aiResult}</pre>}
              </div>
            )}
            {processing && <div className="mt-4 text-sm text-primary">{processingStage}...</div>}
          </Card>
        </div>
      </div>
    </div>
  );
}

// ─── ASR Review ───────────────────────────────────────────────

function ASRReviewScreen({ documentId, onNavigate }: { documentId?: string; onNavigate: (s: Screen) => void }) {
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0.35);
  const [editMode, setEditMode] = useState(false);
  const [document, setDocument] = useState<ApiDocument | null>(null);
  useEffect(() => { if (documentId) getDocument(documentId).then(setDocument).catch(() => setDocument(null)); }, [documentId]);

  const sampleTranscript = [
    "Patient presents with ongoing management of Type 2 Diabetes Mellitus. HbA1c at last check was 7.2%, which represents a slight improvement from the previous 7.6% recorded in October. Current medications include Metformin one thousand milligrams twice daily and Empagliflozin ten milligrams once daily.",
    "Blood pressure today is 128 over 82 millimetres of mercury — within acceptable range. Patient reports no episodes of hypoglycaemia in the past month. Weight stable at 84 kilograms. No new symptoms reported.",
    "Plan: Continue current regimen. Repeat HbA1c in three months. Refer to dietitian for further dietary counselling. Patient education regarding foot care provided.",
  ];

  const sampleTimestamps = [
    { time: "0:00", text: "Patient presents with ongoing management...", warn: false },
    { time: "0:12", text: "HbA1c at last check was 7.2%...",            warn: false },
    { time: "0:28", text: "Current medications include Metformin...",    warn: true  },
    { time: "0:44", text: "Blood pressure today is 128 over 82...",      warn: true  },
    { time: "1:02", text: "Plan: Continue current regimen...",           warn: false },
  ];
  const transcript = document?.text ? document.text.split(/\n+/).filter(Boolean) : [];
  const timestamps = (document?.segments ?? []).map(segment => ({ time: `${Math.floor(segment.start / 60)}:${String(Math.floor(segment.start % 60)).padStart(2, "0")}`, text: segment.text, warn: (segment.confidence ?? 1) < 0.8 }));
  const acceptTranscript = async () => { if (documentId) await finalizeDocument(documentId); };

  const elapsed = Math.floor(progress * 82);

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar
        title="ASR Review"
        subtitle="Visit Note — Jan 15, 2024 · Mega-ASR v2.4 · 94.2% confidence"
        breadcrumbs={[
          { label: "Customers", onClick: () => onNavigate("customers") },
          { label: "Sarah Chen", onClick: () => onNavigate("customer-workspace") },
          { label: "ASR Review" }
        ]}
        actions={
          <>
            <Btn variant="outline" size="sm" icon={<GitCompare className="w-3.5 h-3.5" />} onClick={() => onNavigate("compare")}>Compare</Btn>
            <Btn variant="outline" size="sm" icon={<Stethoscope className="w-3.5 h-3.5" />} onClick={() => onNavigate("clinical-review")}>Clinical Review</Btn>
            <Btn variant="primary" size="sm" icon={<Download className="w-3.5 h-3.5" />}>Export</Btn>
          </>
        }
      />

      <div className="flex-1 overflow-hidden flex">
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          <div className="flex items-start gap-3 p-3.5 bg-amber-50 border border-amber-200 rounded-lg">
            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-amber-800">
              <span className="font-medium">2 low-confidence segments</span> at 0:28 and 0:44 — review recommended before accepting.
            </p>
          </div>

          <Card className="p-5">
            <div className="flex items-center gap-3 mb-4">
              <button
                onClick={() => setPlaying(v => !v)}
                className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white hover:bg-primary/90 transition-colors flex-shrink-0"
              >
                {playing ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
              </button>
              <div className="flex-1">
                <WaveformViz progress={progress} onSeek={setProgress} />
              </div>
              <span className="text-xs font-mono text-muted-foreground w-20 text-right">
                {Math.floor(elapsed / 60)}:{String(elapsed % 60).padStart(2, "0")} / 1:22
              </span>
            </div>
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span className="font-mono">audio_recording_2024-01-15.wav · 1:22 · 48 kHz · Stereo</span>
              <div className="flex items-center gap-3">
                <span className="font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded border border-emerald-200">94.2% confidence</span>
                <span>Mega-ASR v2.4</span>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between px-5 py-3.5 border-b border-border">
              <h3 className="text-sm font-semibold text-foreground">Transcript</h3>
              <div className="flex gap-2">
                <Btn variant={editMode ? "primary" : "outline"} size="sm" icon={<Edit2 className="w-3.5 h-3.5" />} onClick={() => setEditMode(v => !v)}>
                  {editMode ? "Done Editing" : "Edit"}
                </Btn>
              </div>
            </div>
            <div className="p-5">
              {editMode ? (
                <textarea
                  className="w-full min-h-[200px] text-sm text-foreground bg-input-background border border-border rounded-md p-4 focus:outline-none focus:ring-2 focus:ring-ring resize-none leading-relaxed font-mono"
                  defaultValue={transcript.join("\n\n")}
                />
              ) : (
                <div className="space-y-4">
                  {transcript.map((para, i) => (
                    <p key={i} className="text-sm text-foreground leading-relaxed">{para}</p>
                  ))}
                </div>
              )}
            </div>
            <div className="flex items-center justify-between px-5 py-3 border-t border-border bg-muted/20">
              <span className="text-xs text-muted-foreground">127 words · Source: ASR · Not yet verified</span>
              <Btn variant="primary" size="sm" icon={<Check className="w-3.5 h-3.5" />} onClick={acceptTranscript}>Accept Transcript</Btn>
            </div>
          </Card>
        </div>

        <div className="w-60 border-l border-border bg-card flex-shrink-0 overflow-y-auto">
          <div className="px-4 py-3.5 border-b border-border">
            <h3 className="text-sm font-semibold text-foreground">Timestamps</h3>
            <p className="text-xs text-muted-foreground mt-0.5">Click to seek</p>
          </div>
          <div className="divide-y divide-border">
            {timestamps.map((t, i) => (
              <button
                key={i}
                onClick={() => setProgress((i / timestamps.length) * 0.85)}
                className="w-full text-left px-4 py-3 hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-xs font-mono text-primary font-medium">{t.time}</span>
                  {t.warn && <AlertTriangle className="w-3 h-3 text-amber-500" />}
                </div>
                <p className="text-xs text-muted-foreground truncate">{t.text}</p>
              </button>
            ))}
          </div>

          <div className="px-4 py-4 border-t border-border space-y-3">
            <h4 className="text-xs font-semibold text-foreground uppercase tracking-wide">Export As</h4>
            {["Plain Text (.txt)", "Word Document (.docx)", "JSON with timestamps", "CSV"].map(fmt => (
              <button key={fmt} className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors w-full">
                <Download className="w-3 h-3" />{fmt}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── OCR Review ───────────────────────────────────────────────

function OCRReviewScreen({ documentId, onNavigate }: { documentId?: string; onNavigate: (s: Screen) => void }) {
  const [page, setPage] = useState(0);
  const [editMode, setEditMode] = useState(false);
  const [document, setDocument] = useState<ApiDocument | null>(null);
  const [editedText, setEditedText] = useState("");
  const [imageUrls, setImageUrls] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(Boolean(documentId));
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setPage(0);
    setDocument(null);
    setImageUrls({});
    setEditedText("");
    setError("");
    setMessage("");
    if (!documentId) {
      setLoading(false);
      setError("No OCR document was selected.");
      return () => { cancelled = true; };
    }
    setLoading(true);
    getDocument(documentId)
      .then(value => {
        if (cancelled) return;
        setDocument(value);
        setEditedText(value.corrected_text ?? value.text ?? "");
      })
      .catch(reason => {
        if (!cancelled) setError(reason instanceof Error ? reason.message : "Unable to load the OCR document.");
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [documentId]);

  useEffect(() => {
    let cancelled = false;
    const urls: string[] = [];
    const pages = document?.pages ?? [];
    if (!pages.length || !document) return () => { cancelled = true; };
    Promise.all(pages.map(async currentPage => {
      try {
        const url = await getDocumentPageImage(document.document_id, currentPage.page_number);
        urls.push(url);
        return [currentPage.id, url] as const;
      } catch {
        return null;
      }
    })).then(entries => {
      if (cancelled) return;
      setImageUrls(Object.fromEntries(entries.filter((entry): entry is readonly [string, string] => Boolean(entry))));
    });
    return () => {
      cancelled = true;
      urls.forEach(url => URL.revokeObjectURL(url));
    };
  }, [document]);

  const pages = document?.pages ?? [];
  const currentPage = pages[page] ?? pages[0];
  const blocks = currentPage?.blocks ?? [];
  const rawText = document?.corrected_text ?? document?.text ?? "";
  const sourceLabel = document?.original_filename ?? document?.source_name ?? "OCR document";
  const metadata = document?.metadata ?? {};
  const modelLabel = typeof metadata.ocr_engine === "string" ? metadata.ocr_engine : "OCR";
  const pageConfidence = currentPage?.average_confidence ?? document?.average_confidence;
  const confidencePercent = (value?: number | null) => value == null ? null : (value <= 1 ? value * 100 : value);
  const formatConfidence = (value?: number | null) => {
    const percent = confidencePercent(value);
    return percent == null ? "—" : `${percent.toFixed(1)}%`;
  };
  const fields = blocks.map((block, index) => ({
    label: block.region_type || `Block ${index + 1}`,
    value: block.corrected_text ?? block.text,
    conf: confidencePercent(block.confidence ?? pageConfidence ?? document?.average_confidence),
  }));

  const handleEditToggle = async () => {
    if (!document) return;
    if (!editMode) {
      setEditedText(document.corrected_text ?? document.text ?? "");
      setError("");
      setEditMode(true);
      return;
    }
    setSaving(true);
    setError("");
    try {
      const updated = await updateDocumentText(document.document_id, editedText);
      setDocument(updated);
      setEditedText(updated.corrected_text ?? updated.text ?? "");
      setEditMode(false);
      setMessage("OCR text saved.");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to save OCR text.");
    } finally {
      setSaving(false);
    }
  };

  const acceptOcr = async () => {
    if (!document) return;
    try {
      const updated = await finalizeDocument(document.document_id);
      setDocument(updated);
      setMessage("OCR output accepted.");
      setError("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to accept OCR output.");
    }
  };

  if (!document && !loading) {
    return (
      <div className="flex flex-col h-full overflow-hidden">
        <TopBar title="OCR Review" subtitle="Document unavailable" breadcrumbs={[{ label: "OCR Review" }]} />
        <div className="flex-1 flex items-center justify-center p-6">
          <Card className="p-5 max-w-lg w-full"><p className="text-sm text-red-700">{error || "Unable to load the selected OCR document."}</p></Card>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar
        title="OCR Review"
        subtitle={loading ? "Loading OCR document…" : `${sourceLabel} · ${modelLabel} · ${formatConfidence(document?.average_confidence)} avg confidence`}
        breadcrumbs={[
          { label: "Customers", onClick: () => onNavigate("customers") },
          { label: document?.customer_id ?? "Unassigned", onClick: () => onNavigate("customer-workspace") },
          { label: "OCR Review" }
        ]}
        actions={
          <>
            <Btn variant="outline" size="sm" icon={<GitCompare className="w-3.5 h-3.5" />} onClick={() => onNavigate("compare")}>Compare</Btn>
            <Btn variant="primary" size="sm" icon={<Download className="w-3.5 h-3.5" />}>Export</Btn>
          </>
        }
      />

      <div className="flex-1 overflow-hidden flex">
        {/* Thumbnails */}
        <div className="w-20 border-r border-border bg-muted/20 flex flex-col items-center py-3 gap-2 flex-shrink-0 overflow-y-auto">
          {pages.map((thumbnailPage, i) => (
            <button
              key={thumbnailPage.id}
              onClick={() => setPage(i)}
              className={cn("w-14 h-20 rounded border-2 bg-white flex items-center justify-center transition-all",
                page === i ? "border-primary shadow-sm" : "border-border hover:border-primary/40"
              )}
            >
              {imageUrls[thumbnailPage.id]
                ? <img src={imageUrls[thumbnailPage.id]} alt={`Page ${thumbnailPage.page_number}`} className="w-10 h-14 object-contain" />
                : <div className="w-10 h-14 bg-muted/60 rounded p-1 overflow-hidden text-[4px] leading-tight text-muted-foreground">{thumbnailPage.blocks.slice(0, 8).map(block => block.text).join(" ")}</div>}
            </button>
          ))}
          <div className="text-xs text-muted-foreground mt-1">Pg {pages.length ? page + 1 : "—"}/{pages.length || "—"}</div>
        </div>

        {/* Document Preview */}
        <div className="flex-1 bg-muted/20 flex items-center justify-center p-6 overflow-hidden">
          <div className="w-full max-w-xs bg-white border border-border rounded-lg shadow-sm overflow-hidden flex flex-col" style={{ maxHeight: "420px" }}>
            <div className="flex items-center justify-between px-3 py-2 bg-muted/30 border-b border-border">
              <span className="text-xs text-muted-foreground font-mono">Page {currentPage?.page_number ?? "—"}</span>
              <Badge variant="blue">{formatConfidence(pageConfidence)} avg</Badge>
            </div>
            <div className="flex-1 overflow-y-auto p-5">
              {currentPage && imageUrls[currentPage.id] ? (
                <div className="relative w-full bg-white" style={{ aspectRatio: `${currentPage.width} / ${currentPage.height}` }}>
                  <img src={imageUrls[currentPage.id]} alt={`${sourceLabel}, page ${currentPage.page_number}`} className="absolute inset-0 w-full h-full object-contain" />
                  {blocks.map(block => {
                    const [x1, y1, x2, y2] = block.bounding_box;
                    return <span key={block.id} title={block.text} className="absolute border border-primary/60 bg-primary/10 pointer-events-none" style={{ left: `${(x1 / currentPage.width) * 100}%`, top: `${(y1 / currentPage.height) * 100}%`, width: `${((x2 - x1) / currentPage.width) * 100}%`, height: `${((y2 - y1) / currentPage.height) * 100}%` }} />;
                  })}
                </div>
              ) : (
                <div className="text-xs font-mono text-gray-700 space-y-1.5 leading-relaxed">
                  {blocks.length ? blocks.map(block => <div key={block.id}>{block.corrected_text ?? block.text}</div>) : <div className="text-muted-foreground">No OCR page image or blocks were returned.</div>}
                </div>
              )}
            </div>
            <div className="py-2 border-t border-border bg-muted/20 text-xs text-center text-muted-foreground">
              {blocks.length ? "Bounding boxes shown from OCR blocks" : "No OCR blocks returned for this page"}
            </div>
          </div>
        </div>

        {/* Right Panel */}
        <div className="w-80 border-l border-border bg-card flex-shrink-0 overflow-y-auto">
          <div className="px-4 py-3.5 border-b border-border flex items-center justify-between">
            <h3 className="text-sm font-semibold text-foreground">Extracted Text</h3>
            <Btn variant={editMode ? "primary" : "outline"} size="sm" icon={<Edit2 className="w-3 h-3" />} onClick={handleEditToggle}>
              {saving ? "Saving…" : editMode ? "Done" : "Edit"}
            </Btn>
          </div>
          <div className="p-4 border-b border-border">
            {editMode
              ? <textarea className="w-full text-xs font-mono bg-input-background border border-border rounded p-3 min-h-[160px] focus:outline-none focus:ring-2 focus:ring-ring resize-none" value={editedText} onChange={event => setEditedText(event.target.value)} />
              : <pre className="text-xs font-mono text-foreground whitespace-pre-wrap leading-relaxed">{rawText}</pre>
            }
          </div>

          <div className="px-4 py-3 border-b border-border">
            <h3 className="text-sm font-semibold text-foreground">Structured Fields</h3>
          </div>
          <div className="divide-y divide-border">
            {fields.length ? fields.map((f, index) => (
              <div key={`${f.label}-${index}`} className="px-4 py-2.5 hover:bg-muted/20 transition-colors">
                <div className="text-xs text-muted-foreground mb-0.5">{f.label}</div>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-medium text-foreground flex-1">{f.value}</span>
                  <span className={cn("text-xs font-mono flex-shrink-0",
                    (f.conf ?? 0) >= 95 ? "text-emerald-700" : (f.conf ?? 0) >= 85 ? "text-amber-700" : "text-red-700"
                  )}>{f.conf == null ? "—" : `${f.conf.toFixed(1)}%`}</span>
                </div>
              </div>
            )) : <div className="px-4 py-3 text-xs text-muted-foreground">No OCR blocks returned for this page.</div>}
          </div>
          <div className="p-4 border-t border-border">
            {(error || message) && <p className={cn("text-xs mb-3", error ? "text-red-700" : "text-emerald-700")}>{error || message}</p>}
            <Btn variant="primary" size="sm" className="w-full justify-center" icon={<Check className="w-3.5 h-3.5" />} onClick={acceptOcr}>Accept OCR Output</Btn>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Compare ──────────────────────────────────────────────────

function CompareScreen({ documentIds = [], onNavigate }: { documentIds?: string[]; onNavigate: (s: Screen) => void }) {
  const [view, setView] = useState<"side" | "inline">("side");
  const [actions, setActions] = useState<Record<number, "asr" | "ocr" | "flagged">>({});
  const [comparison, setComparison] = useState<Awaited<ReturnType<typeof compareDocuments>> | null>(null);
  const [compareError, setCompareError] = useState("");
  const runComparison = async () => {
    if (documentIds.length < 2) { setCompareError("Select two persisted documents to compare."); return; }
    try { setCompareError(""); setComparison(await compareDocuments(documentIds.slice(0, 2))); }
    catch (error) { setCompareError(error instanceof Error ? error.message : "Comparison failed"); }
  };

  const mismatches = [
    { id: 0, severity: "red",   category: "Dosage",     label: "Metformin dose",     asr: "1000mg twice daily",   ocr: "100mg twice daily" },
    { id: 1, severity: "red",   category: "Medication", label: "Empagliflozin",       asr: "10mg once daily",      ocr: "Not present" },
    { id: 2, severity: "amber", category: "Date",       label: "HbA1c measurement",  asr: "October 2023",         ocr: "Not referenced" },
    { id: 3, severity: "blue",  category: "Format",     label: "HbA1c abbreviation", asr: "haemoglobin A1c 7.2%", ocr: "HbA1c 7.2%" },
  ];

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar
        title="ASR vs OCR Comparison"
        subtitle="Sarah Chen · Visit Note (ASR) vs Prescription Scan (OCR)"
        actions={
          <>
            <div className="flex items-center gap-1 bg-muted rounded-md p-1">
              {(["side", "inline"] as const).map(v => (
                <button key={v} onClick={() => setView(v)} className={cn("px-3 py-1 text-xs rounded font-medium transition-colors", view === v ? "bg-card shadow-sm text-foreground" : "text-muted-foreground")}>
                  {v === "side" ? "Side by Side" : "Inline Diff"}
                </button>
              ))}
            </div>
            <Btn variant="primary" size="sm" icon={<Download className="w-3.5 h-3.5" />} onClick={runComparison}>Run Comparison</Btn>
          </>
        }
      />
      <div className="flex-1 overflow-y-auto p-6 space-y-5">
        {(comparison || compareError) && <Card className="p-4"><p className={compareError ? "text-sm text-red-700" : "text-sm text-foreground"}>{compareError || `WER ${(comparison?.wer ?? 0) * 100}% · CER ${(comparison?.cer ?? 0) * 100}% · ${comparison?.mismatches.length ?? 0} mismatches`}</p></Card>}
        <div className="grid grid-cols-4 gap-4">
          {[
            { label: "Word Error Rate",     val: "4.2%",  color: "text-amber-700" },
            { label: "Char Error Rate",     val: "2.1%",  color: "text-amber-700" },
            { label: "Critical Mismatches", val: "2",     color: "text-red-700" },
            { label: "ASR Word Count",      val: "127",   color: "text-foreground" },
          ].map(m => (
            <Card key={m.label} className="p-4 text-center">
              <div className={cn("text-2xl font-mono font-semibold", m.color)}>{m.val}</div>
              <div className="text-xs text-muted-foreground mt-1">{m.label}</div>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-4">
          {[
            {
              label: "ASR Transcript", badge: "Mega-ASR v2.4", header: "bg-blue-50 border-blue-100",
              segments: [
                { text: "Patient presents with ongoing management of Type 2 Diabetes Mellitus. HbA1c 7.2% — improved from 7.6% in October.", hl: false },
                { text: "Medications: Metformin 1000mg twice daily and Empagliflozin 10mg once daily.", hl: true },
                { text: "BP 128/82 mmHg. No hypoglycaemic episodes. Weight stable at 84 kg.", hl: false },
              ]
            },
            {
              label: "OCR Extracted", badge: "OCR-v2", header: "bg-teal-50 border-teal-100",
              segments: [
                { text: "Patient: Sarah Chen. DOB: 14/03/1978. Prescription date: 12/01/2024.", hl: false },
                { text: "Medication: Metformin Hydrochloride 100mg — one tablet twice daily with meals.", hl: true },
                { text: "Quantity: 60 tablets. Repeats: 5. Prescriber: Dr. A. Kumar, Provider 1234567A.", hl: false },
              ]
            },
          ].map((panel, pi) => (
            <Card key={pi} className="overflow-hidden">
              <div className={cn("flex items-center justify-between px-4 py-3 border-b", panel.header)}>
                <span className="text-sm font-semibold text-foreground">{panel.label}</span>
                <Badge variant={pi === 0 ? "blue" : "teal"}>{panel.badge}</Badge>
              </div>
              <div className="p-4 space-y-3">
                {panel.segments.map((seg, si) => (
                  <p key={si} className={cn("text-sm leading-relaxed rounded p-2",
                    seg.hl ? pi === 0 ? "bg-amber-50 border border-amber-200" : "bg-red-50 border border-red-200" : ""
                  )}>
                    {seg.text}
                  </p>
                ))}
              </div>
            </Card>
          ))}
        </div>

        <Card>
          <div className="px-5 py-3.5 border-b border-border">
            <h3 className="text-sm font-semibold text-foreground">Detected Mismatches</h3>
            <p className="text-xs text-muted-foreground mt-0.5">Numerical, medication, unit, and date discrepancies</p>
          </div>
          <div className="divide-y divide-border">
            {mismatches.map(m => (
              <div key={m.id} className="px-5 py-4 flex items-start gap-4">
                <div className={cn("w-2 h-2 rounded-full mt-1.5 flex-shrink-0",
                  m.severity === "red" ? "bg-red-500" : m.severity === "amber" ? "bg-amber-500" : "bg-blue-400"
                )} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant={m.severity as BadgeVariant}>{m.category}</Badge>
                    <span className="text-sm font-medium text-foreground">{m.label}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs flex-wrap">
                    <span className="text-muted-foreground">ASR:</span>
                    <span className="font-mono bg-blue-50 text-blue-800 px-1.5 py-0.5 rounded">{m.asr}</span>
                    <span className="text-muted-foreground">OCR:</span>
                    <span className={cn("font-mono px-1.5 py-0.5 rounded", m.ocr === "Not present" ? "bg-slate-100 text-slate-600" : "bg-red-50 text-red-800")}>{m.ocr}</span>
                  </div>
                </div>
                <div className="flex gap-1.5 flex-shrink-0">
                  {actions[m.id] ? (
                    <Badge variant="green">
                      {actions[m.id] === "asr" ? "Using ASR" : actions[m.id] === "ocr" ? "Using OCR" : "Flagged"}
                    </Badge>
                  ) : (
                    <>
                      <Btn variant="outline" size="sm" onClick={() => setActions(a => ({ ...a, [m.id]: "asr" }))}>Use ASR</Btn>
                      <Btn variant="outline" size="sm" onClick={() => setActions(a => ({ ...a, [m.id]: "ocr" }))}>Use OCR</Btn>
                      <Btn variant="ghost"   size="sm" onClick={() => setActions(a => ({ ...a, [m.id]: "flagged" }))}>Flag</Btn>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div className="px-5 py-3.5 border-t border-border flex items-center justify-between">
            <span className="text-xs text-muted-foreground">{Object.keys(actions).length} of {mismatches.length} resolved</span>
            <Btn variant="primary" size="sm" icon={<Stethoscope className="w-3.5 h-3.5" />} onClick={() => onNavigate("clinical-review")}>
              Proceed to Clinical Review
            </Btn>
          </div>
        </Card>
      </div>
    </div>
  );
}

// ─── Clinical Review ──────────────────────────────────────────

function ClinicalReviewScreen({ documentIds = [], onNavigate }: { documentIds?: string[]; onNavigate: (s: Screen) => void }) {
  const [resolved, setResolved] = useState<Set<number>>(new Set());
  const [backendResult, setBackendResult] = useState<{ risk_level: string; risk_score: number; summary: string } | null>(null);
  const [reviewError, setReviewError] = useState("");
  const executeReview = async () => {
    if (!documentIds.length) { setReviewError("Open a document before running clinical review."); return; }
    try { setReviewError(""); setBackendResult(await runClinicalReview(documentIds)); }
    catch (error) { setReviewError(error instanceof Error ? error.message : "Clinical review failed"); }
  };

  const issues = [
    {
      id: 0, risk: "red" as const, category: "Medication Discrepancy",
      title: "Metformin dosage mismatch — 10× difference",
      detail: "ASR records Metformin 1000mg twice daily. The scanned prescription shows 100mg — a tenfold discrepancy. This may be a transcription error or a genuine script mismatch. Do not accept either source until confirmed with prescriber or pharmacy records.",
      evidence: ["ASR Transcript — Jan 15, 2024", "Prescription Scan — Jan 12, 2024"],
      actions: ["Accept ASR (1000mg)", "Accept OCR (100mg)", "Flag — prescriber confirmation required"],
    },
    {
      id: 1, risk: "red" as const, category: "Missing Prescription",
      title: "Empagliflozin not documented",
      detail: "Patient verbally reports taking Empagliflozin 10mg OD (confirmed in ASR transcript). This medication does not appear in the scanned prescription. May indicate an unscanned, telephoned, or expired script. Verification required.",
      evidence: ["ASR Transcript — Jan 15, 2024"],
      actions: ["Request updated prescription", "Mark pending — patient self-reported", "Ignore — verbal confirmation sufficient"],
    },
    {
      id: 2, risk: "amber" as const, category: "Contradiction",
      title: "HbA1c date inconsistency across records",
      detail: "ASR references an October HbA1c of 7.6%. A manual note from November 2023 records a baseline of 8.1%. These conflict and should be reconciled before the January trend assessment is accepted.",
      evidence: ["ASR Transcript — Jan 15, 2024", "Manual Note — Nov 14, 2023"],
      actions: ["Accept October value (ASR)", "Accept November value (manual note)", "Mark unclear — flag for clinician review"],
    },
  ];

  const unresolvedCritical = issues.filter(i => i.risk === "red" && !resolved.has(i.id)).length;
  const riskLevel = unresolvedCritical > 0 ? "red" : resolved.size === issues.length ? "green" : "amber";

  const riskCfg = {
    green: { label: "Low Risk — Ready to Accept",      bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-800", Icon: CheckCircle },
    amber: { label: "Review Required — Issues Pending", bg: "bg-amber-50",   border: "border-amber-200",   text: "text-amber-800",   Icon: AlertTriangle },
    red:   { label: "High Risk — Do Not Accept",        bg: "bg-red-50",     border: "border-red-200",     text: "text-red-800",     Icon: XCircle },
  };
  const cfg = riskCfg[riskLevel];

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar
        title="Clinical Review"
        subtitle="Sarah Chen · PT-001847 · Ollama / llama3:8b"
        breadcrumbs={[
          { label: "Customers", onClick: () => onNavigate("customers") },
          { label: "Sarah Chen", onClick: () => onNavigate("customer-workspace") },
          { label: "Clinical Review" }
        ]}
        actions={
          <>
            <Btn variant="outline" size="sm" icon={<Download className="w-3.5 h-3.5" />} onClick={executeReview}>Run Clinical Check</Btn>
            <Btn variant="primary" size="sm" icon={<Check className="w-3.5 h-3.5" />} disabled={unresolvedCritical > 0}>
              {unresolvedCritical > 0 ? `${unresolvedCritical} critical unresolved` : "Accept with Caveats"}
            </Btn>
          </>
        }
      />
      <div className="flex-1 overflow-y-auto p-6 space-y-5">
        {(backendResult || reviewError) && <Card className="p-4"><p className={reviewError ? "text-sm text-red-700" : "text-sm text-foreground"}>{reviewError || `${backendResult?.risk_level} risk (${backendResult?.risk_score}): ${backendResult?.summary}`}</p></Card>}
        <div className={cn("flex items-center gap-4 p-4 rounded-lg border-2", cfg.bg, cfg.border)}>
          <cfg.Icon className={cn("w-6 h-6 flex-shrink-0", cfg.text)} />
          <div className="flex-1">
            <div className={cn("text-base font-semibold", cfg.text)}>{cfg.label}</div>
            <div className={cn("text-sm mt-0.5 opacity-80", cfg.text)}>
              {issues.filter(i => !resolved.has(i.id)).length} unresolved · {unresolvedCritical} critical · {issues.filter(i => i.risk === "amber" && !resolved.has(i.id)).length} warning
            </div>
          </div>
          <Badge variant={riskLevel === "red" ? "red" : riskLevel === "amber" ? "amber" : "green"}>
            {riskLevel.toUpperCase()}
          </Badge>
        </div>

        <div className="space-y-3">
          {issues.map(issue => {
            const isRes = resolved.has(issue.id);
            return (
              <Card key={issue.id} className={cn("overflow-hidden transition-opacity", isRes && "opacity-60")}>
                <div className={cn("flex items-center gap-3 px-5 py-3 border-b border-border",
                  issue.risk === "red" ? "bg-red-50" : "bg-amber-50"
                )}>
                  <div className={cn("w-2 h-2 rounded-full flex-shrink-0", issue.risk === "red" ? "bg-red-500" : "bg-amber-500")} />
                  <Badge variant={issue.risk === "red" ? "red" : "amber"}>{issue.category}</Badge>
                  <span className="text-sm font-semibold text-foreground flex-1 min-w-0 truncate">{issue.title}</span>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    {isRes && <Badge variant="green">Resolved</Badge>}
                    <button
                      onClick={() => setResolved(p => { const n = new Set(p); isRes ? n.delete(issue.id) : n.add(issue.id); return n; })}
                      className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {isRes ? "Unresolve" : "Dismiss"}
                    </button>
                  </div>
                </div>
                {!isRes && (
                  <div className="p-5 space-y-4">
                    <p className="text-sm text-foreground leading-relaxed">{issue.detail}</p>
                    <div>
                      <div className="text-xs font-medium text-muted-foreground mb-2">Evidence Sources</div>
                      <div className="flex flex-wrap gap-2">
                        {issue.evidence.map(e => (
                          <span key={e} className="inline-flex items-center gap-1.5 text-xs bg-muted px-2.5 py-1 rounded border border-border text-muted-foreground">
                            <BookOpen className="w-3 h-3" />{e}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs font-medium text-muted-foreground mb-2">Actions</div>
                      <div className="flex flex-wrap gap-2">
                        {issue.actions.map((action, ai) => (
                          <Btn
                            key={action}
                            variant={ai === 0 ? "primary" : "outline"}
                            size="sm"
                            onClick={() => setResolved(p => new Set([...p, issue.id]))}
                          >
                            {action}
                          </Btn>
                        ))}
                        <Btn variant="ghost" size="sm" icon={<X className="w-3 h-3" />}>Ignore</Btn>
                      </div>
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>

        <Card className="p-5">
          <h3 className="text-sm font-semibold text-foreground mb-3">Auto-Extracted Tasks</h3>
          <div className="space-y-2">
            {[
              "Confirm Metformin dosage with prescriber or pharmacy dispensing records",
              "Locate or request Empagliflozin prescription documentation",
              "Reconcile HbA1c baseline between October ASR note and November manual entry",
            ].map((task, i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-muted/30 rounded-md">
                <ClipboardList className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                <span className="text-sm text-foreground flex-1">{task}</span>
                <Btn variant="ghost" size="sm" icon={<Check className="w-3 h-3" />}>Add</Btn>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

// ─── Batch ────────────────────────────────────────────────────

function BatchScreen({ onNavigate }: { onNavigate: (s: Screen) => void }) {
  return <div className="p-6"><Card className="p-8 text-center"><h2 className="text-base font-semibold">Batch processing is not yet implemented</h2><p className="text-sm text-muted-foreground mt-2">This screen is intentionally disabled until a backend batch job endpoint is available.</p></Card></div>;
  const batch = [
    { id: "B-001", customer: "Marcus Williams", file: "recording_2024-01-15.wav",   type: "ASR", status: "processing", progress: 45 },
    { id: "B-002", customer: "Elena Rodriguez", file: "prescription_scan.pdf",      type: "OCR", status: "processing", progress: 78 },
    { id: "B-003", customer: "Priya Patel",     file: "lab_results_jan.pdf",        type: "OCR", status: "queued",     progress: 0  },
    { id: "B-004", customer: "David Kim",        file: "follow_up_audio.mp3",       type: "ASR", status: "complete",   progress: 100 },
    { id: "B-005", customer: "Sarah Chen",       file: "referral_letter_scan.tiff", type: "OCR", status: "error",      progress: 0  },
  ];

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar
        title="Batch Processing"
        subtitle="Submit and track multiple files simultaneously"
        actions={
          <>
            <Btn variant="outline" size="sm" icon={<RefreshCw className="w-3.5 h-3.5" />}>Refresh</Btn>
            <Btn variant="primary" size="sm" icon={<Plus className="w-3.5 h-3.5" />}>Add Files</Btn>
          </>
        }
      />
      <div className="flex-1 overflow-y-auto p-6 space-y-5">
        <div className="border-2 border-dashed border-border rounded-lg p-10 text-center hover:border-primary/40 transition-colors cursor-pointer bg-card">
          <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
          <p className="text-sm font-medium text-foreground">Drop files here to add to batch queue</p>
          <p className="text-xs text-muted-foreground mt-1">Audio (MP3, WAV, M4A) · PDF · Images — multiple files supported</p>
          <div className="flex gap-2 justify-center mt-4">
            <Btn variant="outline" size="sm">Browse Audio</Btn>
            <Btn variant="outline" size="sm">Browse Documents</Btn>
          </div>
        </div>

        <Card>
          <div className="flex items-center gap-3 px-5 py-3.5 border-b border-border flex-wrap gap-y-2">
            <h3 className="text-sm font-semibold text-foreground">Batch Queue</h3>
            <div className="flex items-center gap-2 ml-auto">
              <Badge variant="processing">2 Processing</Badge>
              <Badge variant="queued">1 Queued</Badge>
              <Badge variant="complete">1 Complete</Badge>
              <Badge variant="error">1 Error</Badge>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  {["ID", "Customer", "File", "Type", "Progress", "Status", ""].map(h => (
                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-5 py-2.5 whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {batch.map(item => (
                  <tr key={item.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-5 py-3.5 font-mono text-xs text-muted-foreground">{item.id}</td>
                    <td className="px-5 py-3.5 font-medium text-foreground">{item.customer}</td>
                    <td className="px-5 py-3.5 text-muted-foreground text-xs max-w-[180px] truncate">{item.file}</td>
                    <td className="px-5 py-3.5"><Badge variant="outline">{item.type}</Badge></td>
                    <td className="px-5 py-3.5 min-w-[140px]">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                          <div
                            className={cn("h-full rounded-full",
                              item.status === "error"    ? "bg-red-500" :
                              item.status === "complete" ? "bg-emerald-500" : "bg-primary"
                            )}
                            style={{ width: `${item.progress}%` }}
                          />
                        </div>
                        <span className="text-xs font-mono text-muted-foreground w-8 text-right">{item.progress}%</span>
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      <Badge variant={item.status as BadgeVariant}>{item.status}</Badge>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex gap-1">
                        {item.status === "error"    && <Btn variant="outline" size="sm" icon={<RefreshCw className="w-3 h-3" />}>Retry</Btn>}
                        {item.status === "complete" && <Btn variant="ghost"   size="sm" icon={<Eye      className="w-3 h-3" />} onClick={() => onNavigate("documents")}>View</Btn>}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}

// ─── Tasks ────────────────────────────────────────────────────

function TasksScreen({
  taskRows = [],
  onCompleteTask,
}: {
  taskRows?: TaskRow[];
  onCompleteTask?: (task: TaskRow) => void;
}) {
  const [filter, setFilter] = useState<"all" | "high" | "overdue">("all");

  const filtered = taskRows.filter(t =>
    filter === "all"     ? true :
    filter === "high"    ? t.priority === "high" :
    t.overdue
  );

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar
        title="Tasks"
        subtitle={`${taskRows.filter(t => t.overdue).length} overdue · ${taskRows.filter(t => !t.overdue).length} upcoming`}
        actions={<Btn variant="primary" size="sm" icon={<Plus className="w-3.5 h-3.5" />}>New Task</Btn>}
      />
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <div className="flex items-center gap-2">
          {(["all", "high", "overdue"] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn("px-3.5 py-1.5 text-sm rounded-md font-medium transition-colors",
                filter === f ? "bg-primary text-primary-foreground" : "bg-card border border-border text-muted-foreground hover:text-foreground"
              )}
            >
              {f === "all" ? "All Tasks" : f === "high" ? "High Priority" : "Overdue"}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          {filtered.map(task => (
            <Card key={task.id} className="p-4">
              <div className="flex items-start gap-3">
                <div className={cn("w-1 self-stretch rounded-full flex-shrink-0",
                  task.priority === "high" ? "bg-red-500" : task.priority === "medium" ? "bg-amber-500" : "bg-emerald-500"
                )} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-foreground leading-snug">{task.title}</div>
                  <div className="flex items-center gap-3 mt-2 flex-wrap">
                    <span className="text-xs text-muted-foreground flex items-center gap-1"><User className="w-3 h-3" />{task.customer}</span>
                    <span className="text-xs text-muted-foreground flex items-center gap-1"><Calendar className="w-3 h-3" />Due: {task.due}</span>
                    {task.overdue && <Badge variant="red">Overdue</Badge>}
                    <Badge variant={task.priority === "high" ? "red" : task.priority === "medium" ? "amber" : "green"}>{task.priority}</Badge>
                  </div>
                </div>
                <div className="flex gap-1.5 flex-shrink-0">
                  <Btn variant="outline" size="sm">Edit</Btn>
                  <Btn variant="ghost" size="sm" onClick={() => onCompleteTask?.(task)}><Check className="w-4 h-4" /></Btn>
                </div>
              </div>
            </Card>
          ))}
          {filtered.length === 0 && (
            <div className="text-center py-14 text-muted-foreground">
              <CheckSquare className="w-8 h-8 mx-auto mb-2 opacity-25" />
              <p className="text-sm">No tasks match this filter</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── History ──────────────────────────────────────────────────

function HistoryScreen() {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [entries, setEntries] = useState<Awaited<ReturnType<typeof listHistory>>>([]);
  useEffect(() => { listHistory().then(setEntries).catch(() => setEntries([])); }, []);

  const filtered = entries.map(entry => ({ id: entry.id, time: new Date(entry.created_at).toLocaleTimeString(), date: new Date(entry.created_at).toLocaleDateString(), customer: entry.customer_id ?? "Tenant", action: entry.action, model: entry.actor, confidence: null, status: "complete" })).filter(h => h.customer.toLowerCase().includes(search.toLowerCase()) || h.action.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar
        title="History"
        subtitle="Complete processing and review audit trail"
        actions={<Btn variant="outline" size="sm" icon={<Download className="w-3.5 h-3.5" />}>Export Log</Btn>}
      />
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <div className="flex items-center gap-3 flex-wrap gap-y-2">
          <div className="relative flex-1 min-w-48">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search history..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-sm bg-input-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring placeholder:text-muted-foreground"
            />
          </div>
          <Btn variant="outline" size="sm" icon={<Calendar className="w-3.5 h-3.5" />}>Date Range</Btn>
          <div className="flex items-center gap-1 bg-muted rounded-md p-1">
            {["all", "ASR", "OCR", "Manual"].map(t => (
              <button key={t} onClick={() => setTypeFilter(t)} className={cn("px-3 py-1 text-xs rounded font-medium transition-colors", typeFilter === t ? "bg-card shadow-sm text-foreground" : "text-muted-foreground")}>
                {t}
              </button>
            ))}
          </div>
        </div>

        <Card>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  {["Time", "Customer", "Action", "Model", "Confidence", "Status"].map(h => (
                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-5 py-2.5 whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map(item => (
                  <tr key={item.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="font-mono text-xs text-foreground">{item.time}</div>
                      <div className="text-xs text-muted-foreground">{item.date}</div>
                    </td>
                    <td className="px-5 py-3.5 font-medium text-foreground whitespace-nowrap">{item.customer}</td>
                    <td className="px-5 py-3.5 text-muted-foreground max-w-[260px] truncate">{item.action}</td>
                    <td className="px-5 py-3.5 font-mono text-xs text-muted-foreground whitespace-nowrap">{item.model}</td>
                    <td className="px-5 py-3.5"><ConfidenceLabel val={item.confidence} /></td>
                    <td className="px-5 py-3.5">
                      <Badge variant={item.status as BadgeVariant}>
                        {item.status === "complete" ? "Complete" : item.status === "review-required" ? "Review Required" : "Error"}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-5 py-3 border-t border-border text-xs text-muted-foreground">
            Showing {filtered.length} of {entries.length} entries
          </div>
        </Card>
      </div>
    </div>
  );
}

// ─── Documents ────────────────────────────────────────────────

function DocumentsScreen({
  documentRows,
  onNavigate,
  onOpenDocument,
}: {
  documentRows?: DocumentRow[];
  onNavigate: (s: Screen) => void;
  onOpenDocument?: (document: DocumentRow) => void;
}) {
  const [viewMode, setViewMode] = useState<"list" | "grid">("list");
  const [search, setSearch] = useState("");
  if (!documentRows) {
    return <div className="p-6 text-sm text-muted-foreground">Loading documents from the backend...</div>;
  }

  const docs = (documentRows ?? [
    { id: "D-1001", name: "Visit Note — Jan 15, 2024",  customer: "Sarah Chen",      type: "ASR",    confidence: 94.2, status: "review-required", date: "Jan 15, 2024" },
    { id: "D-1002", name: "Prescription Scan — Jan 12", customer: "Sarah Chen",      type: "OCR",    confidence: 87.1, status: "complete",         date: "Jan 12, 2024" },
    { id: "D-1003", name: "Lab Results PDF — Jan 8",    customer: "Sarah Chen",      type: "OCR",    confidence: 96.3, status: "complete",         date: "Jan 8, 2024" },
    { id: "D-1004", name: "Follow-up Audio Recording",  customer: "David Kim",       type: "ASR",    confidence: 91.8, status: "complete",         date: "Jan 13, 2024" },
    { id: "D-1005", name: "Referral Letter Scan",       customer: "Elena Rodriguez", type: "OCR",    confidence: null, status: "error",            date: "Jan 15, 2024" },
    { id: "D-1006", name: "Manual Note — Follow-up",    customer: "Marcus Williams", type: "Manual", confidence: null, status: "complete",         date: "Jan 15, 2024" },
  ]).filter(d => d.name.toLowerCase().includes(search.toLowerCase()) || d.customer.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar
        title="Documents"
        subtitle="All processed documents across customers"
        actions={
          <>
            <div className="flex items-center gap-1 bg-muted rounded-md p-1">
              <button onClick={() => setViewMode("list")} className={cn("p-1.5 rounded transition-colors", viewMode === "list" ? "bg-card shadow-sm text-foreground" : "text-muted-foreground")}>
                <List className="w-3.5 h-3.5" />
              </button>
              <button onClick={() => setViewMode("grid")} className={cn("p-1.5 rounded transition-colors", viewMode === "grid" ? "bg-card shadow-sm text-foreground" : "text-muted-foreground")}>
                <LayersIcon className="w-3.5 h-3.5" />
              </button>
            </div>
            <Btn variant="primary" size="sm" icon={<Plus className="w-3.5 h-3.5" />} onClick={() => onNavigate("new-processing")}>New</Btn>
          </>
        }
      />
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <div className="relative max-w-sm">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search documents..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-sm bg-input-background border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring placeholder:text-muted-foreground"
          />
        </div>

        {viewMode === "list" ? (
          <Card>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  {["Document", "Customer", "Type", "Confidence", "Status", "Date", ""].map(h => (
                    <th key={h} className="text-left text-xs font-medium text-muted-foreground px-5 py-2.5 whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {docs.map(doc => (
                  <tr key={doc.id} className="hover:bg-muted/20 transition-colors cursor-pointer group">
                    <td className="px-5 py-3.5">
                      <div className="font-medium text-foreground">{doc.name}</div>
                      <div className="text-xs text-muted-foreground font-mono">{doc.id}</div>
                    </td>
                    <td className="px-5 py-3.5 text-muted-foreground whitespace-nowrap">{doc.customer}</td>
                    <td className="px-5 py-3.5"><Badge variant="outline">{doc.type}</Badge></td>
                    <td className="px-5 py-3.5"><ConfidenceLabel val={doc.confidence} /></td>
                    <td className="px-5 py-3.5"><Badge variant={doc.status as BadgeVariant}>{doc.status === "review-required" ? "Review Required" : doc.status}</Badge></td>
                    <td className="px-5 py-3.5 text-xs text-muted-foreground whitespace-nowrap">{doc.date}</td>
                    <td className="px-5 py-3.5">
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                        <Btn variant="ghost" size="sm" onClick={() => onOpenDocument?.(doc) ?? onNavigate(doc.type === "ASR" ? "asr-review" : "ocr-review")}>Open</Btn>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {docs.map(doc => (
              <Card key={doc.id} className="p-4 cursor-pointer hover:border-primary/40 hover:shadow-sm transition-all"
                onClick={() => onOpenDocument?.(doc) ?? onNavigate(doc.type === "ASR" ? "asr-review" : "ocr-review")}>
                <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center mb-3",
                  doc.type === "ASR" ? "bg-blue-50 text-blue-600" : "bg-teal-50 text-teal-600"
                )}>
                  {doc.type === "ASR" ? <FileAudio className="w-5 h-5" /> : <FileText className="w-5 h-5" />}
                </div>
                <div className="text-sm font-medium text-foreground leading-snug mb-1">{doc.name}</div>
                <div className="text-xs text-muted-foreground mb-3">{doc.customer}</div>
                <div className="flex items-center justify-between">
                  <Badge variant={doc.status as BadgeVariant}>{doc.status === "review-required" ? "Review" : doc.status}</Badge>
                  <ConfidenceLabel val={doc.confidence} />
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Settings ─────────────────────────────────────────────────

function SettingsScreen() {
  return <div className="p-6"><Card className="p-8 text-center"><h2 className="text-base font-semibold">Settings management is not yet implemented</h2><p className="text-sm text-muted-foreground mt-2">Runtime settings are available from the authenticated backend health/configuration endpoints; editing controls are intentionally disabled.</p></Card></div>;
  const [tab, setTab] = useState("general");

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <TopBar title="Settings" subtitle="Platform configuration and service management" />
      <div className="flex border-b border-border bg-card px-6 flex-shrink-0">
        {["General", "ASR", "OCR", "Ollama", "Export", "Users"].map(t => (
          <button
            key={t}
            onClick={() => setTab(t.toLowerCase())}
            className={cn("px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap",
              tab === t.toLowerCase() ? "border-primary text-primary" : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {t}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl space-y-5">
          {tab === "general" && (
            <>
              <Card className="p-5 space-y-4">
                <h3 className="text-sm font-semibold text-foreground border-b border-border pb-3">Platform Identity</h3>
                {[
                  { label: "Organization Name", val: "Clinic ABC",          type: "text" },
                  { label: "Default Language",  val: "English (en-AU)",      type: "select", opts: ["English (en-AU)", "English (en-US)", "Mandarin (zh-CN)"] },
                  { label: "Timezone",          val: "Australia/Sydney",     type: "select", opts: ["Australia/Sydney", "UTC", "America/New_York"] },
                ].map(f => (
                  <div key={f.label} className="flex items-center gap-4">
                    <label className="text-sm text-muted-foreground w-44 flex-shrink-0">{f.label}</label>
                    {f.type === "select"
                      ? <select className="flex-1 text-sm bg-input-background border border-border rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-ring">{f.opts?.map(o => <option key={o}>{o}</option>)}</select>
                      : <input type="text" defaultValue={f.val} className="flex-1 text-sm bg-input-background border border-border rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-ring" />
                    }
                  </div>
                ))}
              </Card>

              <Card className="p-5 space-y-4">
                <h3 className="text-sm font-semibold text-foreground border-b border-border pb-3">Local Processing</h3>
                {[
                  { label: "Storage Path",         val: "/var/noteflow/data" },
                  { label: "Max Concurrent Jobs",  val: "3" },
                  { label: "Job Timeout",          val: "120 min" },
                ].map(f => (
                  <div key={f.label} className="flex items-center gap-4">
                    <label className="text-sm text-muted-foreground w-44 flex-shrink-0">{f.label}</label>
                    <input type="text" defaultValue={f.val} className="flex-1 text-sm font-mono bg-input-background border border-border rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-ring" />
                  </div>
                ))}
                <div className="flex items-center gap-4">
                  <label className="text-sm text-muted-foreground w-44 flex-shrink-0">GPU Acceleration</label>
                  <label className="flex items-center gap-2 cursor-pointer select-none">
                    <div className="relative">
                      <input type="checkbox" defaultChecked className="sr-only peer" />
                      <div className="w-9 h-5 bg-muted rounded-full peer-checked:bg-primary transition-colors" />
                      <div className="absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform peer-checked:translate-x-4" />
                    </div>
                    <span className="text-sm text-foreground">Enabled</span>
                  </label>
                </div>
              </Card>

              <div className="flex gap-3">
                <Btn variant="primary">Save Changes</Btn>
                <Btn variant="outline">Reset to Defaults</Btn>
              </div>
            </>
          )}

          {tab === "asr" && (
            <Card className="p-5 space-y-4">
              <h3 className="text-sm font-semibold text-foreground border-b border-border pb-3">ASR Configuration</h3>
              {[
                { label: "Default Model",       type: "select", opts: ["Mega-ASR v2.4", "Qwen3-ASR v3.1"] },
                { label: "Fallback Model",      type: "select", opts: ["Qwen3-ASR v3.1", "Mega-ASR v2.4"] },
                { label: "Confidence Threshold", val: "85%" },
                { label: "GPU Memory Limit",    val: "4096 MB" },
                { label: "Max Audio Length",    val: "60 min" },
              ].map(f => (
                <div key={f.label} className="flex items-center gap-4">
                  <label className="text-sm text-muted-foreground w-44 flex-shrink-0">{f.label}</label>
                  {f.type === "select"
                    ? <select className="flex-1 text-sm bg-input-background border border-border rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-ring">{f.opts?.map(o => <option key={o}>{o}</option>)}</select>
                    : <input type="text" defaultValue={f.val} className="flex-1 text-sm font-mono bg-input-background border border-border rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-ring" />
                  }
                </div>
              ))}
              <div className="flex gap-3 pt-2">
                <Btn variant="primary">Save ASR Settings</Btn>
                <Btn variant="outline">Test ASR Connection</Btn>
              </div>
            </Card>
          )}

          {tab === "ollama" && (
            <Card className="p-5 space-y-4">
              <h3 className="text-sm font-semibold text-foreground border-b border-border pb-3">Ollama Configuration</h3>
              <div className="flex items-center gap-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                <span className="text-sm text-amber-800">Ollama is connecting — llama3:8b model loading in progress</span>
              </div>
              {[
                { label: "Ollama Host",   val: "http://localhost:11434" },
                { label: "Default Model", val: "llama3:8b" },
                { label: "Context Window", val: "8192 tokens" },
                { label: "Temperature",   val: "0.1" },
              ].map(f => (
                <div key={f.label} className="flex items-center gap-4">
                  <label className="text-sm text-muted-foreground w-44 flex-shrink-0">{f.label}</label>
                  <input type="text" defaultValue={f.val} className="flex-1 text-sm font-mono bg-input-background border border-border rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-ring" />
                </div>
              ))}
              <div className="flex gap-3 pt-2">
                <Btn variant="primary">Save</Btn>
                <Btn variant="outline">Test Connection</Btn>
                <Btn variant="outline">Pull Model</Btn>
              </div>
            </Card>
          )}

          {tab === "ocr" && (
            <Card className="p-5 space-y-4">
              <h3 className="text-sm font-semibold text-foreground border-b border-border pb-3">OCR Configuration</h3>
              {[
                { label: "Default Engine",      type: "select", opts: ["OCR-v2 (Recommended)", "OCR-v1 (Legacy)"] },
                { label: "Confidence Threshold", val: "80%" },
                { label: "DPI Target",          val: "300" },
                { label: "Page Limit",          val: "50 pages" },
              ].map(f => (
                <div key={f.label} className="flex items-center gap-4">
                  <label className="text-sm text-muted-foreground w-44 flex-shrink-0">{f.label}</label>
                  {f.type === "select"
                    ? <select className="flex-1 text-sm bg-input-background border border-border rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-ring">{f.opts?.map(o => <option key={o}>{o}</option>)}</select>
                    : <input type="text" defaultValue={f.val} className="flex-1 text-sm font-mono bg-input-background border border-border rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-ring" />
                  }
                </div>
              ))}
              <div className="flex gap-3 pt-2">
                <Btn variant="primary">Save OCR Settings</Btn>
              </div>
            </Card>
          )}

          {(tab === "export" || tab === "users") && (
            <Card className="p-10 text-center text-muted-foreground">
              <Settings className="w-8 h-8 mx-auto mb-2 opacity-20" />
              <p className="text-sm font-medium">{tab.charAt(0).toUpperCase() + tab.slice(1)} settings</p>
              <p className="text-xs mt-1">Configuration options for {tab} are available here</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── App ──────────────────────────────────────────────────────

export default function App() {
  const [screen, setScreen] = useState<Screen>("dashboard");
  const [collapsed, setCollapsed] = useState(false);
  const [customerRows, setCustomerRows] = useState<CustomerRow[] | undefined>();
  const [documentRows, setDocumentRows] = useState<DocumentRow[] | undefined>();
  const [taskRows, setTaskRows] = useState<TaskRow[] | undefined>();
  const [selectedDocumentId, setSelectedDocumentId] = useState<string>();

  const refreshApiData = async () => {
    const [apiCustomers, apiDocuments, apiTasks] = await Promise.all([
      listCustomers(),
      listDocuments(),
      listTasks(),
    ]);
    const customerNameById = new Map(apiCustomers.map(customer => [customer.id, customer.full_name]));
    const documentCountByCustomer = new Map<string, number>();
    apiDocuments.forEach(document => {
      if (document.customer_id) {
        documentCountByCustomer.set(document.customer_id, (documentCountByCustomer.get(document.customer_id) ?? 0) + 1);
      }
    });
    setCustomerRows(apiCustomers.map(customer => mapCustomer(customer, documentCountByCustomer.get(customer.id) ?? 0)));
    setDocumentRows(apiDocuments.map(document => mapDocument(document, customerNameById.get(document.customer_id ?? "") ?? "Unassigned")));
    setTaskRows(apiTasks.map(task => mapTask(task, customerNameById.get(task.customer_id ?? "") ?? "Unassigned")));
  };

  useEffect(() => {
    refreshApiData().catch(error => {
      console.warn("Backend API unavailable; live customer and document controls are unavailable.", error);
    });
  }, []);

  const handleCreateCustomer = async () => {
    const suffix = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    await createCustomer({ full_name: `New Patient ${suffix}` });
    await refreshApiData();
  };

  const handleSaveManualNote = async (payload: { customerId?: string; sourceName: string; text: string }) => {
    await createManualDocument({
      customer_id: payload.customerId,
      source_name: payload.sourceName,
      text: payload.text,
    });
    await refreshApiData();
    setScreen("documents");
  };

  const handleCompleteTask = async (task: TaskRow) => {
    if (!task.backendId) return;
    await completeTask(task.backendId, task.customerId);
    await refreshApiData();
  };

  const handleProcessedDocument = async (_document: ApiDocument) => {
    await refreshApiData();
    setScreen("documents");
  };

  const openDocument = (document: DocumentRow) => {
    setSelectedDocumentId(document.id);
    setScreen(document.type === "ASR" ? "asr-review" : "ocr-review");
  };

  const screenEl = ((): React.ReactNode => {
    switch (screen) {
      case "dashboard":          return <DashboardScreen          onNavigate={setScreen} />;
      case "customers":          return <CustomersScreen           customerRows={customerRows} onCreateCustomer={handleCreateCustomer} onNavigate={setScreen} />;
      case "customer-workspace": return <CustomerWorkspaceScreen   onNavigate={setScreen} />;
      case "new-processing":     return <NewProcessingScreen       customerRows={customerRows} onSaveManualNote={handleSaveManualNote} onProcessed={handleProcessedDocument} />;
      case "documents":          return <DocumentsScreen           documentRows={documentRows} onNavigate={setScreen} onOpenDocument={openDocument} />;
      case "asr-review":         return <ASRReviewScreen           documentId={selectedDocumentId} onNavigate={setScreen} />;
      case "ocr-review":         return <OCRReviewScreen           documentId={selectedDocumentId} onNavigate={setScreen} />;
      case "compare":            return <CompareScreen             documentIds={documentRows?.slice(0, 2).map(item => item.id)} onNavigate={setScreen} />;
      case "clinical-review":    return <ClinicalReviewScreen      documentIds={selectedDocumentId ? [selectedDocumentId] : []} onNavigate={setScreen} />;
      case "batch":              return <BatchScreen               onNavigate={setScreen} />;
      case "tasks":              return <TasksScreen               taskRows={taskRows} onCompleteTask={handleCompleteTask} />;
      case "history":            return <HistoryScreen />;
      case "settings":           return <SettingsScreen />;
      default:                   return null;
    }
  })();

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar current={screen} onNavigate={setScreen} collapsed={collapsed} onToggle={() => setCollapsed(c => !c)} />
      <main className="flex-1 overflow-hidden flex flex-col min-w-0">
        {screenEl}
      </main>
    </div>
  );
}
