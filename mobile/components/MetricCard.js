import React from "react";
import { View, Text, StyleSheet } from "react-native";

export default function MetricCard({ label, value }) {
  return (
    <View style={styles.card}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{typeof value === "number" ? value.toFixed(4) : value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1a1a2e",
    borderRadius: 10,
    padding: 12,
    flex: 1,
    margin: 4,
    borderWidth: 1,
    borderColor: "#2d2d50",
  },
  label: { color: "#a0a8c0", fontSize: 11, fontWeight: "600", textTransform: "uppercase", letterSpacing: 0.5 },
  value: { color: "#e2e8f0", fontSize: 16, fontWeight: "800", marginTop: 4 },
});
