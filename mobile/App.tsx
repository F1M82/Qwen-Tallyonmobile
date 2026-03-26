import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StatusBar } from 'expo-status-bar';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

// Auth Context
import { AuthProvider, useAuth } from './src/context/AuthContext';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import VoucherEntryScreen from './src/screens/VoucherEntryScreen';
import ReconciliationScreen from './src/screens/ReconciliationScreen';
import ReportsScreen from './src/screens/ReportsScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import VoiceEntryScreen from './src/screens/VoiceEntryScreen';
import InvoiceScanScreen from './src/screens/InvoiceScanScreen';
import PaymentDetectionScreen from './src/screens/PaymentDetectionScreen';
import PartyListScreen from './src/screens/PartyListScreen';
import PartyDetailScreen from './src/screens/PartyDetailScreen';
import VoucherListScreen from './src/screens/VoucherListScreen';
import VoucherDetailScreen from './src/screens/VoucherDetailScreen';
import ComplianceScreen from './src/screens/ComplianceScreen';
import BankReconciliationScreen from './src/screens/BankReconciliationScreen';
import GSTReconciliationScreen from './src/screens/GSTReconciliationScreen';
import AuditTrailScreen from './src/screens/AuditTrailScreen';
import TaxMindChatScreen from './src/screens/TaxMindChatScreen';

// Types
import { RootStackParamList, BottomTabParamList } from './src/types/navigation';

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<BottomTabParamList>();
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 2,
    },
  },
});

// Configure push notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

function BottomTabNavigator() {
  const { user } = useAuth();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Dashboard') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Vouchers') {
            iconName = focused ? 'document-text' : 'document-text-outline';
          } else if (route.name === 'Reconciliation') {
            iconName = focused ? 'swap-horizontal' : 'swap-horizontal-outline';
          } else if (route.name === 'Reports') {
            iconName = focused ? 'analytics' : 'analytics-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          } else {
            iconName = 'help-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2563EB',
        tabBarInactiveTintColor: '#6B7280',
        headerShown: false,
      })}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{ title: 'Home' }}
      />
      <Tab.Screen 
        name="Vouchers" 
        component={VoucherListScreen}
        options={{ title: 'Vouchers' }}
      />
      <Tab.Screen 
        name="Reconciliation" 
        component={ReconciliationScreen}
        options={{ title: 'Reconcile' }}
      />
      <Tab.Screen 
        name="Reports" 
        component={ReportsScreen}
        options={{ title: 'Reports' }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{ title: 'Settings' }}
      />
    </Tab.Navigator>
  );
}

function AppNavigator() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return null; // Or loading screen
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <>
            <Stack.Screen name="Main" component={BottomTabNavigator} />
            <Stack.Screen 
              name="VoiceEntry" 
              component={VoiceEntryScreen}
              options={{ presentation: 'modal' }}
            />
            <Stack.Screen 
              name="InvoiceScan" 
              component={InvoiceScanScreen}
              options={{ presentation: 'modal' }}
            />
            <Stack.Screen 
              name="PaymentDetection" 
              component={PaymentDetectionScreen}
              options={{ presentation: 'modal' }}
            />
            <Stack.Screen name="PartyList" component={PartyListScreen} />
            <Stack.Screen name="PartyDetail" component={PartyDetailScreen} />
            <Stack.Screen name="VoucherDetail" component={VoucherDetailScreen} />
            <Stack.Screen name="Compliance" component={ComplianceScreen} />
            <Stack.Screen name="BankReconciliation" component={BankReconciliationScreen} />
            <Stack.Screen name="GSTReconciliation" component={GSTReconciliationScreen} />
            <Stack.Screen name="AuditTrail" component={AuditTrailScreen} />
            <Stack.Screen 
              name="TaxMindChat" 
              component={TaxMindChatScreen}
              options={{ presentation: 'modal' }}
            />
          </>
        ) : (
          <>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen 
              name="Register" 
              component={RegisterScreen}
              options={{ presentation: 'modal' }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  const [notification, setNotification] = useState<Notifications.Notification | undefined>(undefined);

  useEffect(() => {
    // Register for push notifications
    if (Device.isDevice) {
      Notifications.requestPermissionsAsync();
    }

    // Listen for notifications
    const notificationListener = Notifications.addNotificationReceivedListener(
      (notification) => {
        setNotification(notification);
        // Handle notification (e.g., navigate to specific screen)
      }
    );

    // Listen for notification taps
    const responseListener = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        // Handle notification tap (e.g., navigate to specific screen)
      }
    );

    return () => {
      Notifications.removeNotificationSubscription(notificationListener);
      Notifications.removeNotificationSubscription(responseListener);
    };
  }, []);

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <AppNavigator />
            <StatusBar style="auto" />
          </AuthProvider>
        </QueryClientProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
