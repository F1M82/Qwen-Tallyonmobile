import React, { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  Alert, ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../context/AuthContext';

export default function RegisterScreen() {
  const navigation = useNavigation();
  const { register } = useAuth();
  const [form, setForm] = useState({ email: '', password: '', full_name: '', firm_name: '', is_ca: true });
  const [isLoading, setIsLoading] = useState(false);

  async function handleRegister() {
    if (!form.email || !form.password || !form.full_name) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }
    setIsLoading(true);
    try {
      await register(form);
    } catch (error: any) {
      Alert.alert('Registration Failed', error.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Create Account</Text>
          <Text style={styles.subtitle}>Join TaxMind Platform</Text>
        </View>

        {[
          { label: 'Full Name *', key: 'full_name', placeholder: 'CA Ramesh Kumar' },
          { label: 'Email *', key: 'email', placeholder: 'ca@example.com' },
          { label: 'Password *', key: 'password', placeholder: '••••••••', secure: true },
          { label: 'Firm Name', key: 'firm_name', placeholder: 'Kumar & Associates' },
        ].map(({ label, key, placeholder, secure }) => (
          <View key={key}>
            <Text style={styles.label}>{label}</Text>
            <TextInput
              style={styles.input}
              value={(form as any)[key]}
              onChangeText={(v) => setForm(prev => ({ ...prev, [key]: v }))}
              placeholder={placeholder}
              secureTextEntry={secure}
              autoCapitalize={key === 'email' ? 'none' : 'words'}
              keyboardType={key === 'email' ? 'email-address' : 'default'}
              editable={!isLoading}
            />
          </View>
        ))}

        <TouchableOpacity
          style={[styles.button, isLoading && styles.buttonDisabled]}
          onPress={handleRegister}
          disabled={isLoading}
        >
          {isLoading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Create Account</Text>}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  content: { flexGrow: 1, padding: 24, paddingTop: 60, gap: 16 },
  header: { marginBottom: 16 },
  backBtn: { marginBottom: 16 },
  backText: { color: '#2563EB', fontSize: 16 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#111827' },
  subtitle: { fontSize: 14, color: '#6B7280', marginTop: 4 },
  label: { fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 6 },
  input: { borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 8, padding: 12, fontSize: 16, backgroundColor: '#F9FAFB' },
  button: { backgroundColor: '#2563EB', borderRadius: 8, padding: 16, alignItems: 'center', marginTop: 8 },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' },
});
