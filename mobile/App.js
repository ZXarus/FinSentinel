import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Text } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";

import ManualScreen from "./screens/ManualScreen";
import CSVScreen from "./screens/CSVScreen";
import ImportanceScreen from "./screens/ImportanceScreen";

const Tab = createBottomTabNavigator();

const ICONS = { Manual: "🔢", Batch: "📂", Insights: "📊" };

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: () => <Text style={{ fontSize: 20 }}>{ICONS[route.name]}</Text>,
            tabBarStyle: {
              backgroundColor: "#1a1a2e",
              borderTopColor: "#2d2d50",
              height: 60,
              paddingBottom: 8,
            },
            tabBarActiveTintColor: "#e94560",
            tabBarInactiveTintColor: "#a0a8c0",
            tabBarLabelStyle: { fontSize: 11, fontWeight: "700" },
            headerStyle: { backgroundColor: "#16213e", borderBottomColor: "#2d2d50", borderBottomWidth: 1 },
            headerTintColor: "#e2e8f0",
            headerTitleStyle: { fontWeight: "800" },
            headerTitle: "🏦 FinSentinel",
          })}
        >
          <Tab.Screen name="Manual" component={ManualScreen} />
          <Tab.Screen name="Batch" component={CSVScreen} />
          <Tab.Screen name="Insights" component={ImportanceScreen} />
        </Tab.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
