import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigation, useRoute } from '@react-navigation/native';
import { partyAPI } from '../services/api';

export default function PartyDetailScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { partyId } = route.params as { partyId: string };

  const { data, isLoading } = useQuery({
    queryKey: ['party', partyId],
    queryFn: () => partyAPI.get(partyId),
  });

  const party = data?.data;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>{isLoading ? 'Loading...' : party?.name || 'Party'}</Text>
        <View style={{ width: 24 }} />
      </View>
      <ScrollView style={styles.content}>
        {party && (
          <>
            <View style={styles.card}>
              <Row label="Name" value={party.name} />
              <Row label="Group" value={party.group} />
              <Row label="GSTIN" value={party.gstin || 'Not provided'} />
              <Row label="Phone" value={party.phone || 'Not provided'} />
              <Row label="Email" value={party.email || 'Not provided'} />
            </View>
            <TouchableOpacity
              style={styles.reconcileBtn}
              onPress={() => navigation.navigate('Reconciliation' as never)}
            >
              <Ionicons name="swap-horizontal-outline" size={20} color="#fff" />
              <Text style={styles.reconcileBtnText}>Reconcile with this Party</Text>
            </TouchableOpacity>
          </>
        )}
      </ScrollView>
    </View>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 20, paddingTop: 60, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  title: { fontSize: 18, fontWeight: '600', color: '#111827', flex: 1, textAlign: 'center' },
  content: { padding: 16 },
  card: { backgroundColor: '#fff', borderRadius: 12, borderWidth: 1, borderColor: '#E5E7EB', overflow: 'hidden' },
  row: { flexDirection: 'row', justifyContent: 'space-between', padding: 14, borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  rowLabel: { fontSize: 13, color: '#6B7280' },
  rowValue: { fontSize: 13, fontWeight: '600', color: '#111827', maxWidth: '60%', textAlign: 'right' },
  reconcileBtn: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', backgroundColor: '#2563EB', borderRadius: 12, padding: 16, marginTop: 16, gap: 10 },
  reconcileBtnText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});
