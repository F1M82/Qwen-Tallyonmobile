import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet, Alert,
  ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { voucherAPI } from '../services/api';

const VOUCHER_TYPES = ['Receipt', 'Payment', 'Sales', 'Purchase', 'Journal', 'Contra'];

export default function VoucherEntryScreen() {
  const navigation = useNavigation();
  const [form, setForm] = useState({
    voucher_type: 'Receipt', date: new Date().toISOString().split('T')[0],
    party_name: '', amount: '', narration: '', bank_name: 'Cash',
  });
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit() {
    if (!form.party_name || !form.amount) {
      Alert.alert('Error', 'Party name and amount are required');
      return;
    }
    setIsLoading(true);
    try {
      await voucherAPI.create({ ...form, amount: parseFloat(form.amount), total_amount: parseFloat(form.amount) });
      Alert.alert('Success', 'Voucher created successfully', [{ text: 'OK', onPress: () => navigation.goBack() }]);
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}><Ionicons name="close" size={28} color="#111827" /></TouchableOpacity>
        <Text style={styles.title}>New Voucher</Text>
        <TouchableOpacity onPress={handleSubmit} disabled={isLoading}>
          {isLoading ? <ActivityIndicator size="small" color="#2563EB" /> : <Text style={styles.save}>Save</Text>}
        </TouchableOpacity>
      </View>
      <ScrollView style={styles.content}>
        <Text style={styles.label}>Voucher Type</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.typeRow}>
          {VOUCHER_TYPES.map((t) => (
            <TouchableOpacity key={t} style={[styles.typeBtn, form.voucher_type === t && styles.typeBtnActive]} onPress={() => setForm(p => ({ ...p, voucher_type: t }))}>
              <Text style={[styles.typeBtnText, form.voucher_type === t && styles.typeBtnTextActive]}>{t}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {[
          { label: 'Date', key: 'date', placeholder: 'YYYY-MM-DD' },
          { label: 'Party Name', key: 'party_name', placeholder: 'e.g. Sharma Traders' },
          { label: 'Amount (₹)', key: 'amount', placeholder: '50000', keyboard: 'numeric' as const },
          { label: 'Bank / Cash Account', key: 'bank_name', placeholder: 'e.g. HDFC Bank' },
          { label: 'Narration', key: 'narration', placeholder: 'Optional description' },
        ].map(({ label, key, placeholder, keyboard }) => (
          <View key={key}>
            <Text style={styles.label}>{label}</Text>
            <TextInput
              style={styles.input}
              value={(form as any)[key]}
              onChangeText={(v) => setForm(p => ({ ...p, [key]: v }))}
              placeholder={placeholder}
              keyboardType={keyboard}
            />
          </View>
        ))}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 20, paddingTop: 60, borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  title: { fontSize: 18, fontWeight: '600', color: '#111827' },
  save: { color: '#2563EB', fontSize: 16, fontWeight: '600' },
  content: { padding: 20, gap: 4 },
  label: { fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 6, marginTop: 12 },
  input: { borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 8, padding: 12, fontSize: 15, backgroundColor: '#F9FAFB' },
  typeRow: { flexDirection: 'row', marginBottom: 4 },
  typeBtn: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: '#D1D5DB', marginRight: 8, backgroundColor: '#fff' },
  typeBtnActive: { backgroundColor: '#2563EB', borderColor: '#2563EB' },
  typeBtnText: { fontSize: 13, color: '#374151', fontWeight: '500' },
  typeBtnTextActive: { color: '#fff' },
});
