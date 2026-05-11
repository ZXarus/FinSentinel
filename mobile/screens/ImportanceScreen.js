import React, { useState, useEffect } from "react";
import {
  View, Text, ScrollView, TouchableOpacity,
  StyleSheet, ActivityIndicator, Alert,
} from "react-native";
import { getFeatureImportance } from "../services/api";

export default function ImportanceScreen() {
  const [model, setModel] = useState("random_forest");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { load(); }, [model]);

  async function load() {
    setLoading(true);
    try {
      const res = await getFeatureImportance(model);
      const paired = res.features
        .map((f, i) => ({ name: f, value: res.importances[i] }))
        .sort((a, b) => b.value - a.value);
      setData(paired);
    } catch (e) {
      Alert.alert("Error", e.message);
    } finally {
      setLoading(false);
    }
  }

  const max = data ? data[0].value : 1;

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Feature Importance</Text>

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

      {loading && <ActivityIndicator color="#e94560" style={{ marginTop: 40 }} />}

      {data && data.map(({ name, value }) => (
        <View key={name} style={styles.barRow}>
          <Text style={styles.barLabel}>{name.replace(/_/g, " ")}</Text>
          <View style={styles.barTrack}>
            <View style={[styles.barFill, { width: `${(value / max) * 100}%` }]} />
          </View>
          <Text style={styles.barValue}>{(value * 100).toFixed(1)}%</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#0f0f1a" },
  content: { padding: 16, paddingBottom: 40 },
  heading: { color: "#e2e8f0", fontSize: 22, fontWeight: "800", marginBottom: 16 },
  modelRow: { flexDirection: "row", gap: 8, marginBottom: 20 },
  modelBtn: {
    flex: 1, padding: 10, borderRadius: 8,
    borderWidth: 1, borderColor: "#2d2d50",
    backgroundColor: "#1a1a2e", alignItems: "center",
  },
  modelBtnActive: { backgroundColor: "#e94560", borderColor: "#e94560" },
  modelBtnText: { color: "#a0a8c0", fontSize: 13, fontWeight: "600" },
  modelBtnTextActive: { color: "#fff" },
  barRow: { marginBottom: 14 },
  barLabel: {
    color: "#a0a8c0", fontSize: 12, fontWeight: "600",
    textTransform: "uppercase", marginBottom: 4,
  },
  barTrack: {
    height: 10, backgroundColor: "#1a1a2e",
    borderRadius: 5, overflow: "hidden",
  },
  barFill: { height: "100%", backgroundColor: "#e94560", borderRadius: 5 },
  barValue: { color: "#e2e8f0", fontSize: 12, marginTop: 2, fontWeight: "700" },
});
