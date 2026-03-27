import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

const COMPLIANCE_ITEMS = [
  { name: 'GSTR-1', due: '11th of next month', frequency: 'Monthly', status: 'due-soon', color: '#F59E0B' },
  { name: 'GSTR-3B', due: '20th of next month', frequency: 'Monthly', status: 'pending', color: '#10B981' },
  { name: 'GSTR-9', due: '31 Dec', frequency: 'Annual', status: 'pending', color: '#10B981' },
  { name: 'TDS Return (26Q)', due: '31st of next month', frequency: 'Quarterly', status: 'overdue', color: '#EF4444' },
  { name: 'Advance Tax', due: '15th of quarter end', frequency: 'Quarterly', status: 'pending', color: '#10B981' },
  { name: 'Income Tax Return', due: '31 Jul', frequency: 'Annual', status: 'pending', color: '#10B981' },
];

export default function ComplianceScreen() {
  const navigation = useNavigation();
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}><Ionicons name="arrow-back" size={24} color="#111827" /></TouchableOpacity>
        <Text style={styles.title}>Compliance Calendar</Text>
        <View style={{ width: 24 }} />
      </View>
      <ScrollView style={styles.content}>
        {COMPLIANCE_ITEMS.map((item) => (
          <View key={item.name} style={styles.item}>
            <View style={[styles.indicator, { backgroundColor: item.color }]} />
            <View style={styles.info}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.due}>Due: {item.due} · {item.frequency}</Text>
            </View>
            <View style={[styles.badge, { backgroundColor: item.color + '20' }]}>
              <Text style={[styles.badgeText, { color: item.color }]}>{item.status}</Text>
            </View>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 20, paddingTop: 60, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  title: { fontSize: 18, fontWeight: '600', color: '#111827' },
  content: { padding: 16 },
  item: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 8, gap: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  indicator: { width: 8, height: 8, borderRadius: 4 },
  info: { flex: 1 },
  name: { fontSize: 15, fontWeight: '600', color: '#111827' },
  due: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  badge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8 },
  badgeText: { fontSize: 11, fontWeight: '600', textTransform: 'capitalize' },
});
