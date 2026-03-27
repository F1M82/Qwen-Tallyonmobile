import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigation } from '@react-navigation/native';
import { reportAPI } from '../services/api';

const REPORTS = [
  { id: 'trial-balance', title: 'Trial Balance', icon: 'analytics-outline', color: '#2563EB' },
  { id: 'profit-loss', title: 'Profit & Loss', icon: 'trending-up-outline', color: '#10B981' },
  { id: 'balance-sheet', title: 'Balance Sheet', icon: 'bar-chart-outline', color: '#8B5CF6' },
  { id: 'outstanding', title: 'Outstanding', icon: 'time-outline', color: '#F59E0B' },
  { id: 'gst', title: 'GST Reports', icon: 'document-text-outline', color: '#EF4444' },
  { id: 'tds', title: 'TDS Reports', icon: 'receipt-outline', color: '#06B6D4' },
];

export default function ReportsScreen() {
  const navigation = useNavigation();

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Reports</Text>
      </View>

      <View style={styles.grid}>
        {REPORTS.map((report) => (
          <TouchableOpacity key={report.id} style={styles.card} onPress={() => {}}>
            <View style={[styles.iconBox, { backgroundColor: report.color + '15' }]}>
              <Ionicons name={report.icon as any} size={28} color={report.color} />
            </View>
            <Text style={styles.cardTitle}>{report.title}</Text>
            <Ionicons name="chevron-forward" size={16} color="#9CA3AF" style={styles.arrow} />
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  header: { backgroundColor: '#fff', padding: 20, paddingTop: 60, borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  title: { fontSize: 24, fontWeight: 'bold', color: '#111827' },
  grid: { padding: 16, gap: 12 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 16, flexDirection: 'row', alignItems: 'center', gap: 14, borderWidth: 1, borderColor: '#E5E7EB' },
  iconBox: { width: 48, height: 48, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  cardTitle: { flex: 1, fontSize: 16, fontWeight: '600', color: '#111827' },
  arrow: { marginLeft: 'auto' },
});
