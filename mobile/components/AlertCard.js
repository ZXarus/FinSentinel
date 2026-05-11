import React from "react";
import { View, Text, StyleSheet } from "react-native";

export default function AlertCard({ text }) {
  const isOk = text.includes("✅");
  const isDanger = text.includes("🚨");
  const color = isOk ? "#00d4aa" : isDanger ? "#e94560" : "#ffd60a";

  return (
    <View style={[styles.box, { borderLeftColor: color, backgroundColor: color + "18" }]}>
      <Text style={[styles.text, { color }]}>{text}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  box: {
    borderLeftWidth: 3,
    borderRadius: 8,
    padding: 10,
    marginVertical: 4,
  },
  text: { fontSize: 13, fontWeight: "500" },
});
