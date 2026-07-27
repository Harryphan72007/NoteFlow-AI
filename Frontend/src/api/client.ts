export type ApiCustomer = {
  id: string;
  customer_code: string;
  full_name: string;
  date_of_birth?: string | null;
  status: string;
  updated_at: string;
  duplicate_warning?: boolean;
};

export type ApiOCRBlock = {
  id: string;
  text: string;
  corrected_text?: string | null;
  confidence?: number | null;
  bounding_box: [number, number, number, number];
  reading_order: number;
  region_type: string;
};

export type ApiOCRPage = {
  id: string;
  page_number: number;
  width: number;
  height: number;
  average_confidence?: number | null;
  blocks: ApiOCRBlock[];
};

export type ApiDocument = {
  document_id: string;
  customer_id?: string | null;
  source_type: string;
  source_name: string;
  original_filename?: string | null;
  text: string;
  corrected_text?: string | null;
  language: string;
  status: string;
  processing_status: string;
  average_confidence?: number | null;
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at?: string;
  segments?: Array<{ id: string; start: number; end: number; text: string; confidence?: number | null }>;
  pages?: ApiOCRPage[];
};

export type ApiTask = {
  id: string;
  customer_id?: string | null;
  task_text: string;
  due_date?: string | null;
  priority: string;
  status: string;
  created_at: string;
};

type RequestOptions = RequestInit & {
  query?: Record<string, string | number | null | undefined>;
};

function buildUrl(path: string, query?: RequestOptions["query"]) {
  const url = new URL(`/api${path}`, window.location.origin);
  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

async function ensureToken() {
  const existing = window.localStorage.getItem("noteflow_session");
  if (existing) return existing;
  const username = import.meta.env.VITE_AUTH_USERNAME ?? "local.user";
  const password = import.meta.env.VITE_AUTH_PASSWORD ?? "noteflow-local";
  const response = await fetch(buildUrl("/auth/login"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) throw new Error("Unable to establish a local session");
  const body = await response.json() as { access_token: string };
  window.localStorage.setItem("noteflow_session", body.access_token);
  return body.access_token;
}

async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { query, headers, body, ...init } = options;
  const token = path.startsWith("/auth/") ? undefined : await ensureToken();
  const response = await fetch(buildUrl(path, query), {
    ...init,
    headers: {
      ...(body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function listCustomers() {
  return apiFetch<ApiCustomer[]>("/customers");
}

export function createCustomer(payload: { full_name: string; customer_code?: string }) {
  return apiFetch<ApiCustomer>("/customers", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listDocuments() {
  return apiFetch<ApiDocument[]>("/documents");
}

export function createManualDocument(payload: {
  customer_id?: string;
  source_name: string;
  text: string;
  language?: string;
}) {
  return apiFetch<ApiDocument>("/documents/manual", {
    method: "POST",
    body: JSON.stringify({ language: "en", ...payload }),
  });
}

const ASR_LANGUAGE_NAMES: Record<string, string> = {
  en: "English",
  "en-au": "English",
  "en-us": "English",
  zh: "Chinese",
  "zh-cn": "Chinese",
  "zh-tw": "Chinese",
  yue: "Cantonese",
  ar: "Arabic",
  de: "German",
  fr: "French",
  es: "Spanish",
  pt: "Portuguese",
  id: "Indonesian",
  it: "Italian",
  ko: "Korean",
  ru: "Russian",
  th: "Thai",
  vi: "Vietnamese",
  ja: "Japanese",
  tr: "Turkish",
  hi: "Hindi",
  ms: "Malay",
  nl: "Dutch",
  sv: "Swedish",
  da: "Danish",
  fi: "Finnish",
  pl: "Polish",
  cs: "Czech",
  fil: "Filipino",
  fa: "Persian",
  el: "Greek",
  ro: "Romanian",
  hu: "Hungarian",
  mk: "Macedonian",
};

export function normalizeAsrLanguage(language: string) {
  const normalized = language.trim().toLowerCase();
  return ASR_LANGUAGE_NAMES[normalized] ?? language;
}

export function transcribeFile(file: File, customerId?: string, language = "en") {
  const body = new FormData();
  body.append("file", file);
  if (customerId) body.append("customer_id", customerId);
  body.append("language", normalizeAsrLanguage(language));
  body.append("save_document", "true");
  return apiFetch<ApiDocument>("/transcribe", { method: "POST", body });
}

export function ocrFile(file: File, customerId?: string, language = "en") {
  const body = new FormData();
  body.append("file", file);
  if (customerId) body.append("customer_id", customerId);
  body.append("language", language);
  body.append("preprocess", "true");
  body.append("save_document", "true");
  return apiFetch<ApiDocument>("/ocr", { method: "POST", body });
}

export function listTasks() {
  return apiFetch<ApiTask[]>("/tasks");
}

export function completeTask(taskId: string, customerId?: string | null) {
  return apiFetch<ApiTask>(`/tasks/${taskId}/complete`, {
    method: "POST",
    query: { customer_id: customerId },
  });
}

export function getDashboard() {
  return apiFetch<{ date: string; documents_today: number; pending_reviews: number; processing_queue: number; total_processed: number; activity: Array<{ day: string; asr: number; ocr: number }>; queue: Array<{ id: string; name: string; status: string; type: string }>; services: Record<string, unknown> }>("/dashboard");
}

export function listHistory() {
  return apiFetch<Array<{ id: string; action: string; actor: string; created_at: string; customer_id?: string | null; document_id?: string | null }>>("/history");
}

export function getDocument(documentId: string) {
  return apiFetch<ApiDocument>(`/documents/${documentId}`);
}

export async function getDocumentPageImage(documentId: string, pageNumber: number, processed = true) {
  const token = await ensureToken();
  const url = buildUrl(`/documents/${documentId}/pages/${pageNumber}/image`, { processed: processed ? "true" : "false" });
  const response = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!response.ok) {
    throw new Error((await response.text()) || `Unable to load page image (${response.status})`);
  }
  return URL.createObjectURL(await response.blob());
}

export function updateDocumentText(documentId: string, corrected_text: string) {
  return apiFetch<ApiDocument>(`/documents/${documentId}/text`, { method: "PATCH", body: JSON.stringify({ corrected_text }) });
}

export function finalizeDocument(documentId: string) {
  return apiFetch<ApiDocument>(`/documents/${documentId}/finalize`, { method: "POST" });
}

export function compareDocuments(documentIds: string[]) {
  return apiFetch<{ wer: number; cer: number; mismatches: unknown[]; replacements: unknown[] }>("/compare", { method: "POST", body: JSON.stringify({ document_ids: documentIds }) });
}

export function runClinicalReview(documentIds: string[], noteType = "progress_note") {
  return apiFetch<{ analysis_id: string; risk_level: string; risk_score: number; issues: unknown[]; tasks: unknown[]; summary: string }>("/clinical-review", { method: "POST", body: JSON.stringify({ document_ids: documentIds, note_type: noteType }) });
}

export function runAiAction(action: "summarize" | "translate" | "key-points" | "tasks" | "format-note", text: string, target_language?: string) {
  return apiFetch<Record<string, unknown>>(`/ai/${action}`, { method: "POST", body: JSON.stringify({ text, target_language }) });
}

export function health() {
  return apiFetch<{ status: string; services: Record<string, unknown> }>("/../health");
}
