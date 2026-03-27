import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigation } from '@react-navigation/native';
import { api } from '../services/api';

const ACTION_COLORS: Record<string, string> = {
  created: '#10B981', updated: '#2563EB', deleted: '#EF4444',
  posted: '#8B5CF6', approved: '#F59E0B',
};

export default function AuditTrailScreen() {
  const navigation = useNavigation();
  const { data, isLoading } = useQuery({
    queryKey: ['audit-trail'],
    queryFn: () => api.get('/audit/'),
  });

  const logs: any[] = data?.data || [];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}><Ionicons name="arrow-back" size={24} color="#111827" /></TouchableOpacity>
        <Text style={styles.title}>Audit Trail</Text>
        <View style={{ width: 24 }} />
      </View>
      <FlatList
        data={logs}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <View style={[styles.dot, { backgroundColor: ACTION_COLORS[item.action] || '#6B7280' }]} />
            <View style={styles.info}>
              <Text style={styles.action}>{item.action} · {item.entity_type}</Text>
              <Text style={styles.time}>{new Date(item.created_at).toLocaleString()}</Text>
            </View>
            <Text style={styles.ip}>{item.ip_address || '—'}</Text>
          </View>
        )}
        ItemSeparatorComponent={() => <View style={{ height: 1, backgroundColor: '#F3F4F6', marginLeft: 56 }} />}
        ListEmptyComponent={<Text style={styles.empty}>{isLoading ? 'Loading...' : 'No audit logs yet'}</Text>}
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 20, paddingTop: 60, borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  title: { fontSize: 18, fontWeight: '600', color: '#111827' },
  listContent: { paddingBottom: 24 },
  item: { flexDirection: 'row', alignItems: 'center', padding: 16, gap: 12 },
  dot: { width: 10, height: 10, borderRadius: 5 },
  info: { flex: 1 },
  action: { fontSize: 14, fontWeight: '600', color: '#111827', textTransform: 'capitalize' },
  time: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  ip: { fontSize: 11, color: '#9CA3AF' },
  empty: { textAlign: 'center', color: '#6B7280', marginTop: 64, fontSize: 15 },
});
