import React, { useState } from "react";
import {
  View, Text, TouchableOpacity, ScrollView,
  StyleSheet, ActivityIndicator, Alert,
} from "react-native";
import * as DocumentPicker from "expo-document-picker";
import { predictCSV } from "../services/api";
import AlertCard from "../components/AlertCard";

const RISK_COLORS = { Low: "#00d4aa", Medium: "#ffd60a", High: "#e94560" };

export default function CSVScreen() {
  const [model, setModel] = useState("random_forest");
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState(null);
  const [results, setResults] = useState([]);
  const [expanded, setExpanded] = useState(null);

  async function handlePick() {
    const picked = await DocumentPicker.getDocumentAsync({ type: "text/comma-separated-values" });
    if (picked.canceled) return;
    const file = picked.assets[0];
    setLoading(true);
    setSummary(null);
    setResults([]);
    try {
      const data = await predictCSV(file.uri, file.name, model);
      setSummary(data.summary);
      setResults(data.results);
    } catch (e) {
      Alert.alert("Error", e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>CSV Batch Upload</Text>

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

      <TouchableOpacity style={styles.uploadBtn} onPress={handlePick} disabled={loading}>
        {loading
          ? <ActivityIndicator color="#fff" />
          : <Text style={styles.uploadText}>📂  Pick CSV File</Text>}
      </TouchableOpacity>

      {summary && (
        <View style={styles.summaryCard}>
          <Text style={styles.sectionTitle}>Batch Summary</Text>
          <View style={styles.summaryGrid}>
            <SummaryItem label="Total" value={summary.total_companies} />
            <SummaryItem label="Flagged" value={summary.flagged} color="#e94560" />
            <SummaryItem label="High Risk" value={summary.high_risk} color="#e94560" />
            <SummaryItem label="Medium" value={summary.medium_risk} color="#ffd60a" />
            <SummaryItem label="Low Risk" value={summary.low_risk} color="#00d4aa" />
            <SummaryItem label="Avg Score" value={`${summary.avg_risk_score}%`} />
          </View>
        </View>
      )}

      {results.map((r, i) => (
        <TouchableOpacity
          key={i}
          style={styles.resultRow}
          onPress={() => setExpanded(expanded === i ? null : i)}
        >
          <View style={styles.resultRowHeader}>
            <Text style={styles.companyName}>{r.company_name}</Text>
            <View style={[styles.pill, { borderColor: RISK_COLORS[r.risk_level] }]}>
              <Text style={[styles.pillText, { color: RISK_COLORS[r.risk_level] }]}>
                {r.risk_level}  {r.risk_score}%
              </Text>
            </View>
          </View>
          {expanded === i && (
            <View style={styles.expandedContent}>
              {r.alerts.map((a, j) => <AlertCard key={j} text={a} />)}
            </View>
          )}
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

function SummaryItem({ label, value, color }) {
  return (
    <View style={styles.summaryItem}>
      <Text style={[styles.summaryValue, color && { color }]}>{value}</Text>
      <Text style={styles.summaryLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#0f0f1a" },
  content: { padding: 16, paddingBottom: 40 },
  heading: { color: "#e2e8f0", fontSize: 22, fontWeight: "800", marginBottom: 16 },
  fieldLabel: { color: "#a0a8c0", fontSize: 12, fontWeight: "600", marginBottom: 4, textTransform: "uppercase" },
  modelRow: { flexDirection: "row", gap: 8, marginBottom: 16 },
  modelBtn: {
    flex: 1, padding: 10, borderRadius: 8,
    borderWidth: 1, borderColor: "#2d2d50",
    backgroundColor: "#1a1a2e", alignItems: "center",
  },
  modelBtnActive: { backgroundColor: "#e94560", borderColor: "#e94560" },
  modelBtnText: { color: "#a0a8c0", fontSize: 13, fontWeight: "600" },
  modelBtnTextActive: { color: "#fff" },
  uploadBtn: {
    backgroundColor: "#e94560", borderRadius: 10,
    padding: 14, alignItems: "center", marginBottom: 20,
  },
  uploadText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  summaryCard: {
    backgroundColor: "#16213e", borderRadius: 14,
    padding: 16, marginBottom: 16,
    borderWidth: 1, borderColor: "#2d2d50",
  },
  sectionTitle: {
    color: "#e2e8f0", fontSize: 14, fontWeight: "700",
    borderBottomWidth: 1, borderBottomColor: "#e94560",
    paddingBottom: 4, marginBottom: 12,
  },
  summaryGrid: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  summaryItem: {
    backgroundColor: "#1a1a2e", borderRadius: 8,
    padding: 10, alignItems: "center", minWidth: 80,
    borderWidth: 1, borderColor: "#2d2d50",
  },
  summaryValue: { color: "#e2e8f0", fontSize: 20, fontWeight: "800" },
  summaryLabel: { color: "#a0a8c0", fontSize: 11, marginTop: 2 },
  resultRow: {
    backgroundColor: "#16213e", borderRadius: 10,
    padding: 12, marginBottom: 8,
    borderWidth: 1, borderColor: "#2d2d50",
  },
  resultRowHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  companyName: { color: "#e2e8f0", fontSize: 14, fontWeight: "700", flex: 1 },
  pill: {
    borderWidth: 1, borderRadius: 20,
    paddingHorizontal: 10, paddingVertical: 3,
  },
  pillText: { fontSize: 12, fontWeight: "700" },
  expandedContent: { marginTop: 10 },
});
