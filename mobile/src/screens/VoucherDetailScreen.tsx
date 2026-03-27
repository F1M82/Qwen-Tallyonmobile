import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';
import { useQuery } from '@tanstack/react-query';
import { voucherAPI } from '../services/api';

export default function VoucherDetailScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { voucherId } = route.params as { voucherId: string };
  const { data, isLoading } = useQuery({ queryKey: ['voucher', voucherId], queryFn: () => voucherAPI.get(voucherId) });
  const v = data?.data;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}><Ionicons name="arrow-back" size={24} color="#111827" /></TouchableOpacity>
        <Text style={styles.title}>Voucher Detail</Text>
        <View style={{ width: 24 }} />
      </View>
      <ScrollView style={styles.content}>
        {isLoading && <Text style={styles.loading}>Loading...</Text>}
        {v && (
          <View style={styles.card}>
            {[
              ['Type', v.voucher_type], ['Number', v.voucher_number || '—'],
              ['Date', v.date], ['Amount', `₹${Number(v.total_amount).toLocaleString()}`],
              ['Status', v.status], ['Source', v.source || '—'], ['Narration', v.narration || '—'],
            ].map(([label, value]) => (
              <View key={label} style={styles.row}>
                <Text style={styles.label}>{label}</Text>
                <Text style={styles.value}>{value}</Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 20, paddingTop: 60, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  title: { fontSize: 18, fontWeight: '600', color: '#111827' },
  content: { padding: 16 },
  loading: { textAlign: 'center', color: '#6B7280', marginTop: 48 },
  card: { backgroundColor: '#fff', borderRadius: 12, borderWidth: 1, borderColor: '#E5E7EB', overflow: 'hidden' },
  row: { flexDirection: 'row', justifyContent: 'space-between', padding: 14, borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  label: { fontSize: 13, color: '#6B7280' },
  value: { fontSize: 13, fontWeight: '600', color: '#111827', maxWidth: '60%', textAlign: 'right' },
});
