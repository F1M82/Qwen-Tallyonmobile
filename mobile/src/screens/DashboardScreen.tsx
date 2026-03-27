import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { reportAPI, complianceAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useNavigation } from '@react-navigation/native';

export default function DashboardScreen() {
  // Fix: use generic useNavigation — Dashboard is a tab screen, not stack screen
  const navigation = useNavigation<any>();
  const { user } = useAuth();
  const [refreshing, setRefreshing] = React.useState(false);

  const { data: reports, refetch } = useQuery({
    queryKey: ['dashboard-reports'],
    queryFn: () => reportAPI.trialBalance(),
  });

  const { data: compliance } = useQuery({
    queryKey: ['compliance-calendar'],
    queryFn: () => complianceAPI.calendar(),
  });

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    refetch().finally(() => setRefreshing(false));
  }, [refetch]);

  const quickActions = [
    { icon: 'mic-outline' as const, title: 'Voice Entry', screen: 'VoiceEntry' as const, color: '#3B82F6' },
    { icon: 'camera-outline' as const, title: 'Scan Invoice', screen: 'InvoiceScan' as const, color: '#10B981' },
    { icon: 'swap-horizontal-outline' as const, title: 'Reconcile', screen: 'Reconciliation' as const, color: '#F59E0B' },
    { icon: 'chatbubble-outline' as const, title: 'Ask TaxMind', screen: 'TaxMindChat' as const, color: '#8B5CF6' },
  ];

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hello, {user?.full_name || 'User'}</Text>
          <Text style={styles.firmName}>{user?.firm_name || 'CA Practice'}</Text>
        </View>
        <TouchableOpacity style={styles.notificationBtn}>
          <Ionicons name="notifications-outline" size={24} color="#374151" />
        </TouchableOpacity>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.quickActionsGrid}>
          {quickActions.map((action, index) => (
            <TouchableOpacity
              key={index}
              style={[styles.quickActionCard, { borderLeftColor: action.color }]}
              onPress={() => navigation.navigate(action.screen)}
            >
              <Ionicons name={action.icon} size={28} color={action.color} />
              <Text style={styles.quickActionTitle}>{action.title}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Financial Summary */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Financial Summary</Text>
        <View style={styles.summaryCards}>
          <View style={styles.summaryCard}>
            <Text style={styles.summaryLabel}>Total Assets</Text>
            <Text style={styles.summaryValue}>₹{reports?.data?.assets?.toLocaleString() || '0'}</Text>
          </View>
          <View style={styles.summaryCard}>
            <Text style={styles.summaryLabel}>Total Liabilities</Text>
            <Text style={styles.summaryValue}>₹{reports?.data?.liabilities?.toLocaleString() || '0'}</Text>
          </View>
          <View style={styles.summaryCard}>
            <Text style={styles.summaryLabel}>Outstanding</Text>
            <Text style={styles.summaryValue}>₹{reports?.data?.outstanding?.toLocaleString() || '0'}</Text>
          </View>
        </View>
      </View>

      {/* Compliance Calendar */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Compliance Calendar</Text>
        <View style={styles.complianceList}>
          {compliance?.data?.upcoming?.slice(0, 3).map((item: any, index: number) => (
            <View key={index} style={styles.complianceItem}>
              <View
                style={[
                  styles.complianceIndicator,
                  {
                    backgroundColor:
                      item.status === 'overdue' ? '#EF4444'
                      : item.status === 'due-soon' ? '#F59E0B'
                      : '#10B981',
                  },
                ]}
              />
              <View style={styles.complianceInfo}>
                <Text style={styles.complianceTitle}>{item.return_type}</Text>
                <Text style={styles.complianceDate}>Due: {item.due_date}</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </View>
          ))}
        </View>
      </View>

      {/* Tally Connection Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tally Connection</Text>
        <View style={styles.connectionCard}>
          <View style={styles.connectionStatus}>
            <View style={styles.statusDot} />
            <Text style={styles.statusText}>Connected</Text>
          </View>
          <Text style={styles.connectionSubtext}>Last sync: 2 minutes ago</Text>
          <TouchableOpacity style={styles.syncButton}>
            <Text style={styles.syncButtonText}>Sync Now</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, paddingTop: 60, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  greeting: { fontSize: 24, fontWeight: 'bold', color: '#111827' },
  firmName: { fontSize: 14, color: '#6B7280', marginTop: 4 },
  notificationBtn: { padding: 8 },
  section: { padding: 20 },
  sectionTitle: { fontSize: 18, fontWeight: '600', color: '#111827', marginBottom: 12 },
  quickActionsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  quickActionCard: { width: '48%', backgroundColor: '#fff', padding: 16, borderRadius: 12, borderWidth: 1, borderLeftWidth: 4, borderColor: '#E5E7EB', gap: 8 },
  quickActionTitle: { fontSize: 14, fontWeight: '600', color: '#374151' },
  summaryCards: { gap: 12 },
  summaryCard: { backgroundColor: '#fff', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  summaryLabel: { fontSize: 12, color: '#6B7280', marginBottom: 4 },
  summaryValue: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  complianceList: { backgroundColor: '#fff', borderRadius: 12, borderWidth: 1, borderColor: '#E5E7EB', overflow: 'hidden' },
  complianceItem: { flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  complianceIndicator: { width: 8, height: 8, borderRadius: 4, marginRight: 12 },
  complianceInfo: { flex: 1 },
  complianceTitle: { fontSize: 14, fontWeight: '600', color: '#111827' },
  complianceDate: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  connectionCard: { backgroundColor: '#fff', padding: 16, borderRadius: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  connectionStatus: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  statusDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#10B981', marginRight: 8 },
  statusText: { fontSize: 14, fontWeight: '600', color: '#111827' },
  connectionSubtext: { fontSize: 12, color: '#6B7280', marginBottom: 12 },
  syncButton: { backgroundColor: '#2563EB', padding: 10, borderRadius: 6, alignItems: 'center' },
  syncButtonText: { color: '#fff', fontSize: 14, fontWeight: '600' },
});
