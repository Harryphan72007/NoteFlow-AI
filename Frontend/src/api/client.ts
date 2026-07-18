export type ApiCustomer = {
  id: string;
  customer_code: string;
  full_name: string;
  date_of_birth?: string | null;
  status: string;
  updated_at: string;
  duplicate_warning?: boolean;
};

export type ApiDocument = {
  document_id: string;
  customer_id?: string | null;
  source_type: string;
  source_name: string;
  text: string;
  language: string;
  status: string;
  processing_status: string;
  average_confidence?: number | null;
  created_at: string;
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

async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { query, headers, body, ...init } = options;
  const response = await fetch(buildUrl(path, query), {
    ...init,
    headers: {
      ...(body instanceof FormData ? {} : { "Content-Type": "application/json" }),
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

export function listTasks() {
  return apiFetch<ApiTask[]>("/tasks");
}

export function completeTask(taskId: string, customerId?: string | null) {
  return apiFetch<ApiTask>(`/tasks/${taskId}/complete`, {
    method: "POST",
    query: { customer_id: customerId },
  });
}
