# FILE: mobile/App.tsx

import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import ReconciliationScreen from './src/screens/ReconciliationScreen';
import VoiceEntryScreen from './src/screens/VoiceEntryScreen';
import InvoiceScanScreen from './src/screens/InvoiceScanScreen';
import PaymentDetectionScreen from './src/screens/PaymentDetectionScreen';
import { AuthProvider, useAuth } from './src/context/AuthContext';

const Stack = createNativeStackNavigator();
const queryClient = new QueryClient();

function AppNavigator() {
  const { isAuthenticated } = useAuth();
  
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <>
            <Stack.Screen name="Dashboard" component={DashboardScreen} />
            <Stack.Screen name="Reconciliation" component={ReconciliationScreen} />
            <Stack.Screen name="VoiceEntry" component={VoiceEntryScreen} />
            <Stack.Screen name="InvoiceScan" component={InvoiceScanScreen} />
            <Stack.Screen name="PaymentDetection" component={PaymentDetectionScreen} />
          </>
        ) : (
          <Stack.Screen name="Login" component={LoginScreen} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppNavigator />
      </AuthProvider>
    </QueryClientProvider>
  );
}
