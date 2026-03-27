import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigation } from '@react-navigation/native';
import { voucherAPI } from '../services/api';

const TYPE_COLORS: Record<string, string> = {
  Receipt: '#10B981', Payment: '#EF4444', Sales: '#2563EB',
  Purchase: '#F59E0B', Journal: '#8B5CF6', Contra: '#06B6D4',
};

export default function VoucherListScreen() {
  const navigation = useNavigation();
  const { data, isLoading } = useQuery({
    queryKey: ['vouchers'],
    queryFn: () => voucherAPI.list(),
  });

  const vouchers: any[] = data?.data || [];

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Vouchers</Text>
        <TouchableOpacity
          style={styles.addBtn}
          onPress={() => navigation.navigate('VoucherEntry' as never)}
        >
          <Ionicons name="add" size={22} color="#fff" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={vouchers}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.item}
            onPress={() => navigation.navigate('VoucherDetail' as never, { voucherId: item.id } as never)}
          >
            <View style={[styles.badge, { backgroundColor: (TYPE_COLORS[item.voucher_type] || '#6B7280') + '20' }]}>
              <Text style={[styles.badgeText, { color: TYPE_COLORS[item.voucher_type] || '#6B7280' }]}>
                {item.voucher_type?.charAt(0)}
              </Text>
            </View>
            <View style={styles.info}>
              <Text style={styles.type}>{item.voucher_type} — {item.voucher_number || 'Draft'}</Text>
              <Text style={styles.date}>{item.date} · {item.narration?.slice(0, 40) || '—'}</Text>
            </View>
            <Text style={styles.amount}>₹{Number(item.total_amount || 0).toLocaleString()}</Text>
          </TouchableOpacity>
        )}
        ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>{isLoading ? 'Loading...' : 'No vouchers yet'}</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, paddingTop: 60, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  title: { fontSize: 24, fontWeight: 'bold', color: '#111827' },
  addBtn: { width: 36, height: 36, borderRadius: 18, backgroundColor: '#2563EB', justifyContent: 'center', alignItems: 'center' },
  list: { padding: 16, paddingBottom: 24 },
  item: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 12, padding: 14, gap: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  badge: { width: 40, height: 40, borderRadius: 20, justifyContent: 'center', alignItems: 'center' },
  badgeText: { fontWeight: 'bold', fontSize: 18 },
  info: { flex: 1 },
  type: { fontSize: 14, fontWeight: '600', color: '#111827' },
  date: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  amount: { fontSize: 15, fontWeight: '700', color: '#111827' },
  empty: { textAlign: 'center', color: '#6B7280', marginTop: 48, fontSize: 15 },
});
