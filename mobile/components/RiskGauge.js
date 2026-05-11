import React from "react";
import { View, Text, StyleSheet } from "react-native";

const RISK_COLORS = { Low: "#00d4aa", Medium: "#ffd60a", High: "#e94560" };

export default function RiskGauge({ probability, riskLevel }) {
  const color = RISK_COLORS[riskLevel] || "#ffd60a";
  const pct = Math.round(probability * 100);

  return (
    <View style={styles.container}>
      <View style={[styles.ring, { borderColor: color }]}>
        <Text style={[styles.pct, { color }]}>{pct}%</Text>
        <Text style={[styles.label, { color }]}>{riskLevel?.toUpperCase()}</Text>
      </View>
      <View style={styles.zones}>
        {["Low", "Medium", "High"].map((z) => (
          <View key={z} style={styles.zoneRow}>
            <View style={[styles.dot, { backgroundColor: RISK_COLORS[z] }]} />
            <Text style={styles.zoneText}>{z}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: "center", marginVertical: 16 },
  ring: {
    width: 140,
    height: 140,
    borderRadius: 70,
    borderWidth: 8,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#16213e",
  },
  pct: { fontSize: 28, fontWeight: "800" },
  label: { fontSize: 12, fontWeight: "700", letterSpacing: 1, marginTop: 2 },
  zones: { flexDirection: "row", gap: 16, marginTop: 12 },
  zoneRow: { flexDirection: "row", alignItems: "center", gap: 4 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  zoneText: { color: "#a0a8c0", fontSize: 12 },
});
