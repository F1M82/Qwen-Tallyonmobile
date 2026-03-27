import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

export default function GSTReconciliationScreen() {
  const navigation = useNavigation();
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}><Ionicons name="arrow-back" size={24} color="#111827" /></TouchableOpacity>
        <Text style={styles.title}>GST Reconciliation (2A/2B)</Text>
        <View style={{ width: 24 }} />
      </View>
      <ScrollView style={styles.content}>
        <View style={styles.summary}>
          {[{ label: 'In GSTR-2B', value: '0', color: '#10B981' }, { label: 'In Books', value: '0', color: '#2563EB' }, { label: 'Mismatch', value: '0', color: '#EF4444' }].map(item => (
            <View key={item.label} style={styles.card}>
              <Text style={[styles.cardValue, { color: item.color }]}>{item.value}</Text>
              <Text style={styles.cardLabel}>{item.label}</Text>
            </View>
          ))}
        </View>
        <View style={styles.placeholder}>
          <Ionicons name="document-text-outline" size={48} color="#9CA3AF" />
          <Text style={styles.placeholderText}>Match your purchase register with GSTR-2B to identify ITC mismatches</Text>
          <TouchableOpacity style={styles.startBtn}>
            <Text style={styles.startBtnText}>Start 2B Reconciliation</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 20, paddingTop: 60, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  title: { fontSize: 16, fontWeight: '600', color: '#111827' },
  content: { padding: 16 },
  summary: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  card: { flex: 1, backgroundColor: '#fff', borderRadius: 12, padding: 14, alignItems: 'center', borderWidth: 1, borderColor: '#E5E7EB' },
  cardValue: { fontSize: 24, fontWeight: 'bold' },
  cardLabel: { fontSize: 11, color: '#6B7280', marginTop: 4, textAlign: 'center' },
  placeholder: { alignItems: 'center', padding: 48, backgroundColor: '#fff', borderRadius: 12, borderWidth: 1, borderColor: '#E5E7EB', gap: 12 },
  placeholderText: { fontSize: 14, color: '#6B7280', textAlign: 'center', lineHeight: 20 },
  startBtn: { backgroundColor: '#2563EB', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
  startBtnText: { color: '#fff', fontWeight: '600', fontSize: 15 },
});
