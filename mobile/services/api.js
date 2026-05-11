const BASE_URL = "http://192.168.1.9:8000"; // Your PC's local IP

export async function predictManual(payload) {
  const res = await fetch(`${BASE_URL}/predict/manual`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Server error: ${res.status}`);
  return res.json();
}

export async function predictCSV(fileUri, fileName, modelType = "random_forest") {
  const form = new FormData();
  form.append("file", { uri: fileUri, name: fileName, type: "text/csv" });
  const res = await fetch(`${BASE_URL}/predict/csv?model_type=${modelType}`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(`Server error: ${res.status}`);
  return res.json();
}

export async function getFeatureImportance(modelType = "random_forest") {
  const res = await fetch(`${BASE_URL}/feature-importance?model_type=${modelType}`);
  if (!res.ok) throw new Error(`Server error: ${res.status}`);
  return res.json();
}

export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/health`, { signal: AbortSignal.timeout(3000) });
  return res.ok;
}
