import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

export default function PaymentDetectionScreen() {
  const navigation = useNavigation();
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}><Ionicons name="close" size={28} color="#111827" /></TouchableOpacity>
        <Text style={styles.title}>Payment Detection</Text>
        <View style={{ width: 28 }} />
      </View>
      <ScrollView style={styles.content}>
        <View style={styles.info}>
          <Ionicons name="notifications-outline" size={64} color="#2563EB" />
          <Text style={styles.heading}>Auto-Detect Payments</Text>
          <Text style={styles.description}>
            TaxMind monitors your SMS and email for payment notifications and automatically creates voucher entries.
          </Text>
        </View>
        <View style={styles.card}>
          <Text style={styles.cardTitle}>How it works</Text>
          {['Connect your SMS/email in Settings', 'TaxMind detects payment keywords (NEFT, UPI, RTGS)', 'Parsed amounts and UTRs are shown for review', 'One-tap posting to Tally'].map((step, i) => (
            <View key={i} style={styles.step}>
              <View style={styles.stepNum}><Text style={styles.stepNumText}>{i + 1}</Text></View>
              <Text style={styles.stepText}>{step}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, paddingTop: 60, borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  title: { fontSize: 18, fontWeight: '600', color: '#111827' },
  content: { padding: 24 },
  info: { alignItems: 'center', paddingVertical: 32 },
  heading: { fontSize: 22, fontWeight: 'bold', color: '#111827', marginTop: 16, marginBottom: 8 },
  description: { fontSize: 15, color: '#6B7280', textAlign: 'center', lineHeight: 22 },
  card: { backgroundColor: '#F9FAFB', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#E5E7EB' },
  cardTitle: { fontSize: 16, fontWeight: '600', color: '#111827', marginBottom: 16 },
  step: { flexDirection: 'row', alignItems: 'flex-start', gap: 12, marginBottom: 12 },
  stepNum: { width: 24, height: 24, borderRadius: 12, backgroundColor: '#2563EB', justifyContent: 'center', alignItems: 'center' },
  stepNumText: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  stepText: { flex: 1, fontSize: 14, color: '#374151', lineHeight: 20 },
});
