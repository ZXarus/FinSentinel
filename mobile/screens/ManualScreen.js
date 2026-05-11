import React, { useState } from "react";
import {
  View, Text, TextInput, ScrollView, TouchableOpacity,
  StyleSheet, ActivityIndicator, Alert,
} from "react-native";
import { predictManual } from "../services/api";
import RiskGauge from "../components/RiskGauge";
import AlertCard from "../components/AlertCard";
import MetricCard from "../components/MetricCard";

const FIELDS = [
  { key: "company_name", label: "Company Name", numeric: false },
  { key: "revenue", label: "Revenue ($)" },
  { key: "net_income", label: "Net Income ($)" },
  { key: "total_assets", label: "Total Assets ($)" },
  { key: "total_liabilities", label: "Total Liabilities ($)" },
  { key: "cash_flow_operations", label: "Cash Flow from Operations ($)" },
  { key: "total_debt", label: "Total Debt ($)" },
  { key: "accounts_receivable", label: "Accounts Receivable ($)" },
  { key: "equity", label: "Equity ($)" },
  { key: "operating_income", label: "Operating Income ($) — optional", required: false },
];

const INITIAL = Object.fromEntries(FIELDS.map((f) => [f.key, ""]));

export default function ManualScreen() {
  const [form, setForm] = useState(INITIAL);
  const [model, setModel] = useState("random_forest");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleSubmit() {
    const missing = FIELDS.filter((f) => f.required !== false && f.numeric !== false && !form[f.key]);
    if (missing.length) {
      Alert.alert("Missing fields", missing.map((f) => f.label).join(", "));
      return;
    }
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const payload = { model_type: model };
      FIELDS.forEach(({ key, numeric }) => {
        payload[key] = numeric === false ? form[key] || "Unknown" : parseFloat(form[key]) || 0;
      });
      const data = await predictManual(payload);
      setResult(data);
    } catch (e) {
      setError(e.message.includes("Network") || e.message.includes("fetch")
        ? "Cannot reach backend. Make sure uvicorn is running on port 8000."
        : e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Manual Entry</Text>

      {FIELDS.map(({ key, label, numeric }) => (
        <View key={key} style={styles.fieldWrap}>
          <Text style={styles.fieldLabel}>{label}</Text>
          <TextInput
            style={styles.input}
            placeholder={numeric === false ? "e.g. Acme Corp" : "0"}
            placeholderTextColor="#4a4a6a"
            keyboardType={numeric === false ? "default" : "numeric"}
            value={form[key]}
            onChangeText={(v) => setForm((p) => ({ ...p, [key]: v }))}
          />
        </View>
      ))}

      {/* Model selector */}
      <Text style={styles.fieldLabel}>Model</Text>
      <View style={styles.modelRow}>
        {["random_forest", "logistic_regression"].map((m) => (
          <TouchableOpacity
            key={m}
            style={[styles.modelBtn, model === m && styles.modelBtnActive]}
            onPress={() => setModel(m)}
          >
            <Text style={[styles.modelBtnText, model === m && styles.modelBtnTextActive]}>
              {m === "random_forest" ? "Random Forest" : "Logistic Regression"}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity style={styles.submitBtn} onPress={handleSubmit} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.submitText}>Analyze Risk</Text>}
      </TouchableOpacity>

      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>⚠️ {error}</Text>
        </View>
      )}
      {result && <ResultCard result={result} />}
    </ScrollView>
  );
}

function ResultCard({ result }) {
  const metrics = Object.entries(result.key_metrics);
  return (
    <View style={styles.resultCard}>
      <Text style={styles.companyName}>{result.company_name}</Text>
      <RiskGauge probability={result.manipulation_probability} riskLevel={result.risk_level} />
      <Text style={styles.sectionTitle}>Key Metrics</Text>
      <View style={styles.metricsGrid}>
        {metrics.map(([k, v]) => <MetricCard key={k} label={k} value={v} />)}
      </View>
      <Text style={styles.sectionTitle}>Alerts</Text>
      {result.alerts.map((a, i) => <AlertCard key={i} text={a} />)}
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#0f0f1a" },
  content: { padding: 16, paddingBottom: 40 },
  heading: { color: "#e2e8f0", fontSize: 22, fontWeight: "800", marginBottom: 16 },
  fieldWrap: { marginBottom: 12 },
  fieldLabel: { color: "#a0a8c0", fontSize: 12, fontWeight: "600", marginBottom: 4, textTransform: "uppercase" },
  input: {
    backgroundColor: "#1a1a2e",
    borderWidth: 1,
    borderColor: "#2d2d50",
    borderRadius: 8,
    color: "#e2e8f0",
    padding: 12,
    fontSize: 15,
  },
  modelRow: { flexDirection: "row", gap: 8, marginBottom: 20, marginTop: 4 },
  modelBtn: {
    flex: 1, padding: 10, borderRadius: 8,
    borderWidth: 1, borderColor: "#2d2d50",
    backgroundColor: "#1a1a2e", alignItems: "center",
  },
  modelBtnActive: { backgroundColor: "#e94560", borderColor: "#e94560" },
  modelBtnText: { color: "#a0a8c0", fontSize: 13, fontWeight: "600" },
  modelBtnTextActive: { color: "#fff" },
  submitBtn: {
    backgroundColor: "#e94560", borderRadius: 10,
    padding: 14, alignItems: "center", marginBottom: 24,
  },
  submitText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  resultCard: {
    backgroundColor: "#16213e", borderRadius: 14,
    padding: 16, borderWidth: 1, borderColor: "#2d2d50",
  },
  companyName: { color: "#e2e8f0", fontSize: 18, fontWeight: "800", textAlign: "center" },
  sectionTitle: {
    color: "#e2e8f0", fontSize: 14, fontWeight: "700",
    borderBottomWidth: 1, borderBottomColor: "#e94560",
    paddingBottom: 4, marginTop: 16, marginBottom: 8,
  },
  metricsGrid: { flexDirection: "row", flexWrap: "wrap" },
  errorBox: {
    backgroundColor: "#e9456018", borderLeftWidth: 3,
    borderLeftColor: "#e94560", borderRadius: 8,
    padding: 12, marginBottom: 16,
  },
  errorText: { color: "#e94560", fontSize: 13, fontWeight: "600" },
});
